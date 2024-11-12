####################################################################################
#                                                                                  #
# controller.py -- Contains global variables with SDR controller information       #
# Author: Colton Acosta                                                            #
# Date: 3/31/2023                                                                  #
# Sun Devil Rocketry Avionics                                                      #
#                                                                                  #
####################################################################################


####################################################################################
# Imports                                                                          #
####################################################################################
import sensor_conv


####################################################################################
# Global Variables                                                                 #
####################################################################################


# Controller identification codes
controller_codes = [ 
                  b'\x01', # Engine Controller,    Rev 3.0
                  b'\x02', # Valve Controller ,    Rev 2.0 
                  b'\x03', # Engine Controller,    Rev 4.0 
                  b'\x04', # Flight Computer,      Rev 1.0
                  b'\x05', # Flight Computer,      Rev 2.0
                  b'\x06', # Flight Computer Lite, Rev 1.0
                  b'\x07', # Valve Controller,     Rev 3.0
                  b'\x08'  # Engine Controller,    Rev 5.0
                   ]

# Controller Names
controller_names = [
                   "Liquid Engine Controller (L0002 Rev 3.0)",
                   "Valve Controller (L0005 Rev 2.0)"        ,
                   "Liquid Engine Controller (L0002 Rev 4.0)",
                   "Flight Computer (A0002 Rev 1.0)"         ,
                   "Flight Computer (A0002 Rev 2.0)"         ,
                   "Flight Computer Lite (A0007 Rev 1.0)"    ,
                   "Valve Controller (L0005 Rev 3.0)"        , 
                   "Liquid Engine Controller (L0002 Rev 5.0)"
                   ]

# Controller descriptions from identification codes
controller_descriptions = {
                  b'\x01': "Liquid Engine Controller (L0002 Rev 3.0)",
                  b'\x02': "Valve Controller (L0005 Rev 2.0)"        ,
                  b'\x03': "Liquid Engine Controller (L0002 Rev 4.0)",
                  b'\x04': "Flight Computer (A0002 Rev 1.0)"         ,
                  b'\x05': "Flight Computer (A0002 Rev 2.0)"         ,
                  b'\x06': "Flight Computer Lite (A0007 Rev 1.0)"    ,
                  b'\x07': "Valve Controller (L0005 Rev 3.0)"        ,
                  b'\x08': "Liquid Engine Controller (L0002 Rev 5.0)"
                          }

