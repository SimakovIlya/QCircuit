from numpy import *
import sys
#qt_dir = "D:/qtlab_replacement"
#sys.path.append(qt_dir)
from qsweepy import *
from qsweepy.instruments import *
#import sweep
import time
#import save_pkl
from matplotlib.pyplot import *

#Data mamagement
Data_dir ="D:/Abramov/data" 
path = save_pkl.mk_dir(root = Data_dir)
print("Saving files to: ",path)

na = Agilent_N5242A('pna', address = 'pna')

Fna = na.get_freqpoints()
S21 = na.get_tracedata(format = "REALIMAG")
S21 = S21[0]+1.j*S21[1]
figure("S21")
plot(Fna, 20.*log10(abs(S21) ) )
legend()
savefig(path+"S21.png")

data = {"F":Fna, "S21":S21}
f = open(path+"/vna_data.pkl", "wb")
pickle.dump(data, f)
f.close()

na.close()