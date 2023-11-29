#!/usr/bin/python3
import time
import cv2

from picamera2 import Picamera2
from libcamera import Transform
from cv2.typing import MatLike, Size


class Camera:
    picam2: Picamera2
    hog_detector: cv2.HOGDescriptor

    def setup(self):
        print("Setting up the camera and detection")
        self.hog_detector = cv2.HOGDescriptor()

        self.hog_detector.setSVMDetector(cv2.HOGDescriptor_getDefaultPeopleDetector())
        cv2.startWindowThread()

        self.picam2 = Picamera2()
        self.configuration = self.picam2.create_preview_configuration(
            transform=Transform(vflip=1),
            main={"format": "XRGB8888", "size": (640, 480)},
        )

        self.picam2.configure(self.configuration)

    def capture_array(self) -> MatLike:
        return self.picam2.capture_array()

    def detect_multiscale(self, img: MatLike, hit_threshold: float=3, win_stride: Size=(2,2), scale: float=1.1):
        return self.hog_detector.detectMultiScale(img, winStride=win_stride, scale=scale, hitThreshold=hit_threshold)

    def start(self):
        self.picam2.start()
