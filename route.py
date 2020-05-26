import helper
import copy
from wg84Corrdinates import Wg84Corrdinates, Wg84CorrdinatesProfile


class Route:
    def __init__(self, file):
        [self.data, self.title] = helper.parse(file)

        if not self.data:
            raise Exception("Data cannot be empty")

        self.yPoints = [x.ele for x in self.data]
        self.xPoints = []
        last = 0
        for d in [x for x in self.data if x.dis != None]:
            last += d.dis
            self.xPoints.append(last)

        self.xMarkedPoints = []
        self.yMarkedPoints = []

        self.xMin = min(self.xPoints)
        self.xMax = max(self.xPoints)
        self.yMin = min(self.yPoints)
        self.yMax = max(self.yPoints)

    def calculateProfile(self, includeFirstAndLast):
        currentData = copy.deepcopy(self.data)

        if includeFirstAndLast:
            currentData[0].div = True
            currentData[len(currentData) - 1].div = True

        relDis = []
        profileData = []
        lastPd = None
        relDis = 0.0
        currentData.sort(key=lambda x: x.index)
        for cd in currentData:
            relDis += cd.dis
            if cd.div:
                if lastPd and lastPd.cords:
                    last = lastPd.cords

                    if cd.ele > 0:
                        eleDiv = (cd.ele - last.ele) / 100  # Hektometers
                    else:
                        eleDiv = 0

                    if relDis == 0:
                        grad = 0
                    else:
                        grad = eleDiv / (relDis*10)*100

                    if grad < -20:
                        lkm = -eleDiv / 1.5 + relDis
                    else:
                        if grad < 0:
                            lkm = relDis
                        else:
                            lkm = relDis + eleDiv

                    relDisT = lastPd.relDisT + relDis
                    lkmT = lastPd.lkmT + lkm
                else:
                    eleDiv = 0
                    grad = 0
                    lkm = 0
                    relDisT = 0
                    lkmT = 0

                pd = Wg84CorrdinatesProfile(
                    cd, relDis, relDisT, eleDiv, grad, lkm, lkmT)
                profileData.append(pd)
                lastPd = pd
                relDis = 0.0

        return profileData
