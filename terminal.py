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
    def configComport(baudrate, comport, timeout):
        self.baudrate = baudrate 
        self.comport = comport 
        self.timeout = timeout 
        self.config_status = True

    # Open the serial port
    def openComport():
        # Ensure serial port has been properly configured 
        if(not self.config_status):
            print("Error: Cannot open serial port. Serial port has not been properly configured")
            return

        # open port
        self.serialObj.open()

    # Close the serial port
    def closeComport():
        # check that the serial port is open
        if (not self.serialObj.is_open):
            print("No open serial port detected")
        else:
            self.serialObj.close()

    # Write a single Byte to the serial port
    def sendByte(data):
        if (not self.serialObj.is_open):
            print("Error: Could not transmit byte over serial port. No active" \
                   +"serial port connection")
        else:
            self.serialObj.write(data)

    # Read a single Byte from the serial port
    def readByte():
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
    userinSplit = userin.split() 
    userCommand = userinSplit[0]
    CommandArgs = userinSplit[1:] 

    # Check if user input corresponds to a function
    for command in commands.command_list: 
        if userCommand == command:
           commands.command_list[command](CommandArgs)
           return

    # User input doesn't correspond to a command
    print("Error: Unsupported command")
    userin = input("SDR>> ")
    parseInput(userin)

# Program Loop
while(True):
    # Command prompt
    userin = input("SDR>> ")

    # Parse and eecute command
    parseInput(userin)

