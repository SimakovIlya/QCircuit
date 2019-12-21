from numpy import *
import sys
qt_dir = "D:/qtlab_replacement"
sys.path.append(qt_dir)
import init
from instruments import *
import sweep
import time

currents = arange(-1, 1, 0.01)*1e-3

pna_preset = True

cs = Yokogawa_GS210(address='GPIB0::2::INSTR')
pna = Agilent_N5242A('pna', address = 'pna')

cs.set_range(1e-3)
pna.set_sweep_mode("LIN")
if pna_preset:
	pna.set_nop(400)
	pna.set_power(-30.)
	pna.set_bandwidth(200)
	pna.set_centerfreq(6.6644e9)
	pna.set_span(50e6)

cs.set_status(1)

def set_current(val):
	cs.set_current(0.)
	time.sleep(0.02)
	cs.set_current(val)

sweep.sweep(pna, (currents, set_current, 'Current'))

cs.set_current(0.)	
cs.set_status(0)
pna.close()