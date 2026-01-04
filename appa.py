
####################################################################################
#                                                                                  #
# appa.py -- Contains functions related to APPA prototype                          #
#                                                                                  #
# Author(s): Eli Sells, Journey Hancock, Joseph Hawkins, Nicholas Armistead        #
# Date: 05/17/2025                                                                 #
# Sun Devil Rocketry Avionics                                                      #
#                                                                                  #
####################################################################################

####################################################################################
# Imports                                                                          #
####################################################################################
import csv
import struct
import crc32c #specific library for the checksum algorithm in Python
import math
import numpy as np

import commands
import hw_commands
import sensor_conv

####################################################################################
# Global Variables                                                                 #
####################################################################################

appa_data_bitmasks = {
    "conv": (2 ** 0),
    "state_estim": (2 ** 1),
    "gps": (2 ** 2),
    "canard": (2 ** 3)
}

appa_sensor_names = {
    "conv": {
        "accXconv" :     "Pre-converted Accel X",
        "accYconv" :     "Pre-converted Accel Y",
        "accZconv" :     "Pre-converted Accel Z",
        "gyroXconv" :    "Pre-converted Gyro X",
        "gyroYconv" :    "Pre-converted Gyro Y",
        "gyroZconv" :    "Pre-converted Gyro Z",
        "magXconv" :    "Pre-converted Mag X",
        "magYconv" :    "Pre-converted Mag Y",
        "magZconv" :    "Pre-converted Mag Z",
        "pres" :         "Barometric Pressure   ",
        "temp" :         "Barometric Temperature"
    },
    "state_estim": {
        "rollDeg"    :   "Roll Body Angle",
        "pitchDeg"    :  "Pitch Body Angle",
        "yawDeg"    :  "Pitch Body Angle",
        "rollRate"    :  "Roll Body Rate",
        "pitchRate"    : "Pitch Body Rate",
        "yawRate"    : "Pitch Body Rate",
        "velo"   :       "Velocity",
        "velo_x" :       "Velo X",
        "velo_y" :       "Velo Y",
        "velo_z" :       "Velo Z",
        "pos"   :        "Position",
        "alt" :          "Barometric Altitude",
        "bvelo" :        "Barometric Velocity"
    },
    "gps": {
        "altg" :         "GPS Altitude (ft)",
        "speedg":        "GPS Speed (KmH)",
        "utc_time":      "GPS UTC time",
        "long":          "GPS Longitude (deg)",
        "lat":           "GPS Latitude (deg)",
        "ns":            "GPS North/South",
        "ew":            "GPS East/West",
        "gll_s":         "GPS GLL status",
        "rmc_s":         "GPS RMC status"
    },
    "canard": {
        "feedback":      "Canard Feedback"
    }
}

appa_sensor_sizes = {
    "conv": {
        "accXconv" :     4,
        "accYconv" :     4,
        "accZconv" :     4,
        "gyroXconv" :    4,
        "gyroYconv" :    4,
        "gyroZconv" :    4,
        "magXconv" :     4,
        "magYconv" :     4,
        "magZconv" :     4,
        "pres" :         4,
        "temp" :         4
    },
    "state_estim": {
        "rollDeg"    :   4,
        "pitchDeg"    :  4,
        "yawDeg"    :    4,
        "rollRate"    :  4,
        "pitchRate"    : 4,
        "yawRate"    :   4,
        "velo"   :       4,
        "velo_x" :       4,
        "velo_y" :       4,
        "velo_z" :       4,
        "pos"   :        4,
        "alt" :          4,
        "bvelo" :        4
    },
    "gps": {
        "altg" :         4,
        "speedg":        4,
        "utc_time":      4,
        "long":          4,
        "lat":           4,
        "ns":            1,
        "ew":            1,
        "gll_s":         1,
        "rmc_s":         1
    },
    "canard": {
        "feedback":      4
    }
}

appa_sensor_types = {
    "conv": {
        "accXconv" :     float,
        "accYconv" :     float,
        "accZconv" :     float,
        "gyroXconv" :    float,
        "gyroYconv" :    float,
        "gyroZconv" :    float,
        "magXconv" :     float,
        "magYconv" :     float,
        "magZconv" :     float,
        "pres" :         float,
        "temp" :         float
    },
    "state_estim": {
        "rollDeg"    :   float,
        "pitchDeg"    :  float,
        "yawDeg"       : float,
        "rollRate"    :  float,
        "pitchRate"    : float,
        "yawRate"      : float,
        "velo"   :       float,
        "velo_x" :       float,
        "velo_y" :       float,
        "velo_z" :       float,
        "pos"   :        float,
        "alt" :          float,
        "bvelo" :        float
    },
    "gps": {
        "altg" :         float,
        "speedg":        float,
        "utc_time":      float,
        "long":          float,
        "lat":           float,
        "ns":            int,
        "ew":            int,
        "gll_s":         int,
        "rmc_s":         int
    },
    "canard": {
        "feedback":      float
    }
}

