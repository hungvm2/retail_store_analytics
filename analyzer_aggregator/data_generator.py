import datetime
import json
import time

import cv2
import numpy as np

from temp.person_detector_YOLOv4.tool import do_detect
from temp.person_detector_YOLOv4.tool import plot_boxes_cv2
from temp.video_analyzer import VideoAnalyzer


class DataGenerator(VideoAnalyzer):
    def __init__(self, weights_path, names_path):
        super().__init__(weights_path, names_path)
        self.time_interval = 60

    def save_aggregated_data(self, camera_id, starting_time, frame_count, video_fps):
        coordinates = np.where(self.aggregated_data != 0)
        if len(coordinates[0]) == 0:
            return
        aggregated_data = dict()
        for i, j in zip(coordinates[0], coordinates[1]):
            aggregated_data[f"{i}-{j}"] = int(self.aggregated_data[i][j])
        event_time = datetime.datetime.fromtimestamp(starting_time + frame_count // video_fps).strftime("%Y-%m-%d %H:%M:00")
        print(event_time)
        sql_command = f"INSERT INTO coordinates_aggregation (aggr_time, cam_id, coordinates_data) VALUES ('{event_time}', {camera_id}, '{json.dumps(aggregated_data)}')"
        # print(sql_command)
        self.insert_data_into_db(sql_command)
        self.aggregated_data = np.zeros((self.grid_nums[0], self.grid_nums[1]), dtype=int)

    def process(self, camera_id, videos):
        for video_starting_time, video_url in videos.items():
            starting_timestamp = datetime.datetime.strptime(video_starting_time, "%Y-%m-%d %H:%M:00").timestamp()
            cap = cv2.VideoCapture(video_url)
            width = self.frame_size[0]
            height = self.frame_size[1]
            video_fps = cap.get(cv2.CAP_PROP_FPS)
            bbox_thick = int(0.6 * (height + width) / 600)
            frame_count = 0
            dets = np.empty((0, 5))
            start_time = time.time()
            self.aggregated_data = np.zeros((self.grid_nums[0], self.grid_nums[1]), dtype=int)
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                frame = cv2.resize(frame, dsize=(width, height))
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
                    self.accumulate_aggregated_data(person)
                    result_img = plot_boxes_cv2(frame, person, bbox_thick)

                now = time.time()
                if now - start_time > self.time_interval:
                    self.save_aggregated_data(camera_id, starting_timestamp, frame_count, video_fps)
                    start_time = now

                cv2.imshow('Yolo demo', result_img)
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break
                frame_count += 1

            cap.release()


if __name__ == '__main__':
    weights_file = "temp/person_detector_YOLOv4/network_data/yolov4.pth"
    names_file = "temp/person_detector_YOLOv4/network_data/coco.names"
    video_urls = {
        "2022-03-22 8:00:00": "../temp/real_data/NVR_ch24_main_20220322080011_20220322090011.mp4",
        "2022-03-22 10:00:00": "../temp/real_data/NVR_ch24_main_20220322100011_20220322110011.mp4",
        "2022-03-22 12:00:00": "../temp/real_data/NVR_ch24_main_20220322120011_20220322130011.mp4",
        "2022-03-22 14:00:00": "../temp/real_data/NVR_ch24_main_20220322140011_20220322150011.mp4",
        "2022-03-22 18:00:00": "../temp/real_data/NVR_ch24_main_20220322180011_20220322190011.mp4",
        "2022-03-26 8:00:00": "../temp/real_data/NVR_ch24_main_20220326080011_20220326090011.mp4",
        "2022-03-26 10:00:00": "../temp/real_data/NVR_ch24_main_20220326100011_20220326110011.mp4",
        "2022-03-26 14:00:00": "../temp/real_data/NVR_ch24_main_20220326140011_20220326150011.mp4",
        "2022-03-26 21:00:00": "../temp/real_data/NVR_ch24_main_20220326210011_20220326220012.mp4",
    }
    data_aggregator = DataGenerator(weights_file, names_file)
    data_aggregator.process(1, video_urls)
