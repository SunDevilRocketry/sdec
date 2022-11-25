############################################################### 
#                                                             # 
# Commands.py -- module with general command line functions   # 
# Author: Colton Acosta                                       # 
# Date: 4/16/2022                                             #
# Sun Devil Rocketry Avionics                                 #
#                                                             #
###############################################################


###############################################################
# Standard Imports                                            # 
###############################################################
import sys
import os
import serial.tools.list_ports
import time


###############################################################
# Global Variables                                            #
###############################################################
default_timeout = 0.1 # 1 second timeout
controller_codes = [ 
                  b'\x01', # Engine Controller, Rev 3.0
                  b'\x02', # Valve Controller , Rev 2.0 
                  b'\x03', # Engine Controller, Rev 4.0 
				  b'\x04'  # Flight Computer,   Rev 1.0
                   ]
controller_names = [
                   "Liquid Engine Controller (L0002 Rev 3.0)",
                   "Valve Controller (L0005 Rev 2.0)"        ,
                   "Liquid Engine Controller (L0002 Rev 4.0)",
				   "Flight Computer (A0002 Rev 1.0)"
                   ]
controller_descriptions = {
                  b'\x01': "Liquid Engine Controller (L0002 Rev 3.0)",
                  b'\x02': "Valve Controller (L0005 Rev 2.0)"        ,
                  b'\x03': "Liquid Engine Controller (L0002 Rev 4.0)",
				  b'\x04': "Flight Computer (A0002 Rev 1.0)"
                          }
controller_sensors = {
                  # Engine Controller rev 4.0
                  controller_names[2]: {
						   "pt0": "Pressure Transducer 0",
						   "pt1": "Pressure Transducer 1",
						   "pt2": "Pressure Transducer 2",
						   "pt3": "Pressure Transducer 3",
						   "pt4": "Pressure Transducer 4",
						   "pt5": "Pressure Transducer 5",
						   "pt6": "Pressure Transducer 6",
						   "pt7": "Pressure Transducer 7",
						   "tc ": "Theromcouple         ",
						   "lc ": "Load Cell            "            
                           }
                     }


###############################################################
# Shared Procedures                                           #
###############################################################


###############################################################
#                                                             #
# PROCEDURE:                                                  #
# 		get_bit                                               #
#                                                             #
# DESCRIPTION:                                                #
# 		extracts a specific bit from an integer               #
#                                                             #
###############################################################
def get_bit( num, bit_index ):
	if ( num & ( 1 << bit_index ) ):
		return 1
	else:	
		return 0


###############################################################
#                                                             #
# PROCEDURE:                                                  #
# 		display_help_info                                     #
#                                                             #
# DESCRIPTION:                                                #
# 		displays a command's help info from its doc file      #
#                                                             #
###############################################################
def display_help_info( command ):
	with open ("doc/" + command ) as file:
		doc_lines = file.readlines()
	print()
	for line in doc_lines:
		print( line, end='' )
	print()


###############################################################
#                                                             #
# PROCEDURE:                                                  #
# 		error_msg                                             #
#                                                             #
# DESCRIPTION:                                                #
# 		displays a general software failure error message     #
#                                                             #
###############################################################
def error_msg():
	print( "Something went wrong. Report this issue to " + 
              "the Sun Devil Rocketry development team" )	


###############################################################
#                                                             #
# PROCEDURE:                                                  #
# 		adc_readout_to_voltage                                #
#                                                             #
# DESCRIPTION:                                                #
# 		displays a general software failure error message     #
#                                                             #
###############################################################
def adc_readout_to_voltage( 
                          readout, # ADC readout
                          num_bits # number of bits in ADC readout
                          ):
	voltage_step = 3.3/float(2**(num_bits))
	return readout*voltage_step 


