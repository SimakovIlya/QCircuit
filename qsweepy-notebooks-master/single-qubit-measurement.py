from pympler import tracker
memory_tracker = tracker.SummaryTracker()
memory_tracker.print_diff()

from qsweepy import *
from qsweepy.instruments import *
from qsweepy.save_pkl import save_pkl

print ('Before matplotlib')
memory_tracker.print_diff() 

import matplotlib.pyplot as plt
print ('After matplotlib')
memory_tracker.print_diff() 
import numpy as np
print ('Before matplotlib interactive')
memory_tracker.print_diff() 
from matplotlib import interactive
interactive(True)
print ('After matplotlib interactive')
memory_tracker.print_diff() 
import qsweepy.quantum_two_level_dynamics as dyn

import imp
import qsweepy.save_pkl


#Параметры кубитов.all keys should be str
Qubits = {'2-070818': {'r':{
					'Fr': 7.29775e9,
					 'P': -30 },
			  'q':{
			  '00-1-01': 4.25083e+09,
			  '01-1-02': 4.00871e+09,
			  '00-2-02': 4.12977e+09,
				'P':None}
			 },
		  '2-070818':{'r':{'Fr': 7.2988e9,  'P': -30}, 'q':{'00-1-01': 4.25501e9, '00-2-02': 4.1e9, '01-1-02': 3.98e9}},
		  '2-080818':{'r':{'Fr': 7.2988e9,  'P': -30}, 'q':{'00-1-01': 4.256397e9, '00-2-02': 4.1345e9, '01-1-02': 4.01420e9}},
		  '1-080818':{'r':{'Fr': 7.2059e9, 'P': -30},'q':{ '00-1-01':4.242190e9+1.76e6, '00-2-02': 4.1e9, '01-1-02': 4.00020e9}},
		  '2-100818':{'r':{'Fr': 7.1011e9, 'P': -30}, 'q':{'0-1-1': 3.8199e9}},
		  '1-100818':{'r':{'Fr': 7.0765e9, 'P': -30},'q': {'00-1-01': 3.92173e9, '00-1-10': 3.9406e9}},
		  #'2':{'r':{'Fr': 7.332e9, 'P': -30}, 'q':{'0-1-1': 3.8199e9}},
		  #'1':{'r':{'Fr': 7.2798e9, 'P': -30},'q': {'00-1-01': 3.92173e9, '00-1-10': 3.9406e9}},
		  #'2':{'r':{'Fr': 7.332e9, 'P': -50}, 'q':{'00-1-01': 4.2568e9, '01-1-02': 4.0147e9, '00-1-10': 3.9297e9}},
		  #'1':{'r':{'Fr': 7.278e9, 'P': -50},'q': {'00-1-01': 4.2446e9, '01-1-02': 4.002e9, '00-1-10': 3.9470e9}},
		  '2':{'r':{'Fr': 7.332e9, 'P': -50}, 'q':{'00-1-01': 4.2568e9, '01-1-02': 4.0147e9, '00-1-10': 3.9297e9}},
		  '1':{'r':{'Fr': 7.278e9, 'P': -50},
			   'q':{'00-1-01': 4.246158e9, #4.24607e9, #4.2446e9
					'00-2-02': 4.12454e9,#4.1233e9,
					'00-2-11': 4.1030e9,
					'01-1-02': 4.0030e9, 
					'00-1-10': 3.94780e9,#3.9480e9,
					'01-2-03': 3.8630e9,
					'00-2-20': 3.82293e9,
					'10-1-20': 3.6990e9}},}
qubit_params=Qubits
qubit_id = '1'
switch_to_sample = {'1':4, '2':3}
#it should be dumped too
qubits_dump = {"qubits":qubit_params,'switch':switch_to_sample}
qjson.dump('qubits','qubit_params',qubits_dump)

print ('Before devices')
memory_tracker.print_diff() 

# RF switch for making sure we know what sample we are measuring
pna = Agilent_N5242A('pna', address = 'TCPIP0::10.20.61.48::inst0::INSTR')
lo1 = Agilent_E8257D('lo1', address = 'TCPIP0::10.20.61.59::inst0::INSTR')
rf_switch = nn_rf_switch('rf_switch', address='10.20.61.224')

CHASSIS = 1
SLOT_IN = 11
SLOT_OUT = 7
awg = Keysight_M3202A_S('awg', CHASSIS, SLOT_OUT)
adc = Keysight_M3102A('adc', CHASSIS, SLOT_IN)

sa = Agilent_N9030A('pxa', address = 'TCPIP0::10.20.61.56::inst0::INSTR')
lo_ex = lo1
lo_ro = pna
awg_tek=awg

print ('After devices')
memory_tracker.print_diff() 

# Источник тока - в autorange
#current.set_autorange(1)
#Мощности гетеродинов, постоянные
#Мощность гетеродина для возбуждения 13-16 дБм

