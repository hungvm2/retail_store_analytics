import cv2
import matplotlib.pyplot as plt

from heatmap_db import *
from timeshot import *


class Visualizer:
    def __init__(self):
        self.db = RetailStoreDB('localhost', 'root', 'abcd@1234', 'retail_store_analytics')

    def get_camera_url_from_db(self, camera_id):
        sql_command = f"SELECT url from camera WHERE cam_id = {camera_id}"
        cursor = self.db.conn.cursor()
        cursor.execute(sql_command)
        data = cursor.fetchone()
        camera_url = ""
        if data is not None:
            camera_url = data[0]
        cursor.close()
        return camera_url

    def get_frame_from_cam(self, cam_id):
        camera_url = self.get_camera_url_from_db(cam_id)
        cap = cv2.VideoCapture(camera_url)
        frame = np.zeros((1920, 1080))
        while cap.isOpened():
            ret, _frame = cap.read()
            if _frame is not None:
                frame = _frame
            break
        frame = cv2.resize(frame, dsize=(1920, 1080), interpolation=cv2.INTER_AREA)
        cv2.imwrite("frame1.png", frame)

    def show_heatmap(self, start_time, end_time, cam_id=1):
        s1 = f"SELECT * " \
             f"FROM coordinates_aggregation " \
             f"WHERE aggr_time>='{start_time}' " \
             f"AND aggr_time<='{end_time}' AND cam_id = '{cam_id}'"
        dat = self.db.getData(s1)

        # 1. plot heat map by space
        tshots = timeShots(dat)
        m = tshots.sumData()
        # print(type(m))

        self.get_frame_from_cam(cam_id)
        img = plt.imread("frame1.png")
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        ax.imshow(img)
        ax.set_title("Customer's Interest by Space")
        for item in ([ax.title, ax.xaxis.label, ax.yaxis.label] +
                     ax.get_xticklabels() + ax.get_yticklabels()):
            item.set_fontsize(20)
        im = ax.imshow(m, extent=[1920, 0, 1080, 0], alpha=0.7)

        # Create colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel("customer density", rotation=-90, va="bottom")

    def show_barchart(self, start_time, end_time, cam_id=1):
        s2 = f"SELECT * " \
             f"FROM coordinates_aggregation " \
             f"WHERE aggr_time>='{start_time}' " \
             f"AND aggr_time<='{end_time}' AND cam_id = '{cam_id}'"
        dat2 = self.db.getData(s2)

        # 2. plot bar chart by date
        tshots2 = timeShots(dat2)
        d = tshots2.sumDataByTime()
        # print(d)
        x = []
        y = []
        for cTime, val in d.items():
            if len(x) == 0:
                x.append(cTime[0:13])
                y.append(val)
            elif x[-1] == cTime[0:13]:
                y[-1] += val
            else:
                x.append(cTime[0:13])
                y.append(val)

        fig2, ax2 = plt.subplots(figsize=(19.2, 10.8))
        ax2.bar(x, y)
        ax2.set_ylabel('Customer dense')
        ax2.set_title("Customer's interest by Time")
        ax2.set_xticklabels(x, rotation='vertical')
        for item in ([ax2.title, ax2.xaxis.label, ax2.yaxis.label] +
                     ax2.get_xticklabels() + ax2.get_yticklabels()):
            item.set_fontsize(20)
        plt.show()
