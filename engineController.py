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


###############################################################
# Global Variables                                            #
###############################################################
supported_boards = ["Liquid Engine Controller (L0002 Rev 4.0)",
				    "Flight Computer (A0002 Rev 1.0)"
                    ]


###############################################################
#                                                             #
# COMMAND:                                                    #
# 		ignite                                                #
#                                                             #
# DESCRIPTION:                                                #
# 		issue the ignition signal to the controller or        #
#       display                                               #
#                                                             #
###############################################################
def ignite(Args, serialObj):
	###########################################################
	# Local Variables                                         #
	###########################################################

	# Subcommand Dictionary
	# Options Dictionary
	ignite_inputs = { 
                    'fire': {},
                    'cont': {},
                    'help': {}
                    }
    
	# Maximum number of arguments
	max_args = 1

	# Command type -- subcommand function
	command_type = 'subcommand'

	# Command opcode
	opcode = b'\x20' 

	# Subcommand codes
	ignite_fire_code     = b'\x01'
	ignite_cont_code     = b'\x02'

	# Response codes
	ignite_fire_success_code =     b'\x40'
	ignite_fire_fail_ematch_code = b'\x08'
	ignite_fire_fail_power_code =  b'\x10'
	ignite_fire_fail_code =        b'\x20'

	###########################################################
	# Basic Inputs Parsing                                    #
    ###########################################################
	parse_check = commands.parseArgs(
                                    Args,
                                    max_args,
                                    ignite_inputs,
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
		print("Error: The ignite command requires a valid " + 
              "serial connection to an engine controller "  + 
              "device. Run the \"connect\" command to "     +
              "establish a valid connection.")
		return serialObj

	###########################################################
	# Subcommand: ignite help                                 #
    ###########################################################
	if (user_subcommand == "help"):
		display_help_info('ignite')
		return serialObj

	###########################################################
	# Subcommand: ignite fire                                 #
    ###########################################################
	elif (user_subcommand == "fire"):

		# Send ignite opcode
		serialObj.sendByte(opcode)

		# Send subcommand code
		serialObj.sendByte(ignite_fire_code)

		# Get ignition status code
		ign_status = serialObj.readByte()

		# Display ignition status

        # Succesful ignition
		if (ign_status == ignite_fire_success_code):
			print("Ignition successful")

		# No response code received
		elif (ign_status == b''):
			print('Ignition unsuccessful. No response ' +
				  'code recieved from engine controller' )

        # No continuity in ematch and/or arming switch
		elif (ign_status == ignite_fire_fail_ematch_code):
			print('Ignition unsuccessful. No continuity ' +
				  'in ematch and/or arming switch. '      +
				  'Ensure an ematch is connected and the '+
				  'switch is armed')

		# No power supply
		elif (ign_status == ignite_fire_fail_power_code):
			print('Ignition unsuccessful. The device is ' +
                  'currently being powered via USB. The ' +
                  'engine controller must be powered via '+
                  'the 12V jack or power connector to '   +
                  'trigger to light the ematch.' ) 

        # Ematch continuity is not disrupted after asserting
        # the ignition signal
		elif (ign_status == ignite_fire_fail_code):
			print('Ignition unsuccessful. The ignite signal ' +
                  'was asserted but the ematch was not lit')

		else:
			print("Ignition unsuccessful")

		# Exit
		return serialObj

	###########################################################
	# Subcommand: ignite cont                                 #
    ###########################################################
	elif (user_subcommand == "cont"):

		# Send ignite opcode
		serialObj.sendByte(opcode)

		# Send subcommand code
		serialObj.sendByte(ignite_cont_code)

        # Get ignition status code
		ign_status = serialObj.readByte()

		# Parse response code
		ign_status_int = ord(ign_status)

		# Ematch and switch continuity
		if ((ign_status_int >> 0) & 1):
			print("Ematch and Switch:     Connected")
		else: 
			print("Ematch and Switch:     Disconnected")

		# Solid propellant wire continuity
		if ((ign_status_int >> 1) & 1):
			print("Solid Propellant Wire: Connected")
		else: 
			print("Solid Propellant Wire: Disconnected")

		# Nozzle wire continuity
		if ((ign_status_int >> 2) & 1):
			print("Nozzle Wire:           Connected")
		else: 
			print("Nozzle Wire:           Disconnected")

        # Exit
		return serialObj

    ###########################################################
    # Unknown Subcommand                                      #
    ###########################################################
	else:
		print("Error: unknown subcommand passed to ignite " +
              "function")	
		error_msg()
		return serialObj


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
