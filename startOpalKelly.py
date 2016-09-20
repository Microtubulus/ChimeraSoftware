# Script to read configuration file
# Write output file
# Plot output as function of time
# Manages basic I/O for digitalDemodTest module

import ok
xem = ok.FrontPanel()
xem.OpenBySerial("")
xem.LoadDefaultPLLConfiguration()

xem.ResetFPGA()

xem.ConfigureFPGA("First.bit")

def setAndGetWireValues(samples):
	import math
	import random
	import numpy as np
	outfile=open('/home/nick/digitalDemodTest2/output2.txt','w')
	timeVec=np.linspace(0,1,samples)
	xem.SetWireInValue(0, 5)
	xem.SetWireInValue(3, 0x1999) # 0x1999 = 6553.6 (100 MHz in --> 10 MHz out), 0x5555=21845
	for i in range(samples):
		in1=math.floor(math.cos(2*math.pi*10*timeVec[i])*32768)
		input1=in1 if in1>0 else in1*-1
		input1=int(input1)
		xem.SetWireInValue(4,input1)
		xem.UpdateWireIns()
		xem.UpdateWireOuts()
		a=xem.GetWireOutValue(34)
		b=xem.GetWireOutValue(35)
		c=xem.GetWireOutValue(36)
		d=xem.GetWireOutValue(37)
		print 'Input: ', input1, '\tOutput: ', hex(a + (b>>16)),' ', hex(c + (d>>16))
		outfile.write(str(math.floor(timeVec[i]*32768))+'\t'+str(a + (b>>16))+'\t'+str(c + (d>>16))+'\t'+str(input1)+'\n')
setAndGetWireValues(100)


def justPlot(samples,freq):
	import matplotlib.pyplot as plt
	import matplotlib.mlab as mylab	
	import math
	import numpy as np
	timepts=np.linspace(0,1,samples)
	inputData=[0]*samples
	for i in range(samples):
		inputData[i]=np.uint32(math.cos(2*math.pi*freq*timepts[i])*pow(2,32))
		print 'cos(2*pi*',freq,'*',i,'): ',inputData[i]
	plt.figure(1)
	plt.title('Test input signal: '+'cos(2*pi*'+str(freq)+'*t)')
	plt.plot(timepts,inputData,'g-')
	plt.show()
justPlot(128,10e06)


 
def readAndPlot(samples,goFilter):
	import matplotlib.pyplot as plt
	import matplotlib.mlab as mylab
	import math
	import numpy as np
	timeVec2=[0]*samples
	realOut=[0]*samples
	imagOut=[0]*samples
	input1=[0]*samples
	totalSignal=[0]*samples
	outputData=mylab.csv2rec('outputRAMtestdemod'+str(samples)+'.txt',delimiter='\t')
	myFilter=[-0.000003, 0.000007, -0.000013, 0.000021, -0.000031, 0.000042, -0.000055, 0.000070,
	 -0.000085, 0.000100, -0.000114, 0.000127, -0.000138, 0.000146, -0.000151, 1.000153, 
	 -0.000151, 0.000146, -0.000138, 0.000127, -0.000114, 0.000100, -0.000085, 0.000070, 
	 -0.000055, 0.000042, -0.000031, 0.000021, -0.000013, 0.000007, -0.000003] 
	if goFilter==1:
		print 'filtering...'
		samples=31
		for i in range(samples-1):
			timeVec2[i]=outputData[i][0]
			input1[i]=outputData[i][1]
			realOut[i]=outputData[i][2]+outputData[i][2]*myFilter[i]
			imagOut[i]=outputData[i][3]+outputData[i][3]*myFilter[i]
	else:
		print 'no filtering...'
		for i in range(samples-1):
			timeVec2[i]=outputData[i][0]
			input1[i]=outputData[i][1]
			realOut[i]=outputData[i][2]
			imagOut[i]=outputData[i][3]
	totalSignal=np.vectorize(complex)(realOut,imagOut)
	plt.figure(1)
	plt.subplot(311)
	plt.title('Real Input and Output Signals')
	plt.plot(timeVec2,np.real(input1),'r-',timeVec2,realOut,'b-')
	plt.subplot(312)
	plt.title('Imag Input and Output Signals')
	plt.plot(timeVec2,np.imag(input1),'r-',timeVec2,imagOut,'b-')
	plt.subplot(313)
	plt.title('Total Signal')
	plt.plot(timeVec2,input1,'r-',timeVec2,totalSignal,'b-')
	plt.xlabel('time')
	plt.ylabel('signal')
	plt.show()
	xem.SetWireInValue(0xE,1)
	xem.UpdateWireIns()
	xem.UpdateWireOuts()
readAndPlot(2048,0)

