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
	# Local Variables                                         #
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
						 },
			   'help':   {
						 }
                       
                 }
    
	# Maximum number of arguments
	max_args = 3

	# Command type -- subcommand function
	command_type = 'subcommand'

	###########################################################
	# Basic Inputs Parsing                                    #
    ###########################################################
	parse_check = commands.parseArgs(
                                    Args,
                                    max_args,
                                    sol_inputs,
                                    command_type 
                                    )
	# Return if user input fails parse checks
	if ( not parse_check ):
		return serialObj 

	# Set subcommand and option
	user_subcommand = Args[0]
	if ( len(Args) != 1 ):
		user_option = Args[1]

	###########################################################
	# Command-Specific Checks                                 #
    ###########################################################

	###########################################################
	# Subcommand: sol help                                    #
    ###########################################################
	if (user_subcommand == "help"):
		display_help_info('sol')
		return serialObj

	###########################################################
	# Subcommand: sol on                                      #
    ###########################################################
	elif (user_subcommand == "on"):
		# Option: -h                                          
		if (user_option == '-h'):
			with open("doc/sol") as file:
				sol_doc_lines = file.readlines()
			print()
			for line in sol_doc_lines:
				print(line, end='')
			print()
			return serialObj

		# Option: -n                                          
		elif(user_option == '-n'):
			print("Solenoid on")

	###########################################################
	# Subcommand: sol off                                     #
    ###########################################################
	elif (user_subcommand == "off"):
		# Option: -h                                          
		if (user_option == '-h'):
			with open("doc/sol") as file:
				sol_doc_lines = file.readlines()
			print()
			for line in sol_doc_lines:
				print(line, end='')
			print()
			return serialObj

		# Option: -n                                          
		elif(user_option == '-n'):
			print("Solenoid off")

	###########################################################
	# Subcommand: sol toggle                                  #
    ###########################################################
	elif (user_subcommand == "toggle"):
		# Option: -h                                          
		if (user_option == '-h'):
			with open("doc/sol") as file:
				sol_doc_lines = file.readlines()
			print()
			for line in sol_doc_lines:
				print(line, end='')
			print()
			return serialObj

		# Option: -n                                          
		elif(user_option == '-n'):
			print("Solenoid toggle")

	###########################################################
	# Subcommand: sol reset                                   #
    ###########################################################
	elif (user_subcommand == "reset"):
		print("Reset solenoids")

	return serialObj
