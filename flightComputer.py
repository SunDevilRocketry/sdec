#################################################################################### 
#                                                                                  # 
# flightComputer.py -- module with command line functions specific to the flight   # 
#                      computer                                                    #
# Author: Colton Acosta                                                            # 
# Date: 2/26/2023                                                                  #
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
import datetime
from   matplotlib import pyplot as plt

# Project imports
from   config      import *
from   hw_commands import byte_array_to_int
from   hw_commands import byte_array_to_float
from   hw_commands import get_sensor_frames
from   hw_commands import sensor_extract_data_filter
import commands
import sensor_conv

####################################################################################
# Global Variables                                                                 #
####################################################################################

# Serial port timeouts
if ( sdr_debug ):
    default_timeout = 100 # 100 second timeout
else:
    default_timeout = 1   # 1 second timeout

# Supported boards
supported_boards = [
                   "Flight Computer (A0002 Rev 2.0)" 
                   ]


####################################################################################
# Commands                                                                         #
####################################################################################


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
#         dual_deploy                                                              #
#                                                                                  #
# DESCRIPTION:                                                                     #
#         Probes and tests the dual deploy firmware                                #
#                                                                                  #
####################################################################################
def dual_deploy( Args, serialObj ):
    ################################################################################
    # Local Variables                                                              #
    ################################################################################

    # Options Dictionary
    dual_deploy_inputs = { 
                       'help'   : {},
                       'status' : {},
                       'extract': {},
                       'plot'   : {}
                         }
    
    # Maximum number of arguments
    max_args = 1

    # Opcode
    opcode = b'\xA0'

    # Subcommand opcodes
    sub_opcodes = {
                  'status' : b'\x01',
                  'extract': b'\x02'
                  }

    # Command type -- subcommand function
    command_type = 'subcommand'

    ################################################################################
    # Basic inputs parsing                                                         #
    ################################################################################
    parse_check = commands.parseArgs( Args              ,
                                      max_args          ,
                                      dual_deploy_inputs,
                                      command_type )
    if ( not parse_check ):
        return serialObj # user inputs failed parse tests

    ################################################################################
    # Command Specific Parsing                                                     #
    ################################################################################

    # Check for active flight computer connection running the dual deploy firmware
    if ( serialObj.controller not in supported_boards ):
        print( "Error: The dual-deploy command requires an active connection to " +
               "a flight computer.")
        return serialObj
    
    # Check that the flight computer is running the dual deploy firmware
    if ( serialObj.firmware != "Dual Deploy"):
        print( "Error: The dual-deploy command requires the flight computer to " + 
               "be running the dual-deploy firmware. The flight computer is "    + 
               "currently running the " + serialObj.firmware + " firmware" )
        return serialObj

    # Set the subcommand
    subcommand = Args[0]

    ################################################################################
    # dual-deploy help                                                             #
    ################################################################################
    if ( subcommand == "help" ):
        commands.display_help_info( "dual-deploy" )
        return serialObj

    ################################################################################
    # dual-deploy status                                                           #
    ################################################################################
    elif ( subcommand == "status" ):
        # Send the dual-deploy/status opcode 
        serialObj.sendByte( opcode                )
        serialObj.sendByte( sub_opcodes['status'] )

        # Receive the recovery programmed settings
        main_alt     = byte_array_to_int( serialObj.readBytes( 4 ) )
        drogue_delay = byte_array_to_int( serialObj.readBytes( 4 ) )

        # Receive the ground pressure
        ground_press = byte_array_to_float( serialObj.readBytes( 4 ) )
        ground_press /= 1000

        # Receive the sample rates, ms/sample
        ld_sample_rate = byte_array_to_int( serialObj.readBytes( 4 ) )
        ad_sample_rate = byte_array_to_int( serialObj.readBytes( 4 ) )
        md_sample_rate = byte_array_to_int( serialObj.readBytes( 4 ) )
        zd_sample_rate = byte_array_to_int( serialObj.readBytes( 4 ) )

        # Display Results
        print( "Main Deployment Altitude        : " + str( main_alt       ) + " ft"  )
        print( "Drogue Delay                    : " + str( drogue_delay   ) + " s"   )
        print( "Ground Pressure                 : " + str( ground_press   ) + " kPa" )
        print( "Launch Detect Sample Rate       : " + str( ld_sample_rate ) + " ms"  )
        print( "Apogee Detect Sample Rate       : " + str( ad_sample_rate ) + " ms"  )
        print( "Main Altitude Detect Sample Rate: " + str( md_sample_rate ) + " ms"  )
        print( "Landing Detect Sample Rate      : " + str( zd_sample_rate ) + " ms"  )
        return serialObj

    ################################################################################
    # dual-deploy extract                                                          #
    ################################################################################
    elif ( subcommand == "extract" ):
        # Send the dual-deploy/status opcode 
        serialObj.sendByte( opcode                 )
        serialObj.sendByte( sub_opcodes['extract'] )

        # Get the data logger status to determine if header data is valid
        status_byte = serialObj.readByte()
        if ( status_byte != b'\x00' ):
            print( "Error: The flash header is not valid. No flight data is " +
                   "available" )

        # Receive the recovery programmed settings
        main_alt     = byte_array_to_int( serialObj.readBytes( 4 ) )
        drogue_delay = byte_array_to_int( serialObj.readBytes( 4 ) )

        # Receive the flight events
        main_deploy_time   = byte_array_to_int( serialObj.readBytes( 4 ) )
        drogue_deploy_time = byte_array_to_int( serialObj.readBytes( 4 ) )
        land_time          = byte_array_to_int( serialObj.readBytes( 4 ) )

        # Receive the ground pressure
        ground_press       = byte_array_to_float( serialObj.readBytes( 4 ) )
        ground_press      /= 1000

        # Receive the flight data
        rx_blocks = []
        for i in range( 40960 ):
            if ( i%100 == 0 ):
                print( "Reading block " + str( i ) )
            rx_frame_block = serialObj.readBytes( 12 )
            rx_blocks.append( rx_frame_block )
        
        # Format the flight data
        sensor_frames          = get_sensor_frames( "Flight Computer Lite (A0007 Rev 1.0)", 
                                                     rx_blocks )
        sensor_frames_filtered = sensor_extract_data_filter( sensor_frames )

        # Croeate the output directory
        run_date = datetime.date.today()
        run_date = run_date.strftime("%m-%d-%Y")
        if ( not ( os.path.exists( "output/dual-deploy" ) ) ):
            os.mkdir( "output/dual-deploy" )
        base_output_dir = "output/dual-deploy/" + run_date
        if ( not ( os.path.exists( base_output_dir ) ) ):
            os.mkdir( base_output_dir )
        test_num = 0
        output_dir = base_output_dir + "/data" + str( test_num )
        while( os.path.exists( output_dir ) ):
            test_num += 1
            output_dir = base_output_dir + "/data" + str( test_num )
        os.mkdir( output_dir )
        
        # Export the header data
        with open( output_dir + "/header.txt", "a") as file:
            file.write( "Main Altitude     : " + str( main_alt           ) + " ft \n" )
            file.write( "Drogue Delay      : " + str( drogue_delay       ) + " s  \n" )
            file.write( "Ground Pressure   : " + str( ground_press       ) + " kPa\n" )
            file.write( "Main Deploy Time  : " + str( main_deploy_time   ) + " ms \n" )
            file.write( "Drogue Deploy Time: " + str( drogue_deploy_time ) + " ms \n" )
            file.write( "Landing Time      : " + str( land_time          ) + " ms \n" )

        # Export the flight data
        with open( output_dir + "/data.txt", 'w' ) as file:
            for sensor_frame in sensor_frames_filtered:
                for val in sensor_frame:
                    file.write( str( val ) )
                    file.write( '\t')
                file.write( '\n' )    
        return serialObj
        # dual-deploy extract #

    ################################################################################
    # dual-deploy plot #
    ################################################################################
    elif ( subcommand == 'plot' ):

        # Find most recent date of data extraction 
        base_data_dirs             = os.listdir( "output/dual-deploy" )
        base_data_dirs_recent      = []
        base_data_dirs_most_recent = []
        max_month = 1
        for base_data_dir in base_data_dirs:
            month = base_data_dir[0:2]
            month = int( month )
            if ( month >= max_month ):
                max_month = month
        for base_data_dir in base_data_dirs:
            month = base_data_dir[0:2]
            month = int( month )
            if ( month == max_month ):
                base_data_dirs_recent.append( base_data_dir )
        max_day = 0
        for base_data_dir in base_data_dirs_recent:
            day = base_data_dir[3:5]
            day = int( day )
            if ( day > max_day ):
                max_day = day
        for base_data_dir in base_data_dirs_recent:
            day = base_data_dir[3:5]
            day = int( day )
            if ( day == max_day ):
                base_data_dirs_most_recent.append( base_data_dir )
        base_data_dir = base_data_dirs_most_recent[-1]
        base_data_dir = "output/dual-deploy/" + base_data_dir

        # Find most recent data
        data_num = 0
        while ( os.path.exists( base_data_dir + "/data" + str( data_num ) ) ):
            data_num += 1
        data_dir = base_data_dir + "/data" + str( data_num - 1 )
        header_filename = data_dir + "/header.txt"
        data_filename   = data_dir + "/data.txt"

        # Extract the header data
        with open( header_filename, "r" ) as file:
            header_lines = file.readlines()
            header_lines_split = []
            for line in header_lines:
                header_lines_split.append( line.split() )
        main_deploy_alt    = float( header_lines_split[0][3] )
        drogue_delay       = float( header_lines_split[1][3] )
        ground_press       = float( header_lines_split[2][3] )
        main_deploy_time   = float( header_lines_split[3][4] )/1000.0
        drogue_deploy_time = float( header_lines_split[4][3] )/1000.0
        landing_time       = float( header_lines_split[5][3] )/1000.0

        # Extract the flight data
        sensor_time     = []
        sensor_pressure = []
        sensor_temp     = []
        with open( data_filename, "r" ) as file:
            data_lines = file.readlines()
            for line in data_lines:
                data_line_split = line.split()
                sensor_time.append    ( float( data_line_split[0] ) )
                sensor_pressure.append( float( data_line_split[1] ) )
                sensor_temp.append    ( float( data_line_split[2] ) )
                
        # Calculate Altitude
        sensor_altitude = []
        for press in sensor_pressure:
            sensor_altitude.append( sensor_conv.pressure_to_alt( press, ground_press ) )
        
        # Plot Pressure data
        plt.figure()
        plt.plot( sensor_time, sensor_pressure )
        plt.title( "Pressure Data" )
        plt.xlabel( "Time, s" )
        plt.ylabel( "Pressure, kPa" )
        plt.grid()
        plt.axvline( x = main_deploy_time  , color = 'b', label = "Main Deployment"   )
        plt.axvline( x = drogue_deploy_time, color = 'r', label = "Drogue Deployment" )
        plt.axvline( x = landing_time      , color = 'g', label = "Landed"            )
        plt.legend()
        plt.show( block = False )

        # Plot Temperature Data
        plt.figure()
        plt.plot( sensor_time, sensor_temp )
        plt.title( "Temperature Data" )
        plt.xlabel( "Time, s" )
        plt.ylabel( "Temperature, Degrees C" )
        plt.grid()
        plt.axvline( x = main_deploy_time  , color = 'b', label = "Main Deployment"   )
        plt.axvline( x = drogue_deploy_time, color = 'r', label = "Drogue Deployment" )
        plt.axvline( x = landing_time      , color = 'g', label = "Landed"            )
        plt.legend()
        plt.show( block = False )

        # Plot Altitude Data
        plt.figure()
        plt.plot( sensor_time, sensor_altitude )
        plt.title( "Altitude Data" )
        plt.xlabel( "Time, s" )
        plt.ylabel( "Altitude, ft" )
        plt.grid()
        plt.axvline( x = main_deploy_time  , color = 'b', label = "Main Deployment"   )
        plt.axvline( x = drogue_deploy_time, color = 'r', label = "Drogue Deployment" )
        plt.axvline( x = landing_time      , color = 'g', label = "Landed"            )
        plt.legend()
        plt.show( block = False )
        return serialObj

    return serialObj 
## dual_deploy ##


####################################################################################
# END OF FILE                                                                      # 
####################################################################################