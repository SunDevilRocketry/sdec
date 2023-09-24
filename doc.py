# contains manpage data

comports = """COMPORTS:

USAGE: comports -[OPTIONS] [PORT] [BAUD]

OPTIONS:
    -c [PORT] [BAUD] : connection to port [PORT] with baudrate [BAUD]
    -d : disconnect from comport
    -h : display this help information
    -l : list available serial ports
"""

connect = """CONNECT:

USAGE: connect -[OPTIONS] [INPUTS]

OPTIONS:
    -p [PORT]: establish a connection using serial port [PORT].
    -h : display this help information
    -d : disconnect from active serial port connection
"""

dual_deploy = """DUAL-DEPLOY:

USAGE: dual-deploy [SUBCOMMAND]

SUBCOMMANDS:
    dual-deploy status : Report the altimeter main chute deployment altitude, drogue delay, and
                         event detection sampling rates
    dual-deploy extract: Retrieve all flight data from the flight computer
    dual-deploy plot   : Plot the most recent flight data from the flight computer
    dual-deploy help   : Displays subcommand information
"""

flash = """FLASH:

USAGE: flash [SUBCOMMAND] -[OPTIONS] [INPUTS]

SUBCOMMANDS:
    flash disable : Disables the flash's write protection
                    to allow data to be written to the chip
    flash enable  : Enables the flash's write protection
                    to make the chip read-only
    flash status  : Display the contents of the flash status
                    register
    flash write   : Writes data to the flash chip
    flash read    : Reads data from the flash chip
    flash erase   : Erases the entire flash chip
    flash help    : Shows supported subcommands, options,
                    and descriptions
    flash extract : Extracts all data off the flash memory
                    chip. Data is stored in text file format

OPTIONS:
    -b [BYTE]     : Write byte [BYTE] to flash memory
    -s [STRING]   : Write string [STRING] to flash memory
    -n [NUM]      : Write [NUM] bytes to flash memory
    -a [ADDRESS]  : Use address [ADDRESS] as the base address
                    for write/read operations
    -f [FILENAME] : Use file [FILENAME] to record output
                    read data for write/read operations
    -h            : display flash usage information
"""

ignite = """IGNITE:

USAGE: ignite [SUBCOMMAND]

SUBCOMMANDS:
    ignite fire   : Fires the engine controller's ignition ematch
    ignite cont   : Displays continuity information on the engine controller's
                    or flight computer's ignition system
    ignite main   : Ignites the main parachute ejection ematch
    ignite drogue : Ignites the drogue parachute ejection ematch
    ignite help   : Displays subcommand information
"""

