####################################################################################
#                                                                                  #
# sdec.py -- main terminal program. Contains main program                          #
#            loop and global objects                                               #
#                                                                                  #
# Author: Colton Acosta                                                            #
# Date: 4/16/2022                                                                  #
# Sun Devil Rocketry Avionics                                                      #
#                                                                                  #
####################################################################################

####################################################################################
# Developers                                                                       #
####################################################################################

__credits_2023__ = ["Nick Nguyen"       ,
                    "Anton Sazonov"     ,
                    "Brian Lew"         ,
                    "Alexander Linderman"]


####################################################################################
# Standard Imports                                                                 #
####################################################################################
import time
import serial
import serial.tools.list_ports

####################################################################################
# Project Modules                                                                  #
####################################################################################
import commands         # general terminal commands
import hw_commands      # general hardware commands
import valveController  # valve controller commands
import engineController # engine controller commands
import flightComputer   # flight computer commands
import canard_fc        # active roll application commands
from   config import *  # global settings


####################################################################################
# Global Variables                                                                 #
####################################################################################

# List of terminal commands
command_list = { 
                 "exit"       : commands.exitFunc                ,
                 "help"       : commands.helpFunc                ,
                 "clear"      : commands.clearConsole            ,
                 "comports"   : commands.comports                ,
                 "ping"       : commands.ping                    ,
				 "connect"    : commands.connect                 ,
                 "sol"        : valveController.sol              ,
                 "valve"      : valveController.valve            ,
                 "power"      : engineController.power           ,
                 "ignite"     : hw_commands.ignite               ,
                 "flash"      : hw_commands.flash                ,
                 "sensor"     : hw_commands.sensor               ,
                 "abort"      : engineController.hotfire_abort   ,
                 "telreq"     : engineController.telreq          ,
                 "pfpurge"    : engineController.pfpurge         ,
                 "fillchill"  : engineController.fillchill       ,
                 "standby"    : engineController.standby         ,
                 "hotfire"    : engineController.hotfire         ,
                 "getstate"   : engineController.hotfire_getstate,
                 "stophotfire": engineController.stop_hotfire    ,
                 "stoppurge"  : engineController.stop_purge      ,
                 "loxpurge"   : engineController.lox_purge       ,
                 "dual-deploy": flightComputer.dual_deploy       ,
                 "idle"       : canard_fc.idle                   ,
                 "imu-calibrate": canard_fc.imu_calibrate        ,
                 "pid-run"    : canard_fc.pid_run                ,
                 "fin-setup"  : canard_fc.fin_setup              ,
                 "pid-setup"  : canard_fc.pid_setup              ,
                 "access-terminal": canard_fc.terminal_access    ,
                 "read-preset": canard_fc.read_preset,
                 "save-preset": canard_fc.save_preset
                }


