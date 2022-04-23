### Commands.py -- module with all command line functions 
### Author: Colton Acosta
### Date: 4/16/2021
### Sun Devil Rocketry Avionics

# Standard Imports
import sys
import os
import serial.tools.list_ports

# Global Variables
serialPort = None
baudrate = None
timeout = 1

# exitFunc -- quits the program
def exitFunc(Args):
   sys.exit()

# helpFunc -- displays list of commands
def helpFunc(Args):
    with open('doc/manpage') as file: 
        doc_lines = file.readlines()
    print()
    for line in doc_lines:
        print(line, end="")

# clearConsole -- clears the python terminal
def clearConsole(Args):
    command = 'clear'
    if os.name in ('nt', 'dos'):
        command = 'cls'
    os.system(command)

# comports -- connects to a USB device or displays connectivity info
def comports(Args):

    # Check that user has supplied correct amount of info
    if (len(Args) == 0):
        print("Error: no options supplied to comports function")
        return
    elif (len(Args) > 3):
        print("Error: too many options/arguments supplied to comports function")
        return

    # Function Args parsing:
    option = Args[0]
    port_supplied = False
    baudrate_supplied = False
    if (len(Args) >= 2):
        target_port = Args[1]
        port_supplied = True
    if (len(Args) == 3):
        try: 
            input_baudrate = int(Args[2])
            baudrate_supplied = True
        except ValueError:
            print("Error: invalid baudrate. Check that baudrate is in bits/s and is an integer")
            return

    # List Option (-l): Scan available ports and display connections
    if (option == "-l"):
        avail_ports = serial.tools.list_ports.comports()
        print("\nAvailable COM ports: ")
        for port_num,port in enumerate(avail_ports):
            print("\t" + str(port_num) + ": " + port.device + " - ", end="") 
            if (port.manufacturer != None):
                print(port.manufacturer + ": ", end="")
            if (port.description != None):
                print(port.description)
            else:
                print("device info unavailable")
        print()
        return

    # Help Option (-h): Display all usage information for comports command
    elif (option == "-h"):
        with open("doc/comports") as file:
            comports_doc_lines = file.readlines()
        print()
        for line in comports_doc_lines:
            print(line, end='')
        print()
        return

    # Connect Option (-c): Connect to a USB port
    elif (option == "-c"):
        # Check that port has been supplied
        if (not port_supplied):
            print("Error: no port supplied to comports function")
            return
        elif (not baudrate_supplied):
            print("Error: no baudrate supplied to comports function")
            return

        # Check that inputed port is valid
        avail_ports = serial.tools.list_ports.comports()
        avail_ports_devices = []
        for port in avail_ports:
            avail_ports_devices.append(port.device)
        if (not (target_port in avail_ports_devices)):
            print("Error: Invalid serial port\n")
            comports(["-l"])
            return

        # Set global variables
        global baudrate
        baudrate = input_baudrate
        global serialPort 
        serialPort = target_port
        print("Connected to port " + serialPort + " at " + str(baudrate) + " baud")
        return


    # Disconnect Option (-d): Disconnect a USB device
    elif (option == "-d"):
        baudrate = None
        serialPort = None
        print("Disconnected from active serial port")

    # Invalid Option
    else:
        print("Error: \"" + option + "\" is an invalid option for comports")

# ping - transmit a byte over an active USB connection and await respone from board
def ping(Args):

    # Check for an active serial port connection and valid options/arguments
    if (serialPort == None):
        print("Error: no active serial port connection. Run the comports -c command to connect to a device")
        return
    elif (len(Args) < 1):
        print("Error: no options supplied to ping function")
        return
    elif (len(Args) > 2):
        print("Error: too many options/arguments supplied to ping function")
    else:

        # Arguments parsing
        option = Args[0]
        timeout_supplied = False
        if (len(Args) == 2):
            input_timeout = Args[1]
            timeout_supplied = True

        # Help option
        if (option == "-h"):
            with open("doc/ping") as file:
                comports_doc_lines = file.readlines()
            print()
            for line in comports_doc_lines:
                print(line, end='')
            print()
            return

        # Ping option
        elif (option == "-t"):
            print("Pinging ...")
            return

        # Ping option 
        else:
            print("Error: invalid option supplied to ping function")
            return

# Command List
command_list = { "exit": exitFunc,
                 "help": helpFunc,
                 "clear": clearConsole,
                 "comports": comports,
                 "ping": ping
                }

### END OF FILE