# Lists of sensors on each controller
controller_sensors = {
                # Engine Controller rev 4.0
                controller_names[2]: {
                           "pt0": "Pressure Transducer 0",
                           "pt1": "Pressure Transducer 1",
                           "pt2": "Pressure Transducer 2",
                           "pt3": "Pressure Transducer 3",
                           "pt4": "Pressure Transducer 4",
                           "pt5": "Pressure Transducer 5",
                           "pt6": "Pressure Transducer 6",
                           "pt7": "Pressure Transducer 7",
                           "lc" : "Load Cell            ", 
                           "tc" : "Theromcouple         "
                           },
                # Flight Computer rev 1.0
                controller_names[3]: {
                           "accX" : "Accelerometer X       ",
                           "accY" : "Accelerometer Y       ",
                           "accZ" : "Accelerometer Z       ",
                           "gyroX": "gyroscope X           ",
                           "gyroY": "gyroscope Y           ",
                           "gyroZ": "gyroscope Z           ",
                           "magX" : "Magnetometer X        ",
                           "magY" : "Magnetometer Y        ",
                           "magZ" : "Magnetometer Z        ",
                           "imut" : "IMU Die Temperature   ",
                           "pres" : "Barometric Pressure   ",
                           "temp" : "Barometric Temperature"
                           },
                # Flight Computer rev 2.0
                controller_names[4]: {
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
                           "accXconv" :     "Pre-converted Accel X",
                           "accYconv" :     "Pre-converted Accel Y",
                           "accZconv" :     "Pre-converted Accel Z",
                           "gyroXconv" :    "Pre-converted Gyro X",
                           "gyroYconv" :    "Pre-converted Gyro Y",
                           "gyroZconv" :    "Pre-converted Gyro Z",
                           "rollDeg"    :   "Roll Body Angle",
                           "pitchDeg"    :  "Pitch Body Angle",
                           "rollRate"    :  "Roll Body Rate",
                           "pitchRate"    : "Pitch Body Rate",
                           "velo"   :       "Velocity",
                           "velo_x" :       "Velo X",
                           "velo_y" :       "Velo Y",
                           "velo_z" :       "Velo Z",
                           "pos"   :        "Position",
                           "pres" :         "Barometric Pressure   ",
                           "temp" :         "Barometric Temperature",
                           "alt" :         "Barometric Altitude",
                           "bvelo" :         "Barometric Velocity",
                           },
                # Flight Computer Lite Rev 1.0
                controller_names[5]: {
                           "pres" : "Barometric Pressure   ",
                           "temp" : "Barometric Temperature"
                           },
                # Valve Controller Rev 2.0
                controller_names[1]: {
                           "encO": "Oxygen Valve Encoder",
                           "encF": "Fuel Valve Encoder  "
                           }, 
                # Valve Controller Rev 3.0
                controller_names[6]: {
                           "encO": "Oxygen Valve Encoder",
                           "encF": "Fuel Valve Encoder  "
                           }, 
                # Engine Controller rev 5.0
                controller_names[7]: {
                           "pt0": "Pressure Transducer: LOX Pressure"        ,
                           "pt1": "Pressure Transducer: LOX Flow Upstream"   ,
                           "pt2": "Pressure Transducer: LOX Flow Downstream" ,
                           "pt3": "Pressure Transducer: None"                ,
                           "pt4": "Pressure Transducer: Engine Pressure"     ,
                           "pt5": "Pressure Transducer: Fuel Flow Downstream",
                           "pt6": "Pressure Transducer: Fuel Flow Upstream"  ,
                           "pt7": "Pressure Transducer: Fuel Pressure"       ,
                           "lc" : "Load Cell            "                    , 
                           "tc" : "Theromcouple         "
                           }
                     }

# Size of raw sensor readouts in bytes
sensor_sizes = {
                # Engine Controller rev 4.0
                controller_names[2]: {
                           "pt0": 4,
                           "pt1": 4,
                           "pt2": 4,
                           "pt3": 4,
                           "pt4": 4,
                           "pt5": 4,
                           "pt6": 4,
                           "pt7": 4,
                           "tc" : 4,
                           "lc" : 4            
                           },
                # Flight Computer rev 1.0
                controller_names[3]: {
                           "accX" : 2,
                           "accY" : 2,
                           "accZ" : 2,
                           "gyroX": 2,
                           "gyroY": 2,
                           "gyroZ": 2,
                           "magX" : 2,
                           "magY" : 2,
                           "magZ" : 2,
                           "imut" : 2,
                           "pres" : 4,
                           "temp" : 4
                           },
                # Flight Computer rev 2.0
                controller_names[4]: {
                           "accX" : 2,
                           "accY" : 2,
                           "accZ" : 2,
                           "gyroX": 2,
                           "gyroY": 2,
                           "gyroZ": 2,
                           "magX" : 2,
                           "magY" : 2,
                           "magZ" : 2,
                           "imut" : 2,
                           "accXconv" :     4,
                           "accYconv" :     4,
                           "accZconv" :     4,
                           "gyroXconv" :    4,
                           "gyroYconv" :    4,
                           "gyroZconv" :    4,
                           "rollDeg"    :   4,
                           "pitchDeg"    :  4,
                           "rollRate"    :  4,
                           "pitchRate"    : 4,
                           "velo"   :       4,
                           "velo_x"   :       4,
                           "velo_y"   :       4,
                           "velo_z"   :       4,
                           "pos"   :        4,
                            "pres" : 4,
                           "temp" : 4,
                           "alt" : 4,
                           "bvelo" : 4,
                           },
                # Flight Computer Lite rev 1.0
                controller_names[5]: {
                           "pres" : 4,
                           "temp" : 4 
                           },
                # Valve Controller Rev 2.0
                controller_names[1]: {
                           "encO": 4,
                           "encF": 4 
                           },
                # Valve Controller Rev 3.0
                controller_names[6]: {
                           "encO": 4,
                           "encF": 4 
                           },
                # Engine Controller rev 5.0
                controller_names[7]: {
                           "pt0": 4,
                           "pt1": 4,
                           "pt2": 4,
                           "pt3": 4,
                           "pt4": 4,
                           "pt5": 4,
                           "pt6": 4,
                           "pt7": 4,
                           "tc" : 4,
                           "lc" : 4            
                           }
               }

