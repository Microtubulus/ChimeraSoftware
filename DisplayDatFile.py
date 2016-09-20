## Display Axopatch Traces

import numpy as np
import numpy as np
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import os

graphene=0

app = QtGui.QApplication([])
win = pg.GraphicsWindow(title="Ionic")

datafilename = QtGui.QFileDialog.getOpenFileName(win, 'Open file', os.getcwd(), ("*.dat"))

x=np.fromfile(datafilename, np.dtype('>f4'))
f=open(datafilename, 'rb')

for i in range(0, 8):
    a=str(f.readline())
    if 'Acquisition' in a or 'Sample Rate' in a:
        samplerate=int(''.join(i for i in a if i.isdigit()))/1000
    if 'I_Graphene' in a:
        graphene=1
        print('This File Has a Graphene Channel!')

print(samplerate)
end = len(x)


if graphene:
    win2 = pg.GraphicsWindow(title="Graphene")

    #pore current
    i1 = x[250:end-3:4]
    #graphene current
    i2 = x[251:end-2:4]
    #pore voltage
    v1 = x[252:end-1:4]
    #graphene voltage
    v2 = x[253:end:4]
    time = np.arange(len(i1))/samplerate
    time.shape = [len(i1),]

    p = win.addPlot(title="Current", showGrid=1)
    p.plot(time, i1, title="Ionic Current")
    p.setLabel('bottom', "Time", units='s')
    p.setLabel('left', "Current", units='A')
    win.nextRow()
    p2 = win.addPlot(title="Voltage", showGrid=1)
    p2.plot(time, v1, title="Ionic Voltage")
    p2.setLabel('bottom', "Time", units='s')
    p2.setLabel('left', "Voltage", units='V')

    p3 = win2.addPlot(title="Current", showGrid=1)
    p3.plot(time, i2, title="Gaphene Current")
    p3.setLabel('bottom', "Time", units='s')
    p3.setLabel('left', "Current", units='A')
    win2.nextRow()
    p3 = win2.addPlot(title="Voltage", showGrid=1)
    p3.plot(time, v2, title="Graphene Voltage")
    p3.setLabel('bottom', "Time", units='s')
    p3.setLabel('left', "Voltage", units='V')


else:
    i1 = x[250:end-1:2]
    v1 = x[251:end:2]
    time = np.arange(len(i1))/samplerate
    time.shape = [len(i1),]
    p = win.addPlot(title="Current", showGrid=1)
    p.plot(time, i1, title="Ionic Current")
    p.setLabel('bottom', "Time", units='s')
    p.setLabel('left', "Current", units='A')
    win.nextRow()
    p2 = win.addPlot(title="Voltage", showGrid=1)
    p2.plot(time, v1, title="Ionic Voltage")
    p2.setLabel('bottom', "Time", units='s')
    p2.setLabel('left', "Voltage", units='V')

## Start Qt event loop unless running in interactive mode or using pyside.
if __name__ == '__main__':
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
        QtGui.QApplication.instance().exec_()