lo_ex_pow = 14
lo_ex.set_status(1)
lo_ro_pow = 16
lo_ro.set_power(lo_ro_pow)

pna.write("OUTP ON")
pna.write("SOUR1:POW1:MODE ON")
pna.write("SOUR1:POW2:MODE OFF")
pna.set_sweep_mode("CW")
lo_ex.set_power(lo_ex_pow)

marker_length = 100
readout_trigger_delay = 185
trg_length = 10e-9

ex_clock = 1e9
ro_clock = 1e9

rep_rate = 20e3 # частота повторений эксперимента

awg.stop()
#awg_tek.set_clock(ex_clock) # клок всех авгшк
awg.set_nop(ex_clock/rep_rate) # репрейт нужно задавать по=хорошему только на управляющей,
awg.run()
# а вот длину сэмплов, которая очевидно то же самое, нужно задавать на всех авгшках.
# хорошо, что сейчас она только одна.
#this is zashkvar

awg_tek = awg
# channel 0 is master and triggers all others
awg.trigger_source_types = [0, 6,6,6]
awg.trigger_source_channels = [0, 4000,4000,4000] # pxi trigger 0 
awg.trigger_delays = [40, 0,0,0] # master channel should wait 400 ns for others to start
awg.trigger_behaviours = [0,4,4,4] #rising edge trigger
for channel in range(0,4):
#for channel in range(1,5):
	awg.set_amplitude(.2, channel=channel)
	awg.set_offset(0, channel=channel)
	awg.set_output(1, channel=channel)
	awg.set_waveform(waveform=[0]*awg_tek.get_nop(), channel=channel)

	
awg.set_marker(length=marker_length, delay=0, channel=0)
awg_channels =dict()
ro_trg = awg_digital.awg_digital(awg_tek, 1)
ro_trg.mode = 'set_delay'
ro_trg.delay_setter = lambda x: adc.set_trigger_delay(int(x*adc.get_clock()/iq_ex.get_clock()-readout_trigger_delay))
awg_channels['ro_trg'] = ro_trg

# настройки оцифровщика
adc.set_input(channel=1, input=1)
adc.set_input(channel=2, input=1)
adc.set_trigger_external(channel=1)
adc.set_trigger_external(channel=2)

ro_if = 75e6
lo_freq = 4.05e9
qubit_id='1'

# промежуточные частоты для гетеродинной схемы new:
lo1.set_frequency(lo_freq)
ex_if = lo_freq-qubit_params[qubit_id]['q']['00-1-01']
iq_ex = awg_iq_multi.awg_iq_multi(awg_tek, awg_tek, 0, 1, lo_ex)
for tr,freq in qubit_params[qubit_id]['q'].items():
	iq_ex.carriers[tr] = awg_iq_multi.carrier(iq_ex)
	iq_ex.carriers[tr].set_frequency(freq)
	awg_channels['iq_ex_'+tr]=iq_ex.carriers[tr]

lo_ro.set_frequency(qubit_params[qubit_id]['r']['Fr']+ro_if)
iq_ro = awg_iq_multi.awg_iq_multi(awg_tek, awg_tek, 2, 3, lo_ro)
iq_ro.carriers['iq_ro'] = awg_iq_multi.carrier(iq_ro)
iq_ro.carriers['iq_ro'].set_frequency(qubit_params[qubit_id]['r']['Fr'])
awg_channels['iq_ro'] = iq_ro.carriers['iq_ro']
readout_channels = {'iq_ro':awg_channels['iq_ro']}

print ('Before pulses')
memory_tracker.print_diff() 

pg = pulses.pulses(awg_channels)

print("Excitation channel", end='\n')
iq_ex.do_calibration(sa)
print("Readout channel", end='\n')
iq_ro.do_calibration(sa)

trigger_readout_seq = [pg.p('ro_trg', 10e-9, pg.rect, 1)]

adc.set_nums(50)
adc.set_nop(20000)

print ('Before modem')
memory_tracker.print_diff() 

modem = modem_readout.modem_readout(pg, adc, trigger_readout_seq, axis_mean=0)
modem.readout_channels = readout_channels
ro_trg.delay_setter = lambda x: adc.set_trigger_delay(int(x*adc.get_clock()/iq_ex.get_clock()-0))
readout_trigger_delay = modem.calibrate_delay()[awg_channels['iq_ro']]
readout_trigger_delay_cycles = readout_trigger_delay*adc.get_clock()
print (readout_trigger_delay, readout_trigger_delay_cycles)
ro_trg.delay_setter = lambda x: adc.set_trigger_delay(int(x*adc.get_clock()/iq_ex.get_clock()-readout_trigger_delay_cycles))
readout_trigger_delay_test = modem.calibrate_delay()[awg_channels['iq_ro']]
readout_trigger_delay_cycles_test = readout_trigger_delay*adc.get_clock()
print (readout_trigger_delay_test, readout_trigger_delay_cycles_test)

