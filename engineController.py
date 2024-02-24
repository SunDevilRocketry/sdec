####################################################################################
#                                                                                  #
# engineController.py -- module with engine controller specific command line       #
#                        functions                                                 # 
#                                                                                  #
# Author: Colton Acosta                                                            #
# Date: 6/22/2022                                                                  #
# Sun Devil Rocketry Avionics                                                      #
#                                                                                  #
####################################################################################


####################################################################################
# Standard Imports                                                                 #
####################################################################################
import serial.tools.list_ports
import time


####################################################################################
# Project Modules                                                                  #
####################################################################################
import commands
import hw_commands
import controller
from   config   import *


####################################################################################
# Global Variables                                                                 #
####################################################################################
supported_boards = ["Liquid Engine Controller (L0002 Rev 4.0)",
                    "Liquid Engine Controller (L0002 Rev 5.0)",
				    "Flight Computer (A0002 Rev 1.0)" ]

# Numbers assigned to each valve 
valve_nums = {
			"oxPress"  : 1,
			"fuelPress": 2,
			"oxPurge"  : 5,
			"fuelPurge": 6,
			"oxVent"   : 3,
			"fuelVent" : 4,
			"oxMain"   : 8,
			"fuelMain" : 7
             }

# Valve on/off states
valve_on_states = {
				"oxPress"  : "OPEN",
				"fuelPress": "OPEN",
				"oxPurge"  : "CLOSED",
				"fuelPurge": "CLOSED",
				"oxVent"   : "CLOSED",
				"fuelVent" : "CLOSED",
				"oxMain"   : "OPEN"  ,
				"fuelMain" : "OPEN"
                  }

valve_off_states = {
				"oxPress"  : "CLOSED",
				"fuelPress": "CLOSED",
				"oxPurge"  : "OPEN"  ,
				"fuelPurge": "OPEN"  ,
				"oxVent"   : "OPEN"  ,
				"fuelVent" : "OPEN"  ,
				"oxMain"   : "CLOSED",
				"fuelMain" : "CLOSED"
                   }


####################################################################################
# Shared Procedures                                                                #
####################################################################################


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         extract_valve_state                                                      #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         extracts extracts the state of each valve from telemetry byte            #
#                                                                                  #
####################################################################################
def extract_valve_state( valve_state_byte ):
	valve_state_int = ord( valve_state_byte )
	valve_states    = {}
	for valve in valve_nums:
		if ( valve_state_int & ( 1 << ( valve_nums[valve] - 1 ) ) ):
			valve_states[valve] = valve_on_states[valve]
		else:
			valve_states[valve] = valve_off_states[valve]
	return valve_states
## extract_valve_state ## 


####################################################################################
# Procedures                                                                       #
####################################################################################


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		power                                                                      #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		displays the power source of the MCU                                       #
#                                                                                  #
####################################################################################
def power(Args, serialObj):
	################################################################################
	# Local Variables                                                              #
	################################################################################

	# Inputs
	power_inputs = { 
                    'source': {},
                    'help':   {}
                    }
    
	# Maximum number of arguments
	max_args = 1

	# Command type -- subcommand function
	command_type = 'subcommand'

	# Command opcode
	opcode = b'\x21' 

	# Response codes
	pwr_buck_response_code = b'\x01'
	pwr_usb_response_code =  b'\x02'

	################################################################################
	# Basic Inputs Parsing                                                         #
	################################################################################
	parse_check = commands.parseArgs(
                                    Args,
                                    max_args,
                                    power_inputs,
                                    command_type 
                                    )

	# Return if user input fails parse checks
	if ( not parse_check ):
		return serialObj 

	# Set subcommand
	user_subcommand = Args[0]

	################################################################################
	# Command-Specific Checks                                                      #
	################################################################################

	# Verify Engine Controller Connection
	if ( not ( serialObj.controller in supported_boards ) ):
		print("Error: The power command requires a valid "  + 
              "serial connection to an engine controller "  + 
              "device. Run the \"connect\" command to "     +
              "establish a valid connection.")
		return serialObj

	################################################################################
	# Subcommand: power help                                                       #
	################################################################################
	if (user_subcommand == "help"):
		commands.display_help_info('power')
		return serialObj

	################################################################################
	# Subcommand: power source                                                     #
	################################################################################
	elif (user_subcommand == "source"):

		# Send power opcode
		serialObj.sendByte(opcode)

		# Get power status code
		pwr_status = serialObj.readByte()

		# Display power source
		if (pwr_status == pwr_buck_response_code):
			print("5V power supplied by buck converter")
		elif (pwr_status == pwr_usb_response_code):
			print('5V power supplied by USB')
		elif (ign_status == b''):
			print('Error: No response recieved from ' +
                  'engine controller' )
		else:
			print("Error: Unknown controller response")

		# Exit
		return serialObj

	################################################################################
    # Unknown Option                                                               #
	################################################################################
	else:
		print("Error: unknown subcommand passed to power" +
              "function")	
		commands.error_msg()
		return serialObj
