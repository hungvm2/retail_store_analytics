import argparse
import time

import cv2
import mysql.connector
import numpy as np
import torch
from contextlib import closing

from data_aggregator import DataAggregator
from person_detector.models import Yolov4
from person_detector.tool.torch_utils import do_detect
from person_detector.tool.utils import load_class_names, plot_boxes_cv2
from persons_tracker import PersonsTracker


class VideoAnalyzer:
    def __init__(self, weights_path, names_path):
        self.db_connector = mysql.connector.connect(
            host="localhost",
            user="root",
            password="abcd@1234",
            database="retail_store_analytics"
        )
        self.person_detector = Yolov4(yolov4conv137weight=None, n_classes=80, inference=True)
        pretrained_dict = torch.load(weights_path, map_location=torch.device('cuda'))
        self.person_detector.load_state_dict(pretrained_dict)
        self.use_cuda = True
        if self.use_cuda:
            self.person_detector.cuda()
        self.class_names = load_class_names(names_path)
        self.network_input_size = (416, 416)
        self.person_tracker = PersonsTracker()
        self.frame_size = (1280, 720)
        self.data_aggregator = DataAggregator(self.db_connector, self.frame_size)
        self.time_interval = 60

    def get_camera_url_from_db(self, camera_id):
        sql_command = f"SELECT url from camera WHERE cam_id = {camera_id}"
        # print(sql_command)
        with closing(self.db_connector.cursor()) as cursor:
            cursor.execute(sql_command)
            camera_url = cursor.fetchone()[0]
        return camera_url

    def process(self, camera_id):
        camera_url = self.get_camera_url_from_db(camera_id)
        cap = cv2.VideoCapture(camera_url)
        width = self.frame_size[0]
        height = self.frame_size[1]
        cap.set(3, width)
        cap.set(4, height)
        # video_fps = cap.get(cv2.CAP_PROP_FPS)
        bbox_thick = int(0.6 * (height + width) / 600)
        frame_count = 0
        dets = np.empty((0, 5))
        start_time = time.time()

        while True:
            ret, frame = cap.read()

            if frame_count % 3 == 0:
                sized = cv2.resize(frame, self.network_input_size)
                sized = cv2.cvtColor(sized, cv2.COLOR_BGR2RGB)

                start = time.time()
                dets = np.array(do_detect(self.person_detector, sized, 0.3, 0.6, self.use_cuda, frame)[0])
                finish = time.time()
                print('Predicted in %f seconds.' % (finish - start))

            persons = self.person_tracker.update(dets)

            result_img = frame
            for person in persons:
                self.data_aggregator.accumulate_aggregated_data(person)
                result_img = plot_boxes_cv2(frame, person, bbox_thick)

            now = time.time()
            if now - start_time > self.time_interval:
                self.data_aggregator.save_aggregated_data(camera_id)
                start_time = now

            cv2.imshow('Yolo demo', result_img)
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
    weights_file = "person_detector/network_data/yolov4.pth"
    names_file = "person_detector/network_data/coco.names"
    args = parse_args()
    video_analyzer = VideoAnalyzer(weights_file, names_file)
    video_analyzer.process(args.camera_id)
