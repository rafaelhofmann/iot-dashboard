# Import packages
from tflite_runtime.interpreter import Interpreter
import os
import cv2
import numpy as np
import time
from threading import Thread
import configuration
import json


class VideoStream:
    """
    Define VideoStream class to handle streaming of video from webcam in separate processing thread
    Source - Adrian Rosebrock, PyImageSearch: https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
    """

    def __init__(self, resolution=(640, 480), framerate=30):
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*"MJPG"))
        ret = self.stream.set(3, resolution[0])
        ret = self.stream.set(4, resolution[1])

        (self.grabbed, self.frame) = self.stream.read()

        self.stopped = False

    def start(self):
        Thread(target=self.update, args=()).start()
        return self

    def update(self):
        while True:
            if self.stopped:
                self.stream.release()
                return

            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
        return self.frame

    def stop(self):
        self.stopped = True


config = configuration.load_configuration("umbrella_detection")

MODEL_DIR = config["model_dir"]
MODEL_NAME = "model.tflite"
LABELMAP_NAME = "labelmap.txt"
THRESHOLD = 0.5
CAMERA_WIDTH = 1280
CAMERA_HEIGHT = 720
CAMERA_FRAME_RATE = 30
INTERESTING_LABELS = ["umbrella"]


CWD_PATH = os.getcwd()
MODEL_PATH = os.path.join(CWD_PATH, MODEL_DIR, MODEL_NAME)
LABELS_PATH = os.path.join(CWD_PATH, MODEL_DIR, LABELMAP_NAME)

with open(LABELS_PATH, "r") as f:
    labels = [line.strip() for line in f.readlines()]

# Have to do a weird fix for label map if using the COCO "starter model" from
# https://www.tensorflow.org/lite/models/object_detection/overview
# First label is '???', which has to be removed.
if labels[0] == "???":
    del labels[0]

interpreter = Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

# Get model details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]["shape"][1]
width = input_details[0]["shape"][2]

input_mean = 127.5
input_std = 127.5

# Initialize video stream
videostream = VideoStream(resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=CAMERA_FRAME_RATE).start()
time.sleep(1)

# Grab frame from video stream
original_frame = videostream.read()

# Acquire frame and resize to expected shape [1xHxWx3]
frame = original_frame.copy()
frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
frame_resized = cv2.resize(frame_rgb, (width, height))
input_data = np.expand_dims(frame_resized, axis=0)

# Perform the actual detection by running the model with the image as input
interpreter.set_tensor(input_details[0]["index"], input_data)
interpreter.invoke()

# Retrieve detection results
boxes = interpreter.get_tensor(output_details[0]["index"])[0]
classes = interpreter.get_tensor(output_details[1]["index"])[0]
scores = interpreter.get_tensor(output_details[2]["index"])[0]


def has_found_object(i):
    label_name = labels[int(classes[i])]
    return label_name in INTERESTING_LABELS and scores[i] >= THRESHOLD


# Loop over all detections
# TODO: Remove loop
for i in range(len(scores)):
    if has_found_object(i):
        ymin = int(max(1, (boxes[i][0] * CAMERA_HEIGHT)))
        xmin = int(max(1, (boxes[i][1] * CAMERA_WIDTH)))
        ymax = int(min(CAMERA_HEIGHT, (boxes[i][2] * CAMERA_HEIGHT)))
        xmax = int(min(CAMERA_WIDTH, (boxes[i][3] * CAMERA_WIDTH)))

        cv2.rectangle(frame, (xmin, ymin), (xmax, ymax), (10, 255, 0), 2)

        confidence_percentage = int(scores[i] * 100)

        # Example: 'person: 72%'
        label_name = labels[int(classes[i])]
        label = "%s: %d%%" % (label_name, confidence_percentage)
        labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2)  # Get font size
        # Make sure not to draw label too close to top of window
        label_ymin = max(ymin, labelSize[1] + 10)
        # Draw white box to put label text in
        cv2.rectangle(frame, (xmin, label_ymin - labelSize[1] - 10), (xmin + labelSize[0], label_ymin + baseLine - 10), (255, 255, 255), cv2.FILLED)
        cv2.putText(frame, label, (xmin, label_ymin - 7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2)  # Draw label text

        # Print info
        print("Object " + str(i) + ": " + label_name + " with confidence " + str(int(scores[i] * 100)))

# TODO: Remove me
cv2.imwrite("test.jpg", frame)

found_results = any(has_found_object(i) for i in range(len(scores)))
json_string = json.dumps({"umbrella_detected": found_results})
print(json_string)

# Clean up
videostream.stop()
