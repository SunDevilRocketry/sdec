###############################################################
#                                                             #
# valveController.py -- module with valve controller specific #
#                        command line functions               # 
# Author: Colton Acosta                                       #
# Date: 4/16/2022                                             #
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
from commands import display_help_info


###############################################################
# Global Variables                                            #
###############################################################
supported_boards = ["Valve Controller (L0005 Rev 2.0)"]


###############################################################
#                                                             #
# COMMAND:                                                    #
# 		sol                                                   #
#                                                             #
# DESCRIPTION:                                                #
# 		control the actuation state of solenoids              #
#                                                             #
###############################################################
def sol(Args, serialObj):
	###########################################################
	# Local Variables                                         #
	###########################################################

	# Subcommand and Options Dictionary
	sol_inputs = { 
			   'on':     {
							'-h' : 'Display help info',
							'-n' : 'Specify a solenoid number'
						 } ,
			   'off':    {
							'-h' : 'Display help info',
							'-n' : 'Specify a solenoid number'
						 } , 
			   'toggle': {
							'-h' : 'Display help info',
							'-n' : 'Specify a solenoid number'
						 },
			   'reset':  {
						 },
			   'help':   {
						 }
                       
                 }
    
	# Maximum number of arguments
	max_args = 3

	# Command type -- subcommand function
	command_type = 'subcommand'

	# Command opcode
	opcode = b'\x51' 

	# Subcommand codes
	sol_on_base_code     = b'\x00'
	sol_off_base_code    = b'\x08'
	sol_toggle_base_code = b'\x10'
	sol_reset_code       = b'\x18'

	# Subcommand codes as integers
	sol_on_base_code_int     = ord( b'\x00' )
	sol_off_base_code_int    = ord( b'\x08' )
	sol_toggle_base_code_int = ord( b'\x10' )

	###########################################################
	# Basic Inputs Parsing                                    #
    ###########################################################
	parse_check = commands.parseArgs(
                                    Args,
                                    max_args,
                                    sol_inputs,
                                    command_type 
                                    )
	# Return if user input fails parse checks
	if ( not parse_check ):
		return serialObj 

	# Set subcommand and option
	user_subcommand = Args[0]
	if ( len(Args) != 1 ):
		user_option = Args[1]
		options_command = True
	else:
		options_command = False

	###########################################################
	# Command-Specific Checks                                 #
    ###########################################################
	if (options_command):
		if (user_option == '-n'):
			# No solenoid number entered
			if (len(Args) == 2):
				print('Error: No solenoid specified')
				return serialObj
			# Solenoid number not a number
			try:
				user_solenoid = int(Args[2])
			except ValueError:
				print('Error: Invalid solenoid number. Ensure '
                    + 'the input is an integer in the range of '
                    + '1-6.')
				return serialObj
			# Solenoid number out of range
			if ((user_solenoid < 1) or (user_solenoid > 6)):
				print('Error: Invalid solenoid number. Ensure '
                    + 'the input is an integer in the range of '
                    + '1-6.')
				return serialObj

	# Verify Valve Controller Connection
	if (not (serialObj.controller in supported_boards)):
		print("Error: The sol command requires a valid " + 
              "serial connection to a valve controller " + 
              "device. Run the \"connect\" command to "  +
              "establish a valid connection.")
		return serialObj

	###########################################################
	# Subcommand: sol help                                    #
    ###########################################################
	if (user_subcommand == "help"):
		display_help_info('sol')
		return serialObj

	###########################################################
	# Subcommand: sol on                                      #
    ###########################################################
	elif (user_subcommand == "on"):
		# Option: -h                                          
		if (user_option == '-h'):
			display_help_info('sol')
			return serialObj

		# Option: -n                                          
		elif(user_option == '-n'):
			# Send solenoid opcode
			serialObj.sendByte(opcode)
			# Send subcommand code
			sol_on_code_int = sol_on_base_code_int + user_solenoid
			sol_on_code = sol_on_code_int.to_bytes(1, 
                                                   byteorder = 'big',
                                                   signed = False)
			serialObj.sendByte(sol_on_code)
			return serialObj

	###########################################################
	# Subcommand: sol off                                     #
    ###########################################################
	elif (user_subcommand == "off"):
		# Option: -h                                          
		if (user_option == '-h'):
			display_help_info('sol')
			return serialObj

		# Option: -n                                          
		elif(user_option == '-n'):
			# Send solenoid opcode
			serialObj.sendByte(opcode)
			# Send subcommand code
			sol_off_code_int = sol_off_base_code_int + user_solenoid
			sol_off_code = sol_off_code_int.to_bytes(1, 
                                                   byteorder = 'big',
                                                   signed = False)
			serialObj.sendByte(sol_off_code)
			return serialObj

	###########################################################
	# Subcommand: sol toggle                                  #
    ###########################################################
	elif (user_subcommand == "toggle"):
		# Option: -h                                          
		if (user_option == '-h'):
			display_help_info('sol')
			return serialObj

		# Option: -n                                          
		elif(user_option == '-n'):
			# Send solenoid opcode
			serialObj.sendByte(opcode)
			# Send subcommand code
			sol_toggle_code_int = sol_toggle_base_code_int + user_solenoid
			sol_toggle_code = sol_toggle_code_int.to_bytes(1, 
                                                   byteorder = 'big',
                                                   signed = False)
			serialObj.sendByte(sol_toggle_code)
			return serialObj

	###########################################################
	# Subcommand: sol reset                                   #
    ###########################################################
	elif (user_subcommand == "reset"):
		# Send solenoid opcode
		serialObj.sendByte(opcode)
		# Send subcommand code
		serialObj.sendByte(sol_reset_code)
		return serialObj

    ###########################################################
    # Unknown Option                                          #
    ###########################################################
	else:
		print("Error: unknown option passed to connect function")	
		error_msg()
		return serialObj

### END OF FILE