def initializeBlockRamCOEFile(samples):
	import math
	import random
	import numpy as np
	outfile=open('/home/nick/blockRAMtest/blockRAM_contents.coe','w')
	timeVec=np.linspace(0,1,samples)
	inputData=[0]*samples
	outfile.write('memory_initialization_radix=10;\nmemory_initialization_vector=')
	print 'Writing blockRAM initialization file...'
	for i in range(samples-1):
		inputData[i]=np.uint16(math.cos(2*math.pi*10*timeVec[i])*32768)
		outfile.write(str(inputData[i])+',')
		if i==(samples-2):
			outfile.write(str(inputData[i])+';')
	print 'blockRAM initialization file written with ',samples, 'samples.' 
initializeBlockRamCOEFile(1000)


def WireInWireOutBlockRAM(samples):
	import math
	import random
	import numpy as np
	import time
	clk_period=10e-9
	timepts=[0]*samples
	timepts=np.linspace(0,1,samples)
	inputData=[0xffff,0xc000,0x8000,0x4000,0x0000,0x4000,0x8000,0xc000,
									  0xffff,0xc000,0x8000,0x4000,0x0000,0x4000,0x8000,0xc000,
									  0xffff,0xc000,0x8000,0x4000,0x0000,0x4000,0x8000,0xc000,
									  0xffff,0xc000,0x8000,0x4000,0x0000,0x4000,0x8000,0xc000,0xffff]
	outfile=open('/home/nick/digitalDemodTest2/outputRAM.txt','w')
	writeEnable=0x0000
	# reset counters:
	xem.SetWireInValue(4,0x0001)
	xem.UpdateWireIns()
	xem.UpdateWireOuts()
	time.sleep(4*clk_period)
	print 'Delaying for 4 clock cycles...'
	xem.SetWireInValue(4,0x0000)
	xem.SetWireInValue(0,2)
	xem.SetWireInValue(3,0x1999)
	xem.UpdateWireIns()
	xem.UpdateWireOuts()
	# enable writing:
	writeEnable=0x0001
	xem.SetWireInValue(5,writeEnable)
	xem.UpdateWireIns()
	xem.UpdateWireOuts()
	time.sleep(4.0e-3)
	print 'Delaying for 4 ms...'
	writeEnable=0x0000
	xem.SetWireInValue(5,writeEnable)
	xem.UpdateWireIns()
	xem.UpdateWireOuts()
	for i in range(samples):
		inputData[i]=np.uint16(math.cos(2*math.pi*10*timepts[i])*32768)
		xem.UpdateWireOuts()
		outputReMSB=xem.GetWireOutValue(34)
		outputReLSB=xem.GetWireOutValue(35)
		outputImMSB=xem.GetWireOutValue(36)
		outputImLSB=xem.GetWireOutValue(37)
		print 'Output: ', hex(outputReMSB + (outputReLSB>>16)),' ', hex(outputImMSB + (outputImLSB>>16))
		outfile.write(str(math.floor(timepts[i]*32768))+'\t'+str(inputData[i])+'\t'+str(outputReMSB + (outputReLSB>>16))+'\t'+str(outputImMSB + (outputImLSB>>16))+'\n')
	print '\nblockRAM written to file.'
WireInWireOutBlockRAM(1000)


# read and write from test block RAM:
# Current Functional blockRAM read-write:
# 7/26/13
xem.ConfigureFPGA("../dualPortblockRAM/dualPortblockRAM_top.bit")
def concurrentReadAndWriteBlockRAM(samples):
	import math
	import random
	import time
	import numpy as np
	outfile=open('/home/nick/digitalDemodTest2/outputRAMtest.txt','w')
	timepts=np.linspace(0,1,samples)
	dataInA=[0]*samples
	addrA=range(samples)
	addrB=range(samples)
	dataOutB=[0]*samples
	sumAddresses=[0]*samples
	# reset blockRAM:
	reset=0x1
	xem.SetWireInValue(7,reset)
	xem.UpdateWireIns()
	xem.UpdateWireOuts()
	print '\n\nOutput reset sanity check: ', xem.GetWireOutValue(0x20),'\n'
	time.sleep(1)
	reset=0x0
	xem.SetWireInValue(7,reset)
	xem.UpdateWireIns()
	xem.UpdateWireOuts()
	print 'i', '\t', 'addrB[i]', '\t', 'dataOutB[i]', '\t', 'dataOutB[i] & 0x07ff\n'
	# write to channel A:
	for i in range(samples):
		dataInA[i]=np.uint16(math.cos(2*math.pi*10*timepts[i])*32768)
		enableA=0x1
		writeEnableA=0x1
		enableB=0x0
		xem.SetWireInValue(0x02,enableA)
		xem.SetWireInValue(0x03,writeEnableA)
		xem.SetWireInValue(0x05,enableB)
		xem.SetWireInValue(0x00,int(dataInA[i]))
		xem.SetWireInValue(0x01,addrA[i])
		xem.UpdateWireIns()
		enableA=0x0
		writeEnableA=0x0
		xem.SetWireInValue(0x02,enableA)
		xem.SetWireInValue(0x03,writeEnableA)
		xem.UpdateWireIns()
	# read from channel B:
	for i in range(samples):
		enableB=0x1
		xem.SetWireInValue(0x05,enableB)
		xem.UpdateWireIns()
		xem.SetWireInValue(0x04,addrB[i])
		xem.UpdateWireIns()
		xem.UpdateWireOuts()
		dataOutB[i]=xem.GetWireOutValue(0x20) 
		print i, '\t', addrB[i], '\t', dataInA[i],'\t',dataOutB[i]
		outfile.write(str(addrB[i])+'\t'+str(dataOutB[i])+'\n')
	print '\nReset LEDs to 1010101_2=85.'
	xem.SetWireInValue(6,85)
	xem.UpdateWireIns()