manpage = """Terminal Control Commands:

    clear: clears the terminal window

    help: displays the terminal control commands

    exit: exits the program

    comports -[OPTIONS] [PORTNAME] [BAUD]: allows the user to connect to a device over USB
        options:
            -c [PORTNAME] [BAUD]: connect to port [PORTNAME] with baudrate [BAUD]
            -d : disconnect the device currently being used
            -h : display comports usage information
            -l : list all available devices

    ping -[OPTIONS] [TIMEOUT]: transmits a byte over the serial port and awaits response from board
        options:
            -t [TIMEOUT]: set the timeout of the serial connection to [TIMEOUT].
            -h : display ping options

    connect -[OPTIONS] [INPUTS]: establishes a serial connection with an SDR supported board. A connection
                                 must be established before running any controller-specific commands
        options:
            -p [PORT]: establish a connection using serial port [PORT].
            -h : display connect options
            -d : disconnect from active serial port

    sensor [SUBCOMMAND] -[OPTIONS] [INPUTS]
        subcommands:
            sensor dump: Acquires readings for all onboard sensors once and
                         displays readings
            sensor poll: Displays continuous sensor readings in real-time
            sensor plot: Plots data-logger data produced by flash extract
            sensor list: Lists all available sensors for the board
                         currently connected
            sensor help: Displays subcommand information

        options:
            -n [SENSOR NUM] : specify a sensor for sensor poll
            -h : display sensor usage information

    sol [SUBCOMMAND] -[OPTIONS] [INPUTS]: controls solenoid actuation states
        subcommands:
            sol on: Asserts the acutate solenoid signal of the MCU to supply power to the solenoid
            sol off: Deasserts the acutate solenoid signal of the MCU to return the solenoid to its default state
            sol open: Opens the specified solenoid
            sol closed: Closes the specificed solenoid
            sol toggle: Changes the solenoid state
            sol getstate: Returns the state of the solenoids
            sol reset: Resets all solenoids to the default state

        options:
            -n [SOLENOID] : subcommand acts on solenoid [SOLENOID]
            -h : display solenoid options

    ignite [SUBCOMMAND]: provides control to the engine controller's ignition system
        subcommands:
            ignite fire   : Fires the engine controller's ignition ematch
            ignite cont   : Displays continuity information on the engine controller's ignition system
            ignite main   : Ignites the main parachute ejection ematch
            ignite drogue : Ignites the drogue parachute ejection ematch
            ignite help   : Displays subcommand information

    power [SUBCOMMAND]: provides control to the engine controller's power supply system
        subcommands:
            power source: Displays the power supply source of the MCU
            ignite help: Displays subcommand information

    flash [SUCOMMAND] -[OPTIONS] [INPUTS]: Reads and writes data to the engine controller's flash memory
        subcommands:
            flash disable: Disables the flash's write protection to allow data to be written to the chip
            flash enable : Enables the flash's write protection to make the chip read-only
            flash status : Displays the contents of the status register
            flash write  : Writes data to the flash chip
            flash read   : Reads data from the flash chip
            flash erase  : Erases the entire flash chip
            flash help   : Shows supported subcommands, options,
                           and descriptions

    dual-deploy [SUBCOMMAND]: Allows the user to probe and test the flight computer's dual deploy
                              system. Requires a connection to a flight computer running the dual deploy firmware
        subcommands:
            dual-deploy status : Report the altimeter main chute deployment altitude, drogue delay, and
                                 event detection sampling rates
            dual-deploy extract: Retrieve all flight data from the flight computer
            dual-deploy plot   : Plot the most recent flight data from the flight computer
            dual-deploy help   : Displays subcommand information

    valve [SUBCOMMAND] -[OPTIONS] [INPUTS]: Actuates specified servo-actuated ball valves. Requires a connection
                                            to a valve controller or liquid engine controller
        subcommands:
            valve enable    : Enable the valves to be actuated
            valve disable   : Disable the valves
            valve open      : Open a specified valve
            valve close     : Close a specified valve
            valve calibrate : Calibrate the valves by setting the closed position
            valve list      : List valid valve names
            valve help      : Display valve usage information

        options:
            -n [VALVE] : Subcommand acts on valve [VALVE]
"""

ping = """PING:

USAGE: ping -[OPTIONS] [TIMEOUT]

OPTIONS:
    -t [TIMEOUT]: set the timeout of the serial connection to [TIMEOUT] (seconds).
    -h : display this help information
"""

power = """POWER:

USAGE: power [SUBCOMMAND]

SUBCOMMANDS:
    power source: Displays the power supply source of the MCU
    ignite help: Displays subcommand information
"""

sensor = """SENSOR:

USAGE: SENSOR [SUBCOMMAND] -[OPTIONS] [INPUTS]

SUBCOMMANDS:
    sensor dump: Acquires readings for all onboard sensors once and
                 displays readings
    sensor poll: Displays continuous sensor readings in real-time
    sensor plot: Plots data-logger data produced by flash extract
    sensor list: Lists all available sensors for the board
                 currently connected
    sensor help: Displays subcommand information

OPTIONS:
    -n [SENSOR NUM] : specify a sensor for sensor poll
    -h : display sensor usage information
"""

sol = """SOL:

USAGE: sol [SUBCOMMAND] -[OPTIONS] [INPUTS]

SUBCOMMANDS:
    sol on: Asserts the acutate solenoid signal of the MCU to supply power to the solenoid
    sol off: Deasserts the acutate solenoid signal of the MCU to return the solenoid to its default state
    sol open: Opens the specified solenoid
    sol closed: Closes the specificed solenoid
    sol toggle: Changes the solenoid state
    sol reset: Resets all solenoids to the default state
    sol getstate: Returns the state of the solenoids
    sol help: Displays solenoid help information

OPTIONS:
    -n [SOLENOID] : subcommand acts on solenoid [SOLENOID]
    -h : display solenoid options
"""

valve = """VALVE:

USAGE: valve [SUBCOMMAND] -[OPTIONS] [INPUTS]

SUBCOMMANDS:
    valve enable   : Enables the valves to be actuated
    valve disable  : Disables the valves
    valve open     : Opens the specified valve
    valve close    : Closed the specified valve
    valve calibrate: Calibrates the valves by setting the closed position
    valve list     : List valid valve names
    valve help     : Displays valve help information

OPTIONS:
    -n [VALVE] : Subcommand acts on valve [VALVE]
"""
