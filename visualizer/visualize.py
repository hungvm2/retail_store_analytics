import matplotlib.pyplot as plt
# from contextlib import closing
from heatmap_db import *
from timeshot import *
# from scipy.stats import gaussian_kde
# import numpy as np
# import json

# START_TIME = "2022-03-22 8:00:00"
# END_TIME = "2022-05-25 9:00:00"


class Visualizer:
    def __init__(self):
        self.db = RetailStoreDB('localhost', 'root', 'abcd@1234', 'retail_store_analytics')

    def show_heatmap1(self, start_time, end_time):
        s1 = f"select * " \
             f"from coordinates_aggregation " \
             f"where aggr_time>='{start_time}' " \
             f"   and aggr_time<='{end_time}'"
        dat = self.db.getData(s1)

        # self.db.close_connection()

        # 1. plot heat map by space
        tshots = timeShots(dat)
        m = tshots.sumData()
        # print(type(m))
        img = plt.imread("frame.png")
        fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
        ax.imshow(img)
        ax.set_title("Customer dense by Space")
        im = ax.imshow(m, extent=[1920, 0, 1080, 0], alpha=0.7)  # im = ax.imshow(m, alpha=1)
        # Create colorbar
        cbar = ax.figure.colorbar(im, ax=ax)
        cbar.ax.set_ylabel("customer density", rotation=-90, va="bottom")

    def show_barchart(self, start_time, end_time):
        s2 = f"select * " \
             f"from coordinates_aggregation " \
             f"where aggr_time>='{start_time}' " \
             f"   and aggr_time<='{end_time}'"
        dat2 = self.db.getData(s2)
        # self.db.close_connection()

        # 2. plot bar chart by date
        tshots2 = timeShots(dat2)
        d = tshots2.sumDataByTime()
        # print(d)
        x = []
        y = []
        for cTime, val in d.items():
            if x == []:
                x.append(cTime[0:13])
                y.append(val)
            elif x[-1] == cTime[0:13]:
                y[-1] += val
            else:
                x.append(cTime[0:13])
                y.append(val)
        # print(x)
        # print(y)
        fig2, ax2 = plt.subplots(figsize=(19.2, 10.8))
        # plt.subplots_adjust(bottom=0.3, top=0.9)
        ax2.bar(x, y)
        ax2.set_ylabel('Customer dense')
        ax2.set_title('Customer dense by Time')
        ax2.set_xticklabels(x, rotation='vertical')
        plt.rcParams.update({'font.size': 32})
        plt.show()

    # def show_heatmap2(self, start_time, end_time):
    #     sql_command = f"SELECT * from coordinates_aggregation WHERE aggr_time >= '{start_time}' AND aggr_time <= '{end_time}'"
    #     with closing(self.db.conn.cursor()) as cursor:
    #         cursor.execute(sql_command)
    #         fetched_data = cursor.fetchall()
    #
    #     H = 1080
    #     W = 1920
    #     grid_nums = (20, 20)
    #     grid_size = (int(W / grid_nums[0]), int(H / grid_nums[1]))
    #
    #     coords_accumulate = dict()
    #
    #     max_count = 0
    #     for record in fetched_data:
    #         for cell_pos, value in json.loads(record[-1]).items():
    #             if cell_pos not in coords_accumulate:
    #                 coords_accumulate[cell_pos] = 0
    #             coords_accumulate[cell_pos] += value
    #             max_count = max(max_count, coords_accumulate[cell_pos])
    #     data = list()
    #     for key, value in coords_accumulate.items():
    #         lat_long = key.split("-")
    #         lat = int(lat_long[0]) * grid_size[0] + grid_size[0] // 2
    #         long = int(lat_long[-1]) * grid_size[1] + grid_size[1] // 2
    #         for i in range(10 * value):
    #             data.append([lat, long])
    #     data = np.array(data)
    #     x = data[:, 0]
    #     y = data[:, 1]
    #     k = gaussian_kde(np.vstack([x, y]))
    #     xi, yi = np.mgrid[x.min():x.max():100j, y.min():y.max():100j]
    #     zi = k(np.vstack([xi.flatten(), yi.flatten()]))
    #
    #     img = plt.imread('frame.png')
    #     fig, ax = plt.subplots(figsize=(19.2, 10.8), dpi=100)
    #
    #     ax.pcolormesh(xi, yi, zi.reshape(xi.shape), alpha=0.7)
    #
    #     ax.set_xlim(x.min(), x.max())
    #     ax.set_ylim(y.min(), y.max())
    #
    #     im = ax.imshow(img, extent=[x.min(), x.max(), y.min(), y.max()], aspect="auto")
    #     # Create colorbar
    #     cbar = ax.figure.colorbar(im, ax=ax)
    #     cbar.ax.set_ylabel("customer density", rotation=-90, va="bottom")
