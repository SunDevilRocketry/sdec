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
    for line in doc_lines:
        print(line)

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
    elif (Args[0] == "-l"):
        avail_ports = serial.tools.list_ports.comports()
        print("Available COM ports: ")
        for port_num,port in enumerate(avail_ports):
            print("\t" + str(port_num) + ": " + port.device + " - ", end="") 
            if (port.manufacturer != None):
                print(port.manufacturer + ": ", end="")
            if (port.description != None):
                print(port.description)
            else:
                print("device info unavailable")

    elif (Args[0] == "-h"):
        with open("doc/comports") as file:
            comports_doc_lines = file.readlines()
        for line in comports_doc_lines:
            print(line, end='')
    elif (Args[0] == "-c"):
        print("connect")
    elif (Args[0] == "-d"):
        print("disconnect")
    else:
        print("Error: \""+Args[0]+"\" is an invalid option for comports")


# Command List
commands = { "exit": exitFunc,
             "help": helpFunc,
             "clear": clearConsole,
             "comports": comports
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
    userinSplit = userin.split() 
    userCommand = userinSplit[0]
    CommandArgs = userinSplit[1:] 

    # Check if user input corresponds to a function
    for command in commands: 
        if userCommand == command:
           commands[command](CommandArgs)
           return

    # User input doesn't correspond to a command
    print("Error: Unsupportred command")
    userin = input("> ")
    parseInput(userin)

### END OF FILE
