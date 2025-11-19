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

# Global imports
from queue import PriorityQueue
import math

# Project imports
import hw_commands
import controller

####################################################################################
# Global Variables                                                                 #
####################################################################################
dashboard_dump_size = 72 # constant
lora_packet_size = 96
dashboard_dump_opcode = b'\x30'

latest_data_dump = None # latest dashboard dump

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

# Queue of text messages
msg_queue = PriorityQueue()

# Vehicle information
vehicle_id = {
    'target': "[CONNECTING]",
    'firmware': "[CONNECTING]",
    'latency': 0,
    'sig_strength': 0,
    'status': "[CONNECTING]"
}

def get_next_msg():
    return msg_queue.get( block=False )

def lora_recieve_next( Args, serialObj ):
    global latest_data_dump
    raw_bytes = []
    header = []
    payload = []

    serialObj.serialObj.reset_input_buffer()
    serialObj.sendByte( dashboard_dump_opcode )

    # print("Header Contents:")
    # print("    UID:       " + str(header[0:12]))
    # print("    MID:       " + str(header[12:16]))
    # print("    TIMESTAMP: " + str(header[16:]))


    for byteNum in range( lora_packet_size ):
        to_append = serialObj.readByte()
        raw_bytes.append( to_append )
    
    header = raw_bytes[0:20]
    payload = raw_bytes[20:]

    mid = int.from_bytes(b"".join(header[12:16]), 'little')
    match mid:
        case 1: # vehicle id
            vehicle_id["target"] = controller.controller_names[payload[0]]
            vehicle_id["firmware"] = controller.firmware_ids[payload[1]]
            vehicle_id["status"] = "OK"
        case 2: # dashboard dump
            # print("FSM State: " + str(payload[0]))
            serialObj, latest_data_dump = dashboard_parse_dump( payload[1:1+dashboard_dump_size], serialObj )
        case 3: # warning msg
            msg_queue.put_nowait(0, ("warn", str(payload)))
        case 4: # info msg
            msg_queue.put_nowait(1, ("info", str(payload)))
        case _:
            print(f"ERROR: Unsupported wireless msg type {mid}.")
            return serialObj, False

    return serialObj, True

def dashboard_dump( Args, serialObj ):
    global latest_data_dump

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


    serialObj, latest_data_dump = dashboard_parse_dump( sensor_bytes_list, serialObj )

    return serialObj, True

# Parse the dashboard dump
# Args:
#   - sensor_bytes_list: raw data from FC
#   - serialObj: serial object from caller
def dashboard_parse_dump( sensor_bytes_list, serialObj ):
    # Verify compatible controller
    if serialObj.controller not in controller.dashboard_dump_supported_boards:
        print("UNSUPPORTED CONTROLLER: " + serialObj.controller)
        return serialObj, None
    # Get readouts from byte array
    serialObj.sensor_readouts = hw_commands.get_sensor_readouts( 
                                                    "Flight Computer (A0002 Rev 2.0)", 
                                                    sensor_numbers      ,
                                                    sensor_bytes_list
                                                    )
    # Readouts list for SDEC-API
    readouts = []

    # Display Sensor readouts
    for sensor in serialObj.sensor_readouts:
        readout_formatted = hw_commands.format_sensor_readout(
                                                "Flight Computer (A0002 Rev 2.0)",
                                                sensor               ,
                                                serialObj.sensor_readouts[sensor]
                                                )
        # print( readout_formatted )
        readouts.append(readout_formatted)

    # print(serialObj.sensor_readouts)

    # sanitize invalid values
    for key in serialObj.sensor_readouts:
        if math.isinf(serialObj.sensor_readouts[key]):
            serialObj.sensor_readouts[key] = 999999
        
    return serialObj, serialObj.sensor_readouts