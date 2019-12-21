from qsweepy.instruments import *
from qsweepy import *

from qsweepy import awg_iq_multi

import numpy as np

with __import__('importnb').Notebook(): 
    from QCircuit import *

device_settings = {'vna_address': 'TCPIP0::10.20.61.48::inst0::INSTR',
                   'lo1_address': 'TCPIP0::10.20.61.59::inst0::INSTR',
                   'lo1_timeout': 5000, 'rf_switch_address': '10.20.61.224',
                   'use_rf_switch': True,
                   'pxi_chassis_id': 0,
                   'hdawg_address': 'hdawg-dev8108',
                   'sa_address': 'TCPIP0::10.20.61.56::inst0::INSTR',
                   'adc_timeout': 10,
                   'adc_trig_rep_period': 100 * 125,  # 10 kHz rate period
                   'adc_trig_width': 2,  # 80 ns trigger length
                   }

cw_settings = {}
pulsed_settings = {'lo1_power': 18,
                   'vna_power': 16,
                   'ex_clock': 2000e6,  # 1 GHz - clocks of some devices
                   'rep_rate': 10e3,  # 10 kHz - pulse sequence repetition rate
                   # 500 ex_clocks - all waves is shorten by this amount of clock cycles
                   # to verify that M3202 will not miss next trigger
                   # (awgs are always missing trigger while they are still outputting waveform)
                   'global_num_points_delta': 800,
                   'hdawg_ch0_amplitude': 1.0,
                   'hdawg_ch1_amplitude': 1.0,
                   'hdawg_ch2_amplitude': 0.8,
                   'hdawg_ch3_amplitude': 0.8,
                   'hdawg_ch4_amplitude': 1.0,
                   'hdawg_ch5_amplitude': 1.0,
                   'hdawg_ch6_amplitude': 1.0,
                   'hdawg_ch7_amplitude': 1.0,
                   'lo1_freq': 3.3e9,#3.70e9,
                   'pna_freq': 6.06e9,
                   #'calibrate_delay_nop': 65536,
                   'calibrate_delay_nums': 200,
                   'trigger_readout_channel_name': 'ro_trg',
                   'trigger_readout_length': 200e-9,
                   'modem_dc_calibration_amplitude': 1.0,
                   'adc_nop': 1024,
                   'adc_nums': 10000,  ## Do we need control over this? Probably, but not now... WUT THE FUCK MAN
                   }


