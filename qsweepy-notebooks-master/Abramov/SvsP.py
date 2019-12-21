from numpy import *
import sys
qt_dir = "D:/qtlab_replacement"
sys.path.append(qt_dir)
import init
from instruments import *
import sweep
import time

powers = arange(-60,3, 0.5)
pna = Agilent_N5242A('pna', address = 'pna')

sweep.sweep(pna, (powers, pna.set_power, 'Power'), filename='paramp')

pna.close()