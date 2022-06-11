# Python terminal program for SDR PCBs 

# Library imports
import time
import serial
import serial.tools.list_ports

# SDR modules
import commands # functions for each terminal command
import valveController # functions for valve controller commands

# Serial Port Object
# Used to access a serial port and pass serial information
# to terminal command functions
class terminalData:
    def __init__(self):
        self.baudrate = None
        self.comport = None
        self.timeout = None
        self.serialObj = serial.Serial()
        self.config_status = False 
        self.controller = None

    # Initialize Serial Port
    def initComport(self, baudrate, comport, timeout):
        self.baudrate = baudrate 
        self.comport = comport 
        self.timeout = timeout 
        self.serialObj.baudrate = self.baudrate
        self.serialObj.port = self.comport
        self.serialObj.timeout = self.timeout
        self.config_status = True

    # Configure Serial port from class attributes
    def configComport(self):
        self.serialObj.baudrate = self.baudrate
        self.serialObj.port = self.comport
        self.serialObj.timeout = self.timeout

    # Open the serial port
    # returns a boolean variable indicating whether the port connection
    # was sucessful
    def openComport(self):

        # Ensure serial port has been properly configured 
        if(not self.config_status):
            print("Error: Cannot open serial port. Serial port has not been properly configured")
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
    def sendByte(self, data):
        if (not self.serialObj.is_open):
            print("Error: Could not transmit byte over serial port. No active" \
                   +"serial port connection")
        else:
            self.serialObj.write(data)

    # Read a single Byte from the serial port
    def readByte(self):
        if (not self.serialObj.is_open):
            print("Error: Could not read byte from serial port. No active" \
                   +"serial port connection")
        else:
             return self.serialObj.read()

	# Set the SDR controller to enable board-specific commands
    def set_SDR_controller(self, controller_name):
        self.controller = controller_name

	# Reset the SDR controller to disable board-specific commands
    def reset_SDR_controller(self):
        self.controller = None

# Command List
command_list = { "exit"     : commands.exitFunc,
                 "help"     : commands.helpFunc,
                 "clear"    : commands.clearConsole,
                 "comports" : commands.comports,
                 "ping"     : commands.ping,
				 "connect"  : commands.connect,
                 "sol"      : valveController.sol
                }

# parseInput -- checks user input against command list 
#               options
# input: userin: user inputed string
#        pcbs: PCB bom object
# output: none
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

## Program Loop

# Initialize Serial Port Object
terminalSerObj = terminalData()

while(True):
    # Command prompt
    userin = input("SDR>> ")

    # Parse command
    userin_clean = parseInput(userin)
    userCommand = userin_clean[0]
    userArgs = userin_clean[1:]

    # Execute Command
    terminalSerObj = command_list[userCommand](userArgs, terminalSerObj)

### END OF FILE