# Turn a 2D list into a 1D list
def flatten_list(list):
    to_return = []

    for row in list:
        for item in row:
            to_return.append(item)

    return to_return

# Hold the data bitmask from parsing the preset
preset_data_bitmask = 0

"""
    Note: The length of "thing to print" should be 23 chars.
    "Firmmware version" : [
        {"header" : "header to print"},
        {"print" : "thing to print", "indices" : [byte indices of data], "type" : "data type"},
        {"delete" : index to delete up until}
    ]
"""
preset_size = 88
parse_preset_output_strings = {
    "APPA" : [
        {"header":  "==CONFIG DATA=="},
        {"print" : "Checksum:              ", "indices" : [0, 1, 2, 3], "type" : "int"},
        {"print" : "Feature bitmask:       ", "indices" : [4, 5, 6, 7], "type" : "int"},
        {"print" : "Data bitmask:          ", "indices" : [8, 9, 10, 11], "type" : "int"},
        {"print" : "Sensor calib samples:  ", "indices" : [12, 13], "type" : "int"},
        {"print" : "LD timeout             ", "indices" : [14, 15], "type" : "int"},
        {"print" : "LD baro threshold:     ", "indices" : [16, 17], "type" : "int"},
        {"print" : "LD accel threshold:    ", "indices" : [18], "type" : "int"},
        {"print" : "LD accel samples:      ", "indices" : [19], "type" : "int"},
        {"print" : "LD baro samples:       ", "indices" : [20], "type" : "int"},
        {"print" : "Minimum Frame Delta:   ", "indices" : [21], "type" : "int"},
        {"print" : "Apogee detect samples: ", "indices" : [22], "type" : "int"},
        {"print" : "Pad bits:              ", "indices" : [23, 24], "type" : "int"},
        {"print" : "AC max deflect angle:  ", "indices" : [25], "type" : "int"},
        {"print" : "AR Delay after launch: ", "indices" : [26, 27], "type" : "int"},
        {"print" : "AC Roll PID P const:   ", "indices" : [28, 29, 30, 31], "type" : "float"},
        {"print" : "AC Roll PID I const:   ", "indices" : [32, 33, 34, 35], "type" : "float"},
        {"print" : "AC Roll PID D const:   ", "indices" : [36, 37, 38, 39], "type" : "float"},
        {"print" : "AC P/Y PID P const:    ", "indices" : [40, 41, 42, 43], "type" : "float"},
        {"print" : "AC P/Y PID I const:    ", "indices" : [44, 45, 46, 47], "type" : "float"},
        {"print" : "AC P/Y PID D const:    ", "indices" : [48, 49, 50, 51], "type" : "float"},
        {"header" : "==IMU OFFSETS=="},
        {"print" : "Accel x offset:        ", "indices" : [52, 53, 54, 55], "type" : "float"},
        {"print" : "Accel y offset:        ", "indices" : [56, 57, 58, 59], "type" : "float"},
        {"print" : "Accel z offset:        ", "indices" : [60, 61, 62, 63], "type" : "float"},
        {"print" : "Gyro x offset:         ", "indices" : [64, 65, 66, 67], "type" : "float"},
        {"print" : "Gyro y offset:         ", "indices" : [68, 69, 70, 71], "type" : "float"},
        {"print" : "Gryo z offset:         ", "indices" : [72, 73, 74, 75], "type" : "float"},
        {"header" : "==BARO OFFSETS=="},
        {"print" : "Baro pres offset:      ", "indices" : [76, 77, 78, 79], "type" : "float"},
        {"print" : "Baro temp offset:      ", "indices" : [80, 81, 82, 83], "type" : "float"},
        {"header" : "==SERVO REF PTS=="},
        {"print" : "Servo 1 RP:            ", "indices" : [84], "type" : "int"},
        {"print" : "Servo 2 RP:            ", "indices" : [85], "type" : "int"},
        {"print" : "Servo 3 RP:            ", "indices" : [86], "type" : "int"},
        {"print" : "Servo 4 RP:            ", "indices" : [87], "type" : "int"}
    ]
}

