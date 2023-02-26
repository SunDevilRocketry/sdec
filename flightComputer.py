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
        print( "Display status here" )

    return serialObj 
## dual_deploy ##


####################################################################################
# END OF FILE                                                                      # 
####################################################################################