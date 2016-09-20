from PyQt4.QtGui import QApplication, QMainWindow
from ui2 import Ui_mainWindow
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
from scipy import io
from scipy import signal as si
import IVGeneratorApp

#   Draw UI
app = QApplication(sys.argv)
window = QMainWindow()
ui = Ui_mainWindow()
ui.setupUi(window)

#   Initialize Chimera and Set Values
g.init()
xem = ok.FrontPanel()
functions.InitializeChimera(xem)
ui.zerovoltagevlaue.setValue(g.myvoltageoffset)
ui.ZeroCurrentValue.setText(str(g.SETUP_pAoffset))
ui.IVBounds.setValue(g.HigherIV)
ui.IVStep.setValue(g.StepIV)
ui.IVDwell.setValue(g.timeIV)
ui.ExperimentName.setText(g.experimentName)
ui.LowPassValue.setMaximum(((g.ADCSAMPLERATE/g.displaysubsample)/2)/1e3-1)
ui.LowPassValue.setMinimum(1)
ui.DisplayDownSamplingRate.setValue(g.displaysubsample)
ui.MakeIV.setStyleSheet('QPushButton {background-color: green; color: black;}')
g.DataFolder=os.path.join(os.getcwd(), 'Data')
ui.DataFolder.setText(g.DataFolder)
ui.MinDwellTimeED.setMinimum(1/(g.ADCSAMPLERATE/g.displaysubsample) * 1e6)



# Plots
curve = ui.CurrentPlot.plot(pen='k')
ui.CurrentPlot.setMouseEnabled(x=0, y=1)
ui.CurrentPlot.plotItem.setLabel('left', 'Current [nA]')
ui.CurrentPlot.plotItem.setLabel('bottom', 'Time [s]')
ui.CurrentPlot.setBackground('w')

# Connection Functions
def ChangeVoltageValue(sb):
    ui.AppliedVoltage.display(sb)
    g.newbiasvalue = sb
    g.RestartBuffer=1
    functions.CHIMERA_updateDACvalues1(xem)
def updateBW():
        out = functions.CHIMERA_bandwidthtimer(xem)
        text1 = "Time\n{0}\nUSB Read Rate\n{1:} kHz\nUSB Write Rate\n{2}".format(out['text_time'],out['USB_readrate'], out['USB_writerate'])
        ui.ReadData.setText(text1)
        text2 = "Buffer\n{0} kB\nBuffer Size\n{1} %\nSeconds buffered\n{2:.3f} sec".format(out['buffer'],out['bufferPC'], out['bufferseconds'])
        ui.ReadData2.setText(text2)
def update():
    if ui.USBTransfer.isChecked():
        global curve, data, ptr, p6
        functions.CHIMERA_process_triggers(xem)
        EventsInBlock=0
        if ui.LowPass.checkState():
            functions.PlotValues(ui.LowPassValue.value()*1e3)
        else:
            functions.PlotValues(0)
        if ui.EventDetectionSwitch.checkState():
            if ui.FromRawData.checkState():
                ndown, nup = functions.EventDetection(g.blockvalues, ui.EventCoeff.value(), np.ceil(ui.MinDwellTimeED.value()*1e-6*g.ADCSAMPLERATE), ui.UpwardEventsAllowed.checkState())
            else:
                ndown, nup = functions.EventDetection(g.displaybuffer, ui.EventCoeff.value(), np.ceil(ui.MinDwellTimeED.value()*1e-6*g.ADCSAMPLERATE/g.displaysubsample), ui.UpwardEventsAllowed.checkState())
            ui.EventThreshold.setText('Event Threshold = {:.3f} nA'.format(g.EventLimit))
            if ndown+nup > 0:
                ui.EventsFound.setText('{}  Events Found...'.format(ndown))
                ui.EventsFoundUP.setText('{}  Events Found UP...'.format(nup))
                EventsInBlock=1
            else:
                ui.EventsFound.setText('{}  Events Found...'.format(0))
                ui.EventsFoundUP.setText('{}  Events Found UP...'.format(0))

