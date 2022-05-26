class dot:
    def __init__(self, dotDataKey, dotDataValue):
        xy = dotDataKey
        xy1 = xy.split("-")
        self.x = int(xy1[0])
        self.y = int(xy1[1])
        self.value = int(dotDataValue)

    def getX(self):
        return self.x

    def getY(self):
        return self.y

    def getValue(self):
        return self.value
