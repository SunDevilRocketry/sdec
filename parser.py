import matplotlib.pyplot
import pandas as pd
import matplotlib
from controller import controller_sensors, controller_names, firmware_ids

            

data = []


length = len(data)

def converter(txt_File, output_File):
    hardware = ""
    for i in range(0, len(controller_names)):
        print(str(i + 1) + ". " + controller_names[i])
    number = input("Which Hardware would you like to select? Enter a number. \n")
    
    firmware_names = list(firmware_ids.values())
    for i in range(0, len(firmware_names)):
        print(str(i + 1) + ". " + firmware_names[i])
    firmware_num = int(input("Which Firmware would you like to select? Enter a number. \n"))
    
    hardware = controller_names[int(number) - 1]
    firmware = firmware_names[firmware_num - 1]

    print(f"Selected Hardware: {hardware}")
    print(f"Selected firmware: {firmware}")

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
    if firmware_num - 1 == 4: # Checking if firmware = 4, the index of Active Roll 
        labels.append("feedback")

    with open(txt_File,'r') as file:

        for line in file:
            number = line.split('\t')
            data.append(number[:-1])   

    df = pd.DataFrame.from_records(data, columns=labels)
    df.to_csv(output_File,index=False)
    print("Done! Number of columns: " + str(len(labels)))
#converter('output\flight_comp_rev2_sensor_data_cool.txt', 'output\feb0425.csv')


####################################################################################
#                                                                                  #
# COMMAND:                                                                         #
# 		parse-output                                                               #
#                                                                                  #
# DESCRIPTION:                                                                     #
# 		Reads CSV data from txt file                                               #
#                                                                                  #
####################################################################################
def parse_output( Args, serialObj, show_output = True ):
     filename = input("Enter file path: ")
     if (filename == ""):
        print("Please specify file path: ")
     try:
         f = open(filename, 'r')
     except OSError:
         try:
            filename = "output/" + filename
            f = open(filename, 'r')
         except OSError:
            print("Could not read file: ")
            return
     reader = "output/parsedCSV.csv"
     converter(filename, reader)
## parse_output ##