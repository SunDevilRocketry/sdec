import matplotlib.pyplot
import pandas as pd
import matplotlib
from controller import controller_sensors, controller_names

            

data = []


length = len(data)

def converter(txt_File, output_File):
    hardware = ""
    for i in range(0,len(controller_names) - 1):
        print(str(i) + ". " + controller_names[i])
    number = input("Which Hardware would you like to select? Enter a number. \n")
    hardware = controller_names[int(number)]
    labels = [
            "save_bit",
            "acc_launch_flag",
            # "accel_x_offset",
            # "accel_y_offset",
            # "accel_z_offset",
            # "gyro_x_offset",
            # "gyro_y_offset",
            # "gyro_z_offset",
            # "pres_offset",
            # "pres_temp_offset",
            # "rp_servo1",
            # "rp_servo2",
            "time",
    ]
    for value in controller_sensors[hardware]:
        labels.append(value)
    with open(txt_File,'r') as file:

        for line in file:
            number = line.split('\t')
            data.append(number[:-1])   

    df = pd.DataFrame.from_records(data, columns=labels)
    df.to_csv(output_File,index=False)
    print("Done! Total Length: " + str(len(labels)))
converter('output\\flight_comp_rev2_sensor_data_cool.txt', 'feb0425.csv')


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		readdata                                                                   #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Reads CSV data from txt file                                               #
#                                                                                  #
####################################################################################
def readdata( Args, serialObj, show_output = True ):
     filename = Args[0]
     if (filename == ""):
        print("please specify file name")
     try:
         f = open(filename, 'r')
     except OSError:
         print("Could not read file")
     reader = "readerCSV.csv"
     converter(filename, reader)
     with open(reader, 'r') as f:
         for line in f:
             print(line)
## readData ##