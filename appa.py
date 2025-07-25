####################################################################################
#                                                                                  #
# appa.py -- Contains functions related to APPA prototype                          #
#                                                                                  #
# Author: Eli Sells                                                                #
# Date: 05/17/2025                                                                 #
# Sun Devil Rocketry Avionics                                                      #
#                                                                                  #
####################################################################################

####################################################################################
# Imports                                                                          #
####################################################################################
import csv
import struct

import commands
import hw_commands

####################################################################################
# Global Variables                                                                 #
####################################################################################

appa_data_bitmasks = {
    "raw": (2 ^ 0),
    "conv": (2 ^ 1),
    "state_estim": (2 ^ 2),
    "gps": (2 ^ 3),
    "canard": (2 ^ 4)
}

appa_sensor_names = {
    "raw": {
        "accX" :         "Accelerometer X       ",
        "accY" :         "Accelerometer Y       ",
        "accZ" :         "Accelerometer Z       ",
        "gyroX":         "gyroscope X           ",
        "gyroY":         "gyroscope Y           ",
        "gyroZ":         "gyroscope Z           ",
        "magX" :         "Magnetometer X        ",
        "magY" :         "Magnetometer Y        ",
        "magZ" :         "Magnetometer Z        ",
        "imut" :         "IMU Die Temperature   ",
        "pres" :         "Barometric Pressure   ",
        "temp" :         "Barometric Temperature"
    },
    "conv": {
        "accXconv" :     "Pre-converted Accel X",
        "accYconv" :     "Pre-converted Accel Y",
        "accZconv" :     "Pre-converted Accel Z",
        "gyroXconv" :    "Pre-converted Gyro X",
        "gyroYconv" :    "Pre-converted Gyro Y",
        "gyroZconv" :    "Pre-converted Gyro Z"
    },
    "state_estim": {
        "rollDeg"    :   "Roll Body Angle",
        "pitchDeg"    :  "Pitch Body Angle",
        "rollRate"    :  "Roll Body Rate",
        "pitchRate"    : "Pitch Body Rate",
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
    "raw": {
        "accX" :         2,
        "accY" :         2,
        "accZ" :         2,
        "gyroX":         2,
        "gyroY":         2,
        "gyroZ":         2,
        "magX" :         2,
        "magY" :         2,
        "magZ" :         2,
        "imut" :         2,
        "pres" :         4,
        "temp" :         4
    },
    "conv": {
        "accXconv" :     4,
        "accYconv" :     4,
        "accZconv" :     4,
        "gyroXconv" :    4,
        "gyroYconv" :    4,
        "gyroZconv" :    4
    },
    "state_estim": {
        "rollDeg"    :   4,
        "pitchDeg"    :  4,
        "rollRate"    :  4,
        "pitchRate"    : 4,
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
    "raw": {
        "accX" :         int,
        "accY" :         int,
        "accZ" :         int,
        "gyroX":         int,
        "gyroY":         int,
        "gyroZ":         int,
        "magX" :         int,
        "magY" :         int,
        "magZ" :         int,
        "imut" :         int,
        "pres" :         float,
        "temp" :         float
    },
    "conv": {
        "accXconv" :     float,
        "accYconv" :     float,
        "accZconv" :     float,
        "gyroXconv" :    float,
        "gyroYconv" :    float,
        "gyroZconv" :    float
    },
    "state_estim": {
        "rollDeg"    :   float,
        "pitchDeg"    :  float,
        "rollRate"    :  float,
        "pitchRate"    : float,
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

# Hold the data bitmask from parsing the preset
preset_data_bitmask = None

"""
    Note: The length of "thing to print" should be 23 chars.
    "Firmmware version" : [
        {"header" : "header to print"},
        {"print" : "thing to print", "indices" : [byte indices of data], "type" : "data type"},
        {"delete" : index to delete up until}
    ]
"""
preset_size = 80
parse_preset_output_strings = {
    "APPA" : [
        {"header":  "==CONFIG DATA=="},
        {"print" : "Checksum:              ", "indices" : [0, 1, 2, 3], "type" : "int"},
        {"print" : "Feature bitmask:       ", "indices" : [4], "type" : "int"},
        {"print" : "Data bitmask:          ", "indices" : [5], "type" : "int"},
        {"print" : "Sensor calib samples:  ", "indices" : [6, 7], "type" : "int"},
        {"print" : "LD timeout             ", "indices" : [8, 9], "type" : "int"},
        {"print" : "LD accel threshold:    ", "indices" : [10], "type" : "int"},
        {"print" : "LD accel samples:      ", "indices" : [11], "type" : "int"},
        {"print" : "LD baro threshold:     ", "indices" : [12, 13], "type" : "int"},
        {"print" : "LD baro samples:       ", "indices" : [14], "type" : "int"},
        {"print" : "AC max deflect angle:  ", "indices" : [15], "type" : "int"},
        {"print" : "AC Roll PID P const:   ", "indices" : [16, 17, 18, 19], "type" : "float"},
        {"print" : "AC Roll PID I const:   ", "indices" : [20, 21, 22, 23], "type" : "float"},
        {"print" : "AC Roll PID D const:   ", "indices" : [24, 25, 26, 27], "type" : "float"},
        {"print" : "AC P/Y PID P const:    ", "indices" : [28, 29, 30, 31], "type" : "float"},
        {"print" : "AC P/Y PID I const:    ", "indices" : [32, 33, 34, 35], "type" : "float"},
        {"print" : "AC P/Y PID D const:    ", "indices" : [36, 37, 38, 39], "type" : "float"},
        {"print" : "AR Delay after launch: ", "indices" : [40, 41], "type" : "int"},
        {"print" : "Minimum Frame Delta:   ", "indices" : [42], "type" : "int"},
        {"delete": 44}, # Index 43 empty due to padding
        {"header" : "==IMU OFFSETS=="},
        {"print" : "Accel x offset:        ", "indices" : [0, 1, 2, 3], "type" : "float"},
        {"print" : "Accel y offset:        ", "indices" : [4, 5, 6, 7], "type" : "float"},
        {"print" : "Accel z offset:        ", "indices" : [8, 9, 10, 11], "type" : "float"},
        {"print" : "Gyro x offset:         ", "indices" : [12, 13, 14, 15], "type" : "float"},
        {"print" : "Gyro y offset:         ", "indices" : [16, 17, 18, 19], "type" : "float"},
        {"print" : "Gryo z offset:         ", "indices" : [20, 21, 22, 23], "type" : "float"},
        {"header" : "==BARO OFFSETS=="},
        {"print" : "Baro pres offset:      ", "indices" : [24, 25, 26, 27], "type" : "float"},
        {"print" : "Baro temp offset:      ", "indices" : [28, 29, 30, 31], "type" : "float"},
        {"header" : "==SERVO REF PTS=="},
        {"print" : "Servo 1 RP:            ", "indices" : [32], "type" : "int"},
        {"print" : "Servo 2 RP:            ", "indices" : [33], "type" : "int"},
        {"print" : "Servo 3 RP:            ", "indices" : [34], "type" : "int"},
        {"print" : "Servo 4 RP:            ", "indices" : [35], "type" : "int"}
    ]
}

# Note: there should be 23 chars before the value. Keep that number consistent.
def appa_parse_preset(serialObj, sensor_frame_int):
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
                        if len(indices) == 1 and "Data bitmask" in to_print: preset_data_bitmask = value
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


def calculate_sensor_frame_size(dataBitmask):
    size = 6
    if ( dataBitmask & appa_data_bitmasks.get("raw") != 0 ):
        size += 10 * 2 # IMU raw
        size += 2 * 4 # Baro raw
    if ( dataBitmask & appa_data_bitmasks.get("conv") != 0 ):
        size += 6 * 4 # IMU conv
    if ( dataBitmask & appa_data_bitmasks.get("state_estim") != 0 ):
        size += 9 * 4 # IMU state estims
        size += 2 * 4 # Baro state estims
    if ( dataBitmask & appa_data_bitmasks.get("gps") != 0 ):
        size += 5 * 4 # GPS floats
        size += 4 * 1 # GPS chars
    if ( dataBitmask & appa_data_bitmasks.get("canard") != 0 ):
        size += 1 * 4 # canard feedback
    
    # Calculate
    sensor_frame_size = size
    numFrames = 1
    while ( sensor_frame_size < preset_size + 2 ):
        sensor_frame_size += size
        numFrames += 1

    return sensor_frame_size, numFrames


def flash_extract_parse(serialObj, rx_byte_blocks):
    # Parse contents into bytes
    # TODO: THIS IS PROBABLY WRONG!!
    sensor_frame_int = []
    for sensor_byte in rx_byte_blocks:
        sensor_frame_int.append( ord( sensor_byte ) )

    preset_int = []
    for i in range(0, preset_size):
        preset_int.append(sensor_frame_int[i])
    
    preset_strings = appa_parse_preset(serialObj, preset_int)

    # Write presets to file
    with open( "output/appa_preset_data.txt", 'w' ) as file:
        for line in preset_strings:
            file.write(line + '\n')

    # Get data bitmask (idx 5)
    data_bitmask = preset_int[5]

    sensor_frame_size, numFrames = calculate_sensor_frame_size(data_bitmask)

    # This is where the fun begins

    ## TODO




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
    if serialObj.firemware != "APPA":
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
    serialObj.sendByte(b'\x02')
    serialObj.serialObj.reset_input_buffer()

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
    serialObj.sendByte(b'\x03')

    # Read serial data
    rx_bytes = serialObj.readBytes(1)

    if (rx_bytes[0] == b'\x00'):
        print("Invalid Checksum.")
    else:
        print("Valid Checksum.")

def upload_preset(Args, serialObj):
    print("Upload Preset")
    filename = input( "Enter filename: " )

    if filename == "":
        filename = "input/appa_config.csv"

    data_list = []
    try:
      with open( filename, 'r' ) as file:
        csv_reader = csv.reader( file )
        for row in csv_reader:
            data_list.append( row )
    except FileNotFoundError:
        print(f"Error: File not found: { filename }")
        return []
    except Exception as e:
        print(f"An error occurred: {e}")
        return []
    
    print( data_list )

    raw_data = [0,0] # Start with no features and no data

    for row in data_list:
        # Skip row if it's a label row
        if all(":" in entry for entry in row): continue

        # Extract data from row
        entry_type = row[0]
        data_type = row[2]
        data = row[-1]

        # Counters for storing bit counts
        enabled_ft_ctr = 0
        enabled_data_ctr = 0

        match data_type:
            case "bit":
                match entry_type:
                    case "Enabled Features":
                        raw_data[0] += (int(data << enabled_ft_ctr))
                        enabled_ft_ctr += 1
                    case "Enabled Data":
                        raw_data[1] += (int(data << enabled_data_ctr))
                        enabled_data_ctr += 1
                    case _:
                        raise ValueError("Unknown entry type {}".format(entry_type))
            case "uint8_t":
                raw_data.append(int(data))
            case "uint16_t":
                raw_data.append(int(data) & int("00FF", 16))
                raw_data.append(int(data) & int("FF00", 16 >> 8))
            case "float":
                byte_array = bytearray(struct.pack("f", float(data)))
                for i in range(4): raw_data.append(int(byte_array[i]))
            case _:
                raise ValueError("Unknown data type {}".format(data_type))

    raw_data.append(0)
    raw_data.insert(0, 0)
    raw_data.insert(0, 1)
    raw_data.insert(0, 2)
    raw_data.insert(0, 3)

    print( raw_data )

    serialObj.sendByte(b'\x24')

    serialObj.sendByte(b'\x01')

    serialObj.sendBytes(bytearray(raw_data))

    return serialObj