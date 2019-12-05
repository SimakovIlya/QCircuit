with __import__('importnb').Notebook(): 
    from test_QCircuit import *

test_damping_without_pump()
test_damping_with_pump()
test_change_freq_signal()