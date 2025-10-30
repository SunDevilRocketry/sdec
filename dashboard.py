#################################################################################### 
#                                                                                  # 
# dashboard.py -- module with commands for operation with the dashboard            #
#                                                                                  #
# Author: Eli Sells                                                                # 
# Date: 10/14/2025                                                                 #
# Sun Devil Rocketry Avionics                                                      #
#                                                                                  #
#################################################################################### 

####################################################################################
# Imports                                                                          #
####################################################################################

# Project imports
import hw_commands

####################################################################################
# Global Variables                                                                 #
####################################################################################
dashboard_dump_size = 72 # constant
dashboard_dump_opcode = b'\x30'

# List of sensors used in the dashboard dump
sensor_numbers = [
    "accXconv",
    "accYconv",
    "accZconv",
    "gyroXconv",
    "gyroYconv",
    "gyroZconv",
    "rollDeg",
    "pitchDeg",
    "yawDeg",
    "rollRate",
    "pitchRate",
    "yawRate",
    "pres",
    "temp",
    "alt",
    "bvelo",
    "long",
    "lat"
    ]

def dashboard_dump( Args, serialObj ):
    # Locals
    sensor_bytes_list = []

    # Flush & send opcode
    serialObj.serialObj.reset_input_buffer()
    serialObj.sendByte( dashboard_dump_opcode )

    # Recieve data from controller
    for byteNum in range( dashboard_dump_size ):
        to_append = serialObj.readByte()
        #readouts.append(to_append) bytes not json readable
        sensor_bytes_list.append( to_append )


    # print(sensor_bytes_list)

    # Get readouts from byte array
    serialObj.sensor_readouts = hw_commands.get_sensor_readouts( 
                                                    serialObj.controller, 
                                                    sensor_numbers      ,
                                                    sensor_bytes_list
                                                    )
    # Readouts list for SDEC-API
    readouts = []

    # Display Sensor readouts
    for sensor in serialObj.sensor_readouts:
        readout_formatted = hw_commands.format_sensor_readout(
                                                serialObj.controller,
                                                sensor               ,
                                                serialObj.sensor_readouts[sensor]
                                                )
        # print( readout_formatted )
        readouts.append(readout_formatted)
        
    return serialObj, serialObj.sensor_readouts