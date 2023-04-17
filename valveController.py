#################################################################################### 
#                                                                                  #
# valveController.py -- module with valve controller specific command line         #
#                       functions                                                  # 
# Author: Colton Acosta                                                            #
# Date: 4/16/2022                                                                  #
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
from   config   import *


#################################################################################### 
# Global Variables                                                                 #
#################################################################################### 

# Compatible Boards
supported_boards = [ "Valve Controller (L0005 Rev 2.0)"       ,
                     "Valve Controller (L0005 Rev 3.0)"       ,
                     "Liquid Engine Controller (L0002 Rev 4.0)" ]

# Name and description of each solenoid
solenoid_names = {
				"oxPress"  : "LOX Pressurization" ,
				"fuelPress": "Fuel Pressurization",
				"oxPurge"  : "LOX-side Purge"     ,
				"fuelPurge": "Fuel-side Purge"    ,
				"oxVent"   : "LOX Vent Valve"     ,
				"fuelVent" : "Fuel Vent Valve"
                 }

# Numbers assigned to each solenoid
solenoid_nums = {
				"oxPress"  : 1,
				"fuelPress": 2,
				"oxPurge"  : 5,
				"fuelPurge": 6,
				"oxVent"   : 3,
				"fuelVent" : 4 
                }

# Solenoid on/off states
solenoid_on_states = {
					"oxPress"  : "OPEN",
					"fuelPress": "OPEN",
					"oxPurge"  : "CLOSED",
					"fuelPurge": "CLOSED",
					"oxVent"   : "CLOSED",
					"fuelVent" : "CLOSED" 
                     }

solenoid_off_states = {
					"oxPress"  : "CLOSED",
					"fuelPress": "CLOSED",
					"oxPurge"  : "OPEN",
					"fuelPurge": "OPEN",
					"oxVent"   : "OPEN",
					"fuelVent" : "OPEN" 
                     }



