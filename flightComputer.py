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

# Project imports
from   config      import *
from   hw_commands import byte_array_to_int
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
                       'status' : {}
                         }
    
    # Maximum number of arguments
    max_args = 1

    # Opcode
    opcode = b'\xA0'

    # Subcommand opcodes
    sub_opcodes = {
                  'status': b'\x01'
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
    return serialObj 
## dual_deploy ##


####################################################################################
# END OF FILE                                                                      # 
####################################################################################