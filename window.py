import tkinter.filedialog
from tkinter.messagebox import showerror
import tkinter as tk

from route import Route

import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

# Implement the default Matplotlib key bindings.
from matplotlib.backend_bases import key_press_handler, MouseButton
from matplotlib.figure import Figure


class Window:
    def __init__(self):
        self.route = None
        self.__buildGuiAndRun()

    def onClick(self, e):
        if e.button != MouseButton.LEFT or not self.route or not self.route.data:
            return

        x = e.xdata
        if x == None or x < 0:
            return

        r = self.route

        xLow, xHigh, xLowI, xHighI = r.xMin, r.xMax, 0, len(r.xPoints) - 1
        for di, dx in enumerate(r.xPoints):
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

        d = r.data[valI]

        if d.div:
            r.xMarkedPoints = [v for v in r.xMarkedPoints if v != val]
            r.yMarkedPoints = [v for v in r.yMarkedPoints if v != d.ele]
            d.div = False
        else:
            r.xMarkedPoints.append(val)
            r.yMarkedPoints.append(d.ele)
            d.div = True

        self.markerLine.set_data(r.xMarkedPoints, r.yMarkedPoints)
        self.canvas.draw()

    def onImport(self):
        fileName = tkinter.filedialog.askopenfilename(
            filetypes=[("Corrdinates files", "*.gpx;*.kml"), ("All files", "*.*")])

        if self.fill_between != None:
            self.fill_between.remove()
            self.fill_between = None

        try:
            self.route = r = Route(fileName)
            self.fill_between = self.plt.fill_between(
                r.xPoints, r.yPoints, facecolor="#ff000020")
            self.heightLine.set_data(r.xPoints, r.yPoints)
            self.markerLine.set_data(r.xMarkedPoints, r.yMarkedPoints)
            dif = abs(r.yMin - r.yMax) * 0.2
            self.plt.axis([r.xMin, r.xMax, r.yMin - dif, r.yMax + dif])
        except Exception as e:
            if self.fill_between != None:
                self.fill_between.remove()
                self.fill_between = None
            self.heightLine.set_data([], [])
            self.markerLine.set_data([], [])
            self.plt.axis([0, 10, 100, 500])
            print(e)
            showerror("Error", e.__str__())

        self.canvas.draw()

    def onExport(self):
        if not self.route:
            return
        toExport = self.route.calculateProfile(
            bool(self.includeStartAndEnd.get()))

        txt = ""
        for i, v in enumerate(toExport):
            txt += ("{}".format(v.cords.index)
                    + "\t"
                    + "{:.4f}".format(v.cords.lat)
                    + " / "
                    + "{:.4f}".format(v.cords.lon)
                    + "\t"
                    + "{:.2f}".format(v.cords.ele)
                    + "\t"
                    + "{:.2f}".format(v.eleDiv).replace(".", ",")
                    + "\t"
                    + "{:.1f}%".format(v.grad)
                    + "\t"
                    + "{:.2f}".format(v.relDis).replace(".", ",")
                    + "\t"
                    + "{:.2f}".format(v.lkm).replace(".", ",")
                    + "\t"
                    + "{:.2f}".format(v.relDisT).replace(".", ",")
                    + "\t"
                    + "{:.2f}".format(v.lkmT).replace(".", ",")
                    + "\n"
                    )

        titles = "\t".join([
            "Index", "Cords         ", "MAS", "Rel MAS", "Grad", "Dis", "Lkm", "Dis tot", "Lkm tot"
        ])
        try:
            with tkinter.filedialog.asksaveasfile(filetypes=[("CSV", "*.csv"), ("All files", "*.*")], defaultextension=".csv", initialfile=self.route.title) as f:
                f.write(titles + "\n" + txt.rstrip())
        except:
            pass

        print(titles + "\n"+txt.rstrip())
        print()

    def onKeyPress(self, e):
        # print(e.key)
        if e.key.lower() in ["h", "r", "home", "p", "o", "x", "y", "control"]:
            key_press_handler(e, self.canvas, self.nav)

    def onMousePress(self, e):
        pass
        # if e.button != 1: return
        # x, y = e.xdata, e.ydata
        # self.plt.set_xlim(x - 1, x + 1)
        # self.plt.set_ylim(y - 10, y + 10)
        # self.canvas.draw()

    def __buildGuiAndRun(self):
        self.win = tk.Tk()
        self.win.wm_title("Corrdinates profile")

        self.fig = Figure()
        self.plt = self.fig.add_subplot()
        self.plt.set_title("Elevation")
        self.plt.axis([0, 10, 100, 500])
        self.fill_between = None
        (self.heightLine,) = self.plt.plot([], [], "ro", markerSize=2)
        (self.markerLine,) = self.plt.plot([], [], "bo", markerSize=2)
        self.plt.set_ylabel("Height MAS")
        self.plt.set_xlabel("Distance in km")

        # A tk.DrawingArea.
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.win)

        self.canvas.mpl_connect("button_press_event", self.onClick)

        self.canvas.get_tk_widget().config(width=1200, height=400)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        self.nav = NavigationToolbar2Tk(self.canvas, self.win)
        self.canvas.mpl_connect("key_press_event", self.onKeyPress)
        self.canvas.mpl_connect("button_press_event", self.onMousePress)
        self.nav.update()
        self.nav.pack(side=tkinter.TOP, fill=tkinter.BOTH, expand=1)

        self.openExport = tk.Button(self.win)
        self.openExport.config(text="Open", width=30, command=self.onImport)
        self.openExport.pack(side=tkinter.LEFT, padx=5, pady=5)

        self.btnExport = tk.Button(self.win)
        self.btnExport.config(text="Export", width=30, command=self.onExport)
        self.btnExport.pack(side=tkinter.RIGHT, padx=5, pady=5)

        self.includeStartAndEnd = tk.IntVar(value=1)
        self.cbIncludeStartAndEnd = tk.Checkbutton(
            self.win, variable=self.includeStartAndEnd)
        self.cbIncludeStartAndEnd.config(text="Include start and end")
        self.cbIncludeStartAndEnd.pack(side=tkinter.RIGHT, padx=5, pady=5)

        self.win.mainloop()
