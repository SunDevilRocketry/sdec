# Python terminal program for SDR PCBs 

# Library imports
import time
import serial

serialPortDir = '/dev/ttyUSB1'
baudrate = 9600
serialDataObj = serial.Serial(serialPortDir, baudrate=baudrate, timeout = 1)
while True:
    #data = serialDataObj.readline()
    #data = data.decode("UTF-8")
    #data = data.strip()
    #if (data != ""):
    #    print(data)
    serialDataObj.write(b'1');
    time.sleep(1)
