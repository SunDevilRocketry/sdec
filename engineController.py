###############################################################
#                                                             #
# engineController.py -- module with valve controller         # 
#                        specific command line functions      # 
#                                                             #
# Author: Colton Acosta                                       #
# Date: 6/22/2022                                             #
# Sun Devil Rocketry Avionics                                 #
#                                                             #
###############################################################


###############################################################
# Standard Imports                                            #
###############################################################
import serial.tools.list_ports


###############################################################
# Project Modules                                             #
###############################################################
import commands
from   commands import display_help_info
from   config   import *


###############################################################
# Global Variables                                            #
###############################################################
supported_boards = ["Liquid Engine Controller (L0002 Rev 4.0)",
				    "Flight Computer (A0002 Rev 1.0)"
                    ]




###############################################################
#                                                             #
# COMMAND:                                                    #
# 		power                                                 #
#                                                             #
# DESCRIPTION:                                                #
# 		displays the power source of the MCU                  #
#                                                             #
###############################################################
def power(Args, serialObj):
	###########################################################
	# Local Variables                                         #
	###########################################################

	# Subcommand Dictionary
	# Options Dictionary
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

	###########################################################
	# Basic Inputs Parsing                                    #
    ###########################################################
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

	###########################################################
	# Command-Specific Checks                                 #
    ###########################################################

	# Verify Engine Controller Connection
	if (not (serialObj.controller in supported_boards)):
		print("Error: The power command requires a valid "  + 
              "serial connection to an engine controller "  + 
              "device. Run the \"connect\" command to "     +
              "establish a valid connection.")
		return serialObj

	###########################################################
	# Subcommand: power help                                  #
    ###########################################################
	if (user_subcommand == "help"):
		display_help_info('power')
		return serialObj

	###########################################################
	# Subcommand: power source                                #
    ###########################################################
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

    ###########################################################
    # Unknown Option                                          #
    ###########################################################
	else:
		print("Error: unknown subcommand passed to power" +
              "function")	
		error_msg()
		return serialObj



###############################################################
# END OF FILE                                                 #
###############################################################
