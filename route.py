import xml.etree.ElementTree as ET
import helper
import copy
from wg84Corrdinates import Wg84Corrdinates, Wg84CorrdinatesProfile


class Route:
    def __init__(self, file):

        with open(file, "r", encoding="utf8") as f:
            txt = f.read().strip()

        # Remove sml namespace
        pat = "xmlns="
        try:  # VaueException if Namespace not found, so do nothing
            i1 = txt.index(pat)
            i2 = txt.index('"', i1 + len(pat) + 1)
            txt = txt[0:i1] + txt[i2 + 2:]
        except:
            pass

        root = ET.fromstring(txt)
        
        metaName = root.find(".//metadata/name")
        trkName = root.find(".//trk/name")
        if metaName != None and metaName.text:
            title = metaName.text
        elif trkName != None and trkName.text:
            title = trkName.text
        else:
            title = file
        print(title)

        trkseg = root.find(".//trkseg")

        data = []

        for i, pt in enumerate(trkseg.findall(".//trkpt")):
            lat = float(pt.get("lat"))
            lon = float(pt.get("lon"))
            ele = float(pt.find("ele").text)

            if(i > 0):
                dis = helper.distance(data[i-1].lat, data[i-1].lon, lat, lon)
            else:
                dis = 0

            data.append(Wg84Corrdinates(i, lat, lon, ele, dis))

        if len(data) <= 0:
            raise Exception("Data cannot be empty")

        yAxis = [x.ele for x in data]
        xAxis = []
        last = 0
        for d in data:
            last += d.dis
            xAxis.append(last)

        self.title = title
        self.xmlRoot = root

        self.data = data
        self.xPoints = xAxis
        self.yPoints = yAxis

        self.xMarkedPoints = []
        self.yMarkedPoints = []

        self.xMin = min(xAxis)
        self.xMax = max(xAxis)
        self.yMin = min(yAxis)
        self.yMax = max(yAxis)

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