###############################################################
#                                                             #
# PROCEDURE:                                                  #
# 		parseArgs                                             #
#                                                             #
# DESCRIPTION:                                                #
# 		runs basic checks on command inputs and outputs a     #
#       boolean indicating if the user input passes the       #
#       checks                                                #
#                                                             #
###############################################################
def parseArgs(
             Args,          # function arguments
			 max_num_Args,  # maximum number of function arguments
             Args_dic,      # dictionary of supported inputs
             command_type,  # indicates if command has subcommands
             ):

	###########################################################
	# Local Variables                                         #
	###########################################################

	# Error code returns
	parse_pass = True
	parse_fail = False

	# subcommand support
	if ( command_type == 'subcommand' ):
		subcommand_func = True
	else:
		subcommand_func = False


	###########################################################
	# Input Tests                                             #
	###########################################################

	# No Subcommands/Options
	if ( subcommand_func ):
		if ( len(Args) == 0 ): # no subcommand
			print( 'Error: No subcommand supplied. Valid ' +
                   'subcommands include: ' )
			for subcommand in Args_dic:
				print( '\t' + subcommand )
			print()
			return parse_fail
		user_subcommand = Args[0]
	else:
		if ( len(Args) == 0 ): # no options
			print( 'Error: No options supplied. Valid ' +
                   'options include: ' )
			for option in Args_dic:
				print( '\t' + option + '\t' + Args_dic[option] ) 
			print()
			return parse_fail
		user_option = Args[0]

	# Too Many Inputs
	if ( len(Args) > max_num_Args ): 
		print( 'Error: To many inputs.' )
		return parse_fail

	# Unrecognized Subcommand
	if ( subcommand_func ):
		if ( not (user_subcommand in Args_dic) ): 
			print('Error: Unrecognized subcommand. Valid ' +
                  'subcommands include: ')
			for subcommand in Args_dic:
				print( '\t' + subcommand )
			print()
			return parse_fail
		num_options = len( Args_dic[user_subcommand] )
		# No option supplied after subcommand
		if ( (len(Args) == 1) and (num_options != 0) ):
			print( 'Error: No options supplied. Valid ' +
                   'options include: ' )
			for option in Args_dic[user_subcommand]:
				print( '\t' + option + '\t' + 
                       Args_dic[user_subcommand][option] ) 
			print()
			return parse_fail
		# Subcommand valid, exit if subcommand has no options
		if ( num_options == 0 ):
			return parse_pass
		else: 
			# Organize user options into a list
			user_options = []
			for arg in Args[1:]:
				if ( '-' in arg ):
					user_options.append(arg)
			

	# Unrecognized Option	
	if ( subcommand_func ): #subcommand supported
		for user_option in user_options:	
			if ( not(user_option in Args_dic[user_subcommand]) ): 
				print( 'Error: Unrecognized option. Valid ' +
                       'options include: ')
				for option in Args_dic[user_subcommand]:
					print( '\t' + option + '\t' + 
                           Args_dic[user_subcommand][option] ) 
				print()
				return parse_fail
	else: # subcommand not supported 
		if ( not(user_option in Args_dic) ): 
			print( 'Error: Unrecognized option. Valid ' +
                   'options include: ' )
			for option in Args_dic:
				print( '\t' + option + '\t' + Args_dic[option] ) 
			print()
			return parse_fail

	# User input passes all checks	
	return parse_pass


###############################################################
# Commands                                                    #
###############################################################


###############################################################
#                                                             #
# COMMAND:                                                    #
# 		exit                                                  #
#                                                             #
# DESCRIPTION:                                                #
# 		quits the program                                     #
#                                                             #
###############################################################
def exitFunc(Args, serialObj):
   sys.exit()


###############################################################
#                                                             #
# COMMAND:                                                    #
# 		help                                                  #
#                                                             #
# DESCRIPTION:                                                #
# 		displays command info from manpage                    #
#                                                             #
###############################################################
def helpFunc(Args, serialObj):
    display_help_info('manpage')
    return serialObj 
    

###############################################################
#                                                             #
# COMMAND:                                                    #
# 		clear                                                 #
#                                                             #
# DESCRIPTION:                                                #
# 		clears the python terminal                            #
#                                                             #
###############################################################
# clearConsole -- clears the python terminal
def clearConsole(Args, serialObj):
    command = 'clear'
    if os.name in ('nt', 'dos'):
        command = 'cls'
    os.system(command)
    return serialObj 


