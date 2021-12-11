# Import packages
import os
import argparse
import cv2
import numpy as np
import sys
import time
from threading import Thread
import importlib.util

# Define VideoStream class to handle streaming of video from webcam in separate processing thread
# Source - Adrian Rosebrock, PyImageSearch: https://www.pyimagesearch.com/2015/12/28/increasing-raspberry-pi-fps-with-python-and-opencv/
class VideoStream:
    """Camera object that controls video streaming from the Picamera"""
    def __init__(self,resolution=(640,480),framerate=30):
        # Initialize the PiCamera and the camera image stream
        self.stream = cv2.VideoCapture(0)
        ret = self.stream.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))
        ret = self.stream.set(3,resolution[0])
        ret = self.stream.set(4,resolution[1])
            
        # Read first frame from the stream
        (self.grabbed, self.frame) = self.stream.read()

	# Variable to control when the camera is stopped
        self.stopped = False

    def start(self):
	    # Start the thread that reads frames from the video stream
        Thread(target=self.update,args=()).start()
        return self

    def update(self):
        # Keep looping indefinitely until the thread is stopped
        while True:
            # If the camera is stopped, stop the thread
            if self.stopped:
                # Close camera resources
                self.stream.release()
                return

            # Otherwise, grab the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()

    def read(self):
	# Return the most recent frame
        return self.frame

    def stop(self):
	# Indicate that the camera and thread should be stopped
        self.stopped = True

parser = argparse.ArgumentParser()
parser.add_argument('--modeldir', help='Folder the .tflite file is located in',
                    required=True)

args = parser.parse_args()

MODEL_DIR = args.modeldir
MODEL_NAME = "model.tflite"
LABELMAP_NAME = "labelmap.txt"
THRESHOLD = 0.5
CAMERA_WIDTH=1280
CAMERA_HEIGHT=720
CAMERA_FRAME_RATE=30
INTERESTING_LABELS = ['umbrella']

from tflite_runtime.interpreter import Interpreter

CWD_PATH = os.getcwd()
MODEL_PATH = os.path.join(CWD_PATH, MODEL_DIR, MODEL_NAME)
LABELS_PATH = os.path.join(CWD_PATH, MODEL_DIR, LABELMAP_NAME)

with open(LABELS_PATH, 'r') as f:
    labels = [line.strip() for line in f.readlines()]

# Have to do a weird fix for label map if using the COCO "starter model" from
# https://www.tensorflow.org/lite/models/object_detection/overview
# First label is '???', which has to be removed.
if labels[0] == '???':
    del(labels[0])

interpreter = Interpreter(model_path=MODEL_PATH)
interpreter.allocate_tensors()

# Get model details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
height = input_details[0]['shape'][1]
width = input_details[0]['shape'][2]

floating_model = (input_details[0]['dtype'] == np.float32)

input_mean = 127.5
input_std = 127.5

# Initialize video stream
videostream = VideoStream(resolution=(CAMERA_WIDTH,CAMERA_HEIGHT), framerate=CAMERA_FRAME_RATE).start()
time.sleep(1)

# Grab frame from video stream
original_frame = videostream.read()

# Acquire frame and resize to expected shape [1xHxWx3]
frame = original_frame.copy()
frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
frame_resized = cv2.resize(frame_rgb, (width, height))
input_data = np.expand_dims(frame_resized, axis=0)

# Normalize pixel values if using a floating model (i.e. if model is non-quantized)
if floating_model:
    input_data = (np.float32(input_data) - input_mean) / input_std

# Perform the actual detection by running the model with the image as input
interpreter.set_tensor(input_details[0]['index'], input_data)
interpreter.invoke()

# Retrieve detection results
boxes = interpreter.get_tensor(output_details[0]['index'])[0] # Bounding box coordinates of detected objects
classes = interpreter.get_tensor(output_details[1]['index'])[0] # Class index of detected objects
scores = interpreter.get_tensor(output_details[2]['index'])[0] # Confidence of detected objects

# Loop over all detections
for i in range(len(scores)):
    label_name = labels[int(classes[i])]
    if ((scores[i] >= THRESHOLD) and (scores[i] <= 1.0) and label_name in INTERESTING_LABELS):
        ymin = int(max(1,(boxes[i][0] * CAMERA_HEIGHT)))
        xmin = int(max(1,(boxes[i][1] * CAMERA_WIDTH)))
        ymax = int(min(CAMERA_HEIGHT,(boxes[i][2] * CAMERA_HEIGHT)))
        xmax = int(min(CAMERA_WIDTH,(boxes[i][3] * CAMERA_WIDTH)))
        
        cv2.rectangle(frame, (xmin,ymin), (xmax,ymax), (10, 255, 0), 2)
        
        confidence_percentage = int(scores[i]*100)

        label = '%s: %d%%' % (label_name, confidence_percentage) # Example: 'person: 72%'
        labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2) # Get font size
        label_ymin = max(ymin, labelSize[1] + 10) # Make sure not to draw label too close to top of window
        cv2.rectangle(frame, (xmin, label_ymin-labelSize[1]-10), (xmin+labelSize[0], label_ymin+baseLine-10), (255, 255, 255), cv2.FILLED) # Draw white box to put label text in
        cv2.putText(frame, label, (xmin, label_ymin-7), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 0), 2) # Draw label text

        # Print info
        print('Object ' + str(i) + ': ' + label_name + ' with confidence ' + str(int(scores[i]*100)))

cv2.imwrite('test.jpg', frame)

# Clean up
videostream.stop()