#        f, Pxx_den = si.welch(g.displaybuffer, g.ADCSAMPLERATE/g.displaysubsample)
#        curvePSD.setData(f, Pxx_den)

        g.currentIDC = np.mean(g.displaybuffer)
        g.currentRMS = np.std(g.displaybuffer)
        v = np.arange(len(g.displaybuffer))
        curve.setData(v / (g.ADCSAMPLERATE/g.displaysubsample), g.displaybuffer)
        if ui.CenterPlot.checkState():
            ui.CurrentPlot.setYRange(g.currentIDC-10*g.currentRMS, g.currentIDC+10*g.currentRMS)
        ui.currentIDC.setText('Current Idc = {:.3f} nA'.format(g.currentIDC))
        ui.currentRMS.setText('Current RMS = {:.3f} pA'.format(g.currentRMS*1000))
        ui.currentRMSRaw.setText('Current RMS Raw Data = {:.3f} pA'.format(g.currentRMSRaw*1000))
        if g.newbiasvalue > 0.0001 or g.newbiasvalue < -0.0001:
            ui.CurrentCond.setText('Current Conductance = {:.3f} nS'.format(g.currentIDC/g.newbiasvalue))
        else:
            ui.CurrentCond.setText('Cannot calculate: Bias=0')
        if (ui.SaveData.checkState() and not ui.EventDetectionSwitch.checkState()) or (ui.SaveData.checkState() and EventsInBlock):
            if (g.ADClogreset==1) or (g.ADClogsize > g.MAXLOGBYTES):
                if g.fisopen:
                    g.file.close()
                    g.fisopen=0
                g.ADClogsize=0
                now=datetime.datetime.today()
                nowstr='_{}{:02d}{:02d}_{:02d}{:02d}{:02d}'.format(now.year, now.month, now.day, now.hour, now.minute, now.second)
                if ui.SaveDataFromDisplay.isChecked():
                    mdict = {'DisplayBuffer': len(g.displaybuffer), 'ADCSAMPLERATE': g.ADCSAMPLERATE/g.displaysubsample, 'mytimestamp': str(datetime.datetime.today()), 'bias2value': g.newbiasvalue, 'SETUP_biasvoltage': g.newbiasvalue, 'SETUP_ADCVREF': g.ADCVREF, 'SETUP_ADCSAMPLERATE': g.ADCSAMPLERATE, 'SETUP_ADCBITS': g.ADCBITS, 'SETUP_TIAgain': g.SETUP_TIAgain, 'SETUP_preADCgain': g.SETUP_preADCgain, 'SETUP_pAoffset': g.SETUP_pAoffset, 'SETUP_mVoffset': g.myvoltageoffset}
                else:
                    mdict = {'DisplayBuffer': len(g.displaybuffer), 'ADCSAMPLERATE': g.ADCSAMPLERATE, 'mytimestamp': str(datetime.datetime.today()), 'bias2value': g.newbiasvalue, 'SETUP_biasvoltage': g.newbiasvalue, 'SETUP_ADCVREF': g.ADCVREF, 'SETUP_ADCSAMPLERATE': g.ADCSAMPLERATE, 'SETUP_ADCBITS': g.ADCBITS, 'SETUP_TIAgain': g.SETUP_TIAgain, 'SETUP_preADCgain': g.SETUP_preADCgain, 'SETUP_pAoffset': g.SETUP_pAoffset, 'SETUP_mVoffset': g.myvoltageoffset}
                if g.IVOn:
                    g.file = open(os.path.join(g.DataFolder, g.todaysfolder, '{}'.format(g.experimentName), '{}{}{}{}'.format('IV_', g.experimentName, nowstr, '.log')), 'ab')
                    io.savemat(os.path.join(g.DataFolder, g.todaysfolder, '{}'.format(g.experimentName), '{}{}{}{}'.format('IV_', g.experimentName, nowstr, '.mat')), mdict, True, '5', False, False, 'row')
                else:
                    g.file = open(os.path.join(g.DataFolder, g.todaysfolder, '{}'.format(g.experimentName), '{}{}{}'.format(g.experimentName, nowstr, '.log')), 'ab')
                    io.savemat(os.path.join(g.DataFolder, g.todaysfolder, '{}'.format(g.experimentName), '{}{}{}'.format(g.experimentName, nowstr, '.mat')), mdict, True, '5', False, False, 'row')
                g.fisopen=1
                g.ADClogreset=0
                g.writtenBlocks=0
            if g.fisopen:
                if ui.SaveDataFromDisplay.isChecked():
                    if ui.SaveDataVoltage.isChecked():
                        voltages = np.ones(len(g.displaybuffer))*g.newbiasvalue*1000
                        final = np.vstack((g.displaybuffer, voltages))
                        g.file.write((final.copy(order='C')))
                    else:
                        g.file.write((g.displaybuffer.copy(order='C')))
                    g.ADClogsize+=2*len(g.displaybuffer)
                else:
                    g.file.write(np.uint16(g.blockvalues))
                    g.ADClogsize+=2*len(g.blockvalues)
                g.writtenBlocks+=1
                ui.WrittenBlocks.setText('Written Blocks: {}'.format(g.writtenBlocks))
        elif not ui.SaveData.checkState():
            if g.fisopen:
                g.file.close()
                g.fisopen=0
                g.ADClogreset==1
