### Commands.py -- module with all command line functions 
### Author: Colton Acosta
### Date: 4/16/2021
### Sun Devil Rocketry Avionics

# Standard Imports
import sys
import os
import serial.tools.list_ports

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
    if (len(Args) == 0):
        print("Error: no options supplied to comports function")

    # Function Args:
    option = Args[0]
    port_supplied = False
    if (len(Args) == 2):
        target_port = Args[1]
        port_supplied = True

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
        for line in comports_doc_lines:
            print(line, end='')
        return

    # Connect Option (-c): Connect to a USB port
    elif (option == "-c"):
        # Check that port has been supplied
        if (not port_supplied):
            print("Error: no port supplied to comports function")
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

        print("Connected to " + target_port)
        return


    # Disconnect Option (-d): Disconnect a USB device
    elif (option == "-d"):
        print("disconnect")

    # Invalid Option
    else:
        print("Error: \"" + option + "\" is an invalid option for comports")


# Command List
command_list = { "exit": exitFunc,
                 "help": helpFunc,
                 "clear": clearConsole,
                 "comports": comports
                }

### END OF FILE
