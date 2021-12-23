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
THRESHOLD = 0.4
CAMERA_WIDTH = 1920
CAMERA_HEIGHT = 1080
CAMERA_FRAME_RATE = 30

# Because any COCO dataset is mainly trained with open umbrellas and not closed, we do have some slight issues here,
# as our umbrella at home will always be closed.
# So we become really (really) generous with what labels we accept as an umbrella.
# Of course this increases the rate of error and we might recognize things as an umbrella that is really not an umbrella.
UMBRELLA_LABELS = ["umbrella", "tie", "vase", "suitcase"]

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

# Initialize video stream
videostream = VideoStream(resolution=(CAMERA_WIDTH, CAMERA_HEIGHT), framerate=CAMERA_FRAME_RATE).start()
time.sleep(1)

# Grab frame from video stream
original_frame = videostream.read()

# Acquire frame and resize to expected shape [1xHxWx3]
frame = original_frame.copy()
# frame = cv2.imread("test_umbrella.jpg")
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
    return label_name in UMBRELLA_LABELS and scores[i] >= THRESHOLD


found_results = any(has_found_object(i) for i in range(len(scores)))
json_string = json.dumps({"umbrella_detected": found_results})
print(json_string)

# Clean up
videostream.stop()
