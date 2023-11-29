import cv2
from cv2.typing import MatLike
from smartmonitor.camera import Camera
from smartmonitor.firebase_client import FirestoreClient
from smartmonitor.interface import UserInterface


class Application(object):
    camera: Camera
    fb_db: FirestoreClient
    user_interface: UserInterface

    def run(self):
        self.fb_db = FirestoreClient()
        self.camera = Camera()

        # self.user_interface = UserInterface(self.fb_db)
        # if self.user_interface.run() == 2:
        self.camera.setup()
        self.loop()
            

    def loop(self):
        self.camera.start()

        while True:
            img: MatLike = self.camera.capture_array()

            # grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            # (boxes, weights) = self.camera.hog_detector.detectMultiScale(grey, winStride=(2,2), scale=1.1)
            #
            # for index, value in enumerate(boxes):
            #     (x, y, w, h) = value
            #     cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0))
            #     cv2.putText(
            #         img,
            #         f"Probability: {weights[index]}",
            #         [x, y],
            #         cv2.FONT_HERSHEY_PLAIN,
            #         1,
            #         (255, 255, 255),
            #         2,
            #         cv2.LINE_AA,
            #     )

            cv2.imshow("Camera", img)
            cv2.waitKey(1)
