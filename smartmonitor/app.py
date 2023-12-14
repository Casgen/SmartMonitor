import cv2
import csv

from time import sleep, thread_time
from pathlib import Path
from datetime import datetime
from pathlib import Path
from cv2.typing import MatLike
import numpy
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
        self.camera.setup((640, 1080))
        self.camera.start()
        self.loop_tf(True)

    def record_video(self):
        sleep(5)
        self.camera.picam2.start_and_record_video(
            "vids/test.mp4", duration=15, show_preview=True
        )

    def preview(self):
        while True:
            img: MatLike = self.camera.capture_array()
            cv2.imshow("Camera", img)

            if cv2.waitKey(1) == ord("q"):
                break

    def test_file(self):
        self.camera = Camera()
        self.camera.setup((1920, 1080))
        self.camera.capture_file()

    def test_upload(self):
        self.fb_db = FirestoreClient()
        self.fb_db.upload_image(Path("test.jpg"))

    def analyze_video(self, filename: str):
        cap = cv2.VideoCapture(filename)

        while cap.isOpened():
            ret, img = cap.read()

            if not ret:
                print("Failed to read the given frame!")
                continue

            grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            (boxes, weights) = self.camera.detect_multiscale_hog(
                grey, hit_threshold=1.0
            )

            for index, value in enumerate(boxes):
                (x, y, w, h) = value
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0))

                cv2.putText(
                    img,
                    f"Probability: {weights[index]}",
                    [x, y],
                    cv2.FONT_HERSHEY_PLAIN,
                    1,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            cv2.imshow("Camera", img)

            if cv2.waitKey(1) == ord("q"):
                break

    def create_results_winstride(self, img_filename: str):
        img = cv2.imread(img_filename)
        grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        with open(f"csvs/hog_winstride_scale_0_9.csv", "w") as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=",")
            csv_writer.writerow(["WinStride", "Probability"])

            for win_size in range(15):
                (boxes, weights) = self.camera.detect_multiscale_hog(
                    grey,
                    hit_threshold=0.1,
                    win_stride=(win_size + 1, win_size + 1),
                    scale=0.9,
                )

                for index, value in enumerate(boxes):
                    (x, y, w, h) = value
                    cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0))

                    cv2.putText(
                        img,
                        f"Probability: {weights[index]}",
                        [x, y],
                        cv2.FONT_HERSHEY_PLAIN,
                        1,
                        (255, 255, 255),
                        2,
                        cv2.LINE_AA,
                    )

                cv2.imshow("Camera", img)

                if cv2.waitKey(1) == ord("q"):
                    break

                row = [float(win_size)]

                for value in weights:
                    row.append(value)

                csv_writer.writerow(row)

                print(f"written row with {row}")
            csv_file.close()

    def measure_hog_fps(self, img_filename):
        img = cv2.imread(img_filename)
        grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        with open(f"csvs/winstride_fps_scale_1_3.csv", "w") as csv_file:
            csv_writer = csv.writer(csv_file, delimiter=",")
            csv_writer.writerow(["WinStride", "FPS_Median"])

            for win_size in range(7):
                time_list: list[float] = []

                for frames in range(30):
                    before_time = thread_time()

                    (boxes, weights) = self.camera.detect_multiscale_hog(
                        grey,
                        hit_threshold=0.1,
                        win_stride=(win_size + 1, win_size + 1),
                        scale=1.3,
                    )

                    for index, value in enumerate(boxes):
                        (x, y, w, h) = value
                        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0))

                        cv2.putText(
                            img,
                            f"Probability: {weights[index]}",
                            [x, y],
                            cv2.FONT_HERSHEY_PLAIN,
                            1,
                            (255, 255, 255),
                            2,
                            cv2.LINE_AA,
                        )

                    cv2.imshow("Camera", img)

                    if cv2.waitKey(1) == ord("q"):
                        break

                    time_list.append(thread_time() - before_time)

                time_list.sort()

                fps_median = time_list[16]

                csv_writer.writerow([float(win_size + 1), fps_median])

                print(f"written row with {[float(win_size+1), fps_median]}")

            csv_file.close()

    def loop_hog(self):
        while True:
            img: MatLike = self.camera.capture_array()

            grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            (boxes, weights) = self.camera.detect_multiscale_hog(
                grey, hit_threshold=1.0
            )

            print(f"FPS: {fps}")

            if len(boxes) > 0:
                path = Path(
                    f'imgs/{datetime.now().strftime("%d-%m-%y_%H-%M-%S-%f")}.jpg'
                )
                cv2.imwrite(path.as_posix(), img)

            for index, value in enumerate(boxes):
                (x, y, w, h) = value
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0))

                cv2.putText(
                    img,
                    f"Probability: {weights[index]}",
                    [x, y],
                    cv2.FONT_HERSHEY_PLAIN,
                    1,
                    (255, 255, 255),
                    2,
                    cv2.LINE_AA,
                )

            cv2.imshow("Camera", img)

            # if len(boxes) > 0:
            #     path = Path(f'imgs/{datetime.now().strftime("%d-%m-%y_%H-%M-%S-%f")}.jpg')
            #
            #     if cv2.imwrite(path.as_posix(), img):
            #         self.fb_db.upload_image(path)
            #         self.fb_db.send_notification()
            #         sleep(60)

            if cv2.waitKey(1) == ord("q"):
                break

    def loop_haar(self):
        while True:
            before_time = thread_time()

            img: MatLike = self.camera.capture_array()

            grey = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            boxes = self.camera.detect_multiscale_haar(img, scale=1.5)

            fps = 1.0 / (thread_time() - before_time)

            print(f"FPS: {fps}")

            for value in boxes:
                (x, y, w, h) = value
                cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0))

            cv2.imshow("Camera", img)

            if cv2.waitKey(1) == ord("q"):
                break

            # if len(boxes) > 0:
            #     path = Path(f'imgs/{datetime.now().strftime("%d-%m-%y_%H-%M-%S-%f")}.jpg')
            #
            #     if cv2.imwrite(path.as_posix(), img):
            #         self.fb_db.upload_image(path)
            #         self.fb_db.send_notification()
            #         sleep(60)

    def loop_tf(self, send_notifications: bool = False):

        while True:
            before_time = thread_time()

            img: MatLike = self.camera.capture_array()

            rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            resized_image = cv2.resize(
                rgb_image, (self.camera.tf_width, self.camera.tf_height)
            )
            input_data = numpy.expand_dims(resized_image, axis=0)

            if self.camera.is_floating_model:
                input_data = (numpy.float32(input_data) - 127.5) / 127.5

            self.camera.interpreter.set_tensor(
                self.camera.input_details[0]["index"], input_data
            )
            self.camera.interpreter.invoke()

            boxes = self.camera.get_tf_boxes()
            classes = self.camera.get_tf_classes()
            scores = self.camera.get_tf_scores()

            fps = 1.0 / (thread_time() - before_time)

            print(f"FPS: {fps}")

            for i in range(len(scores)):
                object_name = self.camera.label_map[int(classes[i])]

                if (
                    (scores[i] > 0.50)
                    and (scores[i] <= 1.0)
                    and (object_name == "person")
                ):
                    res = self.camera.resolution
                    # Get bounding box coordinates and draw box
                    # Interpreter can return coordinates that are outside of image dimensions, need to force them to be within image using max() and min()
                    ymin = int(max(1, (boxes[i][0] * res[0])))
                    xmin = int(max(1, (boxes[i][1] * res[1])))
                    ymax = int(min(res[1], (boxes[i][2] * res[1])))
                    xmax = int(min(res[0], (boxes[i][3] * res[0])))

                    cv2.rectangle(img, (xmin, ymin), (xmax, ymax), (10, 255, 0), 4)

                    label = "%s: %d%%" % (
                        object_name,
                        int(scores[i] * 100),
                    )  # Example: 'person: 72%'
                    labelSize, baseLine = cv2.getTextSize(
                        label, cv2.FONT_HERSHEY_SIMPLEX, 0.7, 2
                    )  # Get font size
                    label_ymin = max(
                        ymin, labelSize[1] + 10
                    )  # Make sure not to draw label too close to top of window
                    cv2.rectangle(
                        img,
                        (xmin, label_ymin - labelSize[1] - 10),
                        (xmin + labelSize[0], label_ymin + baseLine - 10),
                        (255, 255, 255),
                        cv2.FILLED,
                    )  # Draw white box to put label text in
                    cv2.putText(
                        img,
                        label,
                        (xmin, label_ymin - 7),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.7,
                        (0, 0, 0),
                        2,
                    )  # Draw label text

                    if send_notifications:
                        path = Path(
                            f'imgs/{datetime.now().strftime("%d-%m-%y_%H-%M-%S-%f")}.jpg'
                        )

                        if cv2.imwrite(path.as_posix(), img):
                            self.fb_db.upload_image(path)
                            self.fb_db.send_notification()
                            sleep(60)

            cv2.imshow("Camera", img)

            cv2.waitKey(1)

