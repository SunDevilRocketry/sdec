# Python terminal program for SDR PCBs 

# Library imports
import time
import serial
import serial.tools.list_ports

# SDR modules
import commands # functions for each terminal command

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

