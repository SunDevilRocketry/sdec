############################################################### 
#                                                             # 
# sensor_conv.py -- Functions for converting raw sensor data  # 
#                   from integer format                       #
# Author: Colton Acosta                                       # 
# Date: 11/25/2022                                            #
# Sun Devil Rocketry Avionics                                 #
#                                                             #
###############################################################


###############################################################
# Standard Imports                                            # 
###############################################################


###############################################################
# Procedures                                                  #
###############################################################


###############################################################
#                                                             #
# PROCEDURE:                                                  #
# 		adc_readout_to_voltage                                #
#                                                             #
# DESCRIPTION:                                                #
# 		Converts a sensor readout from the ADC to a voltage   #
#       in floating point format                              #
#                                                             #
###############################################################
def adc_readout_to_voltage( 
                          readout # ADC readout
                          ):
	num_bits     = 16
	voltage_step = 3.3/float(2**(num_bits))
	return readout*voltage_step 


###############################################################
# END OF FILE                                                 # 
###############################################################
