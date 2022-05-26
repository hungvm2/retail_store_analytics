import json

import numpy as np

from dot import *


class timeShots:
    def __init__(self, dat):
        self.data = dat

        maxX = 0
        maxY = 0
        for i in range(0, len(self.data)):
            hmdict = json.loads(self.data[i][-1])
            for xy, z in hmdict.items():
                d = dot(xy, z)
                maxX = max(maxX, d.getX())
                maxY = max(maxY, d.getY())
        self.maxX = maxX
        self.maxY = maxY

    def sumData(self):
        dotMatrix = np.zeros((self.maxX + 1, self.maxY + 1))
        # dotMatrix = np.zeros((200, 200))
        for i in range(0, len(self.data)):
            aShot = self.data[i]
            dotsData = json.loads(aShot[-1])  # lay cot "data"
            for xy, z in dotsData.items():  # phan giai toa do x, y, z value
                d = dot(xy, z)
                dotMatrix[d.getX(), d.getY()] += z
        return dotMatrix

    def sumDataByTime(self):
        timeArray = np.zeros(len(self.data))
        timeData = dict()
        for i in range(0, len(self.data)):
            aShot = self.data[i]
            dotsData = json.loads(aShot[-1])
            for xy, z in dotsData.items():
                d = dot(xy, z)
                timeArray[i] += z
            timeData[aShot[1].strftime('%Y/%m/%d %H:%M:%S')] = timeArray[i]
        return timeData  # dict


"""
hm = RetailStoreDB('localhost','root','abcd@1234','retail_store_analytics')

dat=hm.getData('select data from heatmap limit 2')
print(dat)
hm.close_connection()

tshots = timeShots(dat)
m = tshots.sumData()
print(m)
"""
