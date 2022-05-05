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

<h2>General Commands:</h2>

<h3>clear</h3>
<p>Description: clears the terminal window</p>

<h3>help</h3>
<p>Description: displays all terminal control commands and options</p>

<h3>exit</h3>
<p>Description: exits the program</p>

<h3>comports</h3>
<p>Description: allows the user to connect to a device over USB</p>
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
<p>Options:
    <ul>
        <li> -t [TIMEOUT]: set the timeout of the serial connection to [TIMEOUT].</li>
	<li> -h : display ping options </li>
    </ul>
</p>

<h2> L0002 Liquid Engine Controller Commands: </h2>
<h2> L0005 Valve Controller Commands: </h2>

<h3>acstat</h3>
<p>Opcode: 0x50</p>
<p>Description: Checks whether AC power is detected by the MCU. </p>