def valueChangedOffset(sb):
    g.myvoltageoffset = sb
    g.RestartBuffer=1
    functions.CHIMERA_updateDACvalues1(xem)
def ZeroCur():
    g.SETUP_pAoffset = g.SETUP_pAoffset - g.currentIDC*1E-9
    ui.ZeroCurrentValue.setText('Current Offset = {:.3e}'.format(g.SETUP_pAoffset))
    g.RestartBuffer=1
def ResetBuffer():
    print("Buffer is resetting...")
    ans1=xem.SetWireInValue(g.EP_WIREIN_TEST1, g.EPBIT_GLOBALRESET, g.EPBIT_GLOBALRESET)
    xem.UpdateWireIns()
    time.sleep(0.1)
    ans2=xem.SetWireInValue(g.EP_WIREIN_TEST1, 0, g.EPBIT_GLOBALRESET)
    xem.UpdateWireIns()
    g.RestartBuffer=1
def ZeroVolt():
    Vdelta=0.02
    ui.VoltageChooser.setValue(Vdelta)
    functions.CHIMERA_updateDACvalues1(xem)
    ResetBuffer()
    time.sleep(1)
    update()
    measI1 = g.currentIDC
    ui.VoltageChooser.setValue(0)
    functions.CHIMERA_updateDACvalues1(xem)
    ResetBuffer()
    time.sleep(1)
    update()
    measI2 = g.currentIDC
    deltaI = measI1-measI2
    measR = Vdelta/deltaI
    ResetBuffer()
    g.myvoltageoffset += -measI2 * measR
    functions.CHIMERA_updateDACvalues1(xem)
    ui.zerovoltagevlaue.setValue(g.myvoltageoffset)
    update()
def saveConfig():
    import pickle
    f = open('store.pckl', 'wb')
    variables ={"Voffset": g.myvoltageoffset, "pAOffset": g.SETUP_pAoffset, "LowerIV": g.LowerIV, "HigherIV": g.HigherIV, "StepIV": g.StepIV, "experimentName": g.experimentName, "timeIV": g.timeIV}
    pickle.dump(variables, f)
    f.close()
def QCloseEvent(w):
    saveConfig()
    print('Application closed, config saved...')
def ExpTextChange():
    sb=ui.ExperimentName.text()
    g.experimentName = sb
    if not os.path.exists(os.path.join(g.DataFolder, g.todaysfolder, sb)):
        os.makedirs(os.path.join(g.DataFolder, g.todaysfolder, sb))
def DownSampleChanged(sb):
    g.displaysubsample=sb
    ui.LowPassValue.setMaximum(((g.ADCSAMPLERATE/sb)/2)/1e3-1)
    ui.MinDwellTimeED.setMinimum(1/(g.ADCSAMPLERATE / sb) * 1e6)
def SaveDataChecked():
        g.ADClogreset=1
def ReconnectF():
    functions.InitializeChimera(xem)
def ChangeIVValues():
    g.HigherIV = ui.IVBounds.value()
    g.StepIV = ui.IVStep.value()
    g.timeIV = ui.IVDwell.value()
