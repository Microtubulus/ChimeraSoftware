# Bandwith Timer
def CHIMERA_bandwidthtimer(xem):
    import ok
    import sys
    import globals
    import datetime
    import math
    import numpy as np
    np.set_printoptions(precision=3)

    #globals.init()
    mytime=datetime.datetime.today()-globals.timezero
    mytimestring=str(mytime)
    text_time=mytimestring
    text_readrate=globals.read_monitor/2000
    text_writerate=globals.write_monitor/2000
    xem.UpdateWireOuts()
    fifolevel = 4*(xem.GetWireOutValue(globals.EP_WIREOUT_ADCFIFOCOUNT) & int('0111111111111111', 2))
    globals.write_monitor=0
    globals.read_monitor=0
    textOutputs = {'text_time': text_time, 'USB_readrate': text_readrate,'USB_writerate':text_writerate,'buffer':fifolevel, 'bufferPC': math.floor(100*fifolevel/globals.HWBUFFERSIZE_KB), 'bufferseconds': fifolevel*1024/(100e6 / 24 * 2)}
    return textOutputs

def CHIMERA_process_triggers(xem):
    import ok
    import sys
    import globals
    import datetime
    import numpy as np
    xem.UpdateTriggerOuts()
    ba = bytearray(globals.ADC_pkt_len)
    out = xem.ReadFromBlockPipeOut(globals.EP_PIPEOUT_ADC, globals.ADC_xfer_blocksize, ba)
    #print(out)
    #int=np.uint8(ba)
    #bytesread = len(readbytes)
    #typecasted = int.view(np.uint32)
    globals.blockvalues = np.uint16((np.uint8(ba)).view(np.uint32))
    globals.read_monitor += 2*len(globals.blockvalues)
    #y = x.view(np.uint32)
    #readvalues = x

def VECTOR_biasDAC_AD5541A(biasdacvalue, fastcdacvalue):
    import globals as g
    import numpy as np
    from sp import multirate
    import scipy


    biasDACdata = np.zeros(g.DAC_SCANCHAIN_LENGTH,dtype=np.int)
    fastcDACdata = np.zeros(g.DAC_SCANCHAIN_LENGTH,dtype=np.int)
    DACbits = 16

    biasDACbinary=np.zeros(DACbits,dtype=np.int)
    binarystring = "{0:b}".format(biasdacvalue)
    binaryarray = np.array(list(binarystring),dtype=int)
    biasDACbinary[DACbits-len(binaryarray):DACbits] = binaryarray


    fastcDACbinary=np.zeros(DACbits,dtype=np.int)
    binarystring = "{0:b}".format(fastcdacvalue)
    binaryarray = np.array(list(binarystring),dtype=int)
    fastcDACbinary[DACbits-len(binaryarray):DACbits] = binaryarray


    biasDACdata = np.flipud(biasDACbinary)
    fastcDACdata = np.flipud(fastcDACbinary)

    returnvector = g.EPBIT_DACSDI * biasDACdata + g.EPBIT_DACSDI_FASTC * fastcDACdata

    upreturn = multirate.upsample(returnvector,2,0) + multirate.upsample(returnvector,2,1)
    vectorlength = len(upreturn)
    v = np.arange(2, vectorlength + 2, dtype=np.int)
    myclk = 0.5+0.5*scipy.signal.square(1/1*3.1416*v)
    returnvector = upreturn + g.EPBIT_DACCLK*myclk
    returnvector = np.flipud(returnvector)
    returnvector = np.concatenate([[g.EPBIT_DACNCS+g.EPBIT_DAC_NLOAD, g.EPBIT_DACNCS+g.EPBIT_DAC_NLOAD, g.EPBIT_DAC_NLOAD], returnvector + g.EPBIT_DAC_NLOAD, [g.EPBIT_DACNCS+g.EPBIT_DAC_NLOAD, g.EPBIT_DACNCS+g.EPBIT_DAQTRIGGER, g.EPBIT_DACNCS+g.EPBIT_DAC_NLOAD]])
    returnvector = returnvector + (g.EP_ACTIVELOWBITS-g.EPBIT_DACNCS-g.EPBIT_DAC_NLOAD)
    lastelement = returnvector[len(returnvector)-1]
    returnvector = np.concatenate([returnvector, lastelement*np.ones(32)])
    return returnvector

