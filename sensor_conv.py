####################################################################################
#                                                                                  # 
# sensor_conv.py -- Functions for converting raw sensor data                       # 
#                   from integer format                                            #
# Author: Colton Acosta                                                            # 
# Date: 11/25/2022                                                                 #
# Sun Devil Rocketry Avionics                                                      #
#                                                                                  #
####################################################################################


####################################################################################
# Standard Imports                                                                 # 
####################################################################################


####################################################################################
# Procedures                                                                       #
####################################################################################


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		adc_readout_to_voltage                                                     #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Converts a sensor readout from the ADC to a voltage                        #
#       in floating point format                                                   #
#                                                                                  #
####################################################################################
def adc_readout_to_voltage( readout ):
	num_bits     = 16
	voltage_step = 3.3/float(2**(num_bits))
	return readout*voltage_step 

## adc_readout_to_voltage ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		imu_accel                                                                  #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Converts a sensor readout from the IMU accelerometer                       #
#       to the m/s^2 acceleration                                                  #
#                                                                                  #
####################################################################################
def imu_accel( readout ):
	
	# Convert from 16 bit unsigned to 16 bit signed
	signed_int = 0
	if ( readout < 2**(15) ):
		signed_int = readout	
	else:
		signed_int = -( ( ~(readout) + 1 ) & 0xFFFF )

	# Convert to acceleration	
	num_bits   = 16
	g_setting  = 2 # +- 2g
	g          = 9.8 # m/s^2
	accel_step = 2*g_setting*g/float(2**(num_bits) - 1)
	
	# Final conversion
	return accel_step*signed_int 

## imu_accel ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		imu_gryo                                                                   #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Converts a sensor readout from the IMU gryoscope                           #
#       to the degree/s angular rate                                               #
#                                                                                  #
####################################################################################
def imu_gryo( readout ):
	
	# Convert from 16 bit unsigned to 16 bit signed
	signed_int = 0
	if ( readout < 2**(15) ):
		signed_int = readout	
	else:
		signed_int = -( ( ~(readout) + 1 ) & 0xFFFF ) 

	# Convert to acceleration	
	num_bits         = 16
	gyro_setting     = 250.0 # +- 250 deg/s
	gyro_sensitivity = float(2**(num_bits) -1 )/(2*gyro_setting)  # LSB/(deg/s)
	
	# Final conversion
	return float(signed_int)/( gyro_sensitivity ) 

## imu_gryo ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		baro_temp                                                                  #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Converts a sensor readout from the baro temperature sensor from the raw    #
#       integer format                                                             #
#                                                                                  #
####################################################################################
def baro_temp( readout ):
	
	# Convert to degrees C 
	baro_temp_setting = (125.0/(2**(16) - 1))# degrees C/ LSB 
	baro_temp_offset  = -40
	
	# Final conversion
	return float(readout)*baro_temp_setting + baro_temp_offset

## baro_temp ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		baro_press                                                                 #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Converts a sensor readout from the baro pressure sensor from the raw       #
#       integer format                                                             #
#                                                                                  #
####################################################################################
def baro_press( readout ):
	
	# Convert to Pa 
	baro_max_press     = 1250.0*100.0                     # Pa
	baro_min_press     = 300.0*100.0                      # Pa
	baro_press_range   = baro_max_press - baro_min_press  # Pa
	baro_press_setting = (baro_press_range/(2**(16) - 1)) # Pa/LSB 
	baro_press         = float(readout)*baro_press_setting + baro_min_press # Pa
	
	# Convert to psi 
	return baro_press*(0.000145038) 

## baro_press ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		time_millis_to_sec                                                         #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Converts an integer representing milliseconds to a floating point seconds  #
#       value                                                                      #
#                                                                                  #
####################################################################################
def time_millis_to_sec( time_millis ):
	return float( time_millis )/1000.0

## time_millis_to_sec ##


####################################################################################
# END OF FILE                                                                      # 
####################################################################################
