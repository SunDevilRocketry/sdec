#################################################################################### 
#                                                                                  # 
# hw_commands.py -- module with general command line functions with hardware       # 
#                   oriented functionality                                         #
#                                                                                  #
# Author: Colton Acosta                                                            # 
# Date: 12/18/2022                                                                 #
# Sun Devil Rocketry Avionics                                                      #
#                                                                                  #
#################################################################################### 


####################################################################################
# Imports                                                                          #
####################################################################################

# Standard imports
import sys
import os
import time
import numpy                    as np
from   matplotlib import pyplot as plt
import struct

# Project imports
import sensor_conv
import commands
from   config      import *
from   controller  import *
from sensor_plot import *
from datetime import datetime
import traceback

####################################################################################
# Global Variables                                                                 #
####################################################################################

if ( sdr_debug ):
    default_timeout = 100 # 100 second timeout
else:
    default_timeout = 1   # 1 second timeout


####################################################################################
# Shared Procedures                                                                #
####################################################################################


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         get_bit                                                                  #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         extracts a specific bit from an integer                                  #
#                                                                                  #
####################################################################################
def get_bit( num, bit_index ):
    if ( num & ( 1 << bit_index ) ):
        return 1
    else:    
        return 0
## get_bit ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         byte_array_to_int                                                        #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         Returns an integer corresponding the hex number passed into the function #
#       as a byte array. Assumes least significant bytes are first                 #
#                                                                                  #
####################################################################################
def byte_array_to_int( byte_array ):
    int_val   = 0 # Intermediate computation value
    result    = 0 # Final result integer
    num_bytes = len( byte_array )
    for i, byte in enumerate( byte_array ):
        int_val = int.from_bytes( byte, 'big')
        int_val = int_val << 8*i
        result += int_val
    return result
## byte_array_to_int ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         byte_array_to_float                                                      #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         Returns an floating point number corresponding the hex number passed     # 
#         into the function as a byte array. Assumes least significant bytes are   # 
#         first                                                                    #
#                                                                                  #
####################################################################################
def byte_array_to_float( byte_array ):
    # Check to NaN
    if ( byte_array == [b'\xFF', b'\xFF', b'\xFF', b'\xFF'] ):
        byte_array = [b'\x00', b'\x00', b'\x00', b'\x00']
    byte_array_joined = b''.join( byte_array )
    #input( byte_array )    
    return struct.unpack( 'f', byte_array_joined )[0]
## byte_array_to_float ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         get_raw_sensor_readouts                                                  #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         Converts an array of bytes into a dictionary containing the raw sensor   #
#       readouts in integer format                                                 #
#                                                                                  #
####################################################################################
def get_raw_sensor_readouts( controller, sensors, sensor_bytes ):

    # Sensor readout sizes
    sensor_size_dict = sensor_sizes[controller]

    # Starting index of bytes corresponding to individual 
    # sensor readout in sensor_bytes array
    index = 0

    # Result
    readouts = {}
    
    # Convert each sensor readout 
    for sensor in sensors:
        size             = sensor_size_dict[sensor]
        readout_bytes    = sensor_bytes[index:index+size]
        if ( sensor_formats[controller][sensor] == float ):
            sensor_val = byte_array_to_float( readout_bytes )
        else:
            sensor_val = byte_array_to_int(   readout_bytes )
        readouts[sensor] = sensor_val
        index           += size 

    return readouts
# get_raw_sensor_readouts #


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         conv_raw_sensor_readouts                                                 #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         Converts raw sensor readouts in integer format into the appropriate      # 
#         format                                                                   #
#                                                                                  #
####################################################################################
def conv_raw_sensor_readouts( controller, raw_readouts ):

    # Conversion functions
    conv_funcs = sensor_conv_funcs[controller]

    # Result
    readouts = {}

    # Convert each readout
    for sensor in raw_readouts:
        if ( conv_funcs[sensor] != None ):
            readouts[sensor] = conv_funcs[sensor]( raw_readouts[sensor] )
        else:
            readouts[sensor] = raw_readouts[sensor]
    
    return readouts
## conv_raw_sensor_readouts ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         get_sensor_readouts                                                      #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         Converts a byte array into sensor readouts and converts digital readout  #
#                                                                                  #
####################################################################################
def get_sensor_readouts( controller, sensors, sensor_bytes ):

    # Convert to integer form
    int_readouts = get_raw_sensor_readouts( controller, sensors, sensor_bytes )

    # Make conversions
    readouts     = conv_raw_sensor_readouts( controller, int_readouts )
    return readouts
