<h1> Sun Devil Embedded Control (sdec)</h1>

<h2>Description:</h2> 

<p>sdec is a python-based terminal program which allows
the user to access all functionality available on Sun Devil Rocketry PCBs.</p>

<h2>Installation:</h2>
<p>The Terminal-Control program requires a functional python installation and the
pyserial module, which can be installed using pip. The program is run within a single 
terminal, and may be invoked from the command line using the python interpreter. Support is
currently available for Windows and Linux operating systems. </p>

<h2>Supported Boards:</h2>
<p>
L0002: Liquid Engine Controller (Rev 3/Rev 4)

A0002: Flight Computer (Rev 1)

L0005: Valve Controller (Rev 2)

</p>
<p>For more information on usage of the above hardware with the Terminal-Control program, please
refer to the board's firmware documentation </p>

<h2>Developer Information:</h2>
<p>Commands which communicate with an embedded board inlcude a 1 byte opcode, which is the first byte
   transmitted to the board when a command is issued. Opcode 0x00 is reserved as the nop command. Nop commands 
   are ignored by the embedded board.</p>

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
<p>sol toggle : Changes the solenoid state. The open/close state of the solenoid depends on whether the attached solenoid is normally open or closed.</p>
<p>sol reset : Resets all solenoids to the default state. The state of each solenoid depends on whether the solenoid is open or closed. No options</p>
<p>sol help : Displays sol usage information. No options. </p>
<p>Options:
    <ul>
        <li> -n [SOLENOID]: operate on solenoid [SOLENOID]. Valid [SOLENOID] inputs range from 1 to 6.</li>
		<li> -h : display sol usage information </li>
    </ul>
</p>
