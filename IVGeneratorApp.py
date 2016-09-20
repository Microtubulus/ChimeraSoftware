import numpy as np
import scipy.signal as sig
import pyqtgraph as pg
from pyqtgraph.Qt import QtGui, QtCore
import os
from scipy import io
import UsefulFunctions as f
#import Database as db


def main():
    #Parameters
    delay = 1000e-3 #delay in seconds
    useGrapheneChannel=0

    #Initializations
    app = QtGui.QApplication([])
    w = QtGui.QWidget()
    #w.setFixedSize(1500, 750)
    pg.setConfigOptions(antialias=True)
    win = pg.GraphicsWindow(title="Current Voltages")

    #App Layout
    Conductivity = pg.SpinBox(value=10, suffix='S/m', siPrefix=True, dec=True, step=0.5, minStep=0.5, bounds=[1E-6, 100])
    PoreLength = pg.SpinBox(value=0.7e-9, suffix='m', siPrefix=True, dec=True, step=1e-9, minStep=1e-9, bounds=[1E-12, 1e-3])
    conductanceText = QtGui.QLabel()
    filesystem = QtGui.QFileSystemModel()
    filesystem.setRootPath(QtCore.QDir.currentPath())
    tree =  QtGui.QColumnView()
    tree.setModel(filesystem)
    tree.setRootIndex(filesystem.index(QtCore.QDir.currentPath()))

    CalculatedPoreSize = QtGui.QLabel()

    mainplot=pg.PlotWidget(None, 'w')
    layout = QtGui.QGridLayout()
    openbutton=QtGui.QPushButton('Load IV Trace')
    w.setLayout(layout)

    layout.addWidget(Conductivity, 0, 1)   # button goes in upper-left
    layout.addWidget(QtGui.QLabel('Conductivity:'), 0, 0)   # button goes in upper-left
    layout.addWidget(PoreLength, 1, 1)   # button goes in upper-left
    layout.addWidget(QtGui.QLabel('Pore Length:'), 1, 0)   # button goes in upper-left
    layout.addWidget(CalculatedPoreSize, 2, 0, 1, 2)   # button goes in upper-left
    layout.addWidget(mainplot, 0, 3, 5, 4)   # button goes in upper-left
    layout.addWidget(conductanceText, 3, 0, 2, 2)   # button goes in upper-left
    #layout.addWidget(tree, 4, 0, 1, 2)   # button goes in upper-left
    w.show()

    datafilename = QtGui.QFileDialog.getOpenFileName(w, 'Open file', os.getcwd(), ("*.log *.dat"))
    if datafilename[-3::]=='dat':
        isdat=1
        output = f.ImportAxopatchData(datafilename)
        if useGrapheneChannel:
            output['i1'] = output['i2']
            output['v1'] = output['v2']
    else:
        isdat=0
        output = f.ImportChimeraData(datafilename)

    #datafilename='/Users/migraf/PycharmProjects/untitled1/1103_31A_500mMKCl.dat'
    delayinpoints = delay*output['samplerate']
    diffVoltages = np.diff(output['v1'])
    VoltageChangeIndexes =diffVoltages
    ChangePoints = np.where(diffVoltages)[0]
    Values = output['v1'][ChangePoints]
    Values = np.append(Values, output['v1'][::-1][0])
    print('Indexes: {}'.format(ChangePoints))
    print('Values: {}'.format(Values))
    print(output['samplerate'])
    #   Store All Data
    AllData={}
    # First
    AllData[str(Values[0])] = output['i1'][0:ChangePoints[0]]
    for i in range(1,len(Values)-1):
        AllData[str(Values[i])] = output['i1'][ChangePoints[i-1]+delayinpoints:ChangePoints[i]]
    #Last
    AllData[str(Values[len(Values)-1])] = output['i1'][ChangePoints[len(ChangePoints)-1]+delayinpoints:len(output['i1'])-1]
    Means = {}
    STD = {}
    IVData=np.zeros((3, len(Values)))
    for i in range(0, len(Values)):
        IVData[0, i] = Values[i]
        IVData[1, i] = np.mean(AllData[str(Values[i])])
        IVData[2, i] = np.std(AllData[str(Values[i])])
        Means[str(Values[i])] = np.mean(AllData[str(Values[i])])
        STD[str(Values[i])] = np.std(AllData[str(Values[i])])


    #print(IVData)

    #Draw
    time=np.arange(len(output['i1']))/output['samplerate']
    time.shape=[len(output['i1']),]
    p2 = win.addPlot(title="Current", showGrid=1)
    p2.plot(time, output['i1'], pen=(255, 0, 0))
    p2.addItem(pg.LinearRegionItem([time[0], time[ChangePoints[0]]], movable=False))
    for i in range(1, len(Values)-1):
        s=int(ChangePoints[i-1]+delayinpoints)
        e=int(ChangePoints[i])
        p2.addItem(pg.LinearRegionItem([time[s], time[e]], movable=False))
    p2.addItem(pg.LinearRegionItem([time[int(ChangePoints[len(ChangePoints)-1]+delayinpoints)], time[len(output['i1'])-1]], movable=False))
    win.nextRow()
    p3 = win.addPlot(title="Voltages", showGrid=1)
    p3.plot(time, output['v1'], pen=(255, 255, 0))
    p2.setLabel('bottom', "Time", units='s')
    p2.setLabel('left', "Current", units='A')
    p3.setLabel('bottom', "Time", units='s')
    p3.setLabel('left', "Voltage", units='V')


    #Fitting
    fitresults = np.polyfit(IVData[0, :], IVData[1, :], 1)
    conductance = fitresults[0]
    resistance = 1/conductance
    #text = pg.TextItem('Resistance R={:.3e} Ohm \nConductivity G={:.3e} siemens'.format(resistance, conductance), color=(255, 0, 0), html=None, anchor=(0, 0), border=None, fill=None, angle=0)
    conductanceText.setText('Resistance R={:.3e} Ohm \nConductance G={:.3e} siemens'.format(resistance, conductance))
    #FitLine
    yvalues=IVData[0, :]*fitresults[0]+fitresults[1]

    #mainplot.addLegend(offset=(550, 350))
    err = pg.ErrorBarItem(x=IVData[0, :], y=IVData[1,:], top=IVData[2, :], bottom=IVData[2, :], beam=0.5*1e-3)
    mainplot.addItem(err)
    mainplot.plot(IVData[0, :], IVData[1,:], pen=None, symbol='o', symbolPen=None, symbolSize=10, symbolBrush=(255, 0, 0), name='Datapoints + STD')
    mainplot.setLabel('left', "Current", units='A')
    mainplot.setLabel('bottom', "Voltage", units='V')
    mainplot.plot(IVData[0, :], yvalues, pen=(0, 255, 0), symbol='o', symbolPen=None, symbolSize=0, symbolBrush=(0, 255, 0), name='Linear Fit')

    d=f.CalculatePoreSize(conductance, PoreLength.value(), Conductivity.value())
    CalculatedPoreSize.setText('Estimated Pore Size: {:.3f} nm'.format(d*1e9))

    def ConductivityChanged(sb):
        d=f.CalculatePoreSize(conductance, PoreLength.value(), Conductivity.value())
        CalculatedPoreSize.setText('Estimated Pore Size: {:.3f} nm'.format(d*1e9))

    Conductivity.sigValueChanged.connect(ConductivityChanged)
    PoreLength.sigValueChanged.connect(ConductivityChanged)
    import sys
    if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
      QtGui.QApplication.instance().exec_()

if __name__ == '__main__':
    main()
