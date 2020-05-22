import xml.etree.ElementTree as ET
import tkinter.filedialog
import tkinter as tk
import numpy as np
from math import cos, asin, sqrt, pi
import copy

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler, MouseButton
from matplotlib.figure import Figure

matplotlib.rcParams["figure.subplot.left"] = 0.06
matplotlib.rcParams["figure.subplot.right"] = 0.98
matplotlib.rcParams["figure.subplot.bottom"] = 0.15
matplotlib.rcParams["figure.subplot.top"] = 0.92

data = []

xAxis, yAxis = [], []
xPts, yPts = [], []
xMin, xMax, yMin, yMax = None, None, None, None
fill_between = None


def openFile():
    global data
    # Parse data
    fn = title = tkinter.filedialog.askopenfilename(
        filetypes=(("GPX files", "*.gpx"), ("all files", "*.*"))
    )
    with open(fn, "r", encoding="utf8") as f:
        txt = f.read().strip()
    pat = "xmlns="
    i1 = txt.index(pat)
    i2 = txt.index('"', i1 + len(pat) + 1)
    txt = txt[0:i1] + txt[i2 + 2 :]

    root = ET.fromstring(txt)

    metaName = root.find(".//metadata/name")
    trkName = root.find(".//trk/name")
    if metaName != None and metaName.text:
        title = metaName.text
    elif trkName != None and trkName.text:
        title = trkName.text
    print(title)
    trkseg = root.find(".//trkseg")

    data = []

    for pt in trkseg.findall(".//trkpt"):
        data.append(
            {
                "lat": float(pt.get("lat")),
                "lon": float(pt.get("lon")),
                "ele": float(pt.find("ele").text),
                "dis": 0,
                "div": False,
            }
        )

    for i, d in enumerate(data[1:]):
        d["dis"] = distance(
            data[i]["lat"], data[i]["lon"], data[i + 1]["lat"], data[i + 1]["lon"]
        )

    # Fit data
    global yAxis, xAxis, xMin, xMax, yMin, yMax, xPts, yPts, fill_between

    yAxis = [x["ele"] for x in data]
    xAxis = []
    last = 0
    for d in data:
        last += d["dis"]
        xAxis.append(last)

    xMin, xMax, yMin, yMax = min(xAxis), max(xAxis), min(yAxis), max(yAxis)
    plt.axis([xMin, xMax, yMin - 100, yMax + 100])

    if fill_between:
        fill_between.remove()
    fill_between = plt.fill_between(xAxis, yAxis, facecolor="#ff000020")
    heightLine.set_data(xAxis, yAxis)

    xPts, yPts = [], []
    markerLine.set_data(xPts, yPts)

    plt.set_title('Elevation of "' + title + '"')

    canvas.draw()


def onClick(e):
    if e.button != MouseButton.LEFT or not data:
        return

    global yPts, xPts

    x = e.xdata
    if x == None or x < 0:
        return

    xLow, xHigh, xLowI, xHighI = xMin, xMax, 0, len(xAxis) - 1
    for di, dx in enumerate(xAxis):
        if dx <= x and dx > xLow:
            xLow = dx
            xLowI = di
        if dx > x and dx < xHigh:
            xHigh = dx
            xHighI = di

    val = None
    valI = None
    if x - xLow > xHigh - x:
        val = xHigh
        valI = xHighI
    else:
        val = xLow
        valI = xLowI

    d = data[valI]

    if d["div"]:
        xPts = [v for v in xPts if v != val]
        yPts = [v for v in yPts if v != d["ele"]]
        d["div"] = False
    else:
        xPts.append(val)
        yPts.append(d["ele"])
        d["div"] = True

    markerLine.set_data(xPts, yPts)
    canvas.draw()


# https://github.com/ValentinMinder/Swisstopo-WGS84-LV03/blame/master/scripts/py/wgs84_ch1903.py
def onExport():
    global data, includeStartAndEnd

    if not data:
        return

    currentData = copy.deepcopy(data)

    if includeStartAndEnd.get():
        if currentData and len(currentData) >= 1:
            currentData[0]["div"] = True
            currentData[len(currentData) - 1]["div"] = True

    relDis = []
    toExport = []
    currentDis = 0.0
    for k in currentData:
        currentDis += k["dis"]
        if k["div"]:
            toExport.append(k)
            relDis.append(currentDis)
            currentDis = 0.0

    txt = ""
    for i, v in enumerate(toExport):
        txt += (
            "{:.4f}".format(v["lat"])
            + " / "
            + "{:.4f}".format(v["lon"])
            + "\t"
            + "{:.2f}".format(v["ele"]).replace(".", ",")
            + "\t"
            + "{:.2f}".format(relDis[i]).replace(".", ",")
            + "\n"
        )
    with tkinter.filedialog.asksaveasfile() as f:
        f.write(txt.rstrip())


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


win1 = tk.Tk()
win1.wm_title("GPX profile")

fig = Figure()
plt = fig.add_subplot()
plt.set_title("Elevation")
plt.axis([0, 10, 100, 500])
(heightLine,) = plt.plot(xAxis, yAxis, "ro", markerSize=2)
(markerLine,) = plt.plot(xPts, yPts, "bo", markerSize=2)
plt.set_ylabel("Height MAS")
plt.set_xlabel("Distance in km")


canvas = FigureCanvasTkAgg(fig, master=win1)  # A tk.DrawingArea.

canvas.mpl_connect("button_press_event", onClick)

canvas.get_tk_widget().config(width=1200, height=400)
canvas.draw()
canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

NavigationToolbar2Tk.toolitems = [
    t
    for t in NavigationToolbar2Tk.toolitems
    if t[0] != None and t[0] in ("Home", "Pan", "Zoom")
]
nav = NavigationToolbar2Tk(canvas, win1)


def on_key_press(event):
    print("you pressed {}".format(event.key))
    key_press_handler(event, canvas, nav)


canvas.mpl_connect("key_press_event", on_key_press)
nav.update()
nav.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

btnExport = tk.Button(win1)
btnExport.config(text="Export", width=30, command=onExport)
btnExport.pack(side=tkinter.RIGHT, padx=5, pady=5)

openExport = tk.Button(win1)
openExport.config(text="Open", width=30, command=openFile)
openExport.pack(side=tkinter.LEFT, padx=5, pady=5)

includeStartAndEnd = tk.IntVar(value=1)
cbIncludeStartAndEnd = tk.Checkbutton(win1, variable=includeStartAndEnd)
cbIncludeStartAndEnd.config(text="Include start and end")
cbIncludeStartAndEnd.pack(side=tkinter.RIGHT, padx=5, pady=5)

win1.mainloop()
