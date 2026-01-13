# SPDX-License-Identifier: BSD-3-Clause
# Copyright (c) 2025 Sun Devil Rocketry

from pynput.keyboard import Key, Listener
from functools import partial
from hw_commands import byte_array_to_float

import time

def idle(Args, serialObj):
    print("IDLE")
    serialObj.sendByte(b'\x20')
    return serialObj

def imu_calibrate(Args, serialObj):
    print("IMU CALIBRATING")
    serialObj.sendByte(b'\x22')
    return serialObj

def pid_run(Args, serialObj):
    print("PID RUN")
    serialObj.sendByte(b'\x23')
    return serialObj

def pid_setup(Args, serialObj):
    print("PID SETUP")
    serialObj.sendByte(b'\x24')
    return serialObj

def terminal_access(Args, serialObj):
    print("TERMINAL")
    serialObj.sendByte(b'\x25')
    return serialObj


def fin_setup(Args, serialObj):
    print( "FIN Setup" )
    print( "CONTROLS:" )
    print( "SERVO 1: d/f -/+, SERVO 2: j/k -/+" )
    print( "SERVO 3: e/r -/+, SERVO 4: u/i -/+" )
    print( "Press q to exit" )
    serialObj.sendByte(b'\x21')
    handle = partial(fin_handle_key_press, serialObj=serialObj)
    with Listener(
        supress=True,
        on_press=handle,
    ) as listener:
        listener.join()
    return serialObj

def read_preset(Args, serialObj):
    print("Read Preset")
    serialObj.sendByte(b'\x26')

    # Read serial data
    rx_bytes = serialObj.readBytes(36)

    sensor_frame_int = []
    for sensor_byte in rx_bytes:
        sensor_frame_int.append( ord( sensor_byte ) )

    accel_x_bytes = [sensor_frame_int[0].to_bytes(1, 'big' ), sensor_frame_int[1].to_bytes(1, 'big' ), sensor_frame_int[2].to_bytes(1, 'big' ), sensor_frame_int[3].to_bytes(1, 'big' )]
    accel_y_bytes = [sensor_frame_int[4].to_bytes(1, 'big' ), sensor_frame_int[5].to_bytes(1, 'big' ), sensor_frame_int[6].to_bytes(1, 'big' ), sensor_frame_int[7].to_bytes(1, 'big' )]
    accel_z_bytes = [sensor_frame_int[8].to_bytes(1, 'big' ), sensor_frame_int[9].to_bytes(1, 'big' ), sensor_frame_int[10].to_bytes(1, 'big' ), sensor_frame_int[11].to_bytes(1, 'big' )]
    
    gyro_x_bytes = [sensor_frame_int[12].to_bytes(1, 'big' ), sensor_frame_int[13].to_bytes(1, 'big' ), sensor_frame_int[14].to_bytes(1, 'big' ), sensor_frame_int[15].to_bytes(1, 'big' )]
    gyro_y_bytes = [sensor_frame_int[16].to_bytes(1, 'big' ), sensor_frame_int[17].to_bytes(1, 'big' ), sensor_frame_int[18].to_bytes(1, 'big' ), sensor_frame_int[19].to_bytes(1, 'big' )]
    gyro_z_bytes = [sensor_frame_int[20].to_bytes(1, 'big' ), sensor_frame_int[21].to_bytes(1, 'big' ), sensor_frame_int[22].to_bytes(1, 'big' ), sensor_frame_int[23].to_bytes(1, 'big' )]

    baro_pres_bytes = [sensor_frame_int[24].to_bytes(1, 'big' ), sensor_frame_int[25].to_bytes(1, 'big' ), sensor_frame_int[26].to_bytes(1, 'big' ), sensor_frame_int[27].to_bytes(1, 'big' )]
    baro_temp_bytes = [sensor_frame_int[28].to_bytes(1, 'big' ), sensor_frame_int[29].to_bytes(1, 'big' ), sensor_frame_int[30].to_bytes(1, 'big' ), sensor_frame_int[31].to_bytes(1, 'big' )]

    accel_x_float = byte_array_to_float(accel_x_bytes)
    accel_y_float = byte_array_to_float(accel_y_bytes)
    accel_z_float = byte_array_to_float(accel_z_bytes)

    gyro_x_float = byte_array_to_float(gyro_x_bytes)
    gyro_y_float = byte_array_to_float(gyro_y_bytes)
    gyro_z_float = byte_array_to_float(gyro_z_bytes)

    baro_pres_float = byte_array_to_float(baro_pres_bytes)
    baro_temp_float = byte_array_to_float(baro_temp_bytes)

    # Servo 1 Reference point
    rp_servo1 = sensor_frame_int[32]

    # Servo 2 Reference point
    rp_servo2 = sensor_frame_int[33]

    # Servo 3 Reference point
    rp_servo3 = sensor_frame_int[34]

    # Servo 4 Reference point
    rp_servo4 = sensor_frame_int[35]

    # Pad bits
    #pad1 = sensor_frame_int[36]
    #pad2 = sensor_frame_int[37]

    print(f"Data receive:\n")
    print(f"Acceleration: {[accel_x_float, accel_y_float, accel_z_float]}\n")
    print(f"Gyro: {[gyro_x_float, gyro_y_float, gyro_z_float]}\n")
    print(f"Baro: {[baro_pres_float, baro_temp_float]}\n")
    print(f"Servo: {[rp_servo1, rp_servo2, rp_servo3, rp_servo4]}\n")


    return serialObj


def save_preset(Args, serialObj):
    print("Preset saved!")
    serialObj.sendByte(b'\x27')
    return serialObj

def fin_handle_key_press(key, serialObj):
    match key.char:
        case 'f': # Servo 1 -
            serialObj.sendByte(b'\x10')
        case 'd': # Servo 1 +
            serialObj.sendByte(b'\x11')
        case 'k': # Servo 2 -
            serialObj.sendByte(b'\x12')
        case 'j': # Servo 2 +
            serialObj.sendByte(b'\x13')
        case 'r': # Servo 3 -
            serialObj.sendByte(b'\x30')
        case 'e': # Servo 3 +
            serialObj.sendByte(b'\x31')
        case 'i': # Servo 4 -
            serialObj.sendByte(b'\x32')
        case 'u': # Servo 4 +
            serialObj.sendByte(b'\x33')
        case 's': # Save (unused)
            serialObj.sendByte(b'\x14')
        case 'q': # Quit
            serialObj.sendByte(b'\x15')
            return False
        case _:
            print("")