# Sensor poll codes
sensor_codes = {
                # Engine Controller rev 4.0
                controller_names[2]: {
                           "pt0": b'\x00',
                           "pt1": b'\x01',
                           "pt2": b'\x02',
                           "pt3": b'\x03',
                           "pt4": b'\x04',
                           "pt5": b'\x05',
                           "pt6": b'\x06',
                           "pt7": b'\x07',
                           "tc" : b'\x08',
                           "lc" : b'\x09' 
                           },
                # Flight Computer rev 1.0
                controller_names[3]: {
                           "accX" : b'\x00',
                           "accY" : b'\x01',
                           "accZ" : b'\x02',
                           "gyroX": b'\x03',
                           "gyroY": b'\x04',
                           "gyroZ": b'\x05',
                           "magX" : b'\x06',
                           "magY" : b'\x07',
                           "magZ" : b'\x08',
                           "imut" : b'\x09',
                           "pres" : b'\x0A',
                           "temp" : b'\x0B' 
                           },
                # Flight Computer rev 2.0
                controller_names[4]: {
                           "accX" : b'\x00',
                           "accY" : b'\x01',
                           "accZ" : b'\x02',
                           "gyroX": b'\x03',
                           "gyroY": b'\x04',
                           "gyroZ": b'\x05',
                           "magX" : b'\x06',
                           "magY" : b'\x07',
                           "magZ" : b'\x08',
                           "imut" : b'\x09',
                           "accXconv" :     b'\x0A',
                           "accYconv" :     b'\x0B',
                           "accZconv" :     b'\x0C',
                           "gyroXconv" :    b'\x0D',
                           "gyroYconv" :    b'\x0E',
                           "gyroZconv" :    b'\x0F',
                           "rollDeg"    :   b'\x10',
                           "pitchDeg"    :  b'\x11',
                           "rollRate"    :  b'\x12',
                           "pitchRate"    : b'\x13',
                           "velo"   :       b'\x14',
                           "velo_x"   :       b'\x15',
                           "velo_y"   :       b'\x16',
                           "velo_z"   :       b'\x17',
                           "pos"   :        b'\x18',
                           "pres" : b'\x19',
                           "temp" : b'\x1A',
                           "alt" : b'\x1B',
                           "bvelo" : b'\x1C',
                           },
                # Flight Computer Lite Rev 1.0
                controller_names[5]: {
                           "pres" : b'\x00',
                           "temp" : b'\x01' 
                           },
                # Valve Controller Rev 2.0
                controller_names[1]: {
                           "encO": b'\x00',
                           "encF": b'\x01' 
                           },
                # Valve Controller Rev 3.0
                controller_names[6]: {
                           "encO": b'\x00',
                           "encF": b'\x01' 
                           },
                # Engine Controller rev 5.0
                controller_names[7]: {
                           "pt0": b'\x00',
                           "pt1": b'\x01',
                           "pt2": b'\x02',
                           "pt3": b'\x03',
                           "pt4": b'\x04',
                           "pt5": b'\x05',
                           "pt6": b'\x06',
                           "pt7": b'\x07',
                           "tc" : b'\x08',
                           "lc" : b'\x09' 
                           }
               }

# Size of a frame of data in flash memory
sensor_frame_sizes = {
                    # Engine Controller rev 4.0
                    controller_names[2]: 44,

                    # Flight Computer rev 1.0
                    controller_names[3]: 32,

                    # Flight Computer rev 2.0
                    controller_names[4]: 136,

                    # Flight Computer Lite rev 1.0
                    controller_names[5]: 12,

                    # Valve Controller rev 2.0
                    controller_names[1]: 12,

                    # Valve Controller rev 3.0
                    controller_names[6]: 12,

                    # Engine Controller rev 5.0
                    controller_names[7]: 44
                     }