# Note: there should be 23 chars before the value. Keep that number consistent.
def appa_parse_preset(serialObj, sensor_frame_int):
    global preset_data_bitmask
    
    output_strings = []
    preset_output_strings = parse_preset_output_strings["APPA"]

    for command in preset_output_strings:
        command_type = next(iter(command))

        match command_type:
            case "header":
                output_strings.append(command["header"])
            case "delete":
                del sensor_frame_int[:command["delete"]]
            case "print":
                to_print = command["print"]
                indices = command["indices"]
                data_type = command["type"]

                match data_type:
                    case "int":
                        value = 0
                        for i in range(len(indices) - 1, 0, -1):
                            index = indices[i]
                            value = value | (sensor_frame_int[index] << (8 * i))
                        value = value | sensor_frame_int[indices[0]]

                        # Check indices length first to reduce string in string checks
                        if len(indices) == 4 and "Data bitmask" in to_print: 
                            preset_data_bitmask = value
                        output_strings.append((to_print + "{}").format(value)) 
                    case "float":
                        value = [sensor_frame_int[indices[0]].to_bytes(1, "big"),
                                 sensor_frame_int[indices[1]].to_bytes(1, "big"),
                                 sensor_frame_int[indices[2]].to_bytes(1, "big"),
                                 sensor_frame_int[indices[3]].to_bytes(1, "big")]
                        value = hw_commands.byte_array_to_float(value)

                        output_strings.append((to_print + "{}").format(value))
                    case _:
                        raise ValueError("Unknown key {}".format(data_type))
            case _:
                raise ValueError("Unknown key {}".format(command_type))

    return output_strings

def appa_parse_telemetry_data(data: list[int], group: str) -> str:
    out_str = ""
    index = 0

    # Get the sensor sizes and data types for the conv, state_estim, gps, or canard group
    sensor_sizes = appa_sensor_sizes[group]
    sensor_types = appa_sensor_types[group]

    # Parse the sizes and types to extract them from sensor_frame_int
    for size, data_type, key in zip(sensor_sizes.values(), sensor_types.values(), sensor_sizes.keys()):
        if data_type is int:
            value = 0
            value_index = index + (size - 1) 
            for i in range(value_index, index, -1):
                value = value | data[i] << (8 * (value_index - index))
            value = value | data[index]
            
            # Apply conversions if applicable
            if key == "accX" or key == "accY" or key == "accZ":
                value = sensor_conv.imu_accel(value)
            if key == "gyroX" or key == "gyroY" or key == "gyroZ":
                value = sensor_conv.imu_gyro(value)

            out_str += (str(value) + ",")

            index += size # Increment current data index by the size we just extracted
        elif data_type is float:
            value = [data[index].to_bytes(1, "big"),
                        data[index + 1].to_bytes(1, "big"),
                        data[index + 2].to_bytes(1, "big"),
                        data[index + 3].to_bytes(1, "big")]
            value = hw_commands.byte_array_to_float(value)
            out_str += (str(value) + ",")

            index += size # Increment current data index by 4 (size of a float)
        else:
            raise ValueError("Unknown type")
        
    return out_str


def appa_parse_frame(frame: list[int], dataBitmask: int):
    # Exists in all
    out_line = ""
    out_line += str(frame[0]) + ","
    out_line += str(frame[1]) + ","

    # Time of frame measurement
    time = ( ( frame[2]       ) + 
             ( frame[3] << 8  ) + 
             ( frame[4] << 16 ) +
             ( frame[5] << 24 ) )
    
    # Conversion to seconds
    out_line += str( time / 1000 ) + ","

    del frame[0:6]

    if ( dataBitmask & appa_data_bitmasks.get("conv") != 0 ):
        out_line += appa_parse_telemetry_data(frame[0:44], "conv")
        del frame[0:44]
    if ( dataBitmask & appa_data_bitmasks.get("state_estim") != 0 ):
        out_line += appa_parse_telemetry_data(frame[0:52], "state_estim")
        del frame[0:52]
    if ( dataBitmask & appa_data_bitmasks.get("gps") != 0 ):
        out_line += appa_parse_telemetry_data(frame[0:24], "gps")
        del frame[0:24]
    if ( dataBitmask & appa_data_bitmasks.get("canard") != 0 ):
        out_line += appa_parse_telemetry_data(frame[0:4], "canard")
        del frame[0:4]

    return out_line


