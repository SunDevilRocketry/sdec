import time
import numpy                    as np
from   matplotlib import pyplot as plt
import struct

# Project imports
import sensor_conv
import commands
from   config      import *
from   controller  import *
from datetime import datetime


####################################################################################
#                                                                                  #
# PROCEDURE:                                                                       #
#         plot_sensor_realtime_init                                                    #
#                                                                                  #
# DESCRIPTION:                                                                     #
#        Initialize sensor readouts plot with labels and units
#        ARGS: 
#              controller: SerialController
#              sensor_readouts: dictionary of sensors and their readouts
#                                                                                  #
####################################################################################
def plot_sensor_realtime_init( controller, sensor_readouts ):
    # Create a fig with sensor number of axs
    fig, axs = plt.subplots(len(sensor_readouts))
    graphs = {}
    axs_sensor = {}
    fig.suptitle("Real time sensor polling plot")
    idx = 0
    readouts_dict = {}
    range_dict = {}
    for sensor in sensor_readouts:
        # Set axis labels containing sensor and unit
        units = sensor_units[controller][sensor]

        axs[idx].set_xlabel("time (s)")

        if (units):
            axs[idx].set_ylabel(sensor + " (" + units + ")")
        else:
            axs[idx].set_ylabel(sensor)
        
        axs_sensor[sensor] = axs[idx]

        # Plot a sample at a time
        readouts = sensor_readouts[sensor]

        readouts_dict[sensor] = [readouts]
        range_dict[sensor] = {"max": readouts, "min": readouts}

        graph = axs[idx].plot(0, readouts_dict[sensor])
        graphs[sensor] = graph
        # Increment an index
        idx = idx + 1
        # plt.pause(0.02)
    return graphs, fig, axs_sensor, readouts_dict, range_dict
## plot_sensor_realtime_init ##

#################################################################################################
#                                                                                               #
# PROCEDURE:                                                                                    #
#         plot_sensor_realtime_start                                                            #
#                                                                                               #
# DESCRIPTION:                                                                                  #
#        Start sensor readouts plot with labels and units                                       #
#        ARGS:                                                                                  #
#              controller: SerialController                                                     #
#              graphs: dictionary of graphs associated with a sensor initialized                #
#              axs_sensor: dictionary of axs associated with a sensor initialized               #
#              readouts_dict: dictionary containing list of readouts associated with a sensor   #
#              sensor_readouts: dictionary of sensors and their readouts                        #
#              seconds: list of seconds lasted                                                  #
#                                                                                               #
#################################################################################################
def plot_sensor_realtime_start( controller, graphs, axs_sensor, readouts_dict, range_dict, sensor_readouts, seconds):
    for sensor in sensor_readouts:
        # Update values
        readouts = sensor_readouts[sensor]
        readouts_dict[sensor].append(readouts)
        
        # Update range
        if readouts > range_dict[sensor]["max"]:
            range_dict[sensor]["max"] = readouts
        if readouts < range_dict[sensor]["min"]:
            range_dict[sensor]["min"] = readouts

        # Destroy old graphs 
        graphs[sensor][0].remove()

        # Plot new graphs
        # Set axis labels containing sensor and unit
        units = sensor_units[controller][sensor]

        axs_sensor[sensor].set_xlabel("time (s)")

        if (units):
            axs_sensor[sensor].set_ylabel(sensor + " (" + units + ")")
        else:
            axs_sensor[sensor].set_ylabel(sensor)

        graphs[sensor] = axs_sensor[sensor].plot(seconds, readouts_dict[sensor][:len(seconds)], "k")

        axs_sensor[sensor].grid("on")
        axs_sensor[sensor].set_xlim([seconds[0], seconds[-1]])
        scale = 0.5
        axs_sensor[sensor].set_ylim([range_dict[sensor]["min"]-abs(range_dict[sensor]["min"])*scale, range_dict[sensor]["max"]+abs(range_dict[sensor]["max"])*scale])    
    
        plt.pause(0.002)
    return graphs
## plot_sensor_realtime_start ##