## power ##


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		hotfire_abort                                                              #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Sends the hotfire abort commands to the engine controller                  #
#                                                                                  #
####################################################################################
def hotfire_abort( Args, serialObj ):
	################################################################################
    # Local Variables                                                              #
	################################################################################

	# Command opcode
	opcode = b'\x90' 

	# Acknowledge/No Acknowledge byte
	ack_byte    = b'\x95'
	no_ack_byte = b'\x98'

	################################################################################
	# Command-Specific Checks                                                      #
	################################################################################

	# Verify Engine Controller Connection
	if ( not ( serialObj.controller in supported_boards ) ):
		print("Error: The abort command requires a valid "  + 
              "serial connection to an engine controller "  + 
              "device. Run the \"connect\" command to "     +
              "establish a valid connection.")
		return serialObj

	################################################################################
	# Command Implementation                                                       #
	################################################################################
	print( "Aborting Hotfire ... " )

	# Send opcode
	serialObj.sendByte( opcode )

	# Wait for and parse acknowledge signal
	response = serialObj.readByte()
	if ( response == ack_byte ):
		print( "Hotfire sucessfully aborted" )
		serialObj.set_engine_state( "Abort State" )
	elif ( response == no_ack_byte ):
		print( "Abort unsuccessful. No response from engine controller" )
	else:
		print( "Abort unsuccessful. Timeout or unrecognized response" )
	return serialObj
## hotfire_abort ##


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		telreq                                                                     #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Telemetry request, gets sensor data from the engine controller             #
#                                                                                  #
####################################################################################
def telreq( Args, serialObj, show_output = True ):
	################################################################################
    # Local Variables                                                              #
	################################################################################

	# Command opcode
	opcode = b'\x96' 

	# Acknowledge/No Acknowledge byte
	ack_byte    = b'\x95'
	no_ack_byte = b'\x98'

	# Size of sensor dump
	sensor_dump_size = 40

	 # Complete list of sensor names/numbers 
	sensor_numbers = list( controller.controller_sensors[serialObj.controller].keys() )

	################################################################################
	# Command-Specific Checks                                                      #
	################################################################################

	# Verify Engine Controller Connection
	if ( not ( serialObj.controller in supported_boards ) ):
		print("Error: The telreq command requires a valid "  + 
              "serial connection to an engine controller "  + 
              "device. Run the \"connect\" command to "     +
              "establish a valid connection.")
		return serialObj

	################################################################################
	# Command Implementation                                                       #
	################################################################################

	# Send opcode 
	serialObj.sendByte( opcode )

	# Wait for acknowledge command
	response = serialObj.readByte()
	if ( response != ack_byte ):
		print( "Telemetry request unsucessful. Cannot reach engine controller" )
		return serialObj

	# Get sensor data
	sensor_data_bytes = serialObj.readBytes( sensor_dump_size )

	# Get the valve state
	valve_state_byte = serialObj.readByte() 

	# Process sensor data
	serialObj.sensor_readouts = hw_commands.get_sensor_readouts(
												serialObj.controller,
												sensor_numbers       ,
												sensor_data_bytes
	                                                           )
	
	# Process the valve data
	serialObj.valve_states = extract_valve_state( valve_state_byte )

	# Display Sensor readouts
	if ( show_output ):
		for sensor in serialObj.sensor_readouts:
			readout_formatted = hw_commands.format_sensor_readout(
													serialObj.controller,
													sensor               ,
													serialObj.sensor_readouts[sensor]
													             )
			print( readout_formatted )
		for valve in serialObj.valve_states:
			print( valve + ": " + serialObj.valve_states[valve] )
	return serialObj
