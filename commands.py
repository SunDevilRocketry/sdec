### Commands.py -- module with all command line functions 
### Author: Colton Acosta
### Date: 4/16/2021
### Sun Devil Rocketry Avionics

# Standard Imports
import sys
import os
import serial.tools.list_ports
import time

# Global Variables
default_timeout = 1 # 1 second timeout

# exitFunc -- quits the program
def exitFunc(Args, serialObj):
   sys.exit()

# helpFunc -- displays list of commands
def helpFunc(Args, serialObj):
    with open('doc/manpage') as file: 
        doc_lines = file.readlines()
    print()
    for line in doc_lines:
        print(line, end="")
    return serialObj 
    

# clearConsole -- clears the python terminal
def clearConsole(Args, serialObj):
    command = 'clear'
    if os.name in ('nt', 'dos'):
        command = 'cls'
    os.system(command)
    return serialObj 

# comports -- connects to a USB device or displays connectivity info
def comports(Args, serialObj):

    # Check that user has supplied correct amount of info
    if (len(Args) == 0):
        print("Error: no options supplied to comports function")
        return serialObj
    elif (len(Args) > 3):
        print("Error: too many options/arguments supplied to comports function")
        return serialObj

    # Function Args parsing:
    option = Args[0]
    port_supplied = False
    baudrate_supplied = False
    if (len(Args) >= 2):
        target_port = Args[1]
        port_supplied = True
    if (len(Args) == 3):
        try: 
            baudrate = int(Args[2])
            baudrate_supplied = True
        except ValueError:
            print("Error: invalid baudrate. Check that baudrate is in bits/s and is an integer")
            return serialObj

    # List Option (-l): Scan available ports and display connections
    if (option == "-l"):
        avail_ports = serial.tools.list_ports.comports()
        print("\nAvailable COM ports: ")
        for port_num,port in enumerate(avail_ports):
            print("\t" + str(port_num) + ": " + port.device + " - ", end="") 
            if (port.manufacturer != None):
                print(port.manufacturer + ": ", end="")
            if (port.description != None):
                print(port.product)
            else:
                print("device info unavailable")
        print()
        return serialObj

    # Help Option (-h): Display all usage information for comports command
    elif (option == "-h"):
        with open("doc/comports") as file:
            comports_doc_lines = file.readlines()
        print()
        for line in comports_doc_lines:
            print(line, end='')
        print()
        return serialObj

    # Connect Option (-c): Connect to a USB port
    elif (option == "-c"):
        # Check that port has been supplied
        if (not port_supplied):
            print("Error: no port supplied to comports function")
            return serialObj
        elif (not baudrate_supplied):
            print("Error: no baudrate supplied to comports function")
            return serialObj

        # Check that inputed port is valid
        avail_ports = serial.tools.list_ports.comports()
        avail_ports_devices = []
        for port in avail_ports:
            avail_ports_devices.append(port.device)
        if (not (target_port in avail_ports_devices)):
            print("Error: Invalid serial port\n")
            comports(["-l"])
            return serialObj

        # Initialize Serial Port
        serialObj.initComport(baudrate, target_port, default_timeout)

        # Connect to serial port
        connection_status = serialObj.openComport()
        if(connection_status):
            print("Connected to port " + target_port + " at " + str(baudrate) + " baud")

        return serialObj


    # Disconnect Option (-d): Disconnect a USB device
    elif (option == "-d"):
        connection_status = serialObj.closeComport()
        if (connection_status):
            print("Disconnected from active serial port")
            return serialObj
        else: 
            print("An error ocurred while closing port " + target_port)
            return serialObj

    # Invalid Option
    else:
        print("Error: \"" + option + "\" is an invalid option for comports")

    return serialObj

# ping - transmit a byte over an active USB connection and await respone from board
def ping(Args, serialObj):

    # Check for an active serial port connection and valid options/arguments
#    if (not serialObj.serialObj.is_open):
#        print("Error: no active serial port connection. Run the comports -c command to connect to a device")
#        return serialObj
    if (len(Args) < 1):
        print("Error: no options supplied to ping function")
        return serialObj
    elif (len(Args) > 2):
        print("Error: too many options/arguments supplied to ping function")
    else:

        # Arguments parsing
        option = Args[0]
        timeout_supplied = False
        if (len(Args) == 2):
            try:
                input_timeout = float(Args[1])
                timeout_supplied = True
            except ValueError:
                print("Error: Invalid ping timeout.")
                return serialObj

        # Help option
        if (option == "-h"):
            with open("doc/ping") as file:
                comports_doc_lines = file.readlines()
            print()
            for line in comports_doc_lines:
                print(line, end='')
            print()
            return serialObj

        # Ping option
        elif (option == "-t"):
            # Check for valid serial port connection
            if (not serialObj.serialObj.is_open):
                print("Error: no active serial port connection. Run the comports -c command to connect to a device")
                return serialObj

            # Set timeout
            serialObj.timeout = input_timeout
            serialObj.configComport()

            # Ping
            opcode = b'\x01'
            ping_start_time = time.time()
            serialObj.sendByte(opcode)
            print("Pinging ...")
            readData = serialObj.serialObj.read()
            if (readData == b''):
                print("Timeout expired. No device response recieved.")
            else:
                ping_recieve_time = time.time()
                ping_time = ping_recieve_time - ping_start_time
                ping_time *= 1000.0
                print("Response recieved at {0:1.4f} ms".format(ping_time))
            return serialObj

        # Ping option 
        else:
            print("Error: invalid option supplied to ping function")
            return serialObj

# Command List
command_list = { "exit": exitFunc,
                 "help": helpFunc,
                 "clear": clearConsole,
                 "comports": comports,
                 "ping": ping
                }

### END OF FILE
