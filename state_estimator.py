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
import math
import numpy as np

import controller

# GLOBAL VARIABLES

# FORMAT: Take the first four words of the sensor data output.
supported_platforms = {
    "flight_comp_rev2_sensor": controller.controller_names[4]
}

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
            return "./output/" + outputFiles[selection - 1]
    return 

# Retrieve the platform for a given file output
def get_platform( file ):
    for platform in supported_platforms:
        if file.find( platform ) > -1:
            return supported_platforms[platform]
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
    idx = 0

    conv = {}
    conv['time'] = []
    for sensor in sensors:
        conv[sensor] = []

    #print(conv)
    #print(sensorOutputs)
    
    #print(len(conv))
    #print(len(sensorOutputs))
    #print("--")
    #for i in range(len(sensorOutputs)):
    #    print(len(sensorOutputs[i]))

    for i in range(len(sensorOutputs)):
        conv['time'].append(sensorOutputs[i][2])

    for i in range(len(sensorOutputs)):
            for j, sensor in enumerate(sensors):
                conv[sensor].append(sensorOutputs[i][j+3])

    return conv

# Returns list of values corresponding to each time
def get_velocity_from_position( columns ):
    time = columns["time"]
    accX = columns["accX"]
    accY = columns["accY"]
    accZ = columns["accZ"]

    # Calculate the velocity: deltaV = deltaT * a
    velocity = {}
    velocity['time'] = time
    velocity['velX'] = [0]
    for i in range(1, len(time)):
        delta = columns["time"][i] - columns["time"][i - 1]
        velocity['velX'].append(delta * columns["accX"][i])
    velocity['velY'] = [0]
    for i in range(1, len(time)):
        delta = columns["time"][i] - columns["time"][i - 1]
        velocity['velY'].append(delta * columns["accY"][i])
    velocity['velZ'] = [0]
    for i in range(1, len(time)):
        delta = columns["time"][i] - columns["time"][i - 1]
        velocity['velZ'].append(delta * columns["accZ"][i])

    velocity['vel'] = [0]
    for val in range(len(velocity['velX'])):
        velocity['vel'].append( math.sqrt( (velocity['velX'][val] ** 2) + (velocity['velY'][val] ** 2) + (velocity['velZ'][val] ** 2) ) )

    return velocity

def get_displacement_from_velocity( velocity ):
    # Calculate the velocity: deltaV = deltaT * a
    displacement = {}
    displacement['dispX'] = [0]
    for i in range(1, len(velocity['time'])):
        delta = velocity["time"][i] - velocity["time"][i - 1]
        displacement['dispX'].append(delta * velocity["velX"][i])
    displacement['dispY'] = [0]
    for i in range(1, len(velocity['time'])):
        delta = velocity["time"][i] - velocity["time"][i - 1]
        displacement['dispY'].append(delta * velocity["velY"][i])
    displacement['dispZ'] = [0]
    for i in range(1, len(velocity['time'])):
        delta = velocity["time"][i] - velocity["time"][i - 1]
        displacement['dispZ'].append(delta * velocity["velZ"][i])

    displacement['disp'] = [0]
    for val in range(len(velocity['time'])):
        displacement['disp'].append( math.sqrt( (displacement['dispX'][val] ** 2) + (displacement['dispY'][val] ** 2) + (displacement['dispZ'][val] ** 2) ) )

    return displacement


        
# These function parameters are unused, but passed in by the terminal. When invoking,
# feel free to just use zeroes.
def state_estimator( userArgs, terminalSerObj ):
    # Get parameters for estimation
    print( "STATE ESTIMATION: \n")
    sensor_data_file = get_sensor_output_file()
    platform = get_platform(sensor_data_file)
    print("Selection: " + sensor_data_file)

    print("Parsing file...")
    sensorOutputs = parse_data_file( sensor_data_file )

    print("Converting columns...")
    columns = convert_outputs( sensorOutputs, platform )

    print("Available subroutines:")
    print("1 - All outputs")
    print("2 - Velocity from Acceleration")
    print("3 - Position from Acceleration")
    print("q - Exit")

    exit = False
    while not exit:
        selection = input("Select option: ")
        match selection:
            case 1:
                velocity = get_velocity_from_position( columns )
                displacement = get_displacement_from_velocity( velocity )
                print(velocity)
                print(displacement)

            case 2:
                print( get_velocity_from_position( columns ) )

            case 3:
                print( get_displacement_from_velocity( get_velocity_from_position( columns ) ) )

            case 'q':
                exit = True

            case _:
                print("Invalid input. Try again.")

    # -.-.-.-.-.-
    return


state_estimator( 0, 0 )