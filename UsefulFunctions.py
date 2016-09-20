import numpy as np
import scipy.signal as sig
#import matplotlib.pyplot as plt
import pyqtgraph as pg
import matplotlib.pyplot as plt
from pyqtgraph.Qt import QtGui, QtCore
import os
from scipy import io
from scipy.optimize import curve_fit


def Reshape1DTo2D(inputarray, buffersize):
    npieces= np.uint16(len(inputarray)/buffersize)

    voltages=np.array([])
    currents=np.array([])

    for i in range(1, npieces+1):
        if i % 2 == 1:
            currents = np.append(currents, inputarray[(i-1)*buffersize:i*buffersize-1])
            #print('Length Currents: {}'.format(len(currents)))

        else:
            voltages = np.append(voltages, inputarray[(i-1)*buffersize:i*buffersize-1])
            #print('Length Voltages: {}'.format(len(voltages)))

    out = {'v1': voltages*1e-3, 'i1': currents*1e-9}

    return out

def CalculatePoreSize(G,L,s):
    return (G+np.sqrt(G*(G+16*L*s/np.pi)))/(2*s)

def ImportAxopatchData(datafilename):
    x=np.fromfile(datafilename, np.dtype('>f4'))
    f=open(datafilename, 'rb')
    graphene=0
    for i in range(0, 8):
        a=str(f.readline())
        if 'Acquisition' in a or 'Sample Rate' in a:
            samplerate=int(''.join(i for i in a if i.isdigit()))/1000
        if 'I_Graphene' in a:
            graphene=1
            print('This File Has a Graphene Channel!')
    end = len(x)
    if graphene:
        #pore current
        i1 = x[250:end-3:4]
        #graphene current
        i2 = x[251:end-2:4]
        #pore voltage
        v1 = x[252:end-1:4]
        #graphene voltage
        v2 = x[253:end:4]
        output={'graphene': 1, 'samplerate': samplerate, 'i1': i1, 'v1': v1, 'i2': i2, 'v2': v2}
    else:
        i1 = x[250:end-1:2]
        v1 = x[251:end:2]
        output={'graphene': 0, 'samplerate': samplerate, 'i1': i1, 'v1': v1}
    return output

def ImportChimeraRaw(datafilename):
    matfile=io.loadmat(str(os.path.splitext(datafilename)[0]))
    data=np.fromfile(datafilename, np.dtype('<u2'))
    samplerate = np.float64(matfile['ADCSAMPLERATE'])
    TIAgain = np.int32(matfile['SETUP_TIAgain'])
    preADCgain = np.float64(matfile['SETUP_preADCgain'])
    currentoffset = np.float64(matfile['SETUP_pAoffset'])
    ADCvref = np.float64(matfile['SETUP_ADCVREF'])
    ADCbits = np.int32(matfile['SETUP_ADCBITS'])
    closedloop_gain = TIAgain*preADCgain
    bitmask = (2**16 - 1) - (2**(16-ADCbits) - 1)
    data = -ADCvref + (2*ADCvref) * (data & bitmask) / 2**16
    data = (data/closedloop_gain + currentoffset)
    #print((data.shape))
    data.shape=[data.shape[1],]
    #data=np.transpose(data)
    return data

def ImportChimeraData(datafilename):
    matfile=io.loadmat(str(os.path.splitext(datafilename)[0]))
    samplerate=matfile['ADCSAMPLERATE']
    output={}
    if samplerate<4e6:
        data=np.fromfile(datafilename, np.dtype('float64'))
        buffersize=matfile['DisplayBuffer']
        output=Reshape1DTo2D(data, buffersize)
    else:
        data=ImportChimeraRaw(datafilename)
        output['i1']=data
    output['samplerate']=samplerate
    return output

def ExpDecay(t, i0, tau, baseline):
    return i0 * np.exp(-t/tau) + baseline

def CalculateIV(Values, AllData):
    IVData = np.zeros((3, len(Values)))
    for i in range(0, len(Values)):
        IVData[0, i] = Values[i]
        IVData[1, i] = np.mean(AllData[str(Values[i])])
        IVData[2, i] = np.std(AllData[str(Values[i])])
    return IVData

def CalculateIVFromDecay(Values, AllData, samplerate, ChangePoints, delay):
    FitData={}
    IVData=np.zeros((3, len(Values)))

    for i in range(0, len(Values)):
        part = AllData[str(Values[i])]
        xdata = np.arange(len(part))/samplerate
        popt, pcov = curve_fit(ExpDecay, xdata, part)
        perr = np.sqrt(np.diag(pcov))
        fittedData = ExpDecay(xdata, popt[0], popt[1], popt[2])
        IVData[0, i] = Values[i]
        IVData[1, i] = popt[2]
        IVData[2, i] = perr[2]
        FitData['FitValues_{}'.format(str(i))] = fittedData
        FitData['Covariance_{}'.format(str(i))] = pcov
        FitData['EstimatedValues_{}'.format(str(i))] = fittedData
        if i==0:
            FitData['FitValuesX_{}'.format(str(i))] = xdata
        else:
            FitData['FitValuesX_{}'.format(str(i))] = xdata+delay+ChangePoints[i-1]/samplerate

    return IVData, FitData