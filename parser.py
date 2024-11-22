import matplotlib.pyplot
import pandas as pd
import matplotlib


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
            "velo_x",
            "velo_y",
            "velo_z",
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

    matplotlib.pyplot.plot()
    # df.to_csv(output_File,index=False)

print(len(labels))

converter('output/flight_comp_rev2_sensor_data.txt', 'nov162024.csv')

