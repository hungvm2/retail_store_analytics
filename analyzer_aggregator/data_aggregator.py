import datetime
import json
import time

import numpy as np
from contextlib import closing


class DataAggregator:
    def __init__(self, db_connector, frame_size):
        self.grid_size = (20, 20)
        self.grid_nums = (frame_size[0] // self.grid_size[0], frame_size[1] // self.grid_size[1])
        self.grid_pos_checking_time_interval = 3
        self.db_connector = db_connector
        self.aggregated_data = np.zeros((self.grid_nums[0], self.grid_nums[1]), dtype=int)

    def accumulate_aggregated_data(self, person):
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
        if new_grid_pos_x > self.grid_nums[0]: new_grid_pos_x = self.grid_nums[0]
        if new_grid_pos_y > self.grid_nums[1]: new_grid_pos_y = self.grid_nums[1]
        if new_grid_pos_x == current_grid_pos_x and new_grid_pos_y == current_grid_pos_y:
            if now - person.last_update_grid_pos_time >= self.grid_pos_checking_time_interval:
                self.aggregated_data[new_grid_pos_x][new_grid_pos_y] += 1
                person.last_update_grid_pos_time = now
            return
        person.current_grid_pos = (new_grid_pos_x, new_grid_pos_y)
        person.last_update_grid_pos_time = now

    def save_aggregated_data(self, camera_id):
        coordinates = np.where(self.aggregated_data != 0)
        if len(coordinates[0]) == 0:
            return
        aggregated_data = dict()
        for i, j in zip(coordinates[0], coordinates[1]):
            aggregated_data[f"{i}-{j}"] = int(self.aggregated_data[i][j])
        event_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:00")
        sql_command = f"INSERT INTO coordinates_aggregation (aggr_time, cam_id, coordinates_data) VALUES ('{event_time}', {camera_id}, '{json.dumps(aggregated_data)}')"
        # print(sql_command)
        self.insert_data_into_db(sql_command)
        self.aggregated_data = np.zeros((self.grid_nums[0], self.grid_nums[1]), dtype=int)

    def insert_data_into_db(self, sql_command):
        with closing(self.db_connector.cursor()) as cursor:
            cursor.execute(sql_command)
            self.db_connector.commit()

    def get_camera_url_from_db(self, camera_id):
        sql_command = f"SELECT url from camera WHERE cam_id = {camera_id}"
        # print(sql_command)
        with closing(self.db_connector.cursor()) as cursor:
            cursor.execute(sql_command)
            camera_url = cursor.fetchone()[0]
        return camera_url