## telreq ##


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		pfpurge                                                                    #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Pre-fire purge, initiates a system purge prior to hotfire                  #
#                                                                                  #
####################################################################################
def pfpurge( Args, serialObj, show_output = True ):
	################################################################################
    # Local Variables                                                              #
	################################################################################

	# Command opcode
	opcode = b'\x91' 

	# Acknowledge/No Acknowledge byte
	ack_byte    = b'\x95'
	no_ack_byte = b'\x98'

	################################################################################
	# Command-Specific Checks                                                      #
	################################################################################

	# Verify Engine Controller Connection
	if ( not ( serialObj.controller in supported_boards ) ):
		print("Error: The pfpurge command requires a valid "  + 
              "serial connection to an engine controller "    + 
              "device. Run the \"connect\" command to "       +
              "establish a valid connection.")
		return serialObj

	################################################################################
	# Command Implementation                                                       #
	################################################################################
	print( "Initiating Pre-Hotfire Purge Sequence ... " )

	# Send opcode
	serialObj.sendByte( opcode )

	# Wait for and parse acknowledge signal
	response = serialObj.readByte()
	if ( response == ack_byte ):
		print( "Pre-Hotfire purge sequence sucessfully initiated" )
		serialObj.set_engine_state( "Pre-Fire Purge State" )
	elif ( response == no_ack_byte ):
		print( "Pre-Hotfire purge unsucessful. No response from engine controller" )
	else:
		print( "Pre-Hotfire purge unsucessful. Timeout or unrecognized response" )
	return serialObj
## pfpurge ##


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		fillchill                                                                  #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Fill and Chill, initiates the fill and chill engine sequence               #
#                                                                                  #
####################################################################################
def fillchill( Args, serialObj, show_output = True ):
	################################################################################
    # Local Variables                                                              #
	################################################################################

	# Command opcode
	opcode = b'\x92' 

	# Acknowledge/No Acknowledge byte
	ack_byte    = b'\x95'
	no_ack_byte = b'\x98'

	################################################################################
	# Command-Specific Checks                                                      #
	################################################################################

	# Verify Engine Controller Connection
	if ( not ( serialObj.controller in supported_boards ) ):
		print("Error: The fillchill command requires a valid "  + 
              "serial connection to an engine controller "    + 
              "device. Run the \"connect\" command to "       +
              "establish a valid connection.")
		return serialObj

	################################################################################
	# Command Implementation                                                       #
	################################################################################
	print( "Initiating Fill and Chill Sequence ... " )

	# Send opcode
	serialObj.sendByte( opcode )

	# Wait for and parse acknowledge signal
	response = serialObj.readByte()
	if ( response == ack_byte ):
		print( "Fill and Chill sequence sucessfully initiated" )
		serialObj.set_engine_state( "Fill and Chill State" )
	elif ( response == no_ack_byte ):
		print( "Fill and Chill unsucessful. No response from engine controller" )
	else:
		print( "Fill and Chill unsucessful. Timeout or unrecognized response" )
	return serialObj
## fillchill ##


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		standby                                                                    #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Initiates the standby engine sequence                                      #
#                                                                                  #
####################################################################################
def standby( Args, serialObj, show_output = True ):
	################################################################################
    # Local Variables                                                              #
	################################################################################
	print("thing")
	# Command opcode
	#opcode = b'\x93'

	# Acknowledge/No Acknowledge byte
	ack_byte    = b'\x95'
	no_ack_byte = b'\x98'

	################################################################################
	# Command-Specific Checks                                                      #
	################################################################################

	# Verify Engine Controller Connection
	if ( not ( serialObj.controller in supported_boards ) ):
		print("Error: The standby command requires a valid "  + 
              "serial connection to an engine controller "    + 
              "device. Run the \"connect\" command to "       +
              "establish a valid connection.")
		return serialObj

	################################################################################
	# Command Implementation                                                       #
	################################################################################
	print( "Initiating Standby State ... " )

	# Send opcode
	serialObj.sendByte( opcode )

	# Wait for and parse acknowledge signal
	response = serialObj.readByte()
	if ( response == ack_byte ):
		print( "Standby sequence sucessfully initiated" )
		serialObj.set_engine_state( "Standby State" )
	elif ( response == no_ack_byte ):
		print( "Standby unsucessful. No response from engine controller" )
	else:
		print( "Standby unsucessful. Timeout or unrecognized response" )


	return serialObj
