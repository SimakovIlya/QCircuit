from visa import *
import time
import sys
from IPython.display import display, clear_output

rm = ResourceManager()
TC=rm.open_resource("LS350", read_termination = '\n')

TC.write("HTRSET 1,1,2,0,1")
TC.write("RANGE 1,5")
TC.write("MOUT 1,90")
n=0
try:
	while(1):
		if int( TC.ask("RANGE? 1") )==0:
				if(n>=1): break
				TC.write("HTRSET 1,2,2,0,1")
				TC.write("RANGE 1,5")
				TC.write("MOUT 1,35")
				n+=1
		clear_output(wait=True)	
		print (" Output: 1 "+ "Level:"+TC.ask("MOUT? 1")+"% "+"Range: "+TC.ask("RANGE? 1"), end = "\r") 
		sys.stdout.flush()
		time.sleep(10.)
except KeyboardInterrupt:
	TC.write("RANGE 1,0")
	pass
TC.close()