concurrentReadAndWriteBlockRAM(100)


# ============================================================================= #
# dualPortblockRAMdemod wireIns, wireOuts:
# configuration for dual-port blockRAM and demod:
xem.ConfigureFPGA("../dualPortblockRAMdemod_top/dualPortblockRAMdemod_top.bit")
def readWriteWiresblockRAMdemod(samples,frequency):
	import math
	import random
	import time
	import numpy as np
	import csv
	bitoffset=pow(2,32) # (2^16 = 65536, 2^32=4294967296)
	# with open('/home/nick/dualPortblockRAMdemod_top/inputData'+str(samples)+'.txt','rb') as csvfile:
	# 	dataInA=csv.reader(csvfile,delimiter=',')
	# for i in range(samples):
	# 	print dataInA.next()
	outfile=open('/home/nick/digitalDemodTest2/outputRAMtestdemod'+str(samples)+'.txt','w')
	dataInA=[0,35556,38582,732,22172,17749,62624,50203,57388,6491,9615,63903,54148,60389,11380,17495,2027,44664,40861,65210,29898,32769,82,27280,23942,64236,45759,50953,3953,13296,4897,57555,57555,4897,13296,3953,50953,45759,64236,23942,27280,82,32768,29898,65210,40861,44664,2027,17495,11380,60389,54148,63903,9615,6491,57388,50203,62624,17749,22172,732,38582,35556,0]            
	# dataInA=[0]*samples
	#dataInA=range(samples)
	timepts=np.linspace(0,1,samples)
	dataOutDemodReTop=[0]*samples
	dataOutDemodReBottom=[0]*samples
	dataOutDemodImTop=[0]*samples
	dataOutDemodImBottom=[0]*samples
	dataOutRe=[0]*samples
	dataOutIm=[0]*samples
	# reset all blockRAM and demodulator:
	print '\n\n======================================================='
	print'Arrays initialized, starting to reset FPGA','\n=======================================================\n'
	wireInBits=0x0003
	xem.SetWireInValue(0x01,wireInBits)
	xem.UpdateWireIns()
	xem.UpdateWireOuts()
	print '\nWait 900 ms...\n'
	time.sleep(0.9)
	wireInBits=0x0000
	xem.SetWireInValue(0x01,wireInBits)
	xem.UpdateWireIns()
	# print 'Check WireOuts: (',xem.GetWireOutValue(0x20),',',xem.GetWireOutValue(0x21),',',xem.GetWireOutValue(0x22),',',xem.GetWireOutValue(0x23),')'
	print 'wireInBits updated, reset pulsed.'
	# set phase increment:
	phaseInc=int(np.uint16(math.floor((pow(2,16)*10)/100)))
	print 'phaseInc set to ',phaseInc
	# write to channel A of input blockRAM:
	print 'writing to input blockRAM...'
	for i in range(samples):
		#dataInA[i]=np.uint32(math.cos(2*math.pi*frequency*timepts[i])*bitoffset)
		xem.SetWireInValue(0x03,int(np.uint16(i)))
		xem.SetWireInValue(0x00,int(np.uint16(dataInA[i])))
		xem.UpdateWireIns()
		xem.ActivateTriggerIn(0x40,0)
	print 'writing demod data...'
	wireInBits=0x0030
	xem.SetWireInValue(0x02,phaseInc)
	xem.SetWireInValue(0x01,wireInBits)
	xem.UpdateWireIns()
	# print 'Check WireOuts again: (',xem.GetWireOutValue(0x20),',',xem.GetWireOutValue(0x21),',',xem.GetWireOutValue(0x22),',',xem.GetWireOutValue(0x23),')'
	# read from channel b of output blockRAM: 
	print '\nreading final data...\n\n'		
	print '\ni \t dataInA \t\t outputRe \t outputIm\n'
	print '--------------------------------------------------------------------------'
	for i in range(samples):
		wireInBits=0x0020
		xem.SetWireInValue(0x01,wireInBits)
		xem.SetWireInValue(0x04,int(np.uint16(i)))
		xem.UpdateWireIns()
		xem.UpdateWireOuts()
		dataOutDemodReTop[i]=xem.GetWireOutValue(0x20)
		dataOutDemodReBottom[i]=xem.GetWireOutValue(0x21)
		dataOutDemodImTop[i]=xem.GetWireOutValue(0x22)
		dataOutDemodImBottom[i]=xem.GetWireOutValue(0x23)
		dataOutRe[i]=((dataOutDemodReTop[i]<<16)+(dataOutDemodReBottom[i]))
		dataOutIm[i]=((dataOutDemodImTop[i]<<16)+(dataOutDemodImBottom[i]))
		print int(i), '\t', dataInA[i],'\t',float(dataInA[i])/pow(2.0,16.0), '\t\t\t', dataOutDemodReTop[i], '\t', dataOutDemodReBottom[i], '\t', dataOutDemodImTop[i], '\t', dataOutDemodImBottom[i]
		outfile.write(str(i)+'\t'+str(int(dataInA[i])*pow(2,16))+'\t'+str(dataOutRe[i])+'\t'+str(dataOutIm[i])+'\n')
		# outfile: [  time | inputSignal | real | imag  ]
	wireInBits=0x0000
	xem.SetWireInValue(0x01,wireInBits)
	xem.UpdateWireIns()
	print '\nwireInBits reset to zero.\n\nDemodulation finished.\n'
	print '\nReset LEDs to 10101010_2=170_10=0x00aa_16.'
	xem.SetWireInValue(0x0E,0x00aa)
	xem.UpdateWireIns()
