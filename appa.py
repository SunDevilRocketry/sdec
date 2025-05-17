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
import commands
import hw_commands

####################################################################################
# Global Variables                                                                 #
####################################################################################

preset_size = 68

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
    
    # Return if user input fails parse checks
    if ( not parse_check ):
        return serialObj 

    # Set subcommand, options, and input data
    user_subcommand = Args[0]

    ################################################################################
    # Subcommand: preset download                                                  #
    ################################################################################
    if (user_subcommand == "download"):
        download_preset(Args, serialObj)
        return serialObj


def download_preset(Args, serialObj):
    print("Download Preset")
    serialObj.sendByte(b'\x02')

    # Read serial data
    rx_bytes = serialObj.readBytes(preset_size)

    sensor_frame_int = []
    for sensor_byte in rx_bytes:
        sensor_frame_int.append( ord( sensor_byte ) )

    output_strings = []

    output_strings.append("==CONFIG DATA==")
    output_strings.append("Checksum:              {value}".format((sensor_frame_int[0] << 8 ^ 3) | (sensor_frame_int[1] << 8 ^ 2) | (sensor_frame_int[2] << 8 ^ 1) | (sensor_frame_int[3])))
    output_strings.append("Feature bitmask:       {value}".format(sensor_frame_int[4]))
    output_strings.append("Data bitmask:          {value}".format(sensor_frame_int[5]))
    output_strings.append("Sensor calib samples:  {value}".format((sensor_frame_int[6] << 8) | sensor_frame_int[7]))
    output_strings.append("LD timeout:            {value}".format((sensor_frame_int[8] << 8) | sensor_frame_int[9]))
    output_strings.append("LD accel threshold:    {value}".format(sensor_frame_int[10]))
    output_strings.append("LD accel samples:      {value}".format(sensor_frame_int[11]))
    output_strings.append("LD baro threshold:     {value}".format((sensor_frame_int[12] << 8)| sensor_frame_int[13]))
    output_strings.append("LD baro samples:       {value}".format(sensor_frame_int[14]))
    output_strings.append("AR max deflect angle:  {value}".format(sensor_frame_int[15]))
    pid_p_const = [sensor_frame_int[16].to_bytes(1, 'big' ), sensor_frame_int[17].to_bytes(1, 'big' ), sensor_frame_int[18].to_bytes(1, 'big' ), sensor_frame_int[19].to_bytes(1, 'big' )]
    output_strings.append("AR PID P const:        {value}".format(hw_commands.byte_array_to_float(pid_p_const)))
    pid_i_const = [sensor_frame_int[20].to_bytes(1, 'big' ), sensor_frame_int[21].to_bytes(1, 'big' ), sensor_frame_int[22].to_bytes(1, 'big' ), sensor_frame_int[23].to_bytes(1, 'big' )]
    output_strings.append("AR PID I const:        {value}".format(hw_commands.byte_array_to_float(pid_i_const)))
    pid_d_const = [sensor_frame_int[24].to_bytes(1, 'big' ), sensor_frame_int[25].to_bytes(1, 'big' ), sensor_frame_int[26].to_bytes(1, 'big' ), sensor_frame_int[27].to_bytes(1, 'big' )]
    output_strings.append("AR PID D const:        {value}".format(hw_commands.byte_array_to_float(pid_d_const)))
    output_strings.append("LD baro threshold:     {value}".format((sensor_frame_int[28] << 8)| sensor_frame_int[29]))
    output_strings.append("LD baro samples:       {value}".format(sensor_frame_int[30]))
    # 31 is empty due to padding
    del sensor_frame_int[:32]

    accel_x_bytes = [sensor_frame_int[0].to_bytes(1, 'big' ), sensor_frame_int[1].to_bytes(1, 'big' ), sensor_frame_int[2].to_bytes(1, 'big' ), sensor_frame_int[3].to_bytes(1, 'big' )]
    accel_y_bytes = [sensor_frame_int[4].to_bytes(1, 'big' ), sensor_frame_int[5].to_bytes(1, 'big' ), sensor_frame_int[6].to_bytes(1, 'big' ), sensor_frame_int[7].to_bytes(1, 'big' )]
    accel_z_bytes = [sensor_frame_int[8].to_bytes(1, 'big' ), sensor_frame_int[9].to_bytes(1, 'big' ), sensor_frame_int[10].to_bytes(1, 'big' ), sensor_frame_int[11].to_bytes(1, 'big' )]
    
    gyro_x_bytes = [sensor_frame_int[12].to_bytes(1, 'big' ), sensor_frame_int[13].to_bytes(1, 'big' ), sensor_frame_int[14].to_bytes(1, 'big' ), sensor_frame_int[15].to_bytes(1, 'big' )]
    gyro_y_bytes = [sensor_frame_int[16].to_bytes(1, 'big' ), sensor_frame_int[17].to_bytes(1, 'big' ), sensor_frame_int[18].to_bytes(1, 'big' ), sensor_frame_int[19].to_bytes(1, 'big' )]
    gyro_z_bytes = [sensor_frame_int[20].to_bytes(1, 'big' ), sensor_frame_int[21].to_bytes(1, 'big' ), sensor_frame_int[22].to_bytes(1, 'big' ), sensor_frame_int[23].to_bytes(1, 'big' )]

    baro_pres_bytes = [sensor_frame_int[24].to_bytes(1, 'big' ), sensor_frame_int[25].to_bytes(1, 'big' ), sensor_frame_int[26].to_bytes(1, 'big' ), sensor_frame_int[27].to_bytes(1, 'big' )]
    baro_temp_bytes = [sensor_frame_int[28].to_bytes(1, 'big' ), sensor_frame_int[29].to_bytes(1, 'big' ), sensor_frame_int[30].to_bytes(1, 'big' ), sensor_frame_int[31].to_bytes(1, 'big' )]

    accel_x_float = hw_commands.byte_array_to_float(accel_x_bytes)
    accel_y_float = hw_commands.byte_array_to_float(accel_y_bytes)
    accel_z_float = hw_commands.byte_array_to_float(accel_z_bytes)

    gyro_x_float = hw_commands.byte_array_to_float(gyro_x_bytes)
    gyro_y_float = hw_commands.byte_array_to_float(gyro_y_bytes)
    gyro_z_float = hw_commands.byte_array_to_float(gyro_z_bytes)

    baro_pres_float = hw_commands.byte_array_to_float(baro_pres_bytes)
    baro_temp_float = hw_commands.byte_array_to_float(baro_temp_bytes)

    output_strings.append("==IMU OFFSETS==")
    output_strings.append("Accel x offset:        {value}".format(accel_x_float))
    output_strings.append("Accel y offset:        {value}".format(accel_y_float))
    output_strings.append("Accel z offset:        {value}".format(accel_z_float))
    output_strings.append("Gyro x offset:         {value}".format(gyro_x_float))
    output_strings.append("Gyro y offset:         {value}".format(gyro_y_float))
    output_strings.append("Gyro z offset:         {value}".format(gyro_z_float))
    output_strings.append("==BARO OFFSETS==")
    output_strings.append("Baro pres offset:      {value}".format(baro_pres_float))
    output_strings.append("Baro temp offset:      {value}".format(baro_temp_float))
    output_strings.append("==SERVO REF PTS==")

    # Servo 1 Reference point
    rp_servo1 = sensor_frame_int[32]

    # Servo 2 Reference point
    rp_servo2 = sensor_frame_int[33]

    # Servo 3 Reference point
    rp_servo3 = sensor_frame_int[34]

    # Servo 4 Reference point
    rp_servo4 = sensor_frame_int[35]

    output_strings.append("Servo 1 RP:            {value}".format(rp_servo1))
    output_strings.append("Servo 2 RP:            {value}".format(rp_servo2))
    output_strings.append("Servo 3 RP:            {value}".format(rp_servo3))
    output_strings.append("Servo 4 RP:            {value}".format(rp_servo4))

    with open( "output/appa_preset_data.txt", 'w' ) as file:
        for line in output_strings:
            file.write(line + '\n')

    print("Data received and written!\n")


    return serialObj