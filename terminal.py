# Python terminal program for SDR PCBs 

# Library imports
import time
import serial
import serial.tools.list_ports

# SDR modules
import commands # functions for each terminal command

#serialPortDir = '/dev/ttyUSB1'
#baudrate = 9600
#serialDataObj = serial.Serial(serialPortDir, baudrate=baudrate, timeout = 1)
#while True:
    #data = serialDataObj.readline()
    #data = data.decode("UTF-8")
    #data = data.strip()
    #if (data != ""):
    #    print(data)
#    serialDataObj.write(b'1');
#    time.sleep(1)

# Program Loop
while(True):
    # Command prompt
    userin = input("> ")

    # Parse and execute command
    commands.parseInput(userin)

