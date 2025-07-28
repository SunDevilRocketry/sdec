from pynput.keyboard import Key, Listener
from functools import partial
from hw_commands import byte_array_to_float

import time


# "print"       : "thing to print",
# "index start" : [first index of the data in the sensor frame], 
# "bytes"       : [amount of bytes for each value],
# "values"      : [amount of values for each part of the data], 
# "type"        : "data type"
read_preset_output_strings = {
    "APPA" : [
        {"header":  "Data Receive:\n"},
        {"print" : "Acceleration: ", "index start": 0,  "bytes" : 4, "values" : 3, "type" : "float"}, # x, y, z
        {"print" : "Gyro:         ", "index start": 12, "bytes" : 4, "values" : 3, "type" : "float"}, # x, y, z
        {"print" : "Baro:         ", "index start": 24, "bytes" : 4, "values" : 2, "type" : "float"}, # pres, temp
        {"print" : "Servo:        ", "index start": 32, "bytes" : 1, "values" : 4, "type" : "int"},   # Servo reference point
        # Pad bytes 37, 38
    ]
}


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

    preset_output_strings = read_preset_output_strings["APPA"]

    for command in preset_output_strings:
        command_type = next(iter(command))

        match command_type:
            case "header":
                print(command["header"])
            case "print":
                to_print        = command["print"]
                bytes_per_value = command["bytes"]
                index           = command["index start"]
                num_values      = command["values"]
                data_type       = command["type"]

                match data_type:
                    case "float":
                        list_to_print = []
                        for _ in range(num_values):
                            single_value = []
                            for i in range (index, index + bytes_per_value):
                                single_value.append(sensor_frame_int[i].to_bytes(1, 'big'))

                            index += bytes_per_value
                            single_value = (byte_array_to_float(single_value))
                            list_to_print.append(single_value)

                        print(f"{to_print} {list_to_print}\n")

                    case "int":
                        list_to_print = []
                        for _ in range(num_values):
                            single_value = 0
                            for offset in range(bytes_per_value - 1, -1, -1):
                                shifted_byte = (sensor_frame_int[index + offset] << (8 * offset))
                                single_value = single_value | shifted_byte

                            index += bytes_per_value
                            list_to_print.append(single_value)

                        print(f"{to_print} {list_to_print}\n")

                    case _:
                        raise ValueError(f"Unknown key {data_type}")
                    
            case _:
                raise ValueError(f"Unknown key {command_type}")

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
