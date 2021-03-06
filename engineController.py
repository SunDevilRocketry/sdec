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
supported_boards = ["Liquid Engine Controller (L0002 Rev 4.0)"]


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
#                                                             #
# COMMAND:                                                    #
# 		flash                                                 #
#                                                             #
# DESCRIPTION:                                                #
# 		read and write data to the engine controller's flash  #
#                                                             #
###############################################################
def flash(Args, serialObj):
	###########################################################
	# Local Variables                                         #
	###########################################################

	# Subcommand and Options Dictionary
	flash_inputs= { 
    'enable' : {
			   },
    'disable': {
			   },
    'status' : {
			   },
	'write'  : {
			'-b' : 'Specify a byte to write to flash memory'  ,
			'-s' : 'Specify a string to write to flash memory',
			'-a' : 'Specify a memory address to write to'     ,
			'-f' : 'Specify a file to use for input data'     ,
			'-h' : 'Display help info'
			   },
	'read'   : {
			'-a' : 'Specify a memory address to read from',
			'-n' : 'Specify a number of bytes to read from flash memory',
			'-f' : 'Specify a file to use for output data',
			'-h' : 'Display help info'
			   }, 
	'erase'  : {
			   },
	'help'   : {
			   }
                 }
    
	# Maximum number of arguments
	max_args = 5

	# Command type -- subcommand function
	command_type = 'subcommand'

	# Command opcode
	opcode = b'\x22' 

    # Subcommand Data format
	# SUBOP2 | SUBOP1 | SUBOP0 | BNUM4 | BNUM3 | BNUM2 | BNUM1 | BNUM0  
	# SUBOP(0-2) Subcommand opcode bits specifies the subcommand to be
	#            executed
	# BNUM(0-4) Number of bytes to read/write (max 31)

	# Subcommand codes
	flash_read_base_code    = b'\x00'  # SUBOP 000 -> 0000 0000
	flash_enable_base_code  = b'\x20'  # SUBOP 001 -> 0010 0000
	flash_disable_base_code = b'\x40'  # SUBOP 010 -> 0100 0000
	flash_write_base_code   = b'\x60'  # SUBOP 011 -> 0110 0000
	flash_erase_base_code   = b'\x80'  # SUBOP 100 -> 1000 0000
	flash_status_base_code  = b'\xa0'  # SUBOP 101 -> 1010 0000

	# Subcommand codes as integers
	flash_read_base_code_int    = ord( flash_read_base_code    )
	flash_enable_base_code_int  = ord( flash_enable_base_code  )
	flash_disable_base_code_int = ord( flash_disable_base_code )
	flash_write_base_code_int   = ord( flash_write_base_code   )
	flash_erase_base_code_int   = ord( flash_erase_base_code   )
	flash_status_base_code_int  = ord( flash_status_base_code  )

	# flash write data
	byte   = None
	string = None
	file   = None

	# Flash return data
	status_register = None


	###########################################################
	# Basic Inputs Parsing                                    #
    ###########################################################
	parse_check = commands.parseArgs(
                                    Args,
                                    max_args,
                                    flash_inputs,
                                    command_type 
                                    )
	# Return if user input fails parse checks
	if ( not parse_check ):
		return serialObj 

	# Set subcommand, options, and input data
	user_subcommand = Args[0]
	if ( len(Args) != 1 ):

		# Pull options from args
		Args_options = Args[1:]

		# Check that two options with input data were supplied
		if ( Args_options[0] == '-h'):
			user_options = [Args_options[0]]
			options_command = False
		elif ( len(Args_options) < 4):
			print("Error: Not enough options/inputs")
			return serialObj
		else:
			user_options = [Args_options[0], Args_options[2]]
			user_inputs  = {
                           user_options[0] : Args_options[1],
                           user_options[1] : Args_options[3]
                           }
			options_command = True
	else:
		options_command = False

	###########################################################
	# Command-Specific Checks                                 #
    ###########################################################

	# Check input data for each option
	if (options_command):

		# Check for duplicate options
		if (user_options[0] == user_options[1]):
			print('Error: Duplicate option supplied')
			return serialObj

		# Perform option specific checks
		for user_option in user_options:

			################# -b option #######################
			if (user_option == '-b'):
				# Check byte is formatted correctly
				# Format: 0xXX --> XX is a hex number

				# Check length
				if(len(user_inputs[user_option]) != 4):
					print('Error: Invalid byte format.')
					return serialObj
				
				# Check for 0x prefix
				if(user_inputs[user_option][0:2] != '0x'):
					print("Error: Invalid byte format. " +
                          " Missing 0x prefix")

				# Convert to integer
				try:
					byte_int = int(user_inputs[user_option], 0)
				except ValueError:
					print('Error: Invalid byte.')
					return serialObj

				# Convert to byte
				byte = byte_int.to_bytes(1, 'big')
				

			################# -s option #######################
			elif (user_option == '-s'):
				# Currently no parse checks needed
				pass

			################# -n option #######################
			elif (user_option == '-n'):
				# Verify number of bytes is an integer
				# Verify numbers of bytes is in range
				pass

			################# -a option #######################
			elif (user_option == '-a'):
				# Check address is formatted correctly
				# Format: 0xXXXXXX

				# Check length
				if(len(user_inputs[user_option]) != 8):
					print('Error: Invalid Address format.')
					return serialObj
				
				# Check for 0x prefix
				if(user_inputs[user_option][0:2] != '0x'):
					print("Error: Invalid byte format. " +
                          " Missing 0x prefix")

				# Convert to integer
				try:
					address_int = int(user_inputs[user_option], 0)
				except ValueError:
					print('Error: Invalid Address.')
					return serialObj

				# Convert to bytes
				address_bytes = address_int.to_bytes(
                                                    3, 
                                                    byteorder='big',
                                                    signed=False
                                                    )

			################# -f option #######################
			elif (user_option == '-f'):
				# Verify output file doesn't already exist 
				# Verify input file exists
				pass

		# Verify read and write subcommands have an address supplied	
		if (   user_subcommand == 'write' 
			or user_subcommand == 'read'):
			if ('-a' not in user_options):
				print('Error: The write and read operations ' +
					  'require an address supplied by the '   +
					  '-a option')
				return serialObj

	# Verify Engine Controller Connection
	if (not (serialObj.controller in supported_boards)):
		print("Error: The flash command requires a valid " + 
			  "serial connection to an engine controller "  + 
			  "device. Run the \"connect\" command to "     +
			  "establish a valid connection.")
		return serialObj

	###########################################################
	# Subcommand: flash help                                  #
    ###########################################################
	if (user_subcommand == "help"):
		display_help_info('flash')
		return serialObj

	###########################################################
	# Subcommand: flash enable                                #
    ###########################################################
	elif (user_subcommand == "enable"):

		# Send the flash Opcode
		serialObj.sendByte(opcode)

		# Send the subcommand Opcode
		serialObj.sendByte(flash_enable_base_code)

		# Recieve the status byte from the engine controller
		return_code = serialObj.readByte()

		# Parse return code
		if (return_code == b''):
			print("Error: No response code recieved")
		elif (return_code == b'\x00'):
			print("Flash write enable successful")
			serialObj.flash_write_enabled = True
		else:
			print("Error: Unrecognised response code recieved")
		

		return serialObj

	###########################################################
	# Subcommand: flash disable                               #
    ###########################################################
	elif (user_subcommand == "disable"):

		# Send the flash opcode
		serialObj.sendByte(opcode)

		# Send the subcommand opcode
		serialObj.sendByte(flash_disable_base_code)

		# Recieve the status byte from the engine controller
		return_code = serialObj.readByte()

		# Parse return code
		if (return_code == b''):
			print("Error: No response code recieved")
		elif (return_code == b'\x00'):
			print("Flash write disable successful")
			serialObj.flash_write_enabled = False 
		else:
			print("Error: Unrecognised response code recieved")

		return serialObj

	###########################################################
	# Subcommand: flash status                                #
    ###########################################################
	elif (user_subcommand == "status"):

		# Send the flash opcode
		serialObj.sendByte(opcode)

		# Send the subcommand opcode
		serialObj.sendByte(flash_status_base_code)

		# Recieve the contents of the flash status register 
		status_register     = serialObj.readByte()
		status_register_int = ord( status_register     )

		# Get the status code of the flash operation
		flash_status_code = serialObj.readByte()

		# Parse return code
		if (status_register == b''):
			print("Error: No response recieved from engine " +
                  "controller")
		else:
			print("Status register contents: ", end="")
			print( format( status_register_int, "b" ).zfill(8) )

		return serialObj

	###########################################################
	# Subcommand: flash write                                 #
    ###########################################################
	elif (user_subcommand == "write"):

		# Check if flash chip has writing operations enabled
		if (not serialObj.flash_write_enabled
            and not (user_options[0] == '-h')):
			print("Error: Flash write has not been enabled."  +
                  "Run flash write enable to enable writing " +
                  "to the flash chip")
			return serialObj

	    ################### -h option #########################
		if (user_options[0] == '-h'):
			display_help_info('flash')
			return serialObj

	    ################### -b option #########################
		elif (byte != None):
			# Send flash opcode
			serialObj.sendByte(opcode)

			# Calculate operation code
			num_bytes_to_send = 1
			operation_code_int = (flash_write_base_code_int + 
                                 num_bytes_to_send)
			operation_code = operation_code_int.to_bytes(
								   1, 
					               byteorder = 'big',
								   signed = False
                                   ) 

			# Send flash operation code
			serialObj.sendByte(operation_code)
			
			# Send base address
			serialObj.sendBytes(address_bytes)

			# Send byte to write to flash
			serialObj.sendBytes(byte)

			# Recieve response code from engine controller
			return_code = serialObj.readByte()

			# Parse return code
			if (return_code == b''):
				print("Error: No response code recieved")
			elif (return_code == b'\x00'):
				print("Flash write successful")
			else:
				print("Error: Unrecognised response code recieved")

			return serialObj

	    ################### -s option #########################
		elif (string != None):
			print("Error: Option not yet supported")
			return serialObj

	    ################### -f option #########################
		elif (file != None):
			print("Error: Option not yet supported")
			return serialObj
		
	    ################# Unknown option #####################
		else:
			print("Error: Something went wrong. The flash "+ 
                  "write command failed to find input "    +
                  "to write to flash")
			return serialObj


	###########################################################
	# Subcommand: flash read                                  #
    ###########################################################
	elif (user_subcommand == "read"):
		# TODO: Implement read subcommand and remove error
        #       message
		print("Error: The read subcommand has not yet been "+
              "implemented. Try again later.")
		return serialObj

		# Option: -h                                          
		if (user_option == '-h'):
			display_help_info('flash')
			return serialObj

		# Option: -n                                          
		elif(user_option == '-n'):
			# Send solenoid opcode
			# Send subcommand code
			return serialObj


	###########################################################
	# Subcommand: flash erase                                 #
    ###########################################################
	elif (user_subcommand == "erase"):
		# TODO: Implement erase subcommand and remove error
        #       message
		print("Error: The erase subcommand has not yet been "+
			  "implemented. Try again later.")
		return serialObj
		# Send solenoid opcode
		# Send subcommand code
		return serialObj

    ###########################################################
    # Unknown Option                                          #
    ###########################################################
	else:
		print("Error: unknown option passed to connect function")	
		error_msg()
		return serialObj

###############################################################
# END OF FILE                                                 #
###############################################################
