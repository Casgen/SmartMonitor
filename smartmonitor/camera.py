#!/usr/bin/python3
import time
import cv2
import numpy

from picamera2 import Picamera2
from libcamera import Transform
from cv2.typing import MatLike, Size
from tflite_runtime.interpreter import Interpreter


class Camera:
    picam2: Picamera2
    hog_detector: cv2.HOGDescriptor
    haar_detector: cv2.CascadeClassifier


    def setup(self, resolution: Size):

        self.resolution = resolution
        # Setup Haar
        print("Setting up the camera and detection")
        self.haar_detector = cv2.CascadeClassifier(
            "opencv_data/haarcascades/haarcascade_fullbody.xml"
        )

        # Setup HOG
        self.hog_detector = cv2.HOGDescriptor()
        self.hog_detector.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())

        # Setup TFLite
        self.interpreter = Interpreter("ai_model/lite_model.tflite")
        self.interpreter.allocate_tensors()

        with open('ai_model/labelmap.txt', 'r') as f:
            self.label_map = [line.strip() for line in f.readlines()]


        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        self.tf_width = self.input_details[0]["shape"][1]
        self.tf_height = self.input_details[0]["shape"][2]

        self.is_floating_model = (
            self.interpreter.get_input_details()[0]["dtype"] == numpy.float32
        )

        # outname = self.output_details[0]["name"]

        self.boxes_idx, self.classes_idx, self.scores_idx = 0, 1, 2

        cv2.startWindowThread()

        self.picam2 = Picamera2()
        self.configuration = self.picam2.create_preview_configuration(
            transform=Transform(vflip=1),
            main={"format": "XRGB8888", "size": resolution},
        )

        self.picam2.configure(self.configuration)

    def capture_array(self) -> MatLike:
        return self.picam2.capture_array()

    def capture_file(self, filename: str = "test"):
        return self.picam2.capture_file(f"test.{filename}")

    def detect_multiscale_hog(
        self,
        img: MatLike,
        hit_threshold: float = 3,
        win_stride: Size = (2, 2),
        scale: float = 1.1,
    ):
        return self.hog_detector.detectMultiScale(
            img, winStride=win_stride, scale=scale, hitThreshold=hit_threshold
        )

    def detect_multiscale_haar(self, img: MatLike, scale: float = 1.1):
        return self.haar_detector.detectMultiScale(
            image=img, scaleFactor=scale, flags=cv2.CASCADE_SCALE_IMAGE
        )

    def start(self):
        self.picam2.start()

    def get_tf_boxes(self):
        return self.interpreter.get_tensor(self.output_details[self.boxes_idx]['index'])[0]

    def get_tf_classes(self):
        return self.interpreter.get_tensor(self.output_details[self.classes_idx]['index'])[0]

    def get_tf_scores(self):
        return self.interpreter.get_tensor(self.output_details[self.scores_idx]['index'])[0]