## get_sensor_readouts ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         get_sensor_frame_bytes                                                   #
#                                                                                  #
# DESCRIPTION:                                                                     #
#        Obtains a frame of sensor data from a controller's flash in byte format   #
#                                                                                  #
####################################################################################
def get_sensor_frame_bytes( serialObj ):

    # Determine the size of the frame
    frame_size = sensor_frame_sizes[serialObj.controller]

    # Get bytes
    rx_bytes = serialObj.readBytes( frame_size )
    return rx_bytes
## get_sensor_frame_bytes ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         get_sensor_frame                                                         #
#                                                                                  #
# DESCRIPTION:                                                                     #
#        Converts a list of sensor frames into measurements                        #
#                                                                                  #
####################################################################################
def get_sensor_frames( controller, sensor_frames_bytes, format = 'converted' ):

    # Convert to integer format
    sensor_frames_int = []
    for frame in sensor_frames_bytes:
        sensor_frame_int = []
        for sensor_byte in frame:
            sensor_frame_int.append( ord( sensor_byte ) )
        sensor_frames_int.append( sensor_frame_int )

    # Combine bytes from integer data and convert
    if ( format == 'converted'):
        sensor_frames = []
        for int_frame in sensor_frames_int:
            sensor_frame = []

            sensor_frame.append(int_frame[0])
            sensor_frame.append(int_frame[1])
            
            # Time of frame measurement
            time = ( ( int_frame[2]       ) + 
                     ( int_frame[3] << 8  ) + 
                     ( int_frame[4] << 16 ) +
                     ( int_frame[5] << 24 ) )
            # Conversion to seconds
            sensor_frame.append( sensor_conv.time_millis_to_sec( time ) )

            # Sensor readouts
            sensor_frame_dict = {}
            index = 6
            for i, sensor in enumerate( sensor_sizes[ controller ] ):
                measurement = 0
                float_bytes = []
                for byte_num in range( sensor_sizes[controller][sensor] ):
                    if ( sensor_formats[controller][sensor] != float ):
                        measurement += ( int_frame[index + byte_num] << 8*byte_num )
                    else:
                        float_bytes.append( ( int_frame[index + byte_num] ).to_bytes(1, 'big' ) ) 
                if ( sensor_formats[controller][sensor] == float ):
                    measurement = byte_array_to_float( float_bytes )
                sensor_frame_dict[sensor] = measurement
                index += sensor_sizes[controller][sensor]
            sensor_vals_list = list( conv_raw_sensor_readouts( controller, sensor_frame_dict ).values() )
            for val in sensor_vals_list:
                sensor_frame.append( val )
            sensor_frames.append( sensor_frame )
        return sensor_frames
    elif ( format == 'bytes' ):
        return sensor_frames_int 
## get_sensor_frame ##

####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         get_preset_value                                                         #
#                                                                                  #
# DESCRIPTION:                                                                     #
#        Converts a list of preset values into measurements.                        #
#                                                                                  #
####################################################################################
def get_preset_values( controller, preset_bytes, preset_size ):

    # Throw an error if the preset encoding is wrong
    # The assert is used to induce a stack trace
    try:
        if( preset_size == 38 ):
            raise Exception("get_preset_values fail: expected preset_size of 38 bytes")
    except Exception as e:
        print(traceback.format_exc())
        exit(1)
        

    # Current Preset Format (1/23/25):
    # NOTE: Potential issue with float conversion (big vs. little endianness)
    # 2 bytes: Save bits
    # 24 bytes: IMU struct
    #   4 bytes each x6: acceleration x,y,z // gyro x,y,z
    # 8 bytes: Baro struct
    #   4 bytes each x2: baro pressure, baro temp
    # 4 bytes: Servo struct
    #   1 byte each x4: servo 1-4
    formatted_values = []
    formatted_values.append( bytes(preset_bytes[0]) )
    formatted_values.append( bytes(preset_bytes[1]) )
    print ( "BYTES:" )
    print( preset_bytes )
    for i in range(8): # 0-7
        temp_array = []
        for j in range(4): # 0-3
            temp_array.append(preset_bytes[(4 * i) + j + 2])
        formatted_values.append( byte_array_to_float(temp_array) )
    formatted_values.append( bytes(preset_bytes[36]) )
    formatted_values.append( bytes(preset_bytes[37]) )
    return formatted_values


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         format_sensor_readout                                                    #
#                                                                                  #
# DESCRIPTION:                                                                     #
#        Formats a sensor readout into a label, rounded readout, and units         #
#                                                                                  #
####################################################################################
def format_sensor_readout( controller, sensor, readout ):

    # Readout units
    units = sensor_units[controller][sensor] 

    # Rounded readout
    if ( units != None ):
        readout_str = "{:.3f}".format( readout )
    else:
        readout_str = str( readout )

    # Concatentate label, readout, and units
    if ( units != None ):
        output = sensor + ": " + readout_str + " " + units
    else:
        output = sensor + ": " + readout_str
    return output