# Sensor raw readout conversion functions
sensor_conv_funcs = {
                # Engine Controller rev 4.0
                controller_names[2]: {
                           "pt0": sensor_conv.pt_pressure           ,
                           "pt1": sensor_conv.pt_pressure           ,
                           "pt2": sensor_conv.pt_pressure           ,
                           "pt3": sensor_conv.pt_pressure           ,
                           "pt4": sensor_conv.pt_pressure           ,
                           "pt5": sensor_conv.pt_pressure           ,
                           "pt6": sensor_conv.pt_pressure           ,
                           "pt7": sensor_conv.pt_pressure           ,
                           "lc" : sensor_conv.loadcell_force        , 
                           "tc" : sensor_conv.tc_temp
                           },
                # Flight Computer rev 1.0
                controller_names[3]: {
                           "accX" : sensor_conv.imu_accel,
                           "accY" : sensor_conv.imu_accel,
                           "accZ" : sensor_conv.imu_accel,
                           "gyroX": sensor_conv.imu_gyro,
                           "gyroY": sensor_conv.imu_gyro,
                           "gyroZ": sensor_conv.imu_gyro,
                           "magX" : None                  ,
                           "magY" : None                  ,
                           "magZ" : None                  ,
                           "imut" : None                  ,
                           "pres" : sensor_conv.baro_press,
                           "temp" : sensor_conv.baro_temp 
                           },
                # Flight Computer rev 2.0
                controller_names[4]: {
                           "accX" : sensor_conv.imu_accel,
                           "accY" : sensor_conv.imu_accel,
                           "accZ" : sensor_conv.imu_accel,
                           "gyroX": sensor_conv.imu_gyro,
                           "gyroY": sensor_conv.imu_gyro,
                           "gyroZ": sensor_conv.imu_gyro,
                           "magX" : None                  ,
                           "magY" : None                  ,
                           "magZ" : None                  ,
                           "imut" : None                  ,
                           "accXconv" :     None,
                           "accYconv" :     None,
                           "accZconv" :     None,
                           "gyroXconv" :    None,
                           "gyroYconv" :    None,
                           "gyroZconv" :    None,
                           "rollDeg"    :   None,
                           "pitchDeg"    :  None,
                           "rollRate"    :  None,
                           "pitchRate"    : None,
                           "velo"   :       None,
                           "velo_x"   :       None,
                           "velo_y"   :       None,
                           "velo_z"   :       None,
                           "pos"   :        None,
                           "pres" : sensor_conv.baro_press,
                           "temp" : sensor_conv.baro_temp ,
                           "alt"   :       None,
                           "bvelo"   :       None,
                           },
                # Flight Computer rev 1.0
                controller_names[5]: {
                           "pres" : sensor_conv.baro_press,
                           "temp" : sensor_conv.baro_temp 
                           },
                # Valve Controller Rev 2.0
                controller_names[1]: {
                           "encO": sensor_conv.encoder_int_to_deg,
                           "encF": sensor_conv.encoder_int_to_deg
                           },
                # Valve Controller Rev 3.0
                controller_names[6]: {
                           "encO": sensor_conv.encoder_int_to_deg,
                           "encF": sensor_conv.encoder_int_to_deg
                           },
                # Engine Controller rev 5.0
                controller_names[7]: {
                           "pt0": sensor_conv.pt_pressure   ,
                           "pt1": sensor_conv.pt_pressure   ,
                           "pt2": sensor_conv.pt_pressure   ,
                           "pt3": sensor_conv.pt_pressure   ,
                           "pt4": sensor_conv.pt_pressure_5V,
                           "pt5": sensor_conv.pt_pressure_5V,
                           "pt6": sensor_conv.pt_pressure_5V,
                           "pt7": sensor_conv.pt_pressure_5V,
                           "lc" : sensor_conv.loadcell_force, 
                           "tc" : sensor_conv.tc_temp
                           }
                    }