def IVExecute():
    g.newbiasvalue = g.AllVoltages[g.IVExecuteCounter]
    if g.IVExecuteCounter == 0:
        ui.EventDetectionSwitch.setChecked(0)
        ui.SaveDataVoltage.setChecked(1)
        ui.SaveDataFromDisplay.setChecked(1)
        ui.SaveData.setCheckState(2)
        SaveDataChecked()
    ui.AppliedVoltage.display(g.newbiasvalue)
    functions.CHIMERA_updateDACvalues1(xem)
    ResetBuffer()
    g.IVExecuteCounter+=1
    print(("Voltage applied: %s Volts" % str(g.newbiasvalue)))
    if g.IVExecuteCounter == len(g.AllVoltages):
        IVTimer.stop()
        ui.MakeIV.setStyleSheet('QPushButton {background-color: green; color: black;}')
        ui.SaveDataVoltage.setChecked(0)
        ui.SaveDataFromDisplay.setChecked(0)
        ui.SaveData.setCheckState(0)
        SaveDataChecked()
        g.IVOn=0
        #IVGeneratorApp.main()
        #GenerateIVFromFileName.MakeIV(r"C:\Users\migraf\PycharmProjects\Opal Kelly 3.4\Data\2015-06-08\NewChimeraSoftwareIV\NewChimeraSoftwareIV_20150608_175745.log", w, mainplot)
def MakeIVPushed():
    g.IVOn=1
    g.IVUseAlternatingV=1
    g.AllVoltages=functions.MakeAllVoltagesForIV(g.StepIV, g.HigherIV)
    g.IVExecuteCounter = 0
    IVTimer.start(g.timeIV*1000)
    ui.MakeIV.setStyleSheet('QPushButton {background-color: red; color: black;}')
def InputChanged():
    ind=ui.InputChooser.currentIndex()
    if ind==0:
        mux='Filtered'
    if ind==1:
        mux='MUX0'
    if ind==2:
        mux='VIN1'
    if ind==3:
        mux='AUXJ14'
    print(mux)
    functions.SetADCInput(xem, mux)
def ZapPressed():
    g.ZapVoltage = ui.ZapVoltage.value()
    g.ZapTime = ui.ZapTime.value()
    g.ZapFrequency = ui.ZappingFrequency.value()
    g.VoltageBeforeZap=g.newbiasvalue
    g.ZapOnce=0
    ZapTimer.start(g.ZapTime*1e3)
def AutoZapPressed():
    if ui.AutoZapOn.checkState():
        AutoZapRoutine.start(g.ZapFrequency*1e3)
    else:
        AutoZapRoutine.stop()
def ZapExecute():
    ui.VoltageChooser.setValue(ui.ZapVoltage.value())
    if g.ZapOnce>0:
        ui.VoltageChooser.setValue(g.VoltageBeforeZap)
        ZapTimer.stop()
    g.ZapOnce+=1
def AutoZapRoutineFct():
    #   Conductance nS
    if g.ZappingInputChoice == 0:
        if(ui.ZappingLimit.value() > g.currentIDC/g.newbiasvalue):
            g.ZapVoltage = ui.ZapVoltage.value()
            g.ZapTime = ui.ZapTime.value()
            g.ZapFrequency = ui.ZappingFrequency.value()
            g.VoltageBeforeZap=g.newbiasvalue
            g.ZapOnce=0
            ZapTimer.start(g.ZapTime*1e3)
    if g.ZappingInputChoice == 1:
        if(ui.ZappingLimit.value() > g.currentIDC):
            g.ZapVoltage = ui.ZapVoltage.value()
            g.ZapTime = ui.ZapTime.value()
            g.ZapFrequency = ui.ZappingFrequency.value()
            g.VoltageBeforeZap=g.newbiasvalue
            g.ZapOnce=0
            ZapTimer.start(g.ZapTime*1e3)
def ZappingInputChanged():
    ind=ui.ZappingChooser.currentIndex()
    if ind==0:
        g.ZappingInputChoice=0
        ui.ZappingLimit.setSuffix(' nS')
    if ind==1:
        g.ZappingInputChoice=1
        ui.ZappingLimit.setSuffix(' nA')
def SetDataFolderPushed():
    folder = QtGui.QFileDialog.getExistingDirectory(window, 'Select in which Folder to save your data', os.getcwd())
    g.DataFolder = folder
    ui.DataFolder.setText(g.DataFolder)
