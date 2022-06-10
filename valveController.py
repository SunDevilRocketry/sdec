###############################################################
#                                                             #
# valveController.py -- module with valve controller specific #
#                        command line functions               # 
# Author: Colton Acosta                                       #
# Date: 4/16/2022                                             #
# Sun Devil Rocketry Avionics                                 #
#                                                             #
###############################################################


###############################################################
# Standard Imports                                            #
###############################################################
import serial.tools.list_ports


###############################################################
# Project Modules                                             #
###############################################################
import commands


###############################################################
#                                                             #
# COMMAND:                                                    #
# 		sol                                                   #
#                                                             #
# DESCRIPTION:                                                #
# 		control the actuation state of solenoids              #
#                                                             #
###############################################################
def sol(Args, serialObj):
	###########################################################
	# local variables                                         #
    ###########################################################

	# Subcommand and Options Dictionary
	sol_inputs = { 
			   'on':     {
							'-h' : 'Display help info',
							'-n' : 'Specify a solenoid number'
						 } ,
			   'off':    {
							'-h' : 'Display help info',
							'-n' : 'Specify a solenoid number'
						 } , 
			   'toggle': {
							'-h' : 'Display help info',
							'-n' : 'Specify a solenoid number'
						 },
			   'reset':  {
							'-h' : 'Display help info',
							'-n' : 'Specify a solenoid number'
						 },
			   'help':   {
						 },
                       
                 }
    
	# Maximum number of arguments
	max_args = 3

	# Command type -- subcommand function
	command_type = 'subcommand'

	###########################################################
	# function inputs parsing                                 #
    ###########################################################
	parse_check = commands.parseArgs(
                                    Args,
                                    max_args,
                                    sol_inputs,
                                    command_type 
                                    )
	if (not parse_check):
		return serialObj # user inputs failed parse tests

	# User input passed parse checks
	return serialObj