# Sensor readout units
sensor_units = {
                # Engine Controller rev 4.0
                controller_names[2]: {
                           "pt0": "psi",
                           "pt1": "psi",
                           "pt2": "psi",
                           "pt3": "psi",
                           "pt4": "psi",
                           "pt5": "psi",
                           "pt6": "psi",
                           "pt7": "psi",
                           "lc" : "lb" , 
                           "tc" : "C"
                           },
                # Flight Computer rev 1.0
                controller_names[3]: {
                           "accX" : "m/s/s",
                           "accY" : "m/s/s",
                           "accZ" : "m/s/s",
                           "gyroX": "deg/s",
                           "gyroY": "deg/s",
                           "gyroZ": "deg/s",
                           "magX" : None   ,
                           "magY" : None   ,
                           "magZ" : None   ,
                           "imut" : None   ,
                           "pres" : "kPa",
                           "temp" : "C" 
                           },
                # Flight Computer rev 2.0
                controller_names[4]: {
                           "accX" : "m/s/s",
                           "accY" : "m/s/s",
                           "accZ" : "m/s/s",
                           "gyroX": "deg/s",
                           "gyroY": "deg/s",
                           "gyroZ": "deg/s",
                           "magX" : None   ,
                           "magY" : None   ,
                           "magZ" : None   ,
                           "imut" : None   ,
                           "accXconv" :     'm/s/s',
                           "accYconv" :     'm/s/s',
                           "accZconv" :     'm/s/s',
                           "gyroXconv" :    'deg/s',
                           "gyroYconv" :    'deg/s',
                           "gyroZconv" :    'deg/s',
                           "rollDeg"    :   'deg',
                           "pitchDeg"    :  'deg',
                           "rollRate"    :  'deg/s',
                           "pitchRate"    : 'deg/s',
                           "velo"   :       'm/s',
                           "velo_x"   :       'm/s',
                           "velo_y"   :       'm/s',
                           "velo_z"   :       'm/s',
                           "pos"   :        'm',
                           "pres" : "kPa",
                           "temp" : "C",
                           "alt" : "m",
                           "bvelo" : "m/s" 
                           },
                # Flight Computer rev 1.0
                controller_names[5]: {
                           "pres" : "kPa",
                           "temp" : "C" 
                           },
                # Valve Controller Rev 2.0
                controller_names[1]: {
                           "encO": "deg",
                           "encF": "deg" 
                           },
                # Valve Controller Rev 3.0
                controller_names[6]: {
                           "encO": "deg",
                           "encF": "deg" 
                           },
                # Engine Controller rev 5.0
                controller_names[7]: {
                           "t"    : "s"   ,
                           "pt0"  : "psi" ,
                           "pt1"  : "psi" ,
                           "pt2"  : "psi" ,
                           "pt3"  : "psi" ,
                           "pt4"  : "psi" ,
                           "pt5"  : "psi" ,
                           "pt6"  : "psi" ,
                           "pt7"  : "psi" ,
                           "lc"   : "lb"  , 
                           "tc"   : "C"   ,
                           "oxfr" : "kg/s",
                           "ffr"  : "kg/s"
                           }
               }

# Inidices of sensors in output file 
sensor_indices = {
                # Flight Computer rev 1.0
                controller_names[3]: {
                            "accX" : 1,
                            "accY" : 2,
                            "accZ" : 3,
                            "gyroX": 4,
                            "gyroY": 5,
                            "gyroZ": 6,
                            "magX" : 7,
                            "magY" : 8,
                            "magZ" : 9,
                            "imut" : 10,
                            "pres" : 11,
                            "temp" : 12 
                                       },
                # Flight Computer rev 2.0
                controller_names[4]: {
                            "accX" : 1,
                            "accY" : 2,
                            "accZ" : 3,
                            "gyroX": 4,
                            "gyroY": 5,
                            "gyroZ": 6,
                            "magX" : 7,
                            "magY" : 8,
                            "magZ" : 9,
                            "imut" : 10,
                            "accXconv" :     11,
                            "accYconv" :     12,
                            "accZconv" :     13,
                            "gyroXconv" :    14,
                            "gyroYconv" :    15,
                            "gyroZconv" :    16,
                            "rollDeg"    :   17,
                            "pitchDeg"    :  18,
                            "rollRate"    :  19,
                            "pitchRate"    : 20,
                            "velo"   :       21,
                            "velo_x"   :       22,
                            "velo_y"   :       23,
                            "velo_z"   :       24,
                            "pos"   :        25, 
                            "pres" : 26,
                            "temp" : 27,
                            "alt" : 28,
                            "bvelo" : 29,
                                       },
                # Flight Computer Lite rev 1.0
                controller_names[5]: {
                            "pres" : 1,
                            "temp" : 2 
                                     },
                # Valve Controller Rev 2.0
                controller_names[1]: {
                           "encO": 1,
                           "encF": 2 
                           },
                # Valve Controller Rev 3.0
                controller_names[6]: {
                           "encO": 1,
                           "encF": 2 
                           }
                 }