def CHIMERA_updateDACvalues1(xem):
    import globals
    import numpy as np
    import math
    Cfastvalue = globals.CFAST_CAP0
    #Cfastvalue = globals.CFAST_CAP0+globals.CFAST_CAP1 #for extended range
    newCfastDACvoltage = - globals.newbiasvalue * globals.myCfast / (globals.CFAST_gain*Cfastvalue)
    biasDACcode = np.uint16((-globals.newbiasvalue-globals.myvoltageoffset+0.5*globals.DACFULLSCALE)/globals.DACFULLSCALE*(math.pow(2, globals.DACBITS)))
    fastcDACcode = np.uint16((-newCfastDACvoltage+0.5*globals.DACFULLSCALE)/globals.DACFULLSCALE * (math.pow(2, globals.DACBITS)))
    mydacvector = np.uint32(VECTOR_biasDAC_AD5541A(biasDACcode,fastcDACcode))
    CHIMERA_sendscanvector1(xem, np.transpose(mydacvector))

def CHIMERA_sendscanvector1(xem, scanvectorfile):
    import globals
    import ok
    import numpy as np
    bitinversions = 0
    pack32 = np.uint32(scanvectorfile)
    packbixor = pack32 | bitinversions
    packet1 = packbixor.view(np.uint8)
    packet = bytearray(packet1)
    modu = np.mod(len(packet), 16)
    if modu:
        packet.reverse()
        for x in range(0, modu):
            packet.append(0)
        packet.reverse()
    bytes_sent = xem.WriteToPipeIn(globals.EP_PIPEIN_SCANCHAINS, packet)

def CHIMERA_updateDPOTvalues1(xem):
    import globals
    import numpy as np
    import math
    myDPOTvalue = globals.freqComp
    DPOTbits = 8
    DPOTcode = np.uint8(np.round(myDPOTvalue/100*(math.pow(2,DPOTbits))))
    mydacvector = np.concatenate([VECTOR_DPOT_AD5262(DPOTcode, 0), VECTOR_DPOT_AD5262(DPOTcode, 1)])
    CHIMERA_sendscanvector1(xem, mydacvector)

def VECTOR_DPOT_AD5262(DPOTvalue, DPOTaddress):
    import numpy as np
    import globals
    import scipy
    from sp import multirate

    DPOTdata = np.zeros(globals.DPOT_SCANCHAIN_LENGTH, dtype=np.int)
    DPOTdata[globals.DPOT_A-1] = DPOTaddress
    DPOTbits = 8

    getBin = lambda x, n: x >= 0 and str(bin(x))[2:].zfill(n) or "-" + str(bin(x))[3:].zfill(n)
    binaryarray = getBin(DPOTvalue,DPOTbits)
    binaryarray = np.array(list(binaryarray),dtype=int)

    DPOTdata[globals.DPOT_LSB-1:globals.DPOT_MSB] = np.flipud(binaryarray)
    returnvector = globals.EPBIT_DPOT_SDI * DPOTdata

    returnvector1  = np.array(multirate.upsample(returnvector,2,0), dtype=np.int)
    returnvector2  = np.array(multirate.upsample(returnvector,2,1), dtype=np.int)
    returnvector = returnvector1 + returnvector2

    vectorlength = len(returnvector)
    v = np.arange(2, vectorlength + 2, dtype=np.int)
    myclk = 0.5 + 0.5 * scipy.signal.square(1/1*3.1416*v)
    returnvector = returnvector + np.array(globals.EPBIT_DPOT_CLK * myclk,dtype=np.int)
    returnvector = np.flipud(returnvector)
    returnvector = np.concatenate((np.array([globals.EPBIT_DPOT_NCS,0],dtype=int), returnvector, np.array([0, globals.EPBIT_DPOT_NCS],dtype=int)))
    returnvector = returnvector + np.array(globals.EP_ACTIVELOWBITS-globals.EPBIT_DPOT_NCS,dtype=int)
    return returnvector

