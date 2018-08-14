
def init():
    import datetime
    import numpy as np
    #Make sure this corresponds to your chimera calibration
    global freqComp
    freqComp = 19
    global SETUP_pAoffset
    SETUP_pAoffset = 1365e-12
    global SETUP_TIAgain
    SETUP_TIAgain = 100e6
    global SETUP_preADCgain
    SETUP_preADCgain = 1.235
    #
    global DataFolder
    DataFolder = ''
    global k
    k = 1.3806503e-23
    global T
    T=298
    global IVOn
    IVOn=0
    global currentIDC
    currentIDC=0
    global currentRMS
    currentRMS=0
    global newbiasvalue
    newbiasvalue=0
    global myCfast
    myCfast=11E-12
    global myvoltageoffset
    myvoltageoffset=-274E-3
    global IVUseAlternatingV
    IVUseAlternatingV=1
    global AllVoltages
    AllVoltages=0
    global IVExecuteCounter
    IVExecuteCounter = 0
    global IVCurrentV
    IVCurrentV=0.0
    global LowerIV
    LowerIV = 0.0
    global HigherIV
    HigherIV = 0.0
    global StepIV
    StepIV = 0.0
    global timeIV
    timeIV=2
    global todaysfolder
    todaysfolder = str(datetime.date.today())
    global experimentName
    experimentName = 'Untitled'
    global Threshold
    Threshold = 8
    global EventLimit
    EventLimit = 0
    global currentRMSRaw
    currentRMSRaw = 0
    global fisopen
    fisopen = 0
    global file
    file = 0
    global writtenBlocks
    writtenBlocks=0
    global blockvalues
    blockvalues=np.empty((1048576,), dtype=np.uint16)
    global StockTime
    StockTime=4
    global StockData
    StockData=np.empty((0,), dtype=np.uint16)
    global RestartBuffer
    RestartBuffer=0
    global ZapVoltage
    ZapVoltage = -0.3
    global ZapTime
    ZapTime = 0.5
    global ZapFrequency
    ZapFrequency = 2
    global VoltageBeforeZap
    global ZapOnce
    ZapOnce = 0
    VoltageBeforeZap = 0.0
    global ZappingInputChoice
    ZappingInputChoice=0

    global BITMASK_ALL
    BITMASK_ALL=int("ffff",16)
    global BITMASK_0
    BITMASK_0=int("0001",16)
    global BITMASK_1
    BITMASK_1=int("0002",16)
    global BITMASK_2
    BITMASK_2=int("0004",16)
    global BITMASK_3
    BITMASK_3=int("0008",16)
    global BITMASK_4
    BITMASK_4=int("0010",16)
    global BITMASK_5
    BITMASK_5=int("0020",16)
    global BITMASK_6
    BITMASK_6=int("0040",16)
    global BITMASK_7
    BITMASK_7=int("0080",16)
    global BITMASK_8
    BITMASK_8=int("0100",16)
    global BITMASK_9
    BITMASK_9=int("0200",16)
    global BITMASK_10
    BITMASK_10=int("0400",16)
    global BITMASK_11
    BITMASK_11=int("0800",16)
    global BITMASK_12
    BITMASK_12=int("1000",16)
    global BITMASK_13
    BITMASK_13=int("2000",16)
    global BITMASK_14
    BITMASK_14=int("4000",16)
    global BITMASK_15
    BITMASK_15=int("8000",16)
    global SAVECONFIGFILE
    SAVECONFIGFILE = "startupconfig.mat"
    global EVENTLOGFILE
    EVENTLOGFILE = "EVENT_LOG.txt"
    global LOGFILE_DIR
    LOGFILE_DIR = "logfiles"
    global FPGAMODEL
    FPGAMODEL = "spartan6_usb3"

    #CLK1FREQDEFAULT = 100e6;
    #CLK2FREQDEFAULT = 4e6;
    global ADCSAMPLERATE
    ADCSAMPLERATE = 100e6 / 24
    global HWBUFFERSIZE_KB
    HWBUFFERSIZE_KB = 128*1024
    global ADCMUXDEFAULT
    ADCMUXDEFAULT = 2
    global RAWDATAFORMAT
    RAWDATAFORMAT = 'uint32'

    global MAXLOGBYTES
    MAXLOGBYTES = 20e6
    global CFAST_gain
    CFAST_gain = 2
    global CFAST_CAP0
    CFAST_CAP0 = 1e-12
    global CFAST_CAP1
    CFAST_CAP1 = 10e-12
    global ADC_xfer_len
    ADC_xfer_len = 4*1024*1024
    global ADC_pkt_len
    ADC_pkt_len = ADC_xfer_len
    global ADC_xfer_blocksize
    ADC_xfer_blocksize = 512
    global ADCcaptureenable
    ADCcaptureenable = 1
    global ADCnumsignals
    ADCnumsignals=1
    global ADCBITS
    ADCBITS = 14        #this may get overwritten by startupconfig.mat
    global ADCVREF
    ADCVREF = 2.5       #this may get overwritten by startupconfig.mat
    global ADClogenable
    ADClogenable = 0
    global ADClogsize
    ADClogsize = 0
    global ADClogreset
    ADClogreset = 0
    global logfid
    logfid = -1
    global DACBITS
    DACBITS = 16
    global DACFULLSCALE
    DACFULLSCALE = 4.5
    global DACcurrent
    DACcurrent = 0
    global DACprevious
    DACprevious = 0
    global ADC_xfer_time
    ADC_xfer_time = ADC_xfer_len / ADCSAMPLERATE

    global EP_TRIGGERIN_TEST1
    EP_TRIGGERIN_TEST1 = int('40',16)
    global EP_TRIGGEROUT_TEST1
    EP_TRIGGEROUT_TEST1 = int('60',16)
    global EP_WIREIN_TEST1
    EP_WIREIN_TEST1 = int('00',16)
    global EP_WIREIN_ADCMUX
    EP_WIREIN_ADCMUX = int('01',16)
    global EP_WIREOUT_TEST1
    EP_WIREOUT_TEST1 = int('20',16)
    global EP_WIREOUT_ADCFIFOCOUNT
    EP_WIREOUT_ADCFIFOCOUNT = int('21', 16)
    global EP_PIPEIN_SCANCHAINS
    EP_PIPEIN_SCANCHAINS = int('80', 16)
    global EP_PIPEOUT_ADC
    EP_PIPEOUT_ADC = int('A0',16)
    global EPBIT_ENABLEADCFIFO
    EPBIT_ENABLEADCFIFO = BITMASK_4
    global EPBIT_GLOBALRESET
    EPBIT_GLOBALRESET = BITMASK_15
    global EPBIT_DACSDI
    EPBIT_DACSDI  = BITMASK_0
    global  EPBIT_DACCLK
    EPBIT_DACCLK = BITMASK_1
    global EPBIT_DACNCS
    EPBIT_DACNCS  = BITMASK_2
    global EPBIT_DACSDI_FASTC
    EPBIT_DACSDI_FASTC = BITMASK_8
    global EPBIT_DAC_NLOAD
    EPBIT_DAC_NLOAD = BITMASK_10
    global EPBIT_DPOT_CLK
    EPBIT_DPOT_CLK = BITMASK_4
    global EPBIT_DPOT_SDI
    EPBIT_DPOT_SDI = BITMASK_5
    global EPBIT_DPOT_NCS
    EPBIT_DPOT_NCS = BITMASK_6
    global EPBIT_FASTC_CAPMUX
    EPBIT_FASTC_CAPMUX = BITMASK_9
    global EPBIT_DAQTRIGGER
    EPBIT_DAQTRIGGER = BITMASK_15
    global EPBIT_ADCDATAREADY
    EPBIT_ADCDATAREADY = BITMASK_0
    global EPBIT_ADC1MUX0
    EPBIT_ADC1MUX0 = BITMASK_0
    global EPBIT_ADC1MUX1
    EPBIT_ADC1MUX1 = BITMASK_1
    global EPBIT_HEADSTAGE_PWR_EN
    EPBIT_HEADSTAGE_PWR_EN = BITMASK_0
    global EPBIT_HEADSTAGE_PWR_LED
    EPBIT_HEADSTAGE_PWR_LED = BITMASK_1
    global EP_ACTIVELOWBITS
    EP_ACTIVELOWBITS = EPBIT_DACNCS + EPBIT_DAC_NLOAD + EPBIT_DPOT_NCS
    global DAC_SCANCHAIN_LENGTH
    DAC_SCANCHAIN_LENGTH = 16
    global DAC_MSB
    DAC_MSB = 16
    global DAC_LSB
    DAC_LSB = 1
    global DPOT_SCANCHAIN_LENGTH
    DPOT_SCANCHAIN_LENGTH = 9
    global DPOT_A
    DPOT_A = 9
    global DPOT_MSB
    DPOT_MSB = 8
    global DPOT_LSB
    DPOT_LSB = 1

    global read_monitor
    read_monitor = 0
    global write_monitor
    write_monitor = 0

    global timezero
    timezero = datetime.datetime.today()

    global displaybuffertime
    displaybuffertime = np.floor(ADC_xfer_time * 10)/50
    global displaycount
    displaycount = 1
    global displayupdaterate
    displayupdaterate = 2
    global displaysubsample
    displaysubsample = 16
    global displaybuffersize
    displaybuffersize = int(np.ceil(ADCnumsignals*ADCSAMPLERATE*displaybuffertime/displaysubsample))
    global displaybuffer
    displaybuffer = np.zeros(displaybuffersize, dtype=np.float)
    global flag
    flag = 0
    global ChimeraIsOn
    ChimeraIsOn = 1