####################################################################################
#                                                                                  #
# OBJECT:                                                                          #
# 		terminalData                                                               #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		serial port user API and handler for passing data                          #
#       between command functions                                                  #
#                                                                                  #
####################################################################################
class terminalData:
    def __init__( self ):
        self.baudrate            = None
        self.comport             = None
        self.timeout             = None
        self.serialObj           = serial.Serial()
        self.config_status       = False 
        self.controller          = None
        self.firmware            = None
        self.flash_write_enabled = False 
        self.sensor_readouts     = {}
        self.engine_state        = None
        self.valve_states        = {}

    # Initialize Serial Port
    def initComport(self, baudrate, comport, timeout):
        self.baudrate            = baudrate 
        self.comport             = comport 
        self.timeout             = timeout 
        self.serialObj.baudrate  = self.baudrate
        self.serialObj.port      = self.comport
        self.serialObj.timeout   = self.timeout
        self.config_status       = True

    # Configure Serial port from class attributes
    def configComport(self):
        self.serialObj.baudrate = self.baudrate
        self.serialObj.port     = self.comport
        self.serialObj.timeout  = self.timeout

    # Open the serial port
    # returns a boolean variable indicating whether the port
    # connection was sucessful
    def openComport(self):

        # Ensure serial port has been properly configured 
        if(not self.config_status):
            print("Error: Cannot open serial port. Serial " +
                  "port has not been properly configured")
            return False

        # open port
        self.serialObj.open()
        return True

    # Close the serial port
    # Returns a boolean value indicating whether the port connection was 
    # successfully closed
    def closeComport(self):
        # check that the serial port is open
        if (not self.serialObj.is_open):
            print("No open serial port detected")
            return False
        else:
            self.serialObj.close()
            return True

	# Check if serial port is active
    def is_active(self):
        return self.serialObj.is_open

	# List available serial port connections
    def list_ports(self):
	    available_ports = serial.tools.list_ports.comports()
	    available_port_names = []
	    for port in available_ports:
		    available_port_names.append(port.device)
	    return available_port_names

    # Write a single Byte to the serial port
    def sendByte(self, byte):
        if (not self.serialObj.is_open):
            print("Error: Could not transmit byte over serial port. No active" \
                   +"serial port connection")
        else:
            self.serialObj.write(byte)

    # Write an array of bytes to the serial port 
    def sendBytes(self, byte_array):
        if (not self.serialObj.is_open):
            print("Error: Could not transmit byte over serial port. No active" \
                   +"serial port connection")
        else:
            self.serialObj.write( byte_array )

    # Read a single Byte from the serial port
    def readByte(self):
        if (not self.serialObj.is_open):
            print("Error: Could not read byte from serial port. No active" \
                   +"serial port connection")
        else:
             return self.serialObj.read()

    # Read multiple bytes from the serial port
    def readBytes( self, num_bytes ):
        if (not self.serialObj.is_open):
            print("Error: Could not read byte from serial port. No active" \
                   +"serial port connection")
        else:
            rx_bytes = []
            for i in range( num_bytes ):
                rx_bytes.append( self.serialObj.read() )
            return rx_bytes 

	# Set the SDR controller to enable board-specific commands
    def set_SDR_controller(self, controller_name, firmware_name = None ):
        self.controller = controller_name
        self.firmware   = firmware_name

	# Reset the SDR controller to disable board-specific commands
    def reset_SDR_controller(self):
        self.controller    = None
        self.firmware_name = None

    # Get the state of the liquid engine
    def get_engine_state( self ):
        return self.engine_state

    # Set the state of the liquid engine
    def set_engine_state( self, engine_state ):
        self.engine_state = engine_state
## class terminalData ##


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
# 		parseInput                                                                 #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		checks user input against command list options                             #
#                                                                                  #
####################################################################################
def parseInput(userin): 

    # Get rid of any whitespace
    userin.strip()

    # Split the input into commands and arguments
    userin = userin.split() 
    try:
        userCommand = userin[0]
        CommandArgs = userin[1:] 
    except TypeError:
        print("Error: Unsupported command")
        userin = input("SDR>> ")
        parseInput(userin)

    # Check if user input corresponds to a function
    for command in command_list: 
        if userCommand == command:
           return userin

    # User input doesn't correspond to a command
    print("Error: Unsupported command")
    userin = input("SDR>> ")
    return parseInput(userin)

####################################################################################
# Application Entry Point                                                          #
####################################################################################
if __name__ == '__main__':
    
    # Initialize Serial Port Object
    terminalSerObj = terminalData()

    # Look for possible connections
    avail_ports = serial.tools.list_ports.comports()
    for port_num, port in enumerate( avail_ports ):
        if ( 'CP2102' in port.description ):
            # Connect
            port_num = port.device
            connect_args  = [ '-p', port_num]
            commands.connect( connect_args, terminalSerObj )
            
    # Display command prompt
    while(True):
        # Command prompt
        userin         = input("SDR>> ")

        # Parse command
        userin_clean   = parseInput(userin)
        userCommand    = userin_clean[0]
        userArgs       = userin_clean[1:]

        # Execute Command
        execute = command_list[userCommand](userArgs, terminalSerObj)
        if isinstance(execute, tuple): 
            terminalSerObj, sdec_api_ignore = execute
        else:
            terminalSerObj = execute
## parseInput ##


####################################################################################
# END OF FILE
####################################################################################
