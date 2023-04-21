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
# Imports                                                                          # 
####################################################################################

# Project imports
from config import *


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
# 		voltage_to_pressure                                                        #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Converts a voltage readout from a pressure transducer to a pressure        #
#       in floating point format                                                   #
#                                                                                  #
####################################################################################
def voltage_to_pressure( voltage ):
	Rgain         = 3.3 # kOhm
	Rref          = 100 # kOhm
	gain          = 1 + ( Rref/Rgain )
	max_voltage   = gain*0.1 # Max pt readout is 0.1 V
	max_pressure  = 1000 # psi
	pressure_step = max_pressure/max_voltage 
	return voltage*pressure_step
## voltage_to_pressure ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		voltage_to_pressure_5V                                                     #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Converts a voltage readout from a pressure transducer to a pressure        #
#       in floating point format, used with pts that have a 5V output              #
#                                                                                  #
####################################################################################
def voltage_to_pressure_5V( voltage ):
	max_voltage   = 5    # V
	max_pressure  = 1000 # psi
	pressure_step = max_pressure/max_voltage 
	return voltage*pressure_step
## voltage_to_pressure ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		voltage_to_force                                                           #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Converts a voltage readout from a load cell to a force measurement in      #
#       floating point format                                                      #
#                                                                                  #
####################################################################################
def voltage_to_force( voltage ):
	Rgain      = 0.47 # kOhm
	Rref       = 100  # kOhm
	gain       = 1 + (Rref/Rgain)
	voltage   /= gain
	force_step = (34.5572*1000) # lb/V
	return voltage*force_step # lb
## voltage_to_force ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		loadcell_force                                                             #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Converts readouts from a load cell to the force in lb                      #
#                                                                                  #
####################################################################################
def loadcell_force( readout ):
	voltage = adc_readout_to_voltage ( readout )
	return voltage_to_force( voltage )
## loadcell_force ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		pt_pressure                                                                #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Converts readouts from a pressure transducer to the pressure psi           #
#                                                                                  #
####################################################################################
def pt_pressure( readout ):
	voltage = adc_readout_to_voltage( readout )
	return voltage_to_pressure( voltage )
## pt_pressure ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		tc_temp                                                                    #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Converts readouts from a thermocouple to a temperature                     #
#                                                                                  #
####################################################################################
def tc_temp( readout ):
	# Split readout bytes
	upper_byte = ( readout & 0xFF00 ) >> 8
	lower_byte = readout & 0x00FF

	# Check for negative readout
	if ( ( upper_byte & 0x80 ) == 0x80 ):
		negative = True
	else:
		negative = False

	# Do conversion
	if ( negative ):
		temp = ( ( float(upper_byte)*16.0 + float(lower_byte)/16.0 ) -4096.0 )
	else:
		temp = ( float(upper_byte)*16.0 + float(lower_byte)/16.0 )

	# Return conversion
	return temp # degrees C
## tc_temp ##


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
	
	# Convert from 16 bit unsigned to 16 bit sRigned
	signed_int = 0
	if ( readout < 2**(15) ):
		signed_int = readout	
	else:
		signed_int = -( ( ~(readout) + 1 ) & 0xFFFF )

	# Convert to acceleration	
	num_bits   = 16
	g_setting  = 16  # +- 16g
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
def imu_gyro( readout ):
	
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
	
	# Final conversion
	return readout 

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
	#baro_max_press     = 1250.0*100.0                     # Pa
	#baro_min_press     = 300.0*100.0                      # Pa
	#baro_press_range   = baro_max_press - baro_min_press  # Pa
	#baro_press_setting = (baro_press_range/(2**(19) - 1)) # Pa/LSB 
	#baro_press         = float(readout)*baro_press_setting + baro_min_press # Pa
	
	# Convert to kPa 
	return readout*0.001 

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


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 	   encoder_int_to_deg                                                          #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Converts an integer representing a encoder ticks to a floating point value #
#       in degrees                                                                 #
#                                                                                  #
####################################################################################
def encoder_int_to_deg( encoder_out ):
	if ( encoder_out & 0x80000000 ):
		encoder_out_sig = encoder_out ^ 0xFFFFFFFF
		encoder_out_sig += 1
		encoder_out_sig *= -1
	else:
		encoder_out_sig = encoder_out
	return encoder_out_sig
## encoder_int_to_deg ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 	   pressure_to_alt                                                             #
#                                                                                  #
# DESCRIPTION:                                                                     #
#     Converts pressure readouts in kPa to altitude using the ground pressure and  #
#     altitude pressure                                                            #
#                                                                                  #
####################################################################################
def pressure_to_alt( pressure, ground_pressure ):
	# Constants
	ps     = 101.3 # kPa
	z_star = 8404.0 # m
	gamma  = 1.4 

	# Calculations
	gamma_const1 = ( gamma - 1.0 )/( gamma )
	gamma_const2 = ( gamma )/( gamma - 1.0 )
	alt          = z_star*gamma_const2*( 1 - ( ( pressure/ps )**( gamma_const1 ) ) )
	ground_alt   = z_star*gamma_const2*( 1 - ( ( ground_pressure/ps)**( gamma_const1 ) ) )
	alt_agl      = alt - ground_alt

	# Convert to feet
	return alt_agl*3.28084
## pressure_to_alt ##


####################################################################################
# END OF FILE                                                                      # 
####################################################################################