## format_sensor_readout ##

####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         sensor_extract_data_filter                                               #
#                                                                                  #
# DESCRIPTION:                                                                     #
#       Finds the end of valid data extracted from flash extract and return a list #
#       containing only good data                                                  #
#                                                                                  #
####################################################################################
def sensor_extract_data_filter( data ):

    # Indices of beginning and end of good data 
    start_index = 0
    end_index   = len( data ) - 1

    # Search exit condition
    exit = False

    # Search index
    search_index = 0
    
    # Begin binary search
    while( not exit ):
        # Set search index
        search_index = ( (end_index - start_index)//2 ) + start_index

        # Check if two consecutive rows are identically equal
        rows_equal = ( data[search_index] == data[search_index+1] )

        # Check for exit condition
        if   (   search_index       == start_index ):
            if ( rows_equal ):
                return None
            else:
                return data[0:search_index-1]
        elif ( ( search_index + 1 ) == end_index   ):
            if ( rows_equal ):
                return data[0:start_index-1]
            else:
                return data[0:end_index-1]
        else: # No exit condfition
            # Update search range
            if ( rows_equal ):
                end_index = search_index
            else:
                start_index = search_index
## sensor_extract_data_filter ## 


####################################################################################
# Commands                                                                         #
####################################################################################


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         sensor                                                                   #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         Displays sensor data and/or info                                         #
#                                                                                  #
####################################################################################
def sensor( Args, serialObj, show_readouts = True ):

    ################################################################################
    # Local Variables                                                              #
    ################################################################################

    # Subcommand and Options Dictionary
    sensor_inputs = {
                    'dump' : {
                             },
                    'poll' : {
                             '-n' : 'Specify a sensor number',
                             '-h' : 'Display sensor usage info'
                             },
                    'plot' : {
                             '-n' : 'Specify a sensor number',
                             '-h' : 'Display sensor usage info'
                             },
                    'pplot' : {
                                    '-n' : 'Specify a sensor number',
                                    '-h' : 'Display sensor usage info'
                                  },
                    'list' : {
                             },
                    'help' : {
                             }
                    }

    # Maximum number of command arguments 
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

    # Complete list of sensor names/numbers 
    sensor_numbers = list( controller_sensors[serialObj.controller].keys() )

    # Sensor poll codes
    sensor_poll_codes = sensor_codes[serialObj.controller]
    sensor_poll_cmds  = {
                         'START'   : b'\xF3',
                         'REQUEST' : b'\x51',
                         'WAIT'    : b'\x44',
                         'RESUME'  : b'\xEF',
                         'STOP'    : b'\x74'
                        }

    # Timeout for sensor poll
    sensor_poll_timeout = 1000

    # Size of sensor readouts
    readout_sizes = sensor_sizes[serialObj.controller]

    # Lists of sensor data
    sensor_bytes_list = []
    sensor_int_list   = []

    ################################################################################
    # Basic Inputs Parsing                                                         #
    ################################################################################
    parse_check = commands.parseArgs(
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
        num_sensors      = len( user_sensor_nums )

    # Verify connection to board with sensors
    if ( not (serialObj.controller in controller_sensors.keys()) ):
        print( "Error: The sensor command requires a valid " +
               "serial connection to a controller with "     +
               "sensors. Run the \"connect\" command to "    +
               "establish a valid connection" )
        return serialObj

    ################################################################################
    # Command-Specific Checks                                                      #
    ################################################################################

    # Verify sensor nums supplied are valid
    if (  ( user_subcommand == "poll" ) or
          ( user_subcommand == "plot" ) or
          ( user_subcommand == "pplot" )):
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

            # Sensor numbers are valid, determine number of bytes needed for 
            # selected sensors
            sensor_poll_frame_size = 0 
            for sensor_num in user_sensor_nums:
                sensor_poll_frame_size += readout_sizes[sensor_num] 

    ################################################################################
    # Subcommand: sensor help                                                      #
    ################################################################################
    if   ( user_subcommand == "help" ):
        commands.display_help_info( "sensor" )
        return serialObj


    ################################################################################
    # Subcommand: sensor dump                                                      #
    ################################################################################
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

        print(sensor_dump_size_bytes)

        # Recieve data from controller
        for byteNum in range( sensor_dump_size_bytes ):
            sensor_bytes_list.append( serialObj.readByte() )

        print(sensor_bytes_list)

        # Get readouts from byte array
        serialObj.sensor_readouts = get_sensor_readouts( 
                                                       serialObj.controller, 
                                                       sensor_numbers      ,
                                                       sensor_bytes_list
                                                       )

        # Display Sensor readouts
        if ( show_readouts ):
            for sensor in serialObj.sensor_readouts:
                readout_formatted = format_sensor_readout(
                                                        serialObj.controller,
                                                        sensor               ,
                                                        serialObj.sensor_readouts[sensor]
                                                        )
                print( readout_formatted )
            
        return serialObj

    ################################################################################
    # Subcommand: sensor pplot                                                      #
    ################################################################################
    elif ( user_subcommand == "pplot" ):

        # Send command opcode
        serialObj.sendByte( opcode )

        user_subcommand = "poll"

        # Send sensor poll subcommand code
        serialObj.sendByte( subcommand_codes[user_subcommand] )

        # Tell the controller how many sensors to use
        serialObj.sendByte( num_sensors.to_bytes( 1, 'big' ) )

        # Send the controller the sensor codes
        for sensor_num in user_sensor_nums:
            serialObj.sendByte( sensor_poll_codes[sensor_num] )
        
        # Start the sensor poll sequence
        serialObj.sendByte( sensor_poll_cmds['START'] )

        # Receive and display sensor readouts 
        timeout_ctr = 0

        try:
            # Initialize graph
            serialObj.sendByte( sensor_poll_cmds['REQUEST'] )
            sensor_bytes_list = serialObj.readBytes( sensor_poll_frame_size ) 
            sensor_readouts   = get_sensor_readouts(
                                                    serialObj.controller, 
                                                    user_sensor_nums    ,
                                                    sensor_bytes_list
                                                )
            
            serialObj.sendByte( sensor_poll_cmds['WAIT'] )

            plt.ion()
            graphs, _, axs_sensor, readouts_dict, range_dict = plot_sensor_realtime_init(serialObj.controller, sensor_readouts)
            secs = []

            serialObj.sendByte( sensor_poll_cmds['RESUME'])

            print("Ctrl+C to exit");
            while ( timeout_ctr <= sensor_poll_timeout ):
                serialObj.sendByte( sensor_poll_cmds['REQUEST'] )
                sensor_bytes_list = serialObj.readBytes( sensor_poll_frame_size ) 
                sensor_readouts   = get_sensor_readouts(
                                                        serialObj.controller, 
                                                        user_sensor_nums    ,
                                                        sensor_bytes_list
                                                    )
                for sensor in sensor_readouts:
                    readout_formated = format_sensor_readout(
                                                            serialObj.controller, 
                                                            sensor              ,
                                                            sensor_readouts[sensor] 
                                                            )
                    print( readout_formated + '\t', end='' )
                print()
            
                serialObj.sendByte( sensor_poll_cmds['WAIT'] )

                secs.append(time.process_time())
                plot_sensor_realtime_start(
                                            serialObj.controller,
                                            graphs,
                                            axs_sensor,
                                            readouts_dict,
                                            range_dict,
                                            sensor_readouts,
                                            secs
                )

                serialObj.sendByte( sensor_poll_cmds['RESUME'] )


                # Pause for readibility
                serialObj.sendByte( sensor_poll_cmds['WAIT'] )
                time.sleep(0.05)
                serialObj.sendByte( sensor_poll_cmds['RESUME'])
                timeout_ctr += 1
        except KeyboardInterrupt:
            # Stop transmission
            print("\nPoll exited!")    
            serialObj.sendByte( sensor_poll_cmds['STOP'] )
            plt.ioff()
        plt.ioff()
        return serialObj

    ################################################################################
    # Subcommand: sensor poll                                                     #
    ################################################################################
    elif ( user_subcommand == "poll" ):

        # Send command opcode
        serialObj.sendByte( opcode )

        # Send sensor poll subcommand code
        serialObj.sendByte( subcommand_codes[user_subcommand] )

        # Tell the controller how many sensors to use
        serialObj.sendByte( num_sensors.to_bytes( 1, 'big' ) )

        # Send the controller the sensor codes
        for sensor_num in user_sensor_nums:
            serialObj.sendByte( sensor_poll_codes[sensor_num] )
        
        # Start the sensor poll sequence
        serialObj.sendByte( sensor_poll_cmds['START'] )

        # Canard Add-on feature: Logging data during poll
        filename = "canard_" + str(datetime.now()) + ".txt"
        file = open("canard/" + filename, "w")
        

        # Receive and display sensor readouts 
        timeout_ctr = 0
        try:    
            print("Ctrl+C to exit");
            while ( timeout_ctr <= sensor_poll_timeout ):
                serialObj.sendByte( sensor_poll_cmds['REQUEST'] )
                sensor_bytes_list = serialObj.readBytes( sensor_poll_frame_size ) 
                sensor_readouts   = get_sensor_readouts(
                                                        serialObj.controller, 
                                                        user_sensor_nums    ,
                                                        sensor_bytes_list
                                                    )
                for sensor in sensor_readouts:
                    readout_formated = format_sensor_readout(
                                                            serialObj.controller, 
                                                            sensor              ,
                                                            sensor_readouts[sensor] 
                                                            )
                    print( readout_formated + '\t', end='' )
                    file.write(readout_formated + '\t')
                file.write("\n")
                print()
                # Pause for readibility
                serialObj.sendByte( sensor_poll_cmds['WAIT'] )
                time.sleep(0.2)
                serialObj.sendByte( sensor_poll_cmds['RESUME'])
                timeout_ctr += 1
        except KeyboardInterrupt:
            # Stop transmission
            print("\nPoll exited!")    
            serialObj.sendByte( sensor_poll_cmds['STOP'] )

        file.close()

        return serialObj

    ################################################################################
    # Subcommand: sensor list                                                      #
    ################################################################################
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
    ## sensor list ##

    ################################################################################
    # Subcommand: sensor plot                                                      #
    ################################################################################
    elif ( user_subcommand == "plot" ):

        # Data Filename 
        filename = sensor_data_filenames[serialObj.controller]

        # Import Data
        with open( filename, "r" ) as file:
            sensor_data_lines = file.readlines()
        sensor_data_str = []
        for line in sensor_data_lines:
            sensor_data_str.append( line.split('\t') )

        # Convert to floating point format
        sensor_data = []
        for frame in sensor_data_str:
            sensor_frame = []
            for val in frame:
                if ( val != '\n' ):
                    sensor_frame.append( float( val ) )
            sensor_data.append( sensor_frame )
        
        # Filter out garbage flash data
        sensor_data_filtered = sensor_extract_data_filter( sensor_data )
        sensor_data_filtered = np.array( sensor_data_filtered )

        # Select data to plot
        sensor_labels = []
        for sensor in user_sensor_nums:
            sensor_index = sensor_indices[serialObj.controller][sensor]
            sensor_label = ( sensor + " (" + 
                             sensor_units[serialObj.controller][sensor] + ")" )
            sensor_labels.append( sensor_label )
            time_data = sensor_data_filtered[:,0]/60.0 # minutes
            plt.plot( time_data, 
                      sensor_data_filtered[:,sensor_index] )

        # Plot parameters
        plt.title( "Data: " + serialObj.controller )
        plt.xlabel( "Time, min" )
        plt.ylabel( "Measurement Value" )
        plt.grid()
        plt.legend( sensor_labels )

        # Display
        plt.show()
        return serialObj

    ################################################################################
    # Unknown subcommand                                                           #
    ################################################################################
    else:
        print( "Error: Unknown subcommand passed to sensor " +
               "function. " )
        commands.error_msg()
        return serialObj
## sensor ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         flash                                                                    #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         read and write data to a controller's extenral flash                     #
#                                                                                  #
####################################################################################
def flash(Args, serialObj):

    ################################################################################
    # Local Variables                                                              #
    ################################################################################

    # Subcommand and Options Dictionary
    flash_inputs= { 
    'enable'  : {
                },
    'disable' : {
                },
    'status'  : {
                },
    'write'   : {
            '-b' : 'Specify a byte to write to flash memory'  ,
            '-s' : 'Specify a string to write to flash memory',
            '-a' : 'Specify a memory address to write to'     ,
            '-f' : 'Specify a file to use for input data'     ,
            '-h' : 'Display help info'
                },
    'read'    : {
            '-a' : 'Specify a memory address to read from',
            '-n' : 'Specify a number of bytes to read from flash memory',
            '-f' : 'Specify a file to use for output data',
            '-h' : 'Display help info'
                }, 
    'erase'   : {
                },
    'help'    : {
                },
    'extract' : {
                },
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
    flash_extract_base_code = b'\xc0'  # SUBOP 110 -> 1100 0000

    # Subcommand codes as integers
    flash_read_base_code_int    = ord( flash_read_base_code    )
    flash_enable_base_code_int  = ord( flash_enable_base_code  )
    flash_disable_base_code_int = ord( flash_disable_base_code )
    flash_write_base_code_int   = ord( flash_write_base_code   )
    flash_erase_base_code_int   = ord( flash_erase_base_code   )
    flash_status_base_code_int  = ord( flash_status_base_code  )
    flash_extract_base_code_int = ord( flash_extract_base_code )

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
                   "Flight Computer (A0002 Rev 1.0)"         ,
                   "Flight Computer (A0002 Rev 2.0)"         ,
                   "Flight Computer Lite (A0007 Rev 1.0)"    ,
                   "Liquid Engine Controller (L0002 Rev 5.0)"
                             ]
    
    # Extract blocks
    extract_frame_size       = sensor_frame_sizes[serialObj.controller]
    extract_num_frames       = 524288 // extract_frame_size
    extract_num_unused_bytes = 524288 %  extract_frame_size


    ################################################################################
    # Basic Inputs Parsing                                                         #
    ################################################################################
    parse_check = commands.parseArgs(
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

    ################################################################################
    # Command-Specific Checks                                                      #
    ################################################################################

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

    ################################################################################
    # Subcommand: flash help                                                       #
    ################################################################################
    if (user_subcommand == "help"):
        commands.display_help_info('flash')
        return serialObj

    ################################################################################
    # Subcommand: flash enable                                                     #
    ################################################################################
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

    ################################################################################
    # Subcommand: flash disable                                                    #
    ################################################################################
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

    ################################################################################
    # Subcommand: flash status                                                     #
    ################################################################################
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
            print("Error: No response recieved from " +
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

    ################################################################################
    # Subcommand: flash write                                                      #
    ################################################################################
    elif (user_subcommand == "write"):

        # Check if flash chip has writing operations enabled
        if (not serialObj.flash_write_enabled
            and not (user_options[0] == '-h')):
            print("Error: Flash write has not been enabled. " +
                  "Run flash write enable to enable writing " +
                  "to the flash chip")
            return serialObj

        ################### -h option #########################
        if (user_options[0] == '-h'):
            commands.display_help_info('flash')
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


    ################################################################################
    # Subcommand: flash read                                                       #
    ################################################################################
    elif (user_subcommand == "read"):

        ################### -h option #########################
        if (user_options[0] == '-h'):
            commands.display_help_info('flash')
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


    ################################################################################
    # Subcommand: flash erase                                                      #
    ################################################################################
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


    ################################################################################
    # Subcommand: flash extract                                                    #
    ################################################################################
    elif ( user_subcommand == "extract" ):

        # Send flash opcode 
        serialObj.sendByte( opcode )

        # Send flash extract subcommand code 
        serialObj.sendByte( flash_extract_base_code )

        # Start timer
        start_time = time.perf_counter()

        preset_bytes = []
        # Recieve preset data if necessary
        if (serialObj.controller == controller_names[4]):
            preset_size = 38
            print( "Reading presets..." )
            preset_bytes = serialObj.readBytes( preset_size )

            # Re-calculate the number of frames to be extracted
            # This should be moved to their initial definition on cleanup
            extract_num_frames = ( 524288 - preset_size ) // extract_frame_size
            extract_num_unused_bytes = ( 524288 - preset_size ) %  extract_frame_size

        print( preset_bytes )
        # Recieve Data in 32 byte blocks
        # Flash contains 4096 blocks of data
        rx_byte_blocks = []
        for i in range( extract_num_frames ):
            if ( i%100 == 0 ):
                print( "Reading block " + str(i) + "..."  )
            rx_sensor_frame_block = get_sensor_frame_bytes( serialObj )
            rx_byte_blocks.append( rx_sensor_frame_block )
        
        # Receive the unused bytes
        unused_bytes = serialObj.readBytes( extract_num_unused_bytes )

        # Recieve the status byte from the engine controller
        return_code = serialObj.readByte()

        # Record ending time
        extract_time = time.perf_counter() - start_time

        # Convert the data from bytes to preset values
        if (serialObj.controller == controller_names[4]):
            preset_values = get_preset_values( serialObj.controller, preset_bytes, preset_size )
            with open( "output/preset_values.txt", 'w') as file:
                for value in preset_values:
                    file.write( str( value ) )
                    file.write( '\t' )
                file.write( '\n' )

        # Convert the data from bytes to measurement readouts
        sensor_frames = get_sensor_frames( serialObj.controller, rx_byte_blocks )

        # Export the data to txt files
        with open( sensor_data_filenames[serialObj.controller], 'w' ) as file:
            for sensor_frame in sensor_frames:
                for val in sensor_frame:
                    file.write( str( val ) )
                    file.write( '\t' )
                file.write( '\n' )    

        # Parse return code
        if (return_code == b''):
            print("Error: No response code recieved")
        elif (return_code == b'\x00'):
            print( "Flash extract successful" )
            print( "Extract time: {:.3f} sec".format( extract_time ) )
        else:
            print("Error: Unrecognised response code recieved")
        return serialObj


    ################################################################################
    # Unknown Option                                                               #
    ################################################################################
    else:
        print("Error: unknown option passed to connect function")    
        commands.error_msg()
        return serialObj
# sensor # 


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         ignite                                                                   #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         issue the ignition signal to the controller or display                   #
#                                                                                  #
####################################################################################
def ignite(Args, serialObj):

    ################################################################################
    # Local Variables                                                              #
    ################################################################################

    # Subcommand Dictionary
    # Options Dictionary
    ignite_inputs = { 
                    'fire'  : {},
                    'main'  : {},
                    'drogue': {},
                    'cont'  : {},
                    'help'  : {}
                    }
    
    # Maximum number of arguments
    max_args = 1

    # Supported boards
    supported_boards = [
                        controller_names[2],  # Engine controller rev 4
                        controller_names[3],  # Flight computer rev 1
                        controller_names[4],  # Flight computer rev 2
                        controller_names[5],  # Flight computer lite rev 1
                        controller_names[7]   # Engine controller rev 5 
                       ]

    # Command type -- subcommand function
    command_type = 'subcommand'

    # Command opcode
    opcode = b'\x20' 

    # Subcommand codes
    ignite_fire_code     = b'\x01'
    ignite_cont_code     = b'\x02'
    ignite_main_code     = b'\x03'
    ignite_drogue_code   = b'\x04'

    # Response codes, correspond to enum values in ignition.h
    ignite_success_code            = b'\x41'
    ignite_fire_fail_ematch_code   = b'\x42'
    ignite_fire_fail_power_code    = b'\x43'
    ignite_fire_fail_code          = b'\x44'
    ignite_main_fail_switch_code   = b'\x45'
    ignite_main_fail_cont_code     = b'\x46'
    ignite_main_fail_code          = b'\x47'
    ignite_drogue_fail_switch_code = b'\x45'
    ignite_drogue_fail_cont_code   = b'\x48'
    ignite_drogue_fail_code        = b'\x49'

    ################################################################################
    # Basic Inputs Parsing                                                         #
    ################################################################################

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

    ################################################################################
    # Command-Specific Checks                                                      #
    ################################################################################

    # Verify Controller Connection
    if ( ( not (serialObj.controller in supported_boards) ) and 
         ( user_subcommand != "help"                      ) ):
        print("Error: The ignite command requires a valid " + 
              "serial connection to an ignition compatible controller "  + 
              "device." )
        print( "Supported boards: " )
        for board in supported_boards:
            print( "\t" + board )
        print( "Run the \"connect\" command to establish a valid connection.")
        return serialObj

    # Engine controller commands check
    if ( user_subcommand == "fire" ):
        if ( not ( "Engine Controller" in serialObj.controller ) ):
            print( "Error: the ignite fire command requires a connection " +
                    "to an engine controller device. Run the \"connect\" " +
                    "command to setup a connection. " )
            return serialObj

    # Flight computer commands check
    if ( ( user_subcommand == "main" ) or ( user_subcommand == "drogue" ) ):
        if ( not ( "Flight Computer" in serialObj.controller ) ):
            print( "Error: the ignite main and ignite drogue commands " + 
                   "require a connection to a flight computer device. " + 
                   "Run the \"connect\" command to setup a connection.")
            return serialObj

    ################################################################################
    # Subcommand: ignite help                                                      #
    ################################################################################
    if (user_subcommand == "help"):
        commands.display_help_info('ignite')
        return serialObj

    ################################################################################
    # Subcommand: ignite fire                                                      #
    ################################################################################
    elif (user_subcommand == "fire"):

        # Send ignite opcode
        serialObj.sendByte(opcode)

        # Send subcommand code
        serialObj.sendByte(ignite_fire_code)

        # Get ignition status code
        ign_status = serialObj.readByte()

        # Display ignition status

        # Succesful ignition
        if (ign_status == ignite_success_code):
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
            print("Ignition unsuccessful. Unrecognized ignition status code.")

        # Exit
        return serialObj

    ################################################################################
    # Subcommand: ignite  main                                                     #
    ################################################################################
    elif (user_subcommand == "main"):

        # Send ignite opcode
        serialObj.sendByte(opcode)

        # Send subcommand code
        serialObj.sendByte(ignite_main_code)

        # Get ignition status code
        ign_status = serialObj.readByte()

        # Display ignition status

        # Succesful ignition
        if (ign_status == ignite_success_code):
            print("Ignition successful")

        # No response code received
        elif (ign_status == b''):
            print('Ignition unsuccessful. No response ' +
                  'code recieved from flight computer.' )

        # No switch continuity 
        elif (ign_status == ignite_main_fail_switch_code):
            print('Ignition unsuccessful. No continuity ' +
                  'in arming switch. Ensure the '+
                  'switch is armed.')

        # No ematch continuity
        elif ( ign_status == ignite_main_fail_cont_code ):
            print( 'Ignition unsuccessful. No continuity in ematch. Ensure an ' +
                   'ematch is connected to the main screw terminals ')

        # Ematch continuity is not disrupted after asserting
        # the ignition signal
        elif (ign_status == ignite_main_fail_code):
            print('Ignition unsuccessful. The ignite signal ' +
                  'was asserted but the ematch was not lit')

        else:
            print("Ignition unsuccessful. Unrecognized ignition status code.")

        # Exit
        return serialObj

    ################################################################################
    # Subcommand: ignite  drogue                                                   #
    ################################################################################
    elif (user_subcommand == "drogue"):

        # Send ignite opcode
        serialObj.sendByte(opcode)

        # Send subcommand code
        serialObj.sendByte(ignite_drogue_code)

        # Get ignition status code
        ign_status = serialObj.readByte()

        # Display ignition status

        # Succesful ignition
        if (ign_status == ignite_success_code):
            print("Ignition successful")

        # No response code received
        elif (ign_status == b''):
            print('Ignition unsuccessful. No response ' +
                  'code recieved from flight computer.' )

        # No switch continuity 
        elif (ign_status == ignite_drogue_fail_switch_code):
            print('Ignition unsuccessful. No continuity ' +
                  'in arming switch. Ensure the '+
                  'switch is armed.')

        # No ematch continuity
        elif ( ign_status == ignite_drogue_fail_cont_code ):
            print( 'Ignition unsuccessful. No continuity in ematch. Ensure an ' +
                   'ematch is connected to the drogue screw terminals ')

        # Ematch continuity is not disrupted after asserting
        # the ignition signal
        elif (ign_status == ignite_drogue_fail_code):
            print('Ignition unsuccessful. The ignite signal ' +
                  'was asserted but the ematch was not lit')

        else:
            print("Ignition unsuccessful. Unrecognized ignition status code.")

        # Exit
        return serialObj

    ################################################################################
    # Subcommand: ignite cont                                                      #
    ################################################################################
    elif (user_subcommand == "cont"):

        # Send ignite opcode
        serialObj.sendByte(opcode)

        # Send subcommand code
        serialObj.sendByte(ignite_cont_code)

        # Get ignition status code
        ign_status = serialObj.readByte()

        # Parse response code
        ign_status_int = ord(ign_status)

        # Display continuity statuses
        if ( "Engine Controller" in serialObj.controller ):

            # Ematch and switch continuity
            if ((ign_status_int >> 3) & 1):
                print("Ematch and Switch:     Connected")
            else: 
                print("Ematch and Switch:     Disconnected")

            # Solid propellant wire continuity
            if ((ign_status_int >> 4) & 1):
                print("Solid Propellant Wire: Connected")
            else: 
                print("Solid Propellant Wire: Disconnected")

            # Nozzle wire continuity
            if ((ign_status_int >> 5) & 1):
                print("Nozzle Wire:           Connected")
            else: 
                print("Nozzle Wire:           Disconnected")

        elif ( "Flight Computer" in serialObj.controller ):

            # Switch continuity
            if ((ign_status_int >> 0) & 1):
                print("Switch:        Connected")
            else: 
                print("Switch:        Disconnected")

            # Main ematch continuity
            if ((ign_status_int >> 1) & 1):
                print("Main Ematch:   Connected")
            else: 
                print("Main Ematch:   Disconnected")

            # Nozzle wire continuity
            if ((ign_status_int >> 2) & 1):
                print("Drogue Ematch: Connected")
            else: 
                print("Drogue Ematch: Disconnected")

        # Exit
        return serialObj

    ################################################################################
    # Unknown Subcommand                                                           #
    ################################################################################
    else:
        print("Error: unknown subcommand passed to ignite " +
              "function")    
        commands.error_msg()
        return serialObj


###################################################################################
# END OF FILE                                                                     # 
###################################################################################