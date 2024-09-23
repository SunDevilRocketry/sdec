# Sun Devil Embedded Control (sdec)

## Description

sdec is a terminal program and Python library which allows
the user to access all functionality available on Sun Devil Rocketry PCBs either interactively or programatically (which is what our [Liquid Engine GUI](https://github.com/SunDevilRocketry/liquid_engine_gui) does).

## Installation
1. Make sure you have a working Python installation with pip. (Be sure it's added to your path, Windows people!)
2. Install SDEC with pip. This will pull all dependencies automatically.

        pip3 install git+https://github.com/SunDevilRocketry/sdec
3. Run sdec

        python -m sdec

    Or on some systems:

        python3 -m sdec
    > If you've git cloned the sdec repository, please make sure you run this command in a different folder from the repository to avoid issues.
When run, if one doesn't already exist, sdec will automically create an output folder. Please make sure you are able to write files in whatever folder you run sdec in.

## Supported Boards:
- L0002: Liquid Engine Controller (Rev 3/Rev 4)
- A0002: Flight Computer (Rev 1)
- L0005: Valve Controller (Rev 2)

For more information on usage of the above hardware with the Terminal-Control program, please refer to the board's firmware documentation.

## Developer Information
### Getting Started
Clone this repo.
Read [Project Directory Structure](#project-directory-structure) for where to make modifications.

To test your changes, you have two options.
Within the repository folder, you can run ```python3 -m sdec``` to use the development version rather than the module installed with pip.

Alternatively, you can run ```pip install PATH/TO/GIT/REPO/sdec/sdec``` to install the module with pip to make sure you haven't broken packaging.

### Installing a different git branch
```pip3 install git+https://github.com/SunDevilRocketry/sdec@branchname```

### Notes for versioning
When you make a branch, push to main, make a major new commit, etcetera, make sure you update the version accordingly. The version format we are using is as follows:
```YYYY.Mversion.MINORVERSION(+branch)```
- ```YYYY```: The year of the commit
- ```M```: The month of the commit, 1 digit long in 1 digit months and 2 digits long in 2 digit months.
- ```MINORVERSION```: The sub-version released within the month.
- ```(+branch)```: The git branch of the library, included only if it is not the main branch.

For instance, for the second version pushed to a branch called "bananas" in September 2024 would be versioned as ```2024.9.1+bananas```.
### Project Directory Structure
The sdec source code is in a folder called sdec. Here is the purpose of each file:
- ```sdec/__main__.py```: Main program loop
- ```sdec/commands.py```: Implementation of general commands
- ```sdec/config.py```: Global configuration parameters
- ```sdec/controller.py```: Hardware information for the supported boards
- ```sdec/engineController.py```: Implementation of liquid engine-specific commands
- ```sdec/flightComputer.py```: Implementation of flight computer-specific commands
- ```sdec/hw_commands.py```: Implementation of general hardware commands
- ```sdec/plot_data.py```: Sensor data output
- ```sdev/valveController.py```: Implementation of commands specific to the valve controller.
### Operating Principle
Commands which communicate with an embedded board inlcude a 1 byte opcode, which is the first byte transmitted to the board when a command is issued. Opcode 0x00 is reserved as the nop command. Nop commands are ignored by the embedded board.

<h2>General Commands:</h2>

<h3>clear</h3>
<p>Description: clears the terminal window</p>

<h3>help</h3>
<p>Description: displays all terminal control commands and options</p>

<h3>exit</h3>
<p>Description: exits the program</p>

<h3>comports</h3>
<p>Description: allows the user to connect to a device over USB</p>
<p>Usage: comports -[OPTION] [INPUTS]</p>
<p>Options: 
<ul>
    <li> -c [PORTNAME] [BAUD]: connect to port [PORTNAME] with baudrate [BAUD] </li> 
    <li> -d : disconnect the device currently being used </li>
    <li> -h : display comports options</li>
    <li> -l : list all available devices</li>
</ul>
</p>

<h3>ping</h3>
<p>Opcode: 0x01</p>
<p>Description: transmits a byte over the serial port and awaits response from board</p>
<p>Usage: ping -[OPTION] [INPUTS]</p>
<p>Options:
    <ul>
        <li> -t [TIMEOUT]: set the timeout of the serial connection to [TIMEOUT].</li>
	<li> -h : display ping options </li>
    </ul>
</p>

<h3>connect</h3>
<p>Opcode: 0x02</p>
<p>Description: Establishes a serial connection with an SDR supported board. A 
connection must be established before running any controller-specific commands.</p>
<p>Usage: connect -[OPTION] [INPUTS]</p>
<p>Options:
    <ul>
    <li> -p [PORT]: establish a connection using serial port [PORT].</li>
	<li> -h : display connect options </li>
	<li> -d : disconnect from active serial port </li>
    </ul>
</p>

<h2>General Hardware Commands:</h2>

<h3>ignite</h3>
<p>Opcode: 0x20</p>
<p>Description: Direct control of ematch ignition circuitry. Requires an active connection
to the engine controller or flight computer. </p>
<p>Usage: ignition [SUBCOMMAND]</p>
<p>Subcommands: </p>
<p>fire:   Triggers the engine ignition ematch (Engine Controller)</p>
<p>main:   Triggers the main parachute deployment ematch (Flight Computer)</p>
<p>drogue: Triggers the drogue parachute deployment ematch (Flight Computer)</p>
<p>cont:   Displays continuity information on ignition components</p>
<p>help:   Shows supported subcommands and descriptions</p>

<h3>sensor</h3>
<p>Opcode: 0x03</p>
<p>Description: Get readings from on-board sensors/ADCs. Requires an active
connection to a Sun Devil Rocketry board.</p>
<p>Usage: sensor [SUBCOMMAND] -[OPTIONS] [INPUTS]</p>
<p>Subcommands: </p>
<p>dump: Polls all onboard sensors and displays readings in console</p>
<p>poll: Displays readings from a specified sensor(s) in real time</p>
<p>plot: Plots data-logger data produced by flash extract </p>
<p>list: Displays all sensors and associated codes for the currently connected board</p>
<p>help: Shows supported subcommands, options, and descriptions</p>
<p>Options:
    <ul>
        <li> -n [SENSOR NUM]: Specify a sensor for the sensor poll subcommand</li>
		<li> -h : display sensor usage information </li>
    </ul>
</p>

<h3>flash</h3>
<p>Opcode: 0x22</p>
<p>Description: Read from and write to the external flash chip. Requires an active
connection to the engine controller or flight computer.</p>
<p>Usage: flash [SUBCOMMAND] -[OPTIONS] [INPUTS]</p>
<p>Subcommands: </p>
<p>enable: Disables the flash write-protection to allow writing to the chip</p>
<p>disable: Enables the flash write-protection to make the chip read-only</p>
<p>status: Displays the contents of the flash chip's status register</p>
<p>write: Write data to the flash chip</p>
<p>read: Read data from the flash chip</p>
<p>erase: Erase the entire flash chip</p>
<p>extract: extract all data from the flash chip and export to a text file</p>
<p>help: Shows supported subcommands, options, and descriptions</p>
<p>Options:
    <ul>
        <li> -b [BYTE]    : Write byte [BYTE] to flash memory.</li>
        <li> -s [STRING]  : Write string [STRING] to flash memory.</li>
        <li> -n [NUM]     : Read [NUM] bytes from flash memory. </li>
        <li> -a [ADDRESS] : Use the address [ADDRESS] as the base address for
                            write/read operations. </li>
        <li> -f [FILENAME]: Use file [FILENAME] to record output read data or
                            input write data. Files are stored in the input/
                            output directories. </li>
		<li> -h : display flash usage information </li>
    </ul>
</p>

<h2> A0002 Flight Computer Commands: </h2>

<h3>dual-deploy</h3>
<p>Opcode: 0xA0</p>
<p>Description: Allows the user to probe and test the flight computer's dual deploy
system. Requires a connection to a flight computer running the dual deploy firmware.</p>
<p>Usage: dual-deploy [SUBCOMMAND]</p>
<p>Subcommands: </p>
<p>status: Report the altimeter main chute deployment altitude, drogue delay, and 
event detection sampling rates.</p>
<p>extract: Retrieve all flight data from the computer</p>
<p>plot:    Plot flight data and events from latest flight</p>
<p>help: Shows supported subcommands and descriptions</p>

<h2> L0002 Liquid Engine Controller Commands: </h2>

<h3>power</h3>
<p>Opcode: 0x21</p>
<p>Description: Direct control of the engine controller power supply. Requires an 
active connection to the engine controller. </p>
<p>Usage: power [SUBCOMMAND]</p>
<p>Subcommands: </p>
<p>source: Determines whether the MCU is being powered by the buck converter or USB</p>
<p>help: Shows supported subcommands and descriptions</p>

<h2> L0005 Valve Controller Commands: </h2>

<h3>acstat</h3>
<p>Opcode: 0x50</p>
<p>Description: Checks whether AC power for solenoid actuation is detected by the MCU. </p>

<h3>sol</h3>
<p>Opcode: 0x51</p>
<p>Description: Actuates a solenoid. </p>
<p>Usage: sol [SUBCOMMAND] -[OPTION] [INPUTS]</p>
<p>Subcommands: </p>
<p>sol on : Asserts the acutate solenoid signal of the MCU to supply power to the solenoid. The open/close state of the solenoid depends on whether the attached solenoid is normally open or closed.</p>
<p>sol off : Deasserts the acutate solenoid signal of the MCU to return the solenoid to its default state. The open/close state of the solenoid depends on whether the attached solenoid is normally open or closed.</p>
<p>sol open: Opens the specified solenoid</p>
<p>sol close: Closes the specified solenoid</p>
<p>sol toggle : Changes the solenoid state. The open/close state of the solenoid depends on whether the attached solenoid is normally open or closed.</p>
<p>sol reset : Resets all solenoids to the default state. The state of each solenoid depends on whether the solenoid is open or closed. No options</p>
<p>sol getstate: Returns the states of the solenoids</p>
<p>sol help : Displays sol usage information. No options. </p>
<p>Options:
    <ul>
        <li> -n [SOLENOID]: operate on solenoid [SOLENOID]. Valid [SOLENOID] inputs range from 1 to 6.</li>
		<li> -h : display sol usage information </li>
    </ul>

<h3>valve</h3>
<p>Opcode: 0x52</p>
<p>Description: Actuates a servo-actuated ball valve. </p>
<p>Usage: valve [SUBCOMMAND] -[OPTION] [INPUTS]</p>
<p>Subcommands: </p>
<p>valve enable    : Enable the valves to be actuated</p>
<p>valve disable   : Disable the valves</p>
<p>valve open      : Opens the specified valve </p>
<p>valve close     : Closes the specified valve </p>
<p>valve calibrate : Calibrates the valves by finding and setting the closed position</p>
<p>valve list      : Lists valid valve names</p>
<p>valve help      : Displays valve usage information </p>
<p>Options:
    <ul>
        <li> -n [VALVE]: operate on valve [VALVE] </li>
    </ul>
</p>
