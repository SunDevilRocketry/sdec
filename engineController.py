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
		if ( show_output ):
			print( "Telemetry request unsucessful. Cannot reach engine controller" )
		return serialObj

	# Get sensor data
	sensor_data_bytes = serialObj.readBytes( sensor_dump_size )

	# Process sensor data
	serialObj.sensor_readouts = hw_commands.get_sensor_readouts(
												serialObj.controller,
												sensor_numbers       ,
												sensor_data_bytes
	                                                           )

	# Display Sensor readouts
	if ( show_output ):
		for sensor in serialObj.sensor_readouts:
			readout_formatted = hw_commands.format_sensor_readout(
													serialObj.controller,
													sensor               ,
													serialObj.sensor_readouts[sensor]
													             )
			print( readout_formatted )
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

	# Command opcode
	opcode = b'\x93' 

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
	## TODO: Implement
	print( "GET STATE" )
	return serialObj
## hotfire_getstate ##


####################################################################################
# END OF FILE                                                                      #
####################################################################################