import pandas as pd

labels = [
            "save_bit",
            "acc_launch_flag",
            "accel_x_offset",
            "accel_y_offset",
            "accel_z_offset",
            "gyro_x_offset",
            "gyro_y_offset",
            "gyro_z_offset",
            "pres_offset",
            "pres_temp_offset",
            "rp_servo1",
            "rp_servo2",
            "time",
            "accX",
            "accY",
            "accZ",
            "gyroX",
            "gyroY",
            "gyroZ",
            "magX",
            "magY",
            "magZ",
            "imut",
            "accXconv",
            "accYconv",
            "accZconv",
            "gyroXconv",
            "gyroYconv",
            "gyroZconv",
            "rollDeg",
            "pitchDeg",
            "rollRate",
            "pitchRate",
            "velo",
            "pos",
            "pres",
            "temp",
            "baro_alt",
            "baro_velo"
          ]
data = []


length = len(data)

def converter(txt_File, output_File):
     
    with open(txt_File,'r') as file:

        for line in file:
            number = line.split('\t')
            data.append(number[:-1])   

    df = pd.DataFrame.from_records(data, columns=labels)
    df.to_csv('output.csv',index=False)

converter('doc/flight_comp_rev2_sensor_data_3.txt', 'output.csv')