###############################################################
#                                                             #
# COMMAND:                                                    #
# 		comports                                              #
#                                                             #
# DESCRIPTION:                                                #
# 		connects to a USB device or displays connectivity     #
#       info                                                  #
#                                                             #
###############################################################
def comports(Args, serialObj):

	###########################################################
	# local variables                                         #
    ###########################################################

	# Options Dictionary
	comports_inputs = { 
					   '-h' : 'Display help info',
					   '-l' : 'List available serial ports',
					   '-c' : 'Connect to a serial port',
					   '-d' : 'Disconnect from a serial port'
                      }
    
	# Maximum number of arguments
	max_args = 3

	# Command type -- subcommand function
	command_type = 'default'

	###########################################################
	# Basic inputs parsing                                    #
    ###########################################################
	parse_check = parseArgs(
                            Args,
                            max_args,
                            comports_inputs,
                            command_type 
                           )
	if ( not parse_check ):
		return serialObj # user inputs failed parse tests

	###########################################################
	# Command Specific Parsing                                #
    ###########################################################
	option            = Args[0]
	port_supplied     = False
	baudrate_supplied = False

	# Set variables if they exist 
	if ( len(Args) >= 2 ):
		target_port   = Args[1]
		port_supplied = True

	# Check for valid baudrate
	if ( len(Args) == 3 ):
		try: 
			baudrate = int( Args[2] )
			baudrate_supplied = True
		except ValueError:
			print( "Error: invalid baudrate. Check that the " +
                  "baudrate is in bits/s and is an integer" )
			return serialObj

    ###########################################################
    # List Option (-l)                                        #
    ###########################################################
	if ( option == "-l" ):

		avail_ports = serial.tools.list_ports.comports()
		print( "\nAvailable COM ports: " )
		for port_num,port in enumerate( avail_ports ):
			print( "\t" + str(port_num) + ": " + port.device + 
                   " - ", end="" ) 
			if ( port.manufacturer != None ):
				print( port.manufacturer + ": ", end="" )
			if ( port.description  != None ):
				print( port.product )
			else:
				print( "device info unavailable" )
		print()
		return serialObj

    ###########################################################
    # Help Option (-h)                                        #
    ###########################################################
	elif ( option == "-h" ):
		display_help_info( 'comports' )
		return serialObj

    ###########################################################
    # Connect Option (-c)                                     #
    ###########################################################
	elif ( option == "-c" ):
		# Check that port has been supplied
		if   ( not port_supplied     ):
			print( "Error: no port supplied to comports " +
                   "function" )
			return serialObj

		# Check that baudrate has been supplied
		elif ( not baudrate_supplied ):
			print( "Error: no baudrate supplied to comports " +
                   "function" )
			return serialObj

		# Check that inputed port is valid
		avail_ports = serial.tools.list_ports.comports()
		avail_ports_devices = []
		for port in avail_ports:
			avail_ports_devices.append(port.device)
		if ( not (target_port in avail_ports_devices) ):
			print( "Error: Invalid serial port\n" )
			comports( ["-l"] )
			return serialObj

		# Initialize Serial Port
		serialObj.initComport(
                             baudrate, 
                             target_port, 
                             default_timeout
                             )

		# Connect to serial port
		connection_status = serialObj.openComport()
		if( connection_status ):
			print( "Connected to port " + target_port + 
                   " at " + str(baudrate) + " baud" )

		return serialObj

    ###########################################################
    # Disconnect Option (-d)                                  #
    ###########################################################
	elif ( option == "-d" ):
		connection_status = serialObj.closeComport()
		if ( connection_status ):
			print( "Disconnected from active serial port" )
			return serialObj
		else: 
			print( "An error ocurred while closing port " + 
                   target_port )
			return serialObj

	return serialObj


###############################################################
#                                                             #
# COMMAND:                                                    #
# 		ping                                                  #
#                                                             #
# DESCRIPTION:                                                #
# 		transmit a byte over an active USB connection and     #
#       await response from board                             #
#                                                             #
###############################################################
def ping( Args, serialObj ):

    # Check for an active serial port connection and valid 
    # options/arguments
    if ( not serialObj.serialObj.is_open ):
        print( "Error: no active serial port connection. "  +
               "Run the comports -c command to connect to " +
               "a device" )
        return serialObj
    if   ( len(Args) < 1 ):
        print("Error: no options supplied to ping function")
        return serialObj
    elif ( len(Args) > 2 ):
        print( "Error: too many options/arguments supplied " +
               "to ping function" )
    else:

        # Arguments parsing
        option = Args[0]
        timeout_supplied = False
        if ( len(Args) == 2 ):
            try:
                input_timeout = float( Args[1] )
                timeout_supplied = True
            except ValueError:
                print( "Error: Invalid ping timeout." )
                return serialObj

        # Help option
        if ( option == "-h" ):
            display_help_info( 'ping' )
            return serialObj

        # Ping option
        elif ( option == "-t" ):
            # Check for valid serial port connection
            if ( not serialObj.serialObj.is_open ):
                print( "Error: no active serial port "    +
                       "connection. Run the comports -c " +
                       "command to connect to a device" )
                return serialObj

            # Set timeout
            serialObj.timeout = input_timeout
            serialObj.configComport()

            # Ping
            opcode = b'\x01'
            ping_start_time = time.time()
            serialObj.sendByte( opcode )
            print( "Pinging ..." )
            pingData = serialObj.serialObj.read()
            if ( pingData == b'' ):
                print( "Timeout expired. No device " +
                       "response recieved." )
            else:
                ping_recieve_time = time.time()
                ping_time = ping_recieve_time - ping_start_time
                ping_time *= 1000.0
                if ( pingData in controller_codes ):
                    print( 
                           ("Response recieved at {0:1.4f} ms " +
                            "from {1}").format(
                                ping_time, 
                                controller_descriptions[pingData]
                                              )
                         )
                else:
                    print( 
                           ("Response recieved at {0:1.4f} ms " +
                           "from an unknown device").format(
                                                           ping_time
                                                           )
                         )
            return serialObj

        # Ping option 
        else:
            print("Error: invalid option supplied to ping function")
            return serialObj