def calculate_sensor_frame_size(dataBitmask):
    size = 6
    if ( dataBitmask & appa_data_bitmasks.get("conv") != 0 ):
        size += 9 * 4 # IMU conv
        size += 2 * 4 # Baro raw
    if ( dataBitmask & appa_data_bitmasks.get("state_estim") != 0 ):
        size += 11 * 4 # IMU state estims
        size += 2 * 4 # Baro state estims
    if ( dataBitmask & appa_data_bitmasks.get("gps") != 0 ):
        size += 5 * 4 # GPS floats
        size += 4 * 1 # GPS chars
    if ( dataBitmask & appa_data_bitmasks.get("canard") != 0 ):
        size += 1 * 4 # canard feedback
    
    # Calculate
    sensor_frame_size = size
    preset_frame_size = size
    numFrames = 1
    while ( preset_frame_size < preset_size + 2 ):
        preset_frame_size += size
        numFrames += 1

    return sensor_frame_size, numFrames

def flash_extract_keys(dataBitmask):
    header_row = "save_bit,fc_state,time,"
    if ( dataBitmask & appa_data_bitmasks.get("conv") != 0 ):
        header_row += "accXconv,accYconv,accZconv,gyroXconv,gyroYconv,gyroZconv,magXconv,magYconv,magZconv,pres,temp,"
    if ( dataBitmask & appa_data_bitmasks.get("state_estim") != 0 ):
        header_row += "rollDeg,pitchDeg,yawDeg,rollRate,pitchRate,yawRate,velo,velo_x,velo_y,velo_z,pos,alt,bvelo,"
    if ( dataBitmask & appa_data_bitmasks.get("gps") != 0 ):
        header_row += "altg,speedg,utc_time,long,lat,ns,ew,gll_s,rmc_s,"
    if ( dataBitmask & appa_data_bitmasks.get("canard") != 0 ):
        header_row += "feedback,"

    return header_row[:-1]


def flash_extract_parse(serialObj, rx_byte_blocks):
    global preset_data_bitmask

    # Parse contents into bytes
    sensor_frame_int = []
    for sensor_block in rx_byte_blocks:
        for sensor_byte in sensor_block:
            sensor_frame_int.append( ord( sensor_byte ) )

    preset_int = []
    preset_strings = appa_parse_preset(serialObj, sensor_frame_int[2:preset_size + 2])

    #print(str(preset_data_bitmask))

    # Write presets to file
    with open( "output/appa_preset_data.txt", 'w' ) as file:
        for line in preset_strings:
            file.write(line + '\n')

    # Get data bitmask (idx 5)
    if( preset_data_bitmask == 0 or preset_data_bitmask == None ):
        print("Failed to parse preset data bitmask.")
        return serialObj

    sensor_frame_size, num_preset_frames = calculate_sensor_frame_size(preset_data_bitmask)

    #print( str(sensor_frame_size) )

    # This is where the fun begins
    # start = math.ceil(preset_size, sensor_frame_size)
    start = num_preset_frames * sensor_frame_size
    stop = int( start + sensor_frame_size )
    #print( str( start ) + " | " + str( stop ) )
    with open("output/appa_sensor_data.csv", "w") as outfile:
        outfile.write(flash_extract_keys(preset_data_bitmask) + "\n")
        # magic number should be moved
        while stop < 524288:
            outfile.write(appa_parse_frame(sensor_frame_int[start:stop], preset_data_bitmask) + "\n")
            start += sensor_frame_size
            stop += sensor_frame_size

    return serialObj

################################################################################
# Command: Preset                                                              #
################################################################################

def preset(Args, serialObj):

    # Subcommand and Options Dictionary
    preset_inputs = { 
    'upload'  : {
                },
    'download': {
                },
    'verify'  : {
                },
                  }

    parse_check = commands.parseArgs(
                            Args        ,
                            1           ,
                            preset_inputs,
                            'subcommand' 
                            )
    
    # Return if firmware version is incompatible 
    if serialObj.firmware != "APPA":
        print("Incompatible firmware version")
        return serialObj
    
    # Return if user input fails parse checks
    if ( not parse_check ):
        return serialObj 

    # Set subcommand, options, and input data
    user_subcommand = Args[0]

    ################################################################################
    # Subcommand: preset download                                                  #
    ################################################################################
    if (user_subcommand == "download"):
        serialObj.sendByte(b'\x24')
        download_preset(Args, serialObj)
        return serialObj
    
    elif (user_subcommand == "verify"):
        serialObj.sendByte(b'\x24')
        verify_preset(Args, serialObj)
        return serialObj
    
    elif (user_subcommand == "upload"):
        upload_preset(Args, serialObj)
        return serialObj