readWriteWiresblockRAMdemod(32,10)


# xem.ResetFPGA()

# non-functional iSim wave-converter:
# intended to extract output from iSim
# to plot simulated signals
def readAndPlotISimWave():
	import matplotlib.pyplot as plt
	import matplotlib.mlab as mylab
	import numpy as np
	file1=open('/home/nick/digitalDemodTest2/FIRST_TEST_isim_beh1.wdb','rb')
	outputData=np.fromfile(file=file1, dtype=np.dtype((str,15)))
	dataLength=len(outputData)
	timeVec=[0]*dataLength
	realOut=[0]*dataLength
	imagOut=[0]*dataLength
	for i in range(dataLength-1):
		time[i]=i
		real[i]=outputData[i]
		imag[i]=outputData[i]
		print i, real[i]
	plt.figure(1)
	plt.subplot(211)
	plt.plot(time,real,'r.')
	plt.subplot(212)
	plt.plot(time,imag,'b.')
	plt.show()
readAndPlotISimWave()

xem.ResetFPGA()

def makeCosWave(samples):
	import math
	import numpy as np
	cosData=[0]*samples
	timepts=np.linspace(0,1,samples)
	mypyfile=open('/home/nick/dualPortblockRAMdemod_top/inputData'+str(samples)+'.txt','wb')
	myfile=open('/home/nick/dualPortblockRAMdemod_top/cosData'+str(samples)+'.txt','w')
	myfile.write('signal mycosine : vector_array:= (')
	for i in range(samples):
		if(i==(samples-1)):
			myfile.write(str(hex(cosData[i]))+');')
			mypyfile.write(str(cosData[i]))
			print hex(cosData[i])
		else:
			cosData[i]=np.uint16(math.cos(2*math.pi*timepts[i])*pow(2,16))
			print hex(cosData[i]),','
			myfile.write(str(hex(cosData[i]))+',')
			mypyfile.write(str(cosData[i])+',')
makeCosWave(256)



def diffHardwareAndSim(samples):
	import math 
	import matplotlib.pyplot as plt
	import matplotlib.mlab as mylab
	import numpy as np
	hardwareFile=mylab.csv2rec('/home/nick/digitalDemodTest2/outputRAMtestdemod.txt',delimiter='\t')
	newFile=open('/home/nick/dualPortblockRAMdemod_top/hardwareOutput'+str(samples)+'.txt','w')
	realOut=[0]*samples
	imagOut=[0]*samples
	for i in range(samples-1):
		realOut[i]=hardwareFile[i][2]
		imagOut[i]=hardwareFile[i][3]
		newFile.write(str('{0:032b}'.format(realOut[i]))+'\t'+str('{0:032b}'.format(imagOut[i]))+'\n')
diffHardwareAndSim(256)



