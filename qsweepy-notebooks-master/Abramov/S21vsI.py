from qsweepy import *
from qsweepy.instruments import *

from numpy import *
import sys
import time

#Data mamagement
Data_dir ="C:/Users/cryopxi/Documents/Abramov/data" 
path = save_pkl.default_measurement_save_path(root = Data_dir, mkdir=True)
print("Saving files to: ",path)

currents = arange(-1.,1, 0.02)*1e-3

pna_preset = True

cs = Yokogawa_GS210(address='GPIB1::1::INSTR')
pna = Agilent_N5242A('pna', address = 'ZVB20-23-100170')
cs.set_range(0.01)
if pna_preset:
   	pna.set_power(-50.)
	pna.set_bandwidth(400)
	pna.set_centerfreq(6.87656e9)
	pna.set_span(100e6)

cs.set_status(1)
sweep.sweep(pna, (currents, cs.set_current, 'Current'))
cs.set_status(0)
pna.close()