def SetADCInput(xem, mux):
    import globals as g

    wiremask = g.EPBIT_ADC1MUX0 + g.EPBIT_ADC1MUX1
    wirevalue=0

    if mux == 'VIN1':
        wirevalue = wirevalue + g.EPBIT_ADC1MUX1
    if mux == 'Filtered':
        wirevalue = wirevalue + g.EPBIT_ADC1MUX0
    if mux == 'AUXJ14':
        wirevalue = 3
    if mux == 'Unfiltered':
        wirevalue = 0

    out = xem.SetWireInValue(g.EP_WIREIN_ADCMUX, wirevalue, wiremask)
    xem.UpdateWireIns()

def PlotValues(cutoff):
    import globals as g
    import numpy as np
    from scipy import signal as si
    import math
    readvalues=g.blockvalues
    mygain = g.SETUP_TIAgain * g.SETUP_preADCgain
    bitmask = (2**16 - 1) - (2**(16-g.ADCBITS) - 1)
    readvalues = -g.ADCVREF + (2*g.ADCVREF) * (readvalues & bitmask) / 2**16
    readvalues = 10**9*(readvalues/mygain + g.SETUP_pAoffset)

    g.currentRMSRaw = np.std(readvalues)

    if cutoff==0:
        g.displaybuffer = si.resample(readvalues, int(1/g.displaysubsample*len(readvalues)))
    else:
        downsampled = si.resample(readvalues, 1/g.displaysubsample*len(readvalues))
        effsamplerate=(g.ADCSAMPLERATE/g.displaysubsample)
        Wn = round(2*cutoff/effsamplerate, 4)
        b, a = si.bessel(4, Wn, btype='low', analog=False)
        g.displaybuffer = si.filtfilt(b, a, downsampled)
        g.displaybuffer=g.displaybuffer[100:len(g.displaybuffer)-100]

def EventDetection(input, Threshold, DwellTime, upwardOn):
    import globals as g
    import numpy as np
    from scipy import signal as si
    import math
    mindistance=np.float(Threshold)
    meanvalue=np.mean(input)
    stdeviation=np.std(input)

    limitdown = meanvalue - mindistance * stdeviation
    g.EventLimit=limitdown
    conditiondown = input < limitdown
    indexes=np.arange(len(input))
    downindexes= np.extract(conditiondown, indexes)
    splitted = np.split(downindexes, np.where(np.diff(downindexes) != 1)[0]+1)
    alllengths=np.array([])

    for i in splitted:
        alllengths = np.append(alllengths, len(i))
    cond = alllengths >= DwellTime
    alldown = np.extract(cond, alllengths)
    ndown = len(alldown)
    nup = 0
    if upwardOn:
        limitup = meanvalue + mindistance * stdeviation
        g.EventLimitUP=limitup
        conditionup = input > limitup
        upindexes = np.extract(indexes, input)
        splittedup = np.split(upindexes, np.where(np.diff(upindexes) != 1)[0]+1)
        alllengthsup=np.array([])
        for i in splittedup:
            np.append(alllengthsup, len(i))
        condup = alllengthsup >= DwellTime
        allup = np.extract(condup, alllengthsup)
        nup = len(allup)
    return ndown, nup