def FromRawDataClicked():
    if ui.FromRawData.checkState():
        ui.MinDwellTimeED.setMinimum(1/(g.ADCSAMPLERATE) * 1e6)
    else:
        ui.MinDwellTimeED.setMinimum(1/(g.ADCSAMPLERATE/g.displaysubsample) * 1e6)

#   Connect  Values
ui.VoltageChooser.valueChanged.connect(ChangeVoltageValue)
ui.mv100.clicked.connect(lambda: ui.VoltageChooser.setValue(0.1))
ui.mv200.clicked.connect(lambda: ui.VoltageChooser.setValue(0.2))
ui.mv300.clicked.connect(lambda: ui.VoltageChooser.setValue(0.3))
ui.mv400.clicked.connect(lambda: ui.VoltageChooser.setValue(0.4))
ui.mv500.clicked.connect(lambda: ui.VoltageChooser.setValue(0.5))
ui.mv100n.clicked.connect(lambda: ui.VoltageChooser.setValue(-0.1))
ui.mv200n.clicked.connect(lambda: ui.VoltageChooser.setValue(-0.2))
ui.mv300n.clicked.connect(lambda: ui.VoltageChooser.setValue(-0.3))
ui.mv400n.clicked.connect(lambda: ui.VoltageChooser.setValue(-0.4))
ui.mv500n.clicked.connect(lambda: ui.VoltageChooser.setValue(-0.5))
ui.ZeroVolt.clicked.connect(lambda: ui.VoltageChooser.setValue(0))
ui.p10.clicked.connect(lambda: ui.VoltageChooser.setValue(g.newbiasvalue+0.01))
ui.p50.clicked.connect(lambda: ui.VoltageChooser.setValue(g.newbiasvalue+0.05))
ui.p100.clicked.connect(lambda: ui.VoltageChooser.setValue(g.newbiasvalue+0.1))
ui.n10.clicked.connect(lambda: ui.VoltageChooser.setValue(g.newbiasvalue-0.01))
ui.n50.clicked.connect(lambda: ui.VoltageChooser.setValue(g.newbiasvalue-0.05))
ui.n100.clicked.connect(lambda: ui.VoltageChooser.setValue(g.newbiasvalue-0.1))
ui.negateBias.clicked.connect(lambda: ui.VoltageChooser.setValue(g.newbiasvalue*-1))
ui.IVStep.valueChanged.connect(ChangeIVValues)
ui.IVBounds.valueChanged.connect(ChangeIVValues)
ui.IVDwell.valueChanged.connect(ChangeIVValues)
window.closeEvent=QCloseEvent
ui.DisplayDownSamplingRate.valueChanged.connect(DownSampleChanged)
ui.Reconnect.clicked.connect(ReconnectF)
ui.SaveData.clicked.connect(SaveDataChecked)
ui.ZeroCurrent.clicked.connect(ZeroCur)
ui.ZeroVoltage.clicked.connect(ZeroVolt)
ui.zerovoltagevlaue.valueChanged.connect(valueChangedOffset)
ui.ResetBufferButton.triggered.connect(ResetBuffer)
ui.ExperimentName.editingFinished.connect(ExpTextChange)
ui.MakeIV.clicked.connect(MakeIVPushed)
ui.InputChooser.currentIndexChanged.connect(InputChanged)
ui.ZapButton.clicked.connect(ZapPressed)
ui.AutoZapOn.clicked.connect(AutoZapPressed)
ui.ZappingChooser.currentIndexChanged.connect(ZappingInputChanged)
ui.SetDataFolder.clicked.connect(SetDataFolderPushed)
ui.FromRawData.clicked.connect(FromRawDataClicked)
#   Timed Events
timer = QtCore.QTimer()
timer.timeout.connect(update)
timer.start(100)

timerBW = QtCore.QTimer()
timerBW.timeout.connect(updateBW)
timerBW.start(1000)

IVTimer = QtCore.QTimer()
IVTimer.timeout.connect(IVExecute)

ZapTimer = QtCore.QTimer()
ZapTimer.timeout.connect(ZapExecute)

AutoZapRoutine = QtCore.QTimer()
AutoZapRoutine.timeout.connect(AutoZapRoutineFct)


window.show()
sys.exit(app.exec_())