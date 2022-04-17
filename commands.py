### Commands.py -- module with all command line functions 
### Author: Colton Acosta
### Date: 4/16/2021
### Sun Devil Rocketry Avionics

# Standard Imports
import sys
from datetime import date
import time
import os

# exitFunc -- quits the program
def exitFunc(Args):
   sys.exit()

# helpFunc -- displays list of commands
def helpFunc(Args):
    print('Terminal Control Commands: \n')
    print("\tclear: clears the terminal window\n")
    print("\thelp: displays the termincal control commands\n")
    print("\texit: exits the program\n")

# clearConsole -- clears the python terminal
def clearConsole(Args):
    command = 'clear'
    if os.name in ('nt', 'dos'):
        command = 'cls'
    os.system(command)

# Command List
commands = { "exit": exitFunc,
             "help": helpFunc,
             "clear": clearConsole
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
    print("Unsupportred command")
    userin = input("> ")
    parseInput(userin)

### END OF FILE