# Sensor raw readout formats
sensor_formats = {
                # Engine Controller rev 4.0
                controller_names[2]: {
                           "pt0": int,
                           "pt1": int,
                           "pt2": int,
                           "pt3": int,
                           "pt4": int,
                           "pt5": int,
                           "pt6": int,
                           "pt7": int,
                           "tc" : int,
                           "lc" : int 
                           },
                # Flight Computer rev 1.0
                controller_names[3]: {
                           "accX" : int  ,
                           "accY" : int  ,
                           "accZ" : int  ,
                           "gyroX": int  ,
                           "gyroY": int  ,
                           "gyroZ": int  ,
                           "magX" : int  ,
                           "magY" : int  ,
                           "magZ" : int  ,
                           "imut" : int  ,
                           "pres" : float,
                           "temp" : float 
                           },
                # Flight Computer rev 2.0
                controller_names[4]: {
                           "accX" : int  ,
                           "accY" : int  ,
                           "accZ" : int  ,
                           "gyroX": int  ,
                           "gyroY": int  ,
                           "gyroZ": int  ,
                           "magX" : int  ,
                           "magY" : int  ,
                           "magZ" : int  ,
                           "imut" : int  ,
                           "accXconv" :     float,
                           "accYconv" :     float,
                           "accZconv" :     float,
                           "gyroXconv" :    float,
                           "gyroYconv" :    float,
                           "gyroZconv" :    float,
                           "rollDeg"    :   float,
                           "pitchDeg"    :  float,
                           "rollRate"    :  float,
                           "pitchRate"    : float,
                           "velo"   :       float,
                           "velo_x"   :       float,
                           "velo_y"   :       float,
                           "velo_z"   :       float,
                           "pos"   :        float, 
                           "pres" : float,
                           "temp" : float,
                           "alt" : float,
                           "bvelo" : float,
                           },
                # Flight Computer rev 1.0
                controller_names[5]: {
                           "pres" : float,
                           "temp" : float 
                           },
                # Valve Controller Rev 2.0
                controller_names[1]: {
                           "encO": int,
                           "encF": int 
                           },
                # Valve Controller Rev 3.0
                controller_names[6]: {
                           "encO": int,
                           "encF": int 
                           },
                # Engine Controller rev 5.0
                controller_names[7]: {
                           "pt0": int,
                           "pt1": int,
                           "pt2": int,
                           "pt3": int,
                           "pt4": int,
                           "pt5": int,
                           "pt6": int,
                           "pt7": int,
                           "tc" : int,
                           "lc" : int 
                           }
                 }

# Filenames for flash extract outputs 
sensor_data_filenames = {
                        # Flight Computer rev 1.0
                        controller_names[3]: "output/flight_comp_rev1_sensor_data.txt",
                        # Flight Computer rev 2.0
                        controller_names[4]: "output/flight_comp_rev2_sensor_data.txt",
                        # Flight Computer Lite rev 1.0
                        controller_names[5]: "output/flight_comp_lite_rev1_sensor_data.txt",
                        # Valve Controller rev 2.0
                        controller_names[1]: "output/valve_controller_rev2_sensor_data.txt",
                        # Valve Controller rev 3.0
                        controller_names[6]: "output/valve_controller_rev3_sensor_data.txt",
                        # Engine Controller rev 5.0
                        controller_names[7]: "output/engine_controller_rev5_sensor_data.txt"
                        }

# Firmware Ids
firmware_ids = {
                b'\x01': "Terminal"   ,
				b'\x02': "Data Logger",
				b'\x03': "Dual Deploy",
                b'\x04': "Hotfire",
                b'\x05': "Active Roll"
               }
			
# Boards that report firmware ids with the connect command
firmware_id_supported_boards = [
                controller_names[4], # Flight Computer Rev 2.0
                controller_names[6]  # Valve Controller Rev 3.0
                               ]

##################################################################################
# END OF FILE                                                                    #
##################################################################################