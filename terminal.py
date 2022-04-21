# Python terminal program for SDR PCBs 

# Library imports
import time
import serial
import serial.tools.list_ports

# SDR modules
import commands # functions for each terminal command

# Program Loop
while(True):
    # Command prompt
    userin = input("> ")

    # Parse and eecute command
    commands.parseInput(userin)

