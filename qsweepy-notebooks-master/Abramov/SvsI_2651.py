from numpy import *
import sys
qt_dir = "D:/qtlab_replacement"
sys.path.append(qt_dir)
import init
from instruments import *
import sweep
import time

CS_Vlim = 10.
currents = arange(0,-0.5,-0.005)
pna = Agilent_N5242A('pna', address = 'pna')
#cs = Yokogawa_GS210(address='gs210')

rm = visa.ResourceManager()
CS = rm.open_resource("2651")
CS.write('''smua.source.func = smua.OUTPUT_DCAMPS;
smua.source.limitv = {:f};
smua.source.autorangei = smua.AUTORANGE_ON;
smua.source.leveli = 0;
smua.source.output = smua.OUTPUT_ON;
'''.format(CS_Vlim))

def set_current(I):
	CS.write( "smua.source.leveli = {:e}".format(I) )
	time.sleep(10)

sweep.sweep(pna, (currents, set_current, 'Current'), filename='test')
#cs.set_current(0)
CS.write('''smua.source.leveli = 0;
smua.source.output = smua.OUTPUT_OFF;''')