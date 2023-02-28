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

# Project imports
from   config      import *
from   hw_commands import byte_array_to_int
from   hw_commands import get_sensor_frames
from   hw_commands import sensor_extract_data_filter
import commands

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
                       'extract': {}
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
        print( "Error: The dual-deploy command requires an active connection to \
               a flight computer.")
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

        # Receive the sample rates, ms/sample
        ld_sample_rate = byte_array_to_int( serialObj.readBytes( 4 ) )
        ad_sample_rate = byte_array_to_int( serialObj.readBytes( 4 ) )
        md_sample_rate = byte_array_to_int( serialObj.readBytes( 4 ) )
        zd_sample_rate = byte_array_to_int( serialObj.readBytes( 4 ) )

        # Display Results
        print( "Main Deployment Altitude        : " + str( main_alt       ) + " ft" )
        print( "Drogue Delay                    : " + str( drogue_delay   ) + " s"  )
        print( "Launch Detect Sample Rate       : " + str( ld_sample_rate ) + " ms" )
        print( "Apogee Detect Sample Rate       : " + str( ad_sample_rate ) + " ms" )
        print( "Main Altitude Detect Sample Rate: " + str( md_sample_rate ) + " ms" )
        print( "Landing Detect Sample Rate      : " + str( zd_sample_rate ) + " ms" )
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

        # Receive the flight data
        rx_blocks = []
        for i in range( 43008 ):
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
        output_dir = "output/dual-deploy/" + run_date
        if ( not ( os.path.exists( output_dir ) ) ):
            os.mkdir( output_dir )
        test_num = 0
        output_dir = output_dir + "/data" + str( test_num )
        while( os.path.exists( output_dir ) ):
            test_num += 1
            output_dir = output_dir + "/data" + str( test_num )
        
        # Export the header data
        with open( output_dir + "/header.txt", "a") as file:
            file.write( "Main Altitude     : " + str( main_alt           ) + " ft" )
            file.write( "Drogue Delay      : " + str( drogue_delay       ) + " s"  )
            file.write( "Main Deploy Time  : " + str( main_deploy_time   ) + " ms" )
            file.write( "Drogue Deploy Time: " + str( drogue_deploy_time ) + " ms" )
            file.write( "Landing Time      : " + str( land_time          ) + " ms" )

        # Export the flight data
        with open( output_dir + "/data.txt", 'w' ) as file:
            for sensor_frame in sensor_frames_filtered:
                for val in sensor_frame:
                    file.write( str( val ) )
                    file.write( '\t')
                file.write( '\n' )    
        return serialObj
        # dual-deploy extract #

    return serialObj 
## dual_deploy ##


####################################################################################
# END OF FILE                                                                      # 
####################################################################################