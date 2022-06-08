###############################################################
#                                                             #
# valveController.py -- module with valve controller specific #
#                        command line functions               # 
# Author: Colton Acosta                                       #
# Date: 4/16/2022                                             #
# Sun Devil Rocketry Avionics                                 #
#                                                             #
###############################################################


# Standard Imports
import serial.tools.list_ports

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

	# Subcommand list
	subcommands = [ 'on'    , \
                    'off'   , \
                    'toggle', \
                    'reset'     ]
    
	# Options list
	options =     [ '-h', \
                    '-n'    ]

    # Option descriptions dictionary
	option_descriptions = {
		'-h' : 'Display help info',
		'-n' : 'Specify a solenoid number'
	}

	###########################################################
	# function inputs parsing                                 #
    ###########################################################

	# no subcommands/options
	if (len(Args) == 0):
		print('Error: No subcommand supplied. Valid subcommands include: ')
		for subcommand in subcommands:
			print('\t' + subcommand)
		print()
		return serialObj

	# too many inputs
	elif (len(Args) > 3): 
		print('Error: To many inputs.')
		return serialObj

	# unrecognized subcommand
	elif (not (Args[0] in subcommands)): 
		print('Error: Unrecognized subcommand. Valid subcommands include: ')
		for subcommand in subcommands:
			print('\t' + subcommand)
		print()
		return serialObj

	# unrecognized option
	elif (not(Args[1] in options)): 
		print('Error: Unrecognized option. Valid options include: ')
		for option in options:
			print('\t' + option + '\t' + option_descriptions[option]) 
		print()
		return serialObj

	# not connected to valve controller
	elif ():
		pass
		# solenoid number out of bounds

    # Help option

    # sol on

	# sol off

    # sol toggle

	# sol reset
	return