###############################################################
#                                                             #
# COMMAND:                                                    #
# 		connect                                               #
#                                                             #
# DESCRIPTION:                                                #
# 		establish a serial connection with an SDR board       #
#                                                             #
###############################################################
def connect(Args, serialObj):
	###########################################################
	# local variables                                         #
    ###########################################################
	opcode = b'\x02'

	# Options Dictionary
	connect_inputs = { 
					   '-h' : 'Display help info',
					   '-p' : 'Specify the connection serial port',
					   '-d' : 'Disconnect from active serial port'
                      }
    
	# Maximum number of arguments
	max_args = 2

	# Command type -- subcommand function
	command_type = 'default'

	###########################################################
	# Basic inputs parsing                                    #
    ###########################################################
	parse_check = parseArgs(
                            Args,
                            max_args,
                            connect_inputs,
                            command_type 
                           )
	if ( not parse_check ):
		return serialObj # user inputs failed parse tests
	user_option = Args[0]
	if ( len(Args) > 1 ):
		user_port = Args[1]

	###########################################################
	# Command-Specific Inputs Parsing                         #
    ###########################################################
	# Check if there is an active serial port
	if ( serialObj.is_active() and user_option == '-p' ):
		print("Error: Serial port " + serialObj.comport + 
               "is active. Disconnect from the active" +
               " serial port before connecting" )
		return serialObj	
	elif ( (not serialObj.is_active()) and user_option == '-d' ):
		print( 'Error: No active serial port to disconnect from' )
		return serialObj

	# Check for valid serial port
	if ( len(Args) > 1 ):
		available_ports = serialObj.list_ports()
		if ( not (user_port in available_ports) ):
			print( "Error: Invalid serial port. Valid ports:" )
			for port_num, port in enumerate( available_ports ):
				print( "\t" + port )
			return serialObj
	else:
		if ( user_option == '-p' and
		     len(Args)   == 1):
			print( "Error: No serial port supplied " )
			return serialObj

    ###########################################################
    # Help Option (-h)                                        #
    ###########################################################
	if ( user_option == '-h' ):
		display_help_info( "connect" )
		return serialObj

    ###########################################################
    # Port Option (-p)                                        #
    ###########################################################
	elif ( user_option == '-p' ):
		serialObj = comports(
                            ['-c', user_port, '9600'], 
                            serialObj
                            )
		serialObj.sendByte( opcode )
		controller_response = serialObj.readByte()
		if ( (controller_response == b''                    ) or
             (not (controller_response in controller_codes) ) ):
			print( "Controller connection was unsuccessful." )
			serialObj = comports( ['-d'], serialObj )
			return serialObj
		else:
			print( "Connection established with " + 
                    controller_descriptions[controller_response] )
			serialObj.set_SDR_controller(
                     controller_descriptions[controller_response]
                                        )
			return serialObj
		

    ###########################################################
    # Disconnect Option (-d)                                  #
    ###########################################################
	elif ( user_option == '-d' ):
		serialObj = comports( ['-d'], serialObj )
		serialObj.reset_SDR_controller()
		return serialObj

    ###########################################################
    # Unknown Option                                          #
    ###########################################################
	else:
		print( "Error: unknown option passed to connect " +
               "function" )	
		error_msg()
		return serialObj


