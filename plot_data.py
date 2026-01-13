# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Sun Devil Rocketry

from matplotlib import pyplot as plt
import numpy as np

with open( "output/sensor_data.txt", "r" ) as file:
	lines = file.readlines()

# Controller Names
controller_names = [
                   "Liquid Engine Controller (L0002 Rev 3.0)",
                   "Valve Controller (L0005 Rev 2.0)"        ,
                   "Liquid Engine Controller (L0002 Rev 4.0)",
				   "Flight Computer (A0002 Rev 1.0)"
                   ]

# Inidices of sensors in output file 
sensor_indices = {
				   "accX" : 1,
				   "accY" : 2,
				   "accZ" : 3,
				   "gryoX": 4,
				   "gryoY": 5,
				   "gryoZ": 6,
				   "magX" : 7,
				   "magY" : 8,
				   "magZ" : 9,
				   "imut" : 10,
				   "pres" : 11,
				   "temp" : 12 
                 }

lines_int = []
for line in lines:
	line_int_str = line.split( "\t" ) 
	line_int = []	
	for val in line_int_str:
		if ( val != '\n' ):
			line_int.append( float(val) )
	lines_int.append( line_int )

sensor_data = np.array( lines_int )
plt.plot( sensor_data[0:1000,0], sensor_data[0:1000,sensor_indices["pres"]] )
plt.show()
