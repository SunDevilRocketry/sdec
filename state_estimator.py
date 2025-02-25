####################################################################################
#                                                                                  #
# state_estimator.py -- Processes sensor outputs to retrieve velocity, position,   #
#            and other estimates of vehicle state                                  #
#                                                                                  #
# Author: Eli Sells                                                                #
# Date: 2/24/2025                                                                  #
# Sun Devil Rocketry Avionics                                                      #
#                                                                                  #
####################################################################################

# IMPORTS
import os
import csv

import controller

# GLOBAL VARIABLES

# FORMAT: Take the first four words of the sensor data output.
supported_platforms = [
    ["flight_comp_rev2_sensor", controller.controller_names[4]]
]

######################################################################
#   Supporting Functions                                             #
######################################################################

# Return type: Tuple { output_file, platform }
def get_sensor_output_file():
    # Get available output files
    outputs = os.listdir('./output')

    # Error check: empty output directory
    if outputs == []:
        print( "Output directory is empty. Could not retrieve file." )
        return
    
    # Retrieve a list of files
    print( "Select a file to use: ")
    currNum = 1
    platform = None

    # Validate file format
    outputFiles = []
    for file in outputs:
        platform = get_platform(file)
        if platform is not None:
            print( str(currNum) + " - " + file )
            currNum = currNum + 1
            outputFiles.append(file)
    
    # Allow the user to select a file
    validInput = False
    while not validInput:
        selection = int(input("\nEnter number: "))
        if selection < 1 or selection > currNum:
            print("Invalid input. Try again.")
        else:
            validInput = True
            return ["./output/" + outputFiles[selection - 1], platform]
    return 

# Retrieve the platform for a given file output
def get_platform( file ):
    for platform in supported_platforms:
        if file.find( platform[0] ) > -1:
            return platform[1]
    return

def parse_data_file( sensor_data_file ):
    # Get the file as a 2d list
    sensorOutputs = []
    with open(sensor_data_file) as file:
        for line in file:
            contents = [float(s) for s in line[:-1].split("\t") if s.strip()]
            if contents[0] == 1:
                sensorOutputs.append(contents)
    
    return sensorOutputs


def convert_outputs( sensorOutputs, platform ):
    sensors = list(controller.controller_sensors[platform].keys())
    for line in sensorOutputs:
        for output in line[2:]:
            return




        
# These function parameters are unused, but passed in by the terminal. When invoking,
# feel free to just use zeroes.
def state_estimator( userArgs, terminalSerObj ):
    # Get parameters for estimation
    print( "STATE ESTIMATION: \n")
    output = get_sensor_output_file()
    sensor_data_file = output[0]
    platform = output[1]
    print("Selection: " + sensor_data_file)

    print("Parsing file...")
    sensorOutputs = parse_data_file( sensor_data_file )

    print("Available subroutines:")
    print("1 - All outputs")
    validInput = False
    while not validInput:
        selection = int(input("Select option: "))
        match selection:
            case 1:
                validInput = True
                print("Converting columns...")
                columns = convert_outputs( sensorOutputs, platform )

            case _:
                print("Invalid input. Try again.")

    # -.-.-.-.-.-
    return


state_estimator( 0, 0 )