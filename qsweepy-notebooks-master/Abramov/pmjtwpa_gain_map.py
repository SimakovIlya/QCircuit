from numpy import *
import sys
sys.path.append("D:/qtlab_replacement")
import init
import time
from instruments import *
from matplotlib.pyplot import *
import save_pkl
import visa
import pickle
import gain_noise

#Data mamagement
Data_dir ="D:/Abramov/data" 
FileComment = ""
path = save_pkl.mk_dir(root = Data_dir)
print("Running pmjtwpa_gain_map.py\nSaving files to: ",path)

Fp_list = arange(5.,5.4,0.002)*1e9
Pp_list = arange(-18.,-3,0.05)

na = Agilent_N5242A('pna', address = 'pna')
pump = Agilent_E8257D('lo1', address = 'GEN1')

Power = na.get_power()
BW = na.get_bandwidth()

Fna = na.get_freqpoints()

Header = '''#{:s}
#Signal power = {:.3f} dBm
#Frequency start={:.10e} Hz 
#Frequency stop={:.10e} Hz
#Bandwidth={:g} Hz
'''.format(FileComment, Power, Fna[0], Fna[-1], BW )	

f_str = '0\t0\t'+'\t'.join([str(x) for x in Fna])
	
File = open(path+'pmjtwpa_gain_map_S.dat','w+')
File.write(Header)
File.write(f_str+"\n")

pump.set_power(-18)
pump.set_status(1)

try:
	for Fp in Fp_list:
		for Pp in Pp_list:
			#Set power
			pump.set_frequency(Fp)
			pump.set_power(Pp)
			print("P={:.3f} dbm  F={:.9e} Hz \r".format(Pp, Fp), end = "\r")
			
			#Run PNA measurement
			data = na.get_tracedata(format = "REALIMAG")
			data = data[0]+1.j*data[1]
			
			data_str = "{:e}\t{:f}\t".format(Fp, Pp) + '\t'.join([str(x) for x in data])
			File.write(data_str + "\n")
			File.flush()
	
except KeyboardInterrupt:
	print("\nInterrupted by user")
finally:
	pump.set_status(0)
	File.close()
