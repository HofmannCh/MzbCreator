import matplotlib
from matplotlib.backends.backend_tkagg import NavigationToolbar2Tk
from window import Window

if __name__ == "__main__":
    matplotlib.rcParams["figure.subplot.left"] = 0.06
    matplotlib.rcParams["figure.subplot.right"] = 0.98
    matplotlib.rcParams["figure.subplot.bottom"] = 0.15
    matplotlib.rcParams["figure.subplot.top"] = 0.92

    NavigationToolbar2Tk.toolitems = [
        t
        for t in NavigationToolbar2Tk.toolitems
        if t[0] != None and t[0] in ("Home", "Pan", "Zoom")
    ]

    Window()