## standby ##


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		hotfire                                                                    #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Initiates the hotfire engine sequence                                      #
#                                                                                  #
####################################################################################
def hotfire( Args, serialObj, show_output = True ):
	################################################################################
    # Local Variables                                                              #
	################################################################################

	# Command opcode
	opcode = b'\x94' 

	# Acknowledge/No Acknowledge byte
	ack_byte    = b'\x95'
	no_ack_byte = b'\x98'

	################################################################################
	# Command-Specific Checks                                                      #
	################################################################################

	# Verify Engine Controller Connection
	if ( not ( serialObj.controller in supported_boards ) ):
		print("Error: The hotfire command requires a valid "  + 
              "serial connection to an engine controller "    + 
              "device. Run the \"connect\" command to "       +
              "establish a valid connection.")
		return serialObj

	################################################################################
	# Command Implementation                                                       #
	################################################################################
	print( "Initiating Hotfire ... " )

	# Send opcode
	serialObj.sendByte( opcode )

	# Wait for and parse acknowledge signal
	response = serialObj.readByte()
	if ( response == ack_byte ):
		print( "Ignition sequence sucessfully initiated" )
		serialObj.set_engine_state( "Fire State" )
	elif ( response == no_ack_byte ):
		print( "Ignition unsucessful. No response from engine controller" )
	else:
		print( "Ignition unsucessful. Timeout or unrecognized response" )
	return serialObj
## hotfire ##


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		hotfire_getstate                                                           #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Gets the state of the hotfire sequence                                     #
#                                                                                  #
####################################################################################
def hotfire_getstate( Args, serialObj, show_output = True ):
	################################################################################
    # Local Variables                                                              #
	################################################################################

	# Command opcode
	opcode = b'\x99' 

	# Acknowledge/No Acknowledge byte
	ack_byte    = b'\x95'
	no_ack_byte = b'\x98'

	# Engine States
	engine_state = {
					b'\x00': "Initialization State",
					b'\x01': "Ready State"         ,
					b'\x02': "Pre Fire Purge State",
					b'\x03': "Fill and Chill State",
					b'\x04': "Standby State"       ,
					b'\x05': "Fire State"          ,
					b'\x06': "Disarm State"        ,
					b'\x07': "Post-Fire State"     ,
					b'\x08': "Manual State"        ,
					b'\x09': "Abort State",
					#b'\x10': "Reset"
	               }

	################################################################################
	# Command-Specific Checks                                                      #
	################################################################################

	# Verify Engine Controller Connection
	if ( not ( serialObj.controller in supported_boards ) ):
		print("Error: The getstate command requires a valid "  + 
              "serial connection to an engine controller "    + 
              "device. Run the \"connect\" command to "       +
              "establish a valid connection.")
		return serialObj

	################################################################################
	# Command Implementation                                                       #
	################################################################################

	# Send opcode 
	serialObj.sendByte( opcode )

	# Get response from engine controller
	response = serialObj.readByte()
	if ( response == no_ack_byte ):
		print( "Error: Could not reach engine controller" )
		return serialObj
	elif ( response == b'' ):
		print( "Error: Timeout")
		return serialObj
	elif ( response not in list( engine_state.keys() ) ):
		print( "Error: Unrecognized engine state" )
		return serialObj

	# Display Engine State	
	print( "Engine State: " )
	print( engine_state[response] )

	# Set the engine state
	serialObj.set_engine_state( engine_state[response] )
	return serialObj
## hotfire_getstate ##


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		stophotfire                                                                #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Terminates the engine burn                                                 #
#                                                                                  #
####################################################################################
def stop_hotfire( Args, serialObj, show_output = True ):
	################################################################################
    # Local Variables                                                              #
	################################################################################

	# Command opcode
	opcode = b'\x9A' 

	# Acknowledge/No Acknowledge byte
	ack_byte    = b'\x95'
	no_ack_byte = b'\x98'

	################################################################################
	# Command-Specific Checks                                                      #
	################################################################################

	# Verify Engine Controller Connection
	if ( not ( serialObj.controller in supported_boards ) ):
		print("Error: The stophotfire command requires a valid "  + 
              "serial connection to an engine controller "    + 
              "device. Run the \"connect\" command to "       +
              "establish a valid connection.")
		return serialObj

	################################################################################
	# Command Implementation                                                       #
	################################################################################
	print( "Halting Hotfire ... " )

	# Send opcode
	serialObj.sendByte( opcode )

	# Wait for and parse acknowledge signal
	response = serialObj.readByte()
	if ( response == ack_byte ):
		print( "Hotfire sucessfully terminated" )
	elif ( response == no_ack_byte ):
		print( "Stop Hotfire unsucessful. No response from engine controller" )
	else:
		print( "Stop Hotfire unsucessful. Timeout or unrecognized response" )
	return serialObj
