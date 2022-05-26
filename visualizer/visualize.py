import matplotlib.pyplot as plt

from heatmap_db import *
from timeshot import *


class Visualizer:
    def __init__(self):
        self.db = RetailStoreDB('localhost', 'root', 'abcd@1234', 'retail_store_analytics')

    def show_heatmap1(self, start_time, end_time):
        s1 = f"select * " \
             f"from coordinates_aggregation " \
             f"where aggr_time>='{start_time}' " \
             f"   and aggr_time<='{end_time}'"
        dat = self.db.getData(s1)

        # 1. plot heat map by space
        tshots = timeShots(dat)
        m = tshots.sumData()
        # print(type(m))
        img = plt.imread("frame.png")
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

    def show_barchart(self, start_time, end_time):
        s2 = f"select * " \
             f"from coordinates_aggregation " \
             f"where aggr_time>='{start_time}' " \
             f"   and aggr_time<='{end_time}'"
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
