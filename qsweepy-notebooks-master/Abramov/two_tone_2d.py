from numpy import *
import sys
qt_dir = "D:/qtlab_replacement"
sys.path.append(qt_dir)
import init
from instruments import *
import time
import save_pkl
from numpy import *
from qubits import *

q_id = 1

Fex_step = 1e6
Fex_offset = 50e6
Fex_start = 6.9e9
cur_step = 0.025e-3

#Data mamagement
Data_dir ="D:/Abramov/data" 
path = save_pkl.mk_dir(root = Data_dir)
print("Saving files to: ",path)

cs = Yokogawa_GS210(address='GPIB0::2::INSTR')
pna = Agilent_N5242A('pna', address = 'pna')
ex = Agilent_E8257D('lo1', address = 'PSG1')
cs.set_range(0.01)

#ex_freqs = arange(Fex_start, Qubits[q_id]['F01']+Fex_offset, Fex_step) 
ex_freqs = linspace(Fex_start, Qubits[q_id]['F01']+Fex_offset, 251) 
#currents = Qubits[q_id]['I0'] + arange( -Qubits[q_id]['Ispan']/2., Qubits[q_id]['Ispan']/2., cur_step)
currents = Qubits[q_id]['I0'] + linspace( -Qubits[q_id]['Ispan']/2., Qubits[q_id]['Ispan']/2., 251)
        
pna.set_power(Qubits[q_id]['P'])
ex.set_power(Qubits[q_id]['Pex'])

def current_setter(I):
	cs.set_current(I)
	
	pna.set_sweep_mode("LIN")
	pna.set_nop(300)
	pna.set_centerfreq(Qubits[q_id]['F'])
	pna.set_span(Qubits[q_id]['Span'])
	pna.set_bandwidth(20)
	pna.set_power(Qubits[q_id]['P'])
	
	pna.ask('INIT:IMM;*OPC?')
	res_data = pna.get_data()
	res_freqs = pna.get_freqpoints()
	center =  res_freqs[np.argmin(abs(res_data))]
	pna.set_nop(1)  
	pna.set_centerfreq( res_freqs[np.argmin(abs(res_data))] )
	pna.set_bandwidth(20)

f_str = '0\t'+'\t'.join([str(x) for x in ex_freqs])
File = open(path+'S.dat','w+')
File.write(f_str+"\n")
	
pna.set_timeout(60000)	
pna.set_trigger_source("MAN")
pna.write(':FORMAT REAL,32; FORMat:BORDer SWAP;')
cs.set_current(0)	
cs.set_status(1)	
ex.set_status(1)

data_buff = zeros( len(ex_freqs) , dtype = 'complex')
ctime = 0.
try:
	for j,I in enumerate(currents):
		t1=time.time()
		current_setter(I)
		for i,Fex in enumerate(ex_freqs):
			ex.set_frequency(Fex)
			pna.ask('INIT:IMM;*OPC?')
			data_buff[i] = pna.get_data()[0]
		data_str = str(I)+'\t' + '\t'.join([str(x) for x in data_buff])
		File.write(data_str + "\n")
		File.flush()
		if ctime: ctime = (time.time()-t1+ctime)/2
		else: ctime = time.time()-t1
		print("Average cycle time: ",ctime, "s", "Time left: ", ctime*(len(currents)-j), end = '\r')	
			
except KeyboardInterrupt:
	pass
	
finally:
	pna.set_trigger_source("IMM")
	cs.set_current(0)
	cs.set_status(0)			
	ex.set_status(0)
	File.close()