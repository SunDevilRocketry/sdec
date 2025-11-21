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
import secrets

# Project imports
import hw_commands
import controller
import commands

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

# Command handler for the telemetry system
def telem_cmd_handler( Args, serialObj ):

    # Standard command handler setup for extensibility
    telem_inputs= { 
        'upload'  : {
            'file' : 'A file name for telemetry configs.'
                    },
        'generate': {
                    }
    }

    command_type = 'subcommand'
    
    parse_check = commands.parseArgs(
                            Args,
                            2,
                            telem_inputs,
                            command_type 
                            )

    # Return if user input fails parse checks
    if ( not parse_check ):
        return serialObj 
    
    # Command opcode
    user_command = b'\x31'

    # Set subcom
    user_subcommand = Args[0]

    match user_subcommand:
        case 'upload':
            filename = Args[1]
            return telem_upload( serialObj, user_command, b'\x01', filename )
        case 'generate':
            filename = Args[1]
            return telem_generate( serialObj, filename )
        
    return serialObj, False

def telem_upload( serialObj, user_command, user_subcommand, filename ):
    file = filename

    with open(file, "r") as f:
        key = bytes.fromhex(f.readline())
        freq = int(f.readline()).to_bytes(4, byteorder='little')
        spread = int(f.readline()).to_bytes(1, byteorder='little')
        bandwidth = int(f.readline()).to_bytes(1, byteorder='little')

        print( str( key + freq + spread + bandwidth ) )

        serialObj.sendByte( user_command )
        serialObj.sendByte( user_subcommand )

    return serialObj, True # Stubbed for now

# Generate telemetry presets
def telem_generate( serialObj, filename ):
    print("Beginning interactive telemetry preset generation.")

    file = filename

    print("\nGenerating AES key...")
    key = secrets.token_hex(16)

    # input = float. take this float and mult by 1000 to get KHz. truncate remaining decimals.
    freq = int(1000 * float(input("\nEnter selected frequency (in MHz w/ decimals): ")))
    if freq > 928000 or freq < 902000:
        print("The selected frequency is outside of the legal ISM band. Exiting.")
        return serialObj, False

    spread = int(input("\nEnter spreading factor (6-12): "))
    if spread > 12 or spread < 6:
        print("Invalid spreading factor. Exiting (try again).")
        return serialObj, False
    
    print("\nAvailable bandwidths:")
    print("  0 - 7.8 kHz")
    print("  1 - 10.4 kHz")
    print("  2 - 15.6 kHz")
    print("  3 - 20.8 kHz")
    print("  4 - 31.25 kHz")
    print("  5 - 41.7 kHz")
    print("  6 - 62.5 kHz")
    print("  7 - 125 kHz")
    print("  8 - 250 kHz")
    print("  9 - 500 kHz")
    bandwidth = int(input("Select your bandwidth setting: "))
    if bandwidth < 0 or bandwidth > 9:
        print("Invalid bandwidth selection. Exiting.")
        return serialObj, False
    
    print("\nWriting to file...")

    with open(file, "w") as f:
        f.write(key + "\n" + str(freq) + "\n" + str(spread) + "\n" + str(bandwidth))

    print("\nDone!")
    
    return serialObj, True