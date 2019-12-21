from unidriver import *
import visa
from numpy import *
import time
import os

#Files
DataDir = "D:/PMJTWPA"
FilePrefix = ""
FileComment = ""

#PNA settings
PnaName = "ZVB20"
Measurement  = 1 	#Number of active measurement. If Preset is False only
Timeout = 200		#Interface timeout
Preset = False		#Do preset if True use current settings otherwise
Fstart = 10e6
Fstop = 20e9
Npoints = 1501
Power = -20
BW = 100.

#Pump source
GenName = "PSG"
Fp_list = arange(5.,5.4,0.002)*1e9
Pp_list = arange(-7.,0,0.05)

#Measurement delay
Delay = 0.
################################################
# PNA configuration 
pna = visa.instrument(PnaName)
gen = visa.instrument(GenName)

if Preset:
	#PnaConfS21(pna)
	pna.write("SOUR:POW "+format(Power))
	pna.write("SENS1:BAND "+format(BW))
	pna.write("SENS1:FREQ:START {:e}".format(Fstart) ) 
	pna.write("SENS1:FREQ:STOP {:e}".format(Fstop) )
	pna.write("SENS1:SWE:POIN {:d}".format(Npoints) )

#pna.write("TRIG:SOUR MAN") #Agilent
pna.write("INIT:CONT OFF")	#R&S
PnaSelMeas(pna,Measurement)

Npoints = int( pna.ask("SENS1:SWE:POIN?") )
Fstart=float( pna.ask("SENS1:FREQ:START?") )
Fstop=float( pna.ask("SENS1:FREQ:STOP?") )
Fstep = (Fstop-Fstart)/(float(Npoints)-1)
Power = float( pna.ask("SOUR:POW?") )
BW = float( pna.ask("SENS1:BAND?") )

if not os.path.isdir(DataDir):
	os.mkdir( DataDir )
time_str = time.localtime()	
DataDir +='/{:d}_{:d}_{:d}'.format(time_str.tm_mday, time_str.tm_mon, time_str.tm_year)
if not os.path.isdir(DataDir):
	os.mkdir( DataDir )
DataDir += "/gain_map_{:d}_{:d}_{:d}/".format(time_str.tm_hour, time_str.tm_min, time_str.tm_sec)	
if not os.path.isdir(DataDir):
	os.mkdir( DataDir )

Header = '''#{:s}
#Signal power = {:.3f} dBm
#Frequency start={:.10e} Hz 
#Frequency stop={:.10e} Hz
#Bandwidth={:g} Hz
'''.format(FileComment, Power, Fstart, Fstop, BW )	

f_points = linspace(Fstart,Fstop,Npoints)
f_str = '0\t0\t'+'\t'.join([str(x) for x in f_points])
	
File = open(DataDir+'S.dat','w+')
File.write(Header)
File.write(f_str+"\n")

gen.ask("OUTP ON;*OPC?")		
#Main loop
try:
	for Fp in Fp_list:
		for Pp in Pp_list:
			#Set power
			gen.ask("POW {:f}".format(Pp)+";" +"FREQ {:e}".format(Fp) + ";*OPC?")
			print "P={:.3f} dbm  F={:.9e} Hz \r".format(Pp, Fp),
			
			#Run PNA measurement
			pna.timeout = Timeout
			pna.ask("INIT:IMM;*OPC?")
			pna.timeout = 20
			data = PnaGetSData(pna)
			
			data_str = "{:e}\t{:f}\t".format(Fp, Pp) + '\t'.join([str(x) for x in data])
			File.write(data_str + "\n")
			File.flush()
	
except KeyboardInterrupt:
	print "Interrupted by user      "
finally:
	pna.close()
	gen.write("OUTP OFF")
	gen.close()