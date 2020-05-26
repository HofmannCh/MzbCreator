class Wg84Corrdinates:
    def __init__(self, index, lat, lon, ele, dis):
        self.lat = lat
        self.lon = lon
        self.ele = ele
        self.dis = dis

        self.index = index
        self.div = False


class Wg84CorrdinatesProfile:
    def __init__(self, cords, relDis, relDisT, eleDiv, grad, lkm, lkmT):
        self.cords = cords
        self.eleDiv = eleDiv
        self.relDis = relDis
        self.relDisT = relDisT
        self.grad = grad
        self.lkm = lkm
        self.lkmT = lkmT
