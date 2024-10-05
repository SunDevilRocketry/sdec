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
