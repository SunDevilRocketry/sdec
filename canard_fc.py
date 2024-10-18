from pynput.keyboard import Key, Listener
from functools import partial

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
    print("FIN Setup")
    print("CONTROLS: j/k RIGHT-/+, f/d LEFT-/+")
    print("Press q to exit")
    serialObj.sendByte(b'\x21')
    # serialObj.sendByte(b'\x05')



    handle = partial(fin_handle_key_press, serialObj=serialObj)
    with Listener(
        supress=True,
        on_press=handle,
    ) as listener:
        listener.join()
    return serialObj

def fin_handle_key_press(key, serialObj):
    match key.char:
        case 'j':
            serialObj.sendByte(b'\x13')
        case 'k':
            serialObj.sendByte(b'\x12')
        case 'f':
            serialObj.sendByte(b'\x11')
        case 'd':
            serialObj.sendByte(b'\x10')
        case 's':
            serialObj.sendByte(b'\x14')
        case 'q':
            serialObj.sendByte(b'\x15')
            return False
        case _:
            print("")
