from qsweepy import *
from qsweepy.instruments import *
import visa
#import qsweepy.save_pkl as save_pkl 

Noise = True
#Data mamagement
Data_dir ="C:/Data/Abramov" 
path = save_pkl.default_measurement_save_path(root = Data_dir, mkdir=True)
print("Saving files to: ",path)

na = Agilent_N5242A('pna', address = 'TCPIP0::10.20.61.48::inst0::INSTR')
sa = Agilent_N9030A('sa', address='TCPIP0::10.20.61.56::inst0::INSTR')
pump = Agilent_E8257D('lo1', address = 'TCPIP0::10.20.61.59::inst0::INSTR')
sw = nn_rf_switch(name='rf_switch', address='10.20.61.224')

rm = visa.ResourceManager()
Cryo=rm.open_resource('DR200')
Cryo.read_termination="\n"
Cryo.write_termination="\n"
Cryo.close()