def ConvertRaw(data, headers, outputsamplerate, LPfiltercutoff):
    import numpy as np
    from scipy import signal

    samplerate = np.float64(headers['ADCSAMPLERATE'])
    TIAgain = np.int32(headers['SETUP_TIAgain'])
    preADCgain = np.float64(headers['SETUP_preADCgain'])
    currentoffset = np.float64(headers['SETUP_pAoffset'])
    ADCvref = np.float64(headers['SETUP_ADCVREF'])
    ADCbits = np.int32(headers['SETUP_ADCBITS'])
    closedloop_gain = TIAgain*preADCgain


    if samplerate < 4000e3:
        data=data[::round(samplerate/outputsamplerate)]
        print('Samplerate is smaller than 4MHz!!!!')


    bitmask = (2**16 - 1) - (2**(16-ADCbits) - 1)
    data = -ADCvref + (2*ADCvref) * (data & bitmask) / 2**16
    data = 10**9*(data/closedloop_gain + currentoffset)

    Wn = round(LPfiltercutoff/(samplerate/2),4)
    b, a = signal.bessel(4, Wn, btype='low')
    data = signal.filtfilt(b, a, data)
    data *= 10 ** -9

    t = np.arange(0, len(data))
    t = t/samplerate

    out = {'x': t, 'y':data}
    return out

def InitializeChimera(xem):
    from PyQt5 import QtGui  # (the example applies equally well to PySide)
    import pyqtgraph as pg
    import ok
    import sys
    import globals
    import time
    import math
    import datetime
    import numpy as np
    import functions
    import matplotlib.pyplot as plt
    import matplotlib.animation as animation
    from pyqtgraph.Qt import QtGui, QtCore
    import os
    import ui
    #Tests

    #Initialize OK element
    #Configure OK
    ndevices = xem.GetDeviceCount()
    if ndevices==0:
        print('No Device Attached!!')
      #  sys.exit()
    serials = xem.GetDeviceListSerial(0)
    models = xem.GetDeviceListModel(0)
    print('OK Devices detected (Model: {}) . Serial number of device 1 is {Serial} '.format(ndevices,models,Serial=serials))
    bitfilename = 'bitfile_fpga_spartan6_usb3.bit'
    openanswer = xem.OpenBySerial(serials)
    print('Device opened with code {}'.format(openanswer))
    confanswer = xem.ConfigureFPGA(bitfilename)
    print('Device configured with code {}'.format(confanswer))

    notempty=os.stat("store.pckl").st_size
    if(notempty):
        import pickle
        f = open('store.pckl','rb')
        variables = pickle.load(f)
        print('Loaded Variables: {}'.format(variables))
        globals.myvoltageoffset = variables['Voffset']
        globals.SETUP_pAoffset = variables['pAOffset']
        globals.LowerIV = variables['LowerIV']
        globals.HigherIV = variables['HigherIV']
        globals.StepIV = variables['StepIV']
        globals.experimentName = variables['experimentName']
       # globals.timeIV = variables['timeIV']
        f.close

    if not os.path.exists('Data'):
        os.makedirs('Data')
    if not os.path.exists(os.path.join('Data', globals.todaysfolder)):
        os.makedirs(os.path.join('Data', globals.todaysfolder))

    #Wire In Tests
    ans1=xem.SetWireInValue(globals.EP_WIREIN_TEST1, globals.EPBIT_GLOBALRESET, globals.EPBIT_GLOBALRESET)
    xem.UpdateWireIns()
    time.sleep(0.1)
    ans2=xem.SetWireInValue(globals.EP_WIREIN_TEST1, globals.EPBIT_ENABLEADCFIFO, globals.EPBIT_ENABLEADCFIFO)
    xem.UpdateWireIns()
    time.sleep(0.1)
    ans3=xem.SetWireInValue(globals.EP_WIREIN_TEST1, 0, globals.EPBIT_GLOBALRESET)
    xem.UpdateWireIns()
    time.sleep(0.1)
    ans4=xem.SetWireInValue(globals.EP_WIREIN_TEST1, globals.EPBIT_HEADSTAGE_PWR_LED, globals.EPBIT_HEADSTAGE_PWR_LED)
    xem.UpdateWireIns()
    time.sleep(0.1)

    functions.CHIMERA_updateDACvalues1(xem)
    functions.CHIMERA_updateDPOTvalues1(xem)

    #Set Input
    functions.SetADCInput(xem, 'Filtered')
    outtext = functions.CHIMERA_bandwidthtimer(xem)

def MakeIV():
    print('MakeIV Values: {}, {}, {}'.format(LowerIV.value(), HigherIV.value(), StepIV.value()))