modem.calibrate_dc()

modem.filters = modem.calibrated_filters
adc_reducer = data_reduce.data_reduce(modem)
adc_reducer.filters = {'S21': data_reduce.mean_reducer(modem, 'iq_ro', axis=0)}
adc_reducer.extra_opts['scatter'] = True
adc_reducer.extra_opts['realimag'] = True

def set_adc_nop(ro_adc_length):
	#adc.stop()
	signal_size = int(np.ceil(4./3.*(ro_adc_length)*adc.get_clock()))
	nop = int( 2**np.ceil(np.log2(signal_size)) )
	posttrigger = nop*15/16
	adc.set_nop(nop)
	
# "Измеритель средних прошедших импульсов"
# Просто усредняет всё по номеру сэмпла.

ro_adc_length = 0.1e-6
ro_dac_length = 0.08e-6
set_adc_nop(ro_adc_length)
adc.set_nums(10000)

print ('Before mean_sample data_reduce')
memory_tracker.print_diff() 

mean_sample = data_reduce.data_reduce(adc)
mean_sample.filters['Mean Voltage (AC)'] = data_reduce.mean_reducer_noavg(adc, 'Voltage', 0)
mean_sample.filters['S21+'] = data_reduce.mean_reducer_freq(adc, 'Voltage', 0, iq_ro.carriers['iq_ro'].get_if())
mean_sample.filters['S21-'] = data_reduce.mean_reducer_freq(adc, 'Voltage', 0, -iq_ro.carriers['iq_ro'].get_if())
# # Этот измеритель мы как правило используем когда точек не слишком много и все результаты его жизнедеятельности как правило 
# # выглядят как ломаные. Чтобы было красиво, давайте лучше сделаем точки (а кривые потом получим фитованые)
mean_sample.extra_opts['scatter'] = True

ro_amplitude = 0.02
ro_parameters = {"adc_len":ro_adc_length,'dac_len': ro_dac_length,'amp': ro_amplitude,'adc nums':adc.nums,
				'trg_length':trg_length}
qjson.dump("setups","readout",ro_parameters)

ex_channels = ['iq_ex_00-1-01', 
			   'iq_ex_00-2-02', 
			   'iq_ex_00-1-10', 
			   'iq_ex_00-2-20']

ex_amplitudes = {'iq_ex_00-1-01':0.5, 
			   'iq_ex_00-2-02':0.5, 
			   'iq_ex_00-1-10':0.5, 
			   'iq_ex_00-2-20':0.5}
qubit_id=1
ro_par = {'qubit_id':qubit_id,'ex_channels':ex_channels}
fitter = lambda x,y: fitting.fit1d(x,y,'S21')
ro_par['fitter']=fitter

rabi_lengths = np.arange(0.,10e-9, 2e-9)
delaysT2 = np.arange(0, 20e-9, 1e-9)
target_freq_offset = -20e6
delaysT2_coherence = np.arange(0, 500e-6, 10e-9)
target_freq_offset_coherence = -2e6
delaysT1 = np.arange(0, 2.5e-6,0.05e-6)

print ('Before diff_readout')
memory_tracker.print_diff() 

diff_adc_reducer = diff_readout.diff_readout(adc_reducer)
#two = dyn.quantum_two_level_dynamics(pg,adc_reducer,**ro_par)
#two_ = dyn.quantum_two_level_dynamics(pg,mean_sample,**ro_par)
ro_sequence = trigger_readout_seq+[pg.p('iq_ro', ro_dac_length, pg.rect, ro_amplitude)]
two_diffs = [dyn.quantum_two_level_dynamics(pg,
										   diff_adc_reducer,
										   ex_channel=ex_channel,
										   ro_channel='iq_ro',
										   ro_sequence=ro_sequence,
										   ex_amplitude=ex_amplitudes[ex_channel],
										   fitter=fitter, 
										   shuffle=True,
										   qubit_id=qubit_id) for ex_channel in ex_channels]

memory_tracker.print_diff() 

iters = 3
for _iter in range(iters):
	for two_diff in two_diffs[:1]:
		two_diff.Rabi_rect(rabi_lengths)
		memory_tracker.print_diff() 
		before = hp.heap()
		#two_diff.Ramsey(delaysT2, target_freq_offset)
		two_diff.Ramsey(delaysT2_coherence,target_freq_offset_coherence)
		memory_tracker.print_diff() 
		two_diff.decay(delaysT1)
		memory_tracker.print_diff() 
		two_diff.spin_echo(delaysT2_coherence,target_freq_offset_coherence)
		after = hp.heap()
		memory_tracker.print_diff() 