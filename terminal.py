# Python terminal program for SDR PCBs 

# Library imports
import time
import serial
import serial.tools.list_ports

# SDR modules
import commands # functions for each terminal command

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

    # Configure Serial Port
    def configComport(self, baudrate, comport, timeout):
        self.baudrate = baudrate 
        self.comport = comport 
        self.timeout = timeout 
        self.serialObj.baudrate = self.baudrate
        self.serialObj.port = self.comport
        self.serialObj.timeout = self.timeout
        self.config_status = True

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
    userCommand = userin[0]
    CommandArgs = userin[1:] 

    # Check if user input corresponds to a function
    for command in commands.command_list: 
        if userCommand == command:
           #commands.command_list[command](CommandArgs)
           return userin

    # User input doesn't correspond to a command
    print("Error: Unsupported command")
    userin = input("SDR>> ")
    parseInput(userin)

## Program Loop

# Initialize Serial Port Object
terminalSerObj = terminalData()

while(True):
    # Command prompt
    userin = input("SDR>> ")

    # Parse command
    userin = parseInput(userin)
    userCommand = userin[0]
    userArgs = userin[1:]

    # Execute Command
    terminalSerObj = commands.command_list[userCommand](userArgs, terminalSerObj)