def ZeroVolt():
    Vdelta=0.01

    voltageBox.setValue(Vdelta)
    functions.CHIMERA_updateDACvalues1(xem)
    ans1=xem.SetWireInValue(globals.EP_WIREIN_TEST1, globals.EPBIT_GLOBALRESET, globals.EPBIT_GLOBALRESET)
    xem.UpdateWireIns()
    time.sleep(0.1)
    ans2=xem.SetWireInValue(globals.EP_WIREIN_TEST1, 0, globals.EPBIT_GLOBALRESET)
    xem.UpdateWireIns()
    time.sleep(0.1)
    time.sleep(1)
    update()
    measI1 = globals.currentIDC

    voltageBox.setValue(0)
    functions.CHIMERA_updateDACvalues1(xem)
    ans1=xem.SetWireInValue(globals.EP_WIREIN_TEST1, globals.EPBIT_GLOBALRESET, globals.EPBIT_GLOBALRESET)
    xem.UpdateWireIns()
    time.sleep(0.1)
    ans2=xem.SetWireInValue(globals.EP_WIREIN_TEST1, 0, globals.EPBIT_GLOBALRESET)
    xem.UpdateWireIns()
    time.sleep(0.1)
    time.sleep(1)
    update()
    measI2 = globals.currentIDC
    deltaI = measI1-measI2
    measR = Vdelta/deltaI

    ans1=xem.SetWireInValue(globals.EP_WIREIN_TEST1, globals.EPBIT_GLOBALRESET, globals.EPBIT_GLOBALRESET)
    xem.UpdateWireIns()
    time.sleep(0.1)
    ans2=xem.SetWireInValue(globals.EP_WIREIN_TEST1, 0, globals.EPBIT_GLOBALRESET)
    xem.UpdateWireIns()
    time.sleep(0.1)

    globals.myvoltageoffset = globals.myvoltageoffset +(-measI2*measR)
    functions.CHIMERA_updateDACvalues1(xem)
    update()
    Voffset.setValue(globals.myvoltageoffset)

def recursive_low_pass(RawSignal,StartCoeff,EndCoeff,FilterCoeff):
    import numpy as np
    Ni = len(RawSignal)
    RoughEventLocations = np.zeros((1E5, 3))
    a = FilterCoeff
    S = StartCoeff
    E = EndCoeff
    ml = np.zeros((Ni))
    vl = np.zeros((Ni))
    s = np.zeros((Ni))
    ml[0] = np.mean(RawSignal)
    vl[0] = np.var(RawSignal)
    i = 0
    NumberOfEvents=0
    while i < (Ni-2):
        i+=1
        ml[i] = a*ml[i-1]+(1-a)*RawSignal[i]
        vl[i] = a*vl[i-1]+(1-a)*(RawSignal[i]-ml[i])**2
        Sl = ml[i]-S*np.sqrt(vl[i])
        if RawSignal[i+1] <= Sl:
            NumberOfEvents=NumberOfEvents+1
            start=i+1
            El=ml[i]-E*np.sqrt(vl[i])
            Mm=ml[i]
            Vv=vl[i]
            while (RawSignal[i+1] < El) and (i < (Ni-1)):
                i+=1
            RoughEventLocations[NumberOfEvents-1, 2] = i+1-start
            RoughEventLocations[NumberOfEvents-1, 0] = start
            RoughEventLocations[NumberOfEvents-1, 1] = i+1
            ml[i] = Mm
            vl[i] = Vv
    RoughEventLocations = RoughEventLocations[0:NumberOfEvents, :]
    return RoughEventLocations


def MakeAllVoltagesForIV(stepV, maxV):
    import numpy as np
    NumberOfElements=(2*maxV)/stepV+2
    AllVoltages=np.zeros(NumberOfElements)
    Counter=1
    for i in range(1, int(NumberOfElements)-1):
        if divmod(i, 2)[1]:
            AllVoltages[i]=-stepV*Counter
        else:
            AllVoltages[i]=stepV*Counter
            Counter+=1

    print('Applied Voltages: {}'.format(AllVoltages))
    return AllVoltages