def download_preset(Args, serialObj):
    print("Download Preset")
    serialObj.serialObj.reset_input_buffer()
    serialObj.sendByte(b'\x02')

    # Read serial data
    rx_bytes = serialObj.readBytes(preset_size)

    print("Data received, beginning processing...")

    sensor_frame_int = []
    for sensor_byte in rx_bytes:
        sensor_frame_int.append( ord( sensor_byte ) )

    output_strings = appa_parse_preset(serialObj, sensor_frame_int)

    with open( "output/appa_preset_data.txt", 'w' ) as file:
        for line in output_strings:
            file.write(line + '\n')

    print("Data processed and written!\n")


    return serialObj

def verify_preset(Args, serialObj):
    print("Verify Preset")
    serialObj.serialObj.reset_input_buffer()
    serialObj.sendByte(b'\x03')

    # Read serial data
    rx_bytes = serialObj.readBytes(1)

    if (rx_bytes[0] == b'\x00'):
        print("Invalid Checksum.")
    else:
        print("Valid Checksum.")

def crc32_checksum(data_config):
    data_format = f'<{len(data_config)}f' #defines formatting based on size based of data_config file
    data_bytes = struct.pack(data_format, *data_config) #serializes data_config into bytes
    checksum = crc32c.crc32(data_bytes) #computes the checksum
    checksum_bytes = struct.pack('>I',checksum) #serializing checksum, checking big-endians
    payload = checksum_bytes+data_bytes #prepend the checksum to the data to form the final payload
    return payload

def upload_preset(Args, serialObj):
    print("Upload Preset")
    filename = input( "Enter filename: " )

    if filename == "":
        filename = "input/appa_config.csv"

    preset_list = []
    try:
      with open( filename, 'r' ) as file:
        csv_reader = csv.reader( file )
        for row in csv_reader:
            preset_list.append( row )
    except FileNotFoundError:
        print(f"Error: File not found: { filename }")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
    # print( preset_list )

    raw_data = [0,0,0,0,0,0,0,0] # Start with no features and no data

    # Construct the feature and data flags
    for byte_idx in range(0,4):
        for i in range(1,9):
            preset_list_row = i + 8 * byte_idx
            raw_data[byte_idx] += (int(preset_list[preset_list_row][4]) << (i - 1))
            raw_data[byte_idx + 4] += (int(preset_list[preset_list_row + 32][4]) << (i - 1))

    # print(raw_data)

    # Sensor Calibration
    raw_data.append(int(preset_list[65][4]) & int('00FF', 16)) # LSB
    raw_data.append((int(preset_list[65][4]) & int('FF00', 16)) >> 8) # MSB

    # Launch Detect
    raw_data.append(int(preset_list[66][4]) & int('00FF', 16)) # LSB
    raw_data.append((int(preset_list[66][4]) & int('FF00', 16)) >> 8) # MSB

    raw_data.append(int(preset_list[67][4]) & int('00FF', 16)) # LSB
    raw_data.append((int(preset_list[67][4]) & int('FF00', 16)) >> 8) # MSB

    raw_data.append(int(preset_list[68][4]))

    raw_data.append(int(preset_list[69][4]))

    raw_data.append(int(preset_list[70][4]))

    # Minimum time for frame
    raw_data.append(int(preset_list[71][4]))

    raw_data.append(int(preset_list[72][4])) # apogee detect
    raw_data.append(0)
    raw_data.append(0)

    # Active Roll
    raw_data.append(int(preset_list[73][4]))

    raw_data.append(int(preset_list[74][4]) & int('00FF', 16)) # LSB
    raw_data.append((int(preset_list[74][4]) & int('FF00', 16)) >> 8) # MSB

    # 24 bytes of floats
    for i in range(75,81):
        ba = bytearray(struct.pack("f", float(preset_list[i][4])))
        raw_data.append(int(ba[0]))
        for j in range(1, 4):
            raw_data.append(int(ba[j]))

    print(len(raw_data))
    checksum = crc32c.crc32(bytearray(raw_data))  # Skip first 4 bytes which will hold the checksum
    checksum_bytes = checksum.to_bytes(4, 'little')   # Little-endian format
    raw_data = checksum_bytes + bytes(raw_data)                    # Prepend to the raw_data

    print( "Checksum: " + str( struct.unpack('>I', checksum_bytes)[0] ) )

    print( list(raw_data) )

    serialObj.sendByte(b'\x24') # Preset opcode (we wait until the data is parsed 
                                # to tell the flight computer to listen for it)

    serialObj.sendByte(b'\x01') # Upload subcommand


    serialObj.sendBytes(raw_data)

    return serialObj