## stop_hotfire ## 


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		stoppurge                                                                  #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Terminates the post-hotfire engine purge                                   #
#                                                                                  #
####################################################################################
def stop_purge( Args, serialObj, show_output = True ):
	################################################################################
    # Local Variables                                                              #
	################################################################################

	# Command opcode
	opcode = b'\x97' 

	# Acknowledge/No Acknowledge byte
	ack_byte    = b'\x95'
	no_ack_byte = b'\x98'

	################################################################################
	# Command-Specific Checks                                                      #
	################################################################################

	# Verify Engine Controller Connection
	if ( not ( serialObj.controller in supported_boards ) ):
		print("Error: The stoppurge command requires a valid "  + 
              "serial connection to an engine controller "    + 
              "device. Run the \"connect\" command to "       +
              "establish a valid connection.")
		return serialObj

	################################################################################
	# Command Implementation                                                       #
	################################################################################
	print( "Stopping Purge ... " )

	# Send opcode
	serialObj.sendByte( opcode )

	# Wait for and parse acknowledge signal
	response = serialObj.readByte()
	if ( response == ack_byte ):
		print( "Purge sucessfully terminated" )
		serialObj.set_engine_state( "Disarm State" )
	elif ( response == no_ack_byte ):
		print( "stoppurge unsucessful. No response from engine controller" )
	else:
		print( "stoppurge unsucessful. Timeout or unrecognized response" )
	return serialObj
## stop_purge ## 


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		kbottleclose                                                               #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Sends the signal indicating that the kbottle has been closed               #
#                                                                                  #
####################################################################################
def kbottle_close( Args, serialObj, show_output = True ):
	################################################################################
    # Local Variables                                                              #
	################################################################################

	# Command opcode
	opcode = b'\x9C' 

	# Acknowledge/No Acknowledge byte
	ack_byte    = b'\x95'
	no_ack_byte = b'\x98'

	################################################################################
	# Command-Specific Checks                                                      #
	################################################################################

	# Verify Engine Controller Connection
	if ( not ( serialObj.controller in supported_boards ) ):
		print("Error: The kbottleclose command requires a valid "  + 
              "serial connection to an engine controller "    + 
              "device. Run the \"connect\" command to "       +
              "establish a valid connection.")
		return serialObj

	################################################################################
	# Command Implementation                                                       #
	################################################################################
	print( "Sending K-Bottle Close Command ... " )

	# Send opcode
	serialObj.sendByte( opcode )

	# Wait for and parse acknowledge signal
	response = serialObj.readByte()
	if ( response == ack_byte ):
		print( "Sucessful" )
		serialObj.set_engine_state( "Post-Fire State" )
	elif ( response == no_ack_byte ):
		print( "Unsucessful. No response from engine controller" )
	else:
		print( "Unsucessful. Timeout or unrecognized response" )
	return serialObj
## kbottleclose ## 


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		tankstat                                                                   #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Checks if the tank pressures are sufficiently low to approach              #
#                                                                                  #
####################################################################################
def tankstat( Args, serialObj, show_output = True ):
	################################################################################
    # Local Variables                                                              #
	################################################################################

	# Command opcode
	opcode = b'\x9D' 

	# Acknowledge/No Acknowledge byte
	ack_byte    = b'\x95'
	no_ack_byte = b'\x98'

	# Engine Tank status responses
	tank_safe_code   = b'\x01'
	tank_unsafe_code = b'\x02'

	################################################################################
	# Command-Specific Checks                                                      #
	################################################################################

	# Verify Engine Controller Connection
	if ( not ( serialObj.controller in supported_boards ) ):
		print("Error: The kbottleclose command requires a valid "  + 
              "serial connection to an engine controller "    + 
              "device. Run the \"connect\" command to "       +
              "establish a valid connection.")
		return serialObj

	################################################################################
	# Command Implementation                                                       #
	################################################################################
	print( "Checking Tank Pressures ... " )

	# Send opcode
	serialObj.sendByte( opcode )

	# Wait for and parse acknowledge signal
	response = serialObj.readByte()
	if ( response == no_ack_byte ):
		print( "Unsuccessful. Could not reach engine controller" )
	elif ( response == tank_unsafe_code ):
		print( "UNSAFE: Tank pressures too high" )
	elif ( response == tank_safe_code ):
		print( "SAFE: Tank pressures OK ")
	else:
		print( "Unsucessful. Timeout or unrecognized response" )
	return serialObj