class hardware_setup():
    def __init__(self, device_settings, pulsed_settings):
        self.device_settings = device_settings
        self.pulsed_settings = pulsed_settings
        self.cw_settings = cw_settings
        self.hardware_state = 'undefined'

        self.pna = None
        self.lo1 = None
        self.rf_switch = None
        self.sa = None
        self.coil_device = None
        self.hdawg = None
        self.adc_device = None
        self.adc = None

        self.ro_trg = None
        self.coil = None
        self.iq_devices = None

    def open_devices(self):

    	C = 5*10**(-14)
		Ij = 40*e**3/hbar/C
		L = 2 * 10**(-8)
		M = 2 * 10**(-8)
		#I = 1.72 * 10**(-8)
		Time = 200
		dt = 0.01
		nums = 2

		transmon = Transmon(psi = [1, 0], C = C, Ij1 = Ij, Ij2 = 0, M = 0)
		coupling = Coupling(C /60)
		alpha = 1
		n_osc = 6
		gamma = 0.01
		osc = Oscillator(psi= np.exp(-alpha**2/2)*alpha**np.arange(n_osc)/np.sqrt(scipy.special.factorial(np.arange(n_osc))),\
		                 L = L, C = C/1., gamma = gamma, noise = 1)
		drive_osc = InSignal()
		circuit = Circuit([transmon, coupling, osc, drive_osc],  [[1], [0, 2], [1], [2]], dt = dt)

		insignal = InSignal()

		lo = LO(insignal)
		lo_m = LO(insignal)
		awg = AWG(insignal)
		mi = MI()
		mi.set_circuit(circuit)
		mi.set_lo(lo_m)

		# paraments
		A = 1
		I0 = 0.3
		Q0 = -0.3
		fc = 10
		fI = fQ = 2

		# подача сигналов
		
		self.lo1 = lo
		self.awg = awg
		self.pna = lo_m
		self.adc = mi
		self.awg_mi = mi
		lo.set_frequency(fc)
		lo.set_power(1.)

        #self.sa = Agilent_N9030A('pxa', address=self.device_settings['sa_address'])

        #self.adc_device = TSW14J56_evm()
        #self.adc = TSW14J56_evm_reducer(self.adc_device)
        self.adc.output_raw = True
        self.adc.avg_cov = False
        self.adc.resultnumber = False

    # self.hardware_state = 'undefined'

    def set_pulsed_mode(self):
        self.lo1.set_power(self.pulsed_settings['lo1_power'])
        self.lo1.set_frequency(self.pulsed_settings['lo1_freq'])

        self.pna.set_power(self.pulsed_settings['vna_power'])
        self.pna.set_frequency(self.pulsed_settings['pna_freq'])

        self.awg.set_clock(self.pulsed_settings['ex_clock'])

        self.adc.set_nop(self.pulsed_settings['adc_nop'])
        self.adc.set_nums(self.pulsed_settings['adc_nums'])

        # setting repetition period for slave devices
        # 'global_num_points_delay' is needed to verify that M3202A and other slave devices will be free
        # when next trigger arrives.
        global_num_points = int(np.round(
            self.pulsed_settings['ex_clock'] / self.pulsed_settings['rep_rate'] - self.pulsed_settings[
                'global_num_points_delta']))

        # global_num_points = 20000

        self.awg.set_nop(global_num_points)

        # а вот длину сэмплов, которая очевидно то же самое, нужно задавать на всех авгшках.
        # хорошо, что сейчас она только одна.
        # this is zashkvar   WUT THE FUCK MAN

    def set_switch_if_not_set(self, value, channel):
        pass

    def setup_iq_channel_connections(self, exdir_db):
        # промежуточные частоты для гетеродинной схемы new:
        self.iq_devices = {'iq_ex1': awg_iq_multi.Awg_iq_multi(self.awg, self.awg, 0, 1, self.lo1, exdir_db=exdir_db),
                           'iq_ro': awg_iq_multi.Awg_iq_multi(self.awg_mi, self.awg_mi, 0, 1, self.pna, exdir_db=exdir_db)}  # M3202A
        # iq_pa = awg_iq_multi.Awg_iq_multi(awg_tek, awg_tek, 3, 4, lo_ro) #M3202A
        self.iq_devices['iq_ex1'].name = 'ex1'
        # iq_pa.name='pa'
        self.iq_devices['iq_ro'].name = 'ro'

        self.iq_devices['iq_ex1'].calibration_switch_setter = lambda: self.set_switch_if_not_set(1, channel=1)
        self.iq_devices['iq_ro'].calibration_switch_setter = lambda: self.set_switch_if_not_set(4, channel=1)

        self.iq_devices['iq_ex1'].sa = self.sa
        self.iq_devices['iq_ro'].sa = self.sa

        self.fast_controls = {#'coil': awg_channel.awg_channel(self.hdawg, 4)
        						}  # coil control

    def get_readout_trigger_pulse_length(self):
        return self.pulsed_settings['trigger_readout_length']

    def get_modem_dc_calibration_amplitude(self):
        return self.pulsed_settings['modem_dc_calibration_amplitude']

    def revert_setup(self, old_settings):
        if 'adc_nums' in old_settings:
            self.adc.set_nums(old_settings['adc_nums'])
        if 'adc_nop' in old_settings:
            self.adc.set_nop(old_settings['adc_nop'])
        if 'adc_posttrigger' in old_settings:
            self.adc.set_posttrigger(old_settings['adc_posttrigger'])
