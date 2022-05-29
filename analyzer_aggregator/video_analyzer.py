import argparse
import time

import cv2
import mysql.connector
import numpy as np
from contextlib import closing

from data_aggregator import DataAggregator

from customers_detector.detector import PersonDetector
from customers_tracker import PersonsTracker


class VideoAnalyzer:
    def __init__(self, weights_path, cfg_path, classes_name_path):
        self.db_connector = mysql.connector.connect(
            host="localhost",
            user="root",
            password="abcd@1234",
            database="retail_store_analytics"
        )
        self.person_detector = PersonDetector(weights_path, cfg_path, classes_name_path, 416)
        self.person_tracker = PersonsTracker()
        self.data_aggregator = DataAggregator(self.db_connector, (1920, 1080))
        self.thresh_interval = 60

    def get_camera_url_from_db(self, camera_id):
        sql_command = f"SELECT url FROM camera WHERE cam_id = {camera_id}"
        # print(sql_command)
        with closing(self.db_connector.cursor()) as cursor:
            cursor.execute(sql_command)
            camera_url = cursor.fetchone()[0]
        return camera_url

    @staticmethod
    def show_fps(frame, fps_value, font_scale=None):
        fps_pos = (30, 40)
        if not font_scale:
            font_scale = int(round(frame.shape[1] / 1200, 1))
        color = (255, 255, 255)
        outter_color = (0, 0, 0)
        x, y = int(fps_pos[0]), int(fps_pos[1])
        cv2.putText(frame, 'FPS: {:.2f}'.format(fps_value), (x, y), cv2.FONT_HERSHEY_SIMPLEX, font_scale,
                    outter_color, 4, cv2.LINE_AA)
        cv2.putText(frame, 'FPS: {:.2f}'.format(fps_value), (x, y), cv2.FONT_HERSHEY_SIMPLEX, font_scale, color,
                    2, cv2.LINE_AA)
        return frame

    def process(self, camera_id):
        camera_url = self.get_camera_url_from_db(camera_id)
        cap = cv2.VideoCapture(camera_url)
        frame_count = 0
        dets = np.empty((0, 5))
        start_time = time.time()
        start = time.time()
        while cap.isOpened():
            ret, frame = cap.read()
            if not ret:
                break

            if frame_count % 3 == 0:
                # start = time.time()
                dets = self.person_detector.detect_image(frame)
                # finish = time.time()
                # print('Predicted in %f seconds.' % (finish - start))

            persons = self.person_tracker.update(dets)

            result_img = frame
            for person in persons:
                self.data_aggregator.accumulate_aggregated_data(person)
                result_img = self.person_detector.plot_boxes_cv2(frame, person)

            now = time.time()
            if now - start_time > self.thresh_interval:
                self.data_aggregator.save_aggregated_data(camera_id)
                start_time = now
            end = time.time()
            result_img = self.show_fps(result_img, frame_count/(end - start))
            cv2.imshow('Retail store demo', result_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            frame_count += 1

        cap.release()


def parse_args():
    parser = argparse.ArgumentParser(description='Args for heatmap analyzer_aggregator')
    parser.add_argument('--camera_id',
                        help="Camera ID to map to Video URL.",
                        type=int, default=1)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    network_name = "yolov3"
    weights_file = f"customers_detector/network_data/{network_name}.weights"
    cfg_file = f"customers_detector/network_data/{network_name}.cfg"
    names_file = "customers_detector/network_data/coco.names"
    args = parse_args()
    video_analyzer = VideoAnalyzer(weights_file, cfg_file, names_file)
    video_analyzer.process(args.camera_id)
