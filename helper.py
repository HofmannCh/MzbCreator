from math import cos, asin, sqrt, pi
import xml.etree.ElementTree as ET
from wg84Corrdinates import Wg84Corrdinates, Wg84CorrdinatesProfile
from tkinter.messagebox import askyesno

import requests


def distance(
    lat1, lon1, lat2, lon2
):  # https://stackoverflow.com/questions/27928/calculate-distance-between-two-latitude-longitude-points-haversine-formula
    p = pi / 180
    a = (
        0.5
        - cos((lat2 - lat1) * p) / 2
        + cos(lat1 * p) * cos(lat2 * p) * (1 - cos((lon2 - lon1) * p)) / 2
    )
    return 12742 * asin(sqrt(a))  # 2*R*asin... # in km


def parseGpx(fileName):
    with open(fileName, "r", encoding="utf8") as f:
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
        title = fileName

    trkseg = root.find(".//trkseg")

    data = []

    for i, pt in enumerate(trkseg.findall(".//trkpt")):
        lat = float(pt.get("lat"))
        lon = float(pt.get("lon"))
        eleEle = pt.find("ele")
        ele = float(eleEle.text) if eleEle != None and eleEle.text else None

        if(i > 0):
            dis = distance(data[i-1].lat, data[i-1].lon, lat, lon)
        else:
            dis = 0

        data.append(Wg84Corrdinates(i, lat, lon, ele, dis))

    return [data, title]


def parseKml(fileName):
    with open(fileName, "r", encoding="utf8") as f:
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

    docName = root.find(".//Document/name")
    if docName != None and docName.text:
        title = docName.text
    else:
        title = fileName

    coordinates = root.find(".//coordinates")
    if coordinates == None or not coordinates.text:
        raise Exception("Corrdinates are null or empty")

    data = []
    for i, x in enumerate([x.split(",") for x in coordinates.text.split(" ")]):
        lon = float(x[0])
        lat = float(x[1])
        if(i > 0):
            dis = distance(data[i-1].lat, data[i-1].lon, lat, lon)
        else:
            dis = 0

        data.append(Wg84Corrdinates(i, lat, lon, None, dis))

    return [data, title]


def parse(fileName=""):
    if not fileName:
        raise Exception("FileName is empty")
    fn = fileName.lower()
    if fn.endswith(".gpx"):
        ret = parseGpx(fileName)
    elif fn.endswith(".kml"):
        ret = parseKml(fileName)
    else:
        raise Exception("Unknown type " + fileName)
    ret[0] = completeMissingElevation(ret[0])

    return ret


def completeMissingElevation(cords):
    missing = [x for x in cords if x.ele == None]

    if len(missing) <= 0:
        return cords

    yes = askyesno("Use api", "Do you want to use web api to complete your missing corrdinated (" +
                   len(missing).__str__()+"x)? If no the empty ones will be removed and not displayed")

    if not yes:
        return [x for x in cords if x.ele != None]

    pts = ",".join([str(m.lat)+","+str(m.lon) for m in missing])
    res = requests.get(
        "https://api.airmap.com/elevation/v1/ele", {"points": pts})

    r = res.json()
    status = r["status"]
    data = r["data"]

    if res.status_code < 200 and res.status_code >= 400 or status != "success":
        raise Exception(res.status_code.__str__() + " " +
                        status.__str__() + " " + data.__str__())

    for i, m in enumerate(missing):
        m.ele = data[i]
    
    return cords
