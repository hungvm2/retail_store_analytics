import argparse
import datetime
import json
import time

import cv2
import mysql.connector
import numpy as np
import torch

from person_detector.models import Yolov4
from person_detector.tool.torch_utils import do_detect
from person_detector.tool.utils import load_class_names, plot_boxes_cv2
from persons_tracker import PersonsTracker


class HeatMapGenerator:
    def __init__(self, weights_path, names_path, id_camera):
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
        self.grid_size = (20, 20)
        self.grid_nums = (self.frame_size[0] // self.grid_size[0], self.frame_size[1] // self.grid_size[1])
        self.time_interval = 60
        self.heatmap_data = None
        self.grid_pos_checking_time_interval = 3
        self.cnx = mysql.connector.connect(
            host="localhost",
            user="root",
            password="abcd@1234",
            database="retail_store_analytics"
        )
        self.id_camera = id_camera

    def accumulate_heatmap_data(self, person):
        if person.last_update_grid_pos_time is None:
            person.last_update_grid_pos_time = time.time()
            person.current_grid_pos = (int(person.centroid_coords[0] // self.grid_size[0]),
                                       int(person.centroid_coords[1] // self.grid_size[1]))
            return
        now = time.time()
        new_grid_pos_x = int(person.centroid_coords[0] // self.grid_size[0])
        new_grid_pos_y = int(person.centroid_coords[1] // self.grid_size[1])
        current_grid_pos_x = person.current_grid_pos[0]
        current_grid_pos_y = person.current_grid_pos[1]
        if new_grid_pos_x == current_grid_pos_x and new_grid_pos_y == current_grid_pos_y:
            if now - person.last_update_grid_pos_time >= self.grid_pos_checking_time_interval:
                self.heatmap_data[new_grid_pos_x][new_grid_pos_y] += 1
                person.last_update_grid_pos_time = now
            return
        person.current_grid_pos = (new_grid_pos_x, new_grid_pos_y)
        person.last_update_grid_pos_time = now

    def save_heatmap_data(self):
        heatmap_coordinates = np.where(self.heatmap_data != 0)
        if len(heatmap_coordinates[0]) == 0:
            return
        heatmap_data = dict()
        for i, j in zip(heatmap_coordinates[0], heatmap_coordinates[1]):
            heatmap_data[f"{i}-{j}"] = int(self.heatmap_data[i][j])
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:00")
        sql = f"INSERT INTO heatmap (timestamp, id_camera, data) VALUES ('{timestamp}', {self.id_camera}, '{json.dumps(heatmap_data)}')"
        # print(sql)
        mysql_cursor = self.cnx.cursor()
        mysql_cursor.execute(sql)
        self.cnx.commit()
        mysql_cursor.close()
        self.heatmap_data = np.zeros((self.grid_nums[0], self.grid_nums[1]), dtype=int)

    def process(self, url):
        cap = cv2.VideoCapture(url)
        width = self.frame_size[0]
        height = self.frame_size[1]
        cap.set(3, width)
        cap.set(4, height)
        video_fps = cap.get(cv2.CAP_PROP_FPS)
        bbox_thick = int(0.6 * (height + width) / 600)
        frame_count = 0
        dets = np.empty((0, 5))
        start_time = time.time()
        self.heatmap_data = np.zeros((self.grid_nums[0], self.grid_nums[1]), dtype=int)
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
                self.accumulate_heatmap_data(person)
                result_img = plot_boxes_cv2(frame, person, bbox_thick)

            now = time.time()
            if now - start_time > self.time_interval:
                self.save_heatmap_data()
                start_time = now

            cv2.imshow('Yolo demo', result_img)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
            frame_count += 1

        cap.release()


def parse_args():
    parser = argparse.ArgumentParser(description='Args for heatmap generator')
    parser.add_argument('--id_camera',
                        help="Camera ID to map to Video URL.",
                        type=int, default=1)
    args = parser.parse_args()
    return args


if __name__ == '__main__':
    cameras = {
        1: "../temp/test_data/retail_store1.mp4",
        2: "../temp/test_data/retail_store1.mp4"
    }
    weights_file = "person_detector/network_data/yolov4.pth"
    names_file = "person_detector/network_data/coco.names"
    args = parse_args()
    id_camera = args.id_camera
    video_url = cameras[id_camera]
    heat_map_generator = HeatMapGenerator(weights_file, names_file, id_camera)
    heat_map_generator.process(video_url)
