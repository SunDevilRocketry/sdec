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
default_timeout = 1 # 1 second timeout
controller_codes = [ 
                  b'\x01', # Engine Controller, Rev 3.0
                  b'\x02', # Valve Controller , Rev 2.0 
                  b'\x03'  # Engine Controller, Rev 4.0 
                      ]
controller_names = [
                   "Liquid Engine Controller (L0002 Rev 3.0)",
                   "Valve Controller (L0005 Rev 2.0)"        ,
                   "Liquid Engine Controller (L0002 Rev 4.0)"
                   ]
controller_descriptions = {
                  b'\x01': "Liquid Engine Controller (L0002 Rev 3.0)",
                  b'\x02': "Valve Controller (L0005 Rev 2.0)",
                  b'\x03': "Liquid Engine Controller (L0002 Rev 4.0)"
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
						   "tc ": "Theromcouple"         ,
						   "lc ": "Load Cell"            
                           }
                     }

sensor_dump_sizes = {
                    # Engine Controller rev 4.0
                    # 10 sensors, 2 bytes each
                    controller_names[2]: (2*10)
                    }


###############################################################
# Shared Procedures                                           #
###############################################################


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

    # List of bytes containing sensor data
    sensor_bytes_list = []

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

    # Set sensor dump size
    sensor_dump_size_bytes = sensor_dump_sizes[serialObj.controller]
    

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
        serialObj.sendBye( subcommand_codes[user_subcommand] )

        # Recieve data from controller
        for byteNum in range( sensor_dump_size_bytes ):
            sensor_bytes_list.append( serialObj.readByte() )

        # print data to console
        print( "Sensor bytes" )
        for byte in sensor_bytes_list:
            print( byte, end="" )
            print( ", ", end="" )
        print()

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
# END OF FILE                                                 # 
###############################################################