####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		sol                                                                        #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		control the actuation state of solenoids                                   #
#                                                                                  #
#################################################################################### 
def sol(Args, serialObj):
	################################################################################
	# Local Variables                                                              #
	################################################################################

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
						 },
			    'list': {
				        },
				'getstate': {
				            },
			    'open': {
						'-h' : 'Display help info',
						'-n' : 'Specify a solenoid number'
						}, 
			    'close': {
						'-h' : 'Display help info',
						'-n' : 'Specify a solenoid number'
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
	sol_getstate_code    = b'\x20'
	sol_open_base_code   = b'\x28'
	sol_close_base_code  = b'\x30'

	# Subcommand codes as integers
	sol_on_base_code_int     = ord( sol_on_base_code     )
	sol_off_base_code_int    = ord( sol_off_base_code    )
	sol_toggle_base_code_int = ord( sol_toggle_base_code )
	sol_open_base_code_int   = ord( sol_open_base_code   )
	sol_close_base_code_int  = ord( sol_close_base_code  )


	################################################################################
	# Basic Inputs Parsing                                                         #
	################################################################################
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

	################################################################################
	# Command-Specific Checks                                                      #
	################################################################################
	if (options_command):
		if (user_option == '-n'):
			# No solenoid number entered
			if (len(Args) == 2):
				print('Error: No solenoid specified')
				return serialObj
			# Invalid solenoid
			if ( not Args[2] in solenoid_names ):
				print( "Error: Invalid Solenoid" )
				return serialObj

			# Solenoid number not a number
			try:
				user_solenoid = int( solenoid_nums[Args[2]] )
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

	################################################################################
	# Subcommand: sol help                                                         #
	################################################################################
	if (user_subcommand == "help"):
		commands.display_help_info('sol')
		return serialObj

	################################################################################
	# Subcommand: sol on                                                           #
	################################################################################
	elif (user_subcommand == "on"):
		# Option: -h                                          
		if (user_option == '-h'):
			commands.display_help_info('sol')
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

	################################################################################
	# Subcommand: sol off                                                          #
	################################################################################
	elif (user_subcommand == "off"):
		# Option: -h                                          
		if (user_option == '-h'):
			commands.display_help_info('sol')
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

	################################################################################
	# Subcommand: sol toggle                                                       #
	################################################################################
	elif (user_subcommand == "toggle"):
		# Option: -h                                          
		if (user_option == '-h'):
			commands.display_help_info('sol')
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

	################################################################################
	# Subcommand: sol reset                                                        #
	################################################################################
	elif (user_subcommand == "reset"):
		# Send solenoid opcode
		serialObj.sendByte(opcode)
		# Send subcommand code
		serialObj.sendByte(sol_reset_code)
		return serialObj


	################################################################################
	# Subcommand: sol list                                                         #
	################################################################################
	elif ( user_subcommand == "list" ):
		print( "Solenoid names:" )
		for solenoid in solenoid_names:
			print( "\t" + solenoid + ": " + solenoid_names[solenoid] )
		return serialObj
	

	################################################################################
	# Subcommand: sol getstate                                                     #
	################################################################################
	elif ( user_subcommand == "getstate" ):
		
		# Send solenoid opcode and subcommand
		serialObj.sendByte( opcode            )
		serialObj.sendByte( sol_getstate_code )

		# Get the state of the solenoids
		sol_state = serialObj.readByte()
		sol_state = ord( sol_state )

		# Parse results
		print( "Solenoid States:" )
		for solenoid in solenoid_nums:
			if ( sol_state & ( 1 << ( solenoid_nums[solenoid] - 1 ) ) ):
				print( "\t" + solenoid + ": " + solenoid_on_states[solenoid] )
			else:
				print( "\t" + solenoid + ": " + solenoid_off_states[solenoid] )
		return serialObj
	

	################################################################################
	# Subcommand: sol open                                                         #
	################################################################################
	elif ( user_subcommand == "open" ):
		# Option: -h                                          
		if (user_option == '-h'):
			commands.display_help_info('sol')
			return serialObj

		# Option: -n                                          
		elif(user_option == '-n'):
			# Send solenoid opcode
			serialObj.sendByte( opcode )
			# Send subcommand code
			sol_open_code_int = sol_open_base_code_int + user_solenoid
			sol_open_code = sol_open_code_int.to_bytes(1, 
                                                       byteorder = 'big',
                                                       signed = False)
			serialObj.sendByte( sol_open_code )
			return serialObj
	# sol open #
	

	################################################################################
	# Subcommand: sol close                                                        #
	################################################################################
	elif ( user_subcommand == "close" ):
		# Option: -h                                          
		if (user_option == '-h'):
			commands.display_help_info('sol')
			return serialObj

		# Option: -n                                          
		elif(user_option == '-n'):
			# Send solenoid opcode
			serialObj.sendByte( opcode )
			# Send subcommand code
			sol_close_code_int = sol_close_base_code_int + user_solenoid
			sol_close_code = sol_close_code_int.to_bytes(1, 
                                                         byteorder = 'big',
                                                         signed = False)
			serialObj.sendByte( sol_close_code )
			return serialObj
	# sol close #


	################################################################################
    # Unknown Option                                                               #
	################################################################################
	else:
		print("Error: unknown option passed to sol function")	
		commands.error_msg()
		return serialObj
## sol ##


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		valve                                                                      #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		control the actuation servo-actuated ball valves                           #
#                                                                                  #
#################################################################################### 
def valve( Args, serialObj ):
	################################################################################
	# Local Variables                                                              #
	################################################################################

	# Subcommand and Options Dictionary
	valve_inputs= { 
			   'enable'    : {
			                 },
			   'disable'   : {
			                 },
			   'open'      : {
						     '-n' : 'Specify a valve'
						     } ,
			   'close'     : {
						     '-n' : 'Specify a valve'
						     } , 
			   'crack'     : {
							 '-n' : "Specify a valve"
			                 },
			   'calibrate' : {
						     },
			   'reset'     : {
			                 },
			   'list'      : {
						     },
			   'help'      : {
						     }
                 }
    
	# Maximum number of arguments
	max_args = 3

	# Command type -- subcommand function
	command_type = 'subcommand'

	# Command opcode
	opcode = b'\x52' 

	# Subcommand codes
	valve_enable_code     = b'\x00'
	valve_disable_code    = b'\x02'
	valve_open_base_code  = b'\x04'
	valve_close_base_code = b'\x06'
	valve_calibrate_code  = b'\x08'
	valve_crack_base_code = b'\x0A'
	valve_reset_code      = b'\x10'

	# Subcommand codes as integers
	valve_open_base_code_int  = ord( valve_open_base_code  )
	valve_close_base_code_int = ord( valve_close_base_code )
	valve_crack_base_code_int = ord( valve_crack_base_code )

	# Valve names
	valve_names        = [ 'ox', 'fuel' ]
	valve_descriptions = {
                  'ox'  : "Oxidizer main valve ( LOX )",
				  'fuel': "Fuel main valve ( RP1 )"
	                     }
	
	# Valve numbers
	valve_nums = {
				 'ox'  : 0,
				 'fuel': 1
	             }

	################################################################################
	# Basic Inputs Parsing                                                         #
	################################################################################
	parse_check = commands.parseArgs(
                                    Args        ,
                                    max_args    ,
                                    valve_inputs,
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

	################################################################################
	# Command-Specific Checks                                                      #
	################################################################################
	if ( options_command ):
		if ( user_option == '-n' ):
			# No valve number entered
			if ( len( Args ) == 2 ):
				print('Error: No valve specified')
				return serialObj

			# Invalid valve name 
			user_valve = Args[2] 
			if ( not ( user_valve in valve_names ) ):
				print( "Error: Invalid valve name. Run the valve list command " +
				       "to see a list of valid valve names")
				return serialObj

	# Verify Valve Controller Connection
	if ( not ( serialObj.controller in supported_boards ) ):
		print("Error: The valve command requires a valid " + 
              "serial connection to a valve controller or engine controller " + 
              "device. Run the \"connect\" command to "  +
              "establish a valid connection.")
		return serialObj

	################################################################################
	# Pre-processing                                                               #
	################################################################################
	if ( user_subcommand == "open" ):
		subcommand_code_int = valve_open_base_code_int + valve_nums[ user_valve ]
		subcommand_code     = subcommand_code_int.to_bytes( 1                , 
		                                                    byteorder = 'big',
															signed    = False )
	elif ( user_subcommand == "close" ):
		subcommand_code_int = valve_close_base_code_int + valve_nums[ user_valve ]
		subcommand_code     = subcommand_code_int.to_bytes( 1                 , 
		                                                     byteorder = 'big',
															 signed    = False)
	elif ( user_subcommand == "crack" ):
		subcommand_code_int = valve_crack_base_code_int + valve_nums[ user_valve ]
		subcommand_code     = subcommand_code_int.to_bytes( 1                 , 
		                                                     byteorder = 'big',
															 signed    = False)
	

	################################################################################
	# Subcommand: valve help                                                       #
	################################################################################
	if ( user_subcommand == "help" ):
		commands.display_help_info('valve')
		return serialObj

	################################################################################
	# Subcommand: valve enable                                                     #
	################################################################################
	elif ( user_subcommand == "enable" ):

		# Send opcode
		serialObj.sendByte( opcode )

		# Send subcommand code
		serialObj.sendByte( valve_enable_code )
		return serialObj

	################################################################################
	# Subcommand: valve disable                                                    #
	################################################################################
	elif ( user_subcommand == "disable" ):

		# Send opcode
		serialObj.sendByte( opcode )

		# Send subcommand opcode 
		serialObj.sendByte( valve_disable_code )
		return serialObj	

	################################################################################
	# Subcommand: valve open/close/crack                                           #
	################################################################################
	elif ( ( user_subcommand == "open"  ) or
	       ( user_subcommand == "close" ) or
		   ( user_subcommand == "crack" ) ):

		# Send opcode
		serialObj.sendByte( opcode )

		# send subcommand code
		serialObj.sendByte( subcommand_code )
		return serialObj	


	################################################################################
	# Subcommand: valve calibrate                                                  #
	################################################################################
	elif ( user_subcommand == "calibrate" ):
		# Send Opcode
		serialObj.sendByte( opcode )

		# Send subcommand code
		serialObj.sendByte( valve_calibrate_code )
		return serialObj	
	

	################################################################################
	# Subcommand: valve reset                                                      #
	################################################################################
	elif ( user_subcommand == "reset" ):
		# Send Opcode
		serialObj.sendByte( opcode )

		# Send subcommand code
		serialObj.sendByte( valve_reset_code )
		return serialObj	


	################################################################################
	# Subcommand: valve list                                                       #
	################################################################################
	elif ( user_subcommand == "list" ):

		# Print out valve names
		print( "Servo actuated ball valve names:" )
		for valve in valve_names:
			print( "\t" + valve + " : " + valve_descriptions[valve] )
		return serialObj	

	################################################################################
    # Unknown Option                                                               #
	################################################################################
	else:
		print("Error: unknown option passed to valve function")	
		commands.error_msg()
		return serialObj

### END OF FILE ###