###############################################################
#                                                             #
# COMMAND:                                                    #
# 		sensor                                                #
#                                                             #
# DESCRIPTION:                                                #
# 		Displays sensor data and/or info                      #
#                                                             #
###############################################################
def sensor( Args, serialObj ):

    ###########################################################
    # Local Variables                                         #
    ###########################################################

	# Subcommand and Options Dictionary
    sensor_inputs = {
					'dump' : {
                             },
                    'poll' : {
                             '-n' : 'Specify a sensor number',
                             '-h' : 'Display sensor usage info'
                             },
                    'list' : {
                             },
                    'help' : {
                             }
                    }

    # Maximum number of args
    max_args = 7

	# Command type -- subcommand function
    command_type = 'subcommand'

	# Command opcode 
    opcode = b'\x03'

    # Subcommand codes
    subcommand_codes = {
                       'dump' : b'\x01',
                       'poll' : b'\x02'
                       }

    # Lists of sensor data
    sensor_bytes_list = []
    sensor_int_list   = []

    ###########################################################
    # Basic Inputs Parsing                                    #
    ###########################################################
    parse_check = parseArgs(
                           Args,
                           max_args,
                           sensor_inputs,
                           command_type
                           )

	# Return if user input fails parse checks
    if ( not parse_check ):
        return serialObj

	# Set subcommand, options, and input data
    user_subcommand = Args[0]
    if ( len(Args) != 1 ):
        
        # Extract option
        user_option = Args[1]

		# Extract inputs
        user_sensor_nums = Args[2:]

	# Verify connection to board with sensors
    if ( not (serialObj.controller in controller_sensors.keys()) ):
        print( "Error: The sensor command requires a valid " +
               "serial connection to a controller with "     +
               "sensors. Run the \"connect\" command to "    +
               "establish a valid connection" )
        return serialObj

    ###########################################################
    # Command-Specific Checks                                 #
    ###########################################################


	# Verify sensor nums supplied are valid
    if ( user_subcommand == "poll" ):
        if ( user_option == "-n" ):

			# Throw error if no sensors were supplied
            if ( len(user_sensor_nums) == 0 ):
                print( "Error: no sensor numbers supplied" )

            # Loop over input sensors and validity of each
            for sensor_num in user_sensor_nums:
                if ( not (sensor_num in 
                          controller_sensors[serialObj.controller].keys())
                   ):
                    print("Error: \"" + sensor_num + "\" is "  +
                          "is not a valid sensor for "         +
                          serialObj.controller + ". Run "      +
                          "the \"sensor list\" subcommand to " +
                          "see a list of all available "       +
                          "sensors and their corresponding "   +
                          "codes." )
                    return serialObj

    ###########################################################
    # Subcommand: sensor help                                 #
    ###########################################################
    if   ( user_subcommand == "help" ):
        display_help_info( "sensor" )
        return serialObj

    ###########################################################
    # Subcommand: sensor dump                                 #
    ###########################################################
    elif ( user_subcommand == "dump" ):

        # Send command opcode 
        serialObj.sendByte( opcode )

		# Send sensor dump subcommand code
        serialObj.sendByte( subcommand_codes[user_subcommand] )

		# Determine how many bytes are to be recieved
        sensor_dump_size_bytes = serialObj.readByte()
        sensor_dump_size_bytes = int.from_bytes( 
                                     sensor_dump_size_bytes, 
                                     "big" )

        # Recieve data from controller
        for byteNum in range( sensor_dump_size_bytes ):
            sensor_bytes_list.append( serialObj.readByte() )

        # Loop over all sensors in list and print
        for i,sensor_num in enumerate( controller_sensors[serialObj.controller].keys() ):
            sensor_val = 0
            for j in range(4): # Hex to integer conversion
                sensor_val += ( int.from_bytes( sensor_bytes_list[4*i + j], 'big') << 8*(3-j) )
            sensor_val = adc_readout_to_voltage( sensor_val, 16 )
            sensor_int_list.append( sensor_val )
            print(     
                 controller_sensors[serialObj.controller][sensor_num] + 
				 ": " + "{:.2f}".format(sensor_val) + "V"
                 ) 

        return serialObj

    ###########################################################
    # Subcommand: sensor poll                                 #
    ###########################################################
    elif ( user_subcommand == "poll" ):
        print( "Error: sensor poll has not yet been added " +
               "to the sdec terminal by SDR developers. "   + 
               "Try again later or contact SDR for assistance" )
        return serialObj

    ###########################################################
    # Subcommand: sensor list                                 #
    ###########################################################
    elif ( user_subcommand == "list" ):
        # Identify current serial connection
        print("Sensor numbers for " + serialObj.controller +
               " :" )

        # Loop over all sensors in list and print
        for sensor_num in controller_sensors[serialObj.controller].keys():
            print( "\t" + sensor_num + " : " +
                    controller_sensors[serialObj.controller][sensor_num] 
                 ) 
        return serialObj

    ###########################################################
    # Unknown subcommand                                      #
    ###########################################################
    else:
        print( "Error: Unknown subcommand passed to sensor " +
               "function. " )
        error_msg()
        return serialObj


###############################################################
#                                                             #
# COMMAND:                                                    #
# 		flash                                                 #
#                                                             #
# DESCRIPTION:                                                #
# 		read and write data to a controller's extenral flash  #
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
	max_num_bytes = 31

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

	# flash IO data
	byte            = None
	string          = None
	file            = None
	num_bytes       = None

	# Flash status register contents 
	status_register = None

	# Supported flash boards
	flash_supported_boards = [
                   "Liquid Engine Controller (L0002 Rev 4.0)",
				   "Flight Computer (A0002 Rev 1.0)"
							 ]


	###########################################################
	# Basic Inputs Parsing                                    #
    ###########################################################
	parse_check = parseArgs(
                            Args        ,
                            max_args    ,
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
				try:
					num_bytes = int(user_inputs[user_option], 0)
				except ValueError:
					print('Error: Invalid number of bytes.')
					return serialObj

				# Verify numbers of bytes is in range
				if ( num_bytes <= 0 or num_bytes > max_num_bytes ): 
					print( "Error: Invalid number of bytes." )
					return serialObj

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
	if (not (serialObj.controller in flash_supported_boards) ):
		print("Error: The flash command requires a valid " + 
			  "serial connection to a controller with \n"    + 
			  "external flash. This includes the following " +
		      "boards: \n" )
		for board in flash_supported_boards:
			print( board )
		print()
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
			print("Status register contents: \n") 
			print( "BUSY: ", get_bit( status_register_int, 0 ) )
			print( "WEL : ", get_bit( status_register_int, 1 ) )
			print( "BP0 : ", get_bit( status_register_int, 2 ) )
			print( "BP1 : ", get_bit( status_register_int, 3 ) )
			print( "BP2 : ", get_bit( status_register_int, 4 ) )
			print( "BP3 : ", get_bit( status_register_int, 5 ) )
			print( "AAI : ", get_bit( status_register_int, 6 ) )
			print( "BPL : ", get_bit( status_register_int, 7 ) )
			print( )

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
			serialObj.sendByte(byte)

			# Recieve response code from engine controller
			return_code = serialObj.readByte()

			# Parse return code
			if (return_code == b''):
				print("Error: No response code recieved")
			elif ( return_code == b'\x00' ):
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

	    ################### -h option #########################
		if (user_options[0] == '-h'):
			display_help_info('flash')
			return serialObj

	    ################### -n option #########################
		elif( num_bytes != None ):

			# Send flash opcode
			serialObj.sendByte(opcode)

			# Calculate operation code
			operation_code_int = ( flash_read_base_code_int + 
                                 num_bytes )
			operation_code = operation_code_int.to_bytes(
								   1, 
					               byteorder = 'big',
								   signed = False
                                   ) 

			# Send flash operation code
			serialObj.sendByte(operation_code)
			
			# Send base address
			serialObj.sendBytes(address_bytes)

			# Receive Bytes into a byte array
			rx_bytes = []
			for i in range( num_bytes ):
				rx_bytes.append( serialObj.readByte() )

			# Get flash status code
			flash_read_status = serialObj.readByte() 
			if ( flash_read_status != b'\x00' ):
				print( "Error: Flash Read Unsuccessful" )

			# Display Bytes on the terminal
			print( "Received bytes: \n" )
			for rx_byte in rx_bytes:
				print( rx_byte, ", ", end = "" )
			print()

			return serialObj

	    ################### -f option #########################
		elif( file!= None ):
			print("Error: Option not yet supported")
			return serialObj


	###########################################################
	# Subcommand: flash erase                                 #
    ###########################################################
	elif (user_subcommand == "erase"):
		
		# Send flash opcode 
		serialObj.sendByte( opcode )

		# Send flash erase subcommand code 
		serialObj.sendByte( flash_erase_base_code )

		# Get and Display status of flash erase operation
		flash_erase_status = serialObj.readByte()
		if ( flash_erase_status == b'\x00'):
			print( "Flash erase sucessful" )
		else:
			print( "Error: Flash erase unsuccessful" )

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