## tankstat ## 


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		lox_purge                                                                  #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Sends the signal to initiate the LOX purge                                 #
#                                                                                  #
####################################################################################
def lox_purge( Args, serialObj, show_output = True ):
	################################################################################
    # Local Variables                                                              #
	################################################################################

	# Command opcode
	opcode = b'\x9B' 

	# Acknowledge/No Acknowledge byte
	ack_byte    = b'\x95'
	no_ack_byte = b'\x98'

	################################################################################
	# Command-Specific Checks                                                      #
	################################################################################

	# Verify Engine Controller Connection
	if ( not ( serialObj.controller in supported_boards ) ):
		print("Error: The loxpurge command requires a valid "  + 
              "serial connection to an engine controller "    + 
              "device. Run the \"connect\" command to "       +
              "establish a valid connection.")
		return serialObj

	################################################################################
	# Command Implementation                                                       #
	################################################################################
	print( "Initiating LOX Tank Purge ... " )

	# Send opcode
	serialObj.sendByte( opcode )

	# Wait for and parse acknowledge signal
	response = serialObj.readByte()
	if ( response == ack_byte ):
		print( "Sucessful" )
	elif ( response == no_ack_byte ):
		print( "Unsucessful. No response from engine controller" )
	else:
		print( "Unsucessful. Timeout or unrecognized response" )
	return serialObj
## lox_purge ## 


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		manual                                                                     #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Puts the engine into manual mode                                           #
#                                                                                  #
####################################################################################
def manual( Args, serialObj, show_output = True ):
	################################################################################
    # Local Variables                                                              #
	################################################################################

	# Command opcode
	opcode = b'\x9E' 

	# Acknowledge/No Acknowledge byte
	ack_byte    = b'\x95'
	no_ack_byte = b'\x98'

	################################################################################
	# Command-Specific Checks                                                      #
	################################################################################

	# Verify Engine Controller Connection
	if ( not ( serialObj.controller in supported_boards ) ):
		print("Error: The loxpurge command requires a valid "  + 
              "serial connection to an engine controller "    + 
              "device. Run the \"connect\" command to "       +
              "establish a valid connection.")
		return serialObj

	################################################################################
	# Command Implementation                                                       #
	################################################################################
	print( "Entering manual mode ... " )

	# Send opcode
	serialObj.sendByte( opcode )

	# Wait for and parse acknowledge signal
	response = serialObj.readByte()
	if ( response == ack_byte ):
		print( "Sucessful. Now in manual mode" )
		serialObj.set_engine_state( "Manual State" )
	elif ( response == no_ack_byte ):
		print( "Unsucessful. No response from engine controller" )
	else:
		print( "Unsucessful. Timeout or unrecognized response" )
	return serialObj
## lox_purge ##


# remote reset
def reset( Args, serialObj, show_output = True ):
	################################################################################
    # Local Variables                                                              #
	################################################################################

	# Command opcode
	opcode = b'\x04'

	# Acknowledge/No Acknowledge byte
	ack_byte    = b'\x52'
	no_ack_byte = b'\x98'
	
	# Options Dictionary
	connect_inputs = {
		'-h': 'Display help info',
	}

	# Maximum number of arguments
	max_args = 1

	# Command type -- subcommand function
	command_type = 'default'

	# Firmware version
	firmware_version = None

	##############################################################################
	# Basic inputs parsing                                                       #
	##############################################################################
	# parse_check = commands.parseArgs(
	# 	Args,
	# 	max_args,
	# 	connect_inputs,
	# 	command_type
	# # )
	# if (not parse_check):
	# 	return serialObj  # user inputs failed parse tests
	user_option = Args[0]

	if ( user_option == '-h' ):
		print( "This is reset" )
		return serialObj

	# Send opcode
	serialObj.sendByte( opcode )

	# Wait for and parse acknowledge signal
	response = serialObj.readByte()
	if ( response == ack_byte ):
		print( "Sucessful" )
	elif ( response == no_ack_byte ):
		print( "Unsucessful. No response from engine controller" )
	else:
		print( "Unsucessful. Timeout or unrecognized response" )
	return serialObj



####################################################################################
# END OF FILE                                                                      #
####################################################################################