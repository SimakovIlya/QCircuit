from qsweepy import *
from qsweepy.instruments import *

from numpy import *
import sys
import time
from matplotlib.pyplot import *
import visa
import pickle

Noise = True

#Data mamagement
Data_dir ="C:/Data/Abramov" 
path = save_pkl.default_measurement_save_path(root = Data_dir, mkdir=True)
print("Saving files to: ",path)

#Sources
#(name,(sw position,cnah), Tsensor, attenuation)
Sources = ( ("cold",(5,1),'T5', 0.), ("hot",(1,1),'T3', 0.), ("signal",(2,1),'T5', 0.), ("signal_tst",(4,1),'T5', 0.) )
Delay =70 #sec Cryostat measures temperature too slow, wait for him
MeasDelay =1

#Temperatures
T_sensor = "T5"
T_meas = 0.030 #K

#Instruments
CryoName = "DR200"
na = Agilent_N5242A('pna', address = 'TCPIP0::10.20.61.48::inst0::INSTR')
sa = Agilent_N9030A('sa', address='TCPIP0::10.20.61.56::inst0::INSTR')
pump = Agilent_E8257D('lo1', address = 'TCPIP0::10.20.61.59::inst0::INSTR')
sw = nn_rf_switch(name='rf_switch', address='10.20.61.224')

##+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
sa.set_detector('rms')
rm = visa.ResourceManager()
Cryo=rm.open_resource(CryoName)
Cryo.read_termination="\n"
Cryo.write_termination="\n"
Cryo.timeout = 5000

def TritonGetTemp(Sensor):
	buff=Cryo.query("READ:DEV:"+Sensor+":TEMP:SIG:TEMP")
	strings=buff.split(":")
	Tstring=strings[len(strings)-1]
	Tstring=Tstring[:len(Tstring)-1]
	return float(Tstring)

def stupid_waiting(t):
	for i in range(int(t),0,-1):
		time.sleep(1)
		print("Delay... {:d}   ".format(i),end = "\r")

def wait_for_Tmeas():
	T = TritonGetTemp(T_sensor)
	while(T>T_meas):
		time.sleep(1)
		T = TritonGetTemp(T_sensor)
		print("Waiting for temperature... {:.3f} K".format(T),end = "\r")
	print()
	
def gain():
	pump.set_status(1)
	wait_for_Tmeas()
	print("Gain...")
	Fna = na.get_freqpoints()
	pump.set_status(0)
	
	na.set_status(1)
	na.set_trigger_source('MAN')
	S21_off = na.get_tracedata(format = "REALIMAG")
	S21_off = S21_off[0]+1.j*S21_off[1]
	
	pump.set_status(1)
	S21_on = na.get_tracedata(format = "REALIMAG")
	S21_on = S21_on[0]+1.j*S21_on[1]
	print("Done!")
	na.set_trigger_source('IMM')
	return Fna, S21_on, S21_off
		
	
try:
	Fna, S21_on, S21_off = gain()
	figure("S21")
	clf()
	plot(Fna, 20.*log10(abs(S21_off)),label = "off")
	plot(Fna, 20.*log10(abs(S21_on)), label = "on")
	legend()
	savefig(path+"/S21.png")
	'''
	pump.set_status(1)
	wait_for_Tmeas()
	print("Gain...")
	Fna = na.get_freqpoints()
	pump.set_status(0)
	
	na.set_status(1)
	na.set_trigger_source('MAN')
	S21_off = na.get_tracedata(format = "REALIMAG")
	S21_off = S21_off[0]+1.j*S21_off[1]
	
	pump.set_status(1)
	S21_on = na.get_tracedata(format = "REALIMAG")
	S21_on = S21_on[0]+1.j*S21_on[1]
	print("Done!")
	na.set_trigger_source('IMM')
	figure("S21")
	plot(Fna, 20.*log10(abs(S21_off)),label = "off")
	plot(Fna, 20.*log10(abs(S21_on)), label = "on")
	legend()
	savefig(path+"/S21.png")
	'''
	if Noise:
		pump.set_status(0)
		sa.set_detector('rms')
		Fsa = sa.get_freqpoints()
		bw = sa.get_res_bw()
		na.set_status(0)
		
		#Noise
		Spec = {}
		for source in Sources:
			print("Source: ",source[0])
			sw_code = source[1]
			sw.do_set_switch(sw_code[0], sw_code[1])
			stupid_waiting(Delay)
			wait_for_Tmeas()
			stupid_waiting(MeasDelay)
			T = TritonGetTemp(source[2])
			print("T= {:.3f} K. Measuring...".format(T))
			Spec[source[0]] = {'T':T, 'A':source[3], 'P': sa.measure()["Power"]}
			print("Done!")
			
			figure("Spec")
			clf()
			bottom = []
			for key in Spec.keys():
				plot(Fsa,Spec[key]['P'], label = str(key))
				bottom = bottom + [min(Spec[key]['P'])]
			ylim((min(bottom), min(bottom)+0.25))	
			legend()
			savefig(path+"/spec.png")	
			
		na.set_status(1)
		'''
		figure("Spec")
		bottom = []
		for key in Spec.keys():
			plot(Fsa,Spec[key]['P'], label = str(key))
			bottom = bottom + [min(Spec[key]['P'])]
		ylim((min(bottom), min(bottom)+10.))	
		legend()
		savefig(path+"/spec.png")
	'''
		Fna, S21_on_fin, S21_off_fin = gain()
		
		figure("S21")
		clf()
		plot(Fna, 20.*log10(abs(S21_off)),label = "off")
		plot(Fna, 20.*log10(abs(S21_on)), label = "on")
		plot(Fna, 20.*log10(abs(S21_on_fin)), label = "on_fin")
		legend()
		savefig(path+"/S21.png")
		
		data = {"F_S21":Fna, "S21_off":S21_off, "S21_on":S21_on, "S21_on_fin":S21_on_fin, "F_S":Fsa, "S":Spec, "BW":bw}
	else:	
		data = {"F_S21":Fna, "S21_off":S21_off, "S21_on":S21_on}		
	f = open(path+"/raw_data.pkl", "wb")
	pickle.dump(data, f)
	f.close()
except: raise	
	
finally:
	Cryo.close()
	na.set_trigger_source('IMM')
	na.set_status(1)