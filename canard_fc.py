def imu_calibrate(Args, serialObj):
    print("IMU CALIBRATING")
    serialObj.sendByte(b'\x03')

def pid_run(Args, serialObj):
    print("PID RUN")
    serialObj.sendByte(b'\x04')
