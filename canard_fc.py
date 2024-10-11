from pynput.keyboard import Key, Listener
from functools import partial

import time

def idle(Args, serialObj):
    print("IDLE")
    serialObj.sendByte(b'\x01')
    return serialObj

def imu_calibrate(Args, serialObj):
    print("IMU CALIBRATING")
    serialObj.sendByte(b'\x04')
    return serialObj

def pid_run(Args, serialObj):
    print("PID RUN")
    serialObj.sendByte(b'\x05')
    return serialObj

def pid_setup(Args, serialObj):
    print("PID SETUP")
    serialObj.sendByte(b'\x06')
    return serialObj
    

def fin_setup(Args, serialObj):
    print("FIN Setup")
    print("CONTROLS: j/k RIGHT-/+, f/d LEFT-/+")
    print("Press q to exit")
    serialObj.sendByte(b'\x03')
    # serialObj.sendByte(b'\x05')

    time.sleep(4)

    serialObj.sendByte(b'\x05')


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
            serialObj.sendByte(b'\0x04')
        case 'k':
            serialObj.sendByte(b'\0x03')
        case 'f':
            serialObj.sendByte(b'\0x02')
        case 'd':
            serialObj.sendByte(b'\0x01')
        case 'q':
            serialObj.sendByte(b'\0x05')
            return False
        case _:
            return
