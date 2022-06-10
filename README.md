<h1> Terminal-Control</h1>

<h2>Description:</h2> 

<p>The Terminal-Control program is a python-based terminal program which allows
the user to access all functionality available on Sun Devil Rocketry PCBs.</p>

<h2>Installation:</h2>
<p>The Terminal-Control program requires a functional python installation and the
pyserial module, which can be installed using pip. The program is run within a single 
terminal, and may be invoked from the command line using the python interpreter. Support is
currently available for Windows and Linux operating systems. </p>

<h2>Supported Boards:</h2>
<p>
L0002: Liquid Engine Controller (Rev 3)

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
<p>Description: Establishes a serial connection with an SDR supported board. A connection must
be established before running any controller-specific commands.</p>
<p>Usage: connect -[OPTION] [INPUTS]</p>
<p>Options:
    <ul>
    <li> -p [PORT]: establish a connection using serial port [PORT].</li>
	<li> -h : display connect options </li>
	<li> -d : disconnect from active serial port </li>
    </ul>
</p>

<h2> L0002 Liquid Engine Controller Commands: </h2>
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
		<li> -h : display sol off options </li>
    </ul>
</p>
