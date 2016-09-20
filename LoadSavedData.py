import pyqtgraph as pg
import ok
import sys
import os
import globals as g
import time
import math
import datetime
import numpy as np
import functions
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph import exporters
from tables import *
import tables
import scipy.ndimage as ndi
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
from pyqtgraph.Point import Point

g.init()

#generate layout
app = QtGui.QApplication([])
win = pg.GraphicsWindow()
win.setWindowTitle('pyqtgraph example: crosshair')
label = pg.LabelItem(justify='right')
win.addItem(label)
p1 = win.addPlot(row=0, col=0)

datafilename = QtGui.QFileDialog.getOpenFileName(win,'Open file', os.getcwd(), ("*.log"))
print(datafilename)

file=open(datafilename, 'r')

values = file.read()

array = f.root.array.read()
nparray = np.array(array, dtype=np.uint16)
headers = f.root.headers.read()
print(headers['Bias'])

headers = np.array(headers,dtype=[('ADCSAMPLERATE', float), ('SETUP_TIAgain', float), ('SETUP_preADCgain', float), ('SETUP_pAoffset', float), ('SETUP_ADCVREF', float), ('SETUP_ADCBITS', float), ('Bias', float)])

signal = functions.ConvertRaw(nparray, headers, 1, 100e3)
data1 = signal['y']
t = signal['x']
del signal
f.close()
p1.plot(t, data1, pen="r")

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()

