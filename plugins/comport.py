import time
from typing import Union
from omegaconf import DictConfig
import serial.tools.list_ports

import click


class SerialController():
    def __init__(self, conf:DictConfig):
        self.conf = conf
        self.comport = None
        self.baudrate = None
        self.timeout = None
        self.serial = serial.Serial()
        self.configured = False
        self.codes = {k: v.name for k, v in conf.controllers.items()}
        self.code = None
        self.board = ''
        self.firmware = ''

    def init_comport(self, baudrate:int, comport:str, timeout:float):
        """Initialize the comport.

        Parameters
        ----------
        baudrate : int
            Baudrate of the serial port.
        comport : str
            Name of the comport (e.g. COM2 on Windows or /dev/ttyS4 on Linux).
        timeout : float
            Serial connection timeout.
        """
        self.baudrate = baudrate
        self.comport = comport
        self.timeout = timeout
        self.serial.baudrate = self.baudrate
        self.serial.port = self.comport
        self.serial.timeout = self.timeout
        self.serial.write_timeout = self.timeout
        self.configured = True

    def config_comport(self):
        """Set the serial object's settings to those of the class.
        """
        self.serial.baudrate = self.baudrate
        self.serial.comport = self.comport
        self.serial.timeout = self.timeout
        self.serial.write_timeout = self.timeout
        self.configured = True

    def list_comports(self):
        """List available comports.
        """
        def port_info(port):
            d = port.device
            m = port.manufacturer
            p = port.product or "device info unavailable"
            c = self.serial.is_open and self.serial.port == d
            return (f"{d}{' (Connected)' if c else ''}"
                    f"{' - ' + m if m else ''} - {p}")
        available_ports = serial.tools.list_ports.comports()
        msg = "Available COM ports:"
        for i, port in enumerate(available_ports):
            msg += f"\n  {i}: {port_info(port)}"
        return msg

    def open_comport(self):
        """Open the serial port.

        Returns
        -------
        str | None
            Returns an error message or nothing if successful.
        """
        if not self.configured:
            return "[ERROR] Serial port had not be properly configured."

        try:
            self.serial.open()
        except serial.SerialException as e:
            return f"[ERROR] Opening port failed with message: {e.args[0]}"

    def close_comport(self):
        """Close the serial port

        Returns
        -------
        str | None
            Returns an error message or nothing if successful.
        """
        if not self.serial.is_open:
            return "[ERROR] No open serial port detected."

        try:
            self.serial.close()
        except serial.SerialException as e:
            return f"[ERROR] Closing port failed with message: {e.args[0]}"

    def send_byte(self, byte:Union[bytes, int]):
        """Write a single byte to the serial port.

        Parameters
        ----------
        byte : bytes | int
            A single-byte bytestring to pass over the port. Integers are also
            accepted and converted to a bytestring.

        Returns
        -------
        str | None
            Returns an error message or nothing if successful.
        """
        if isinstance(byte, int):
            if byte > 0xFF:
                return "[ERROR] Cannot write more than one byte at a time!"
            byte = byte.to_bytes(1, 'big', signed=False)

        if not self.serial.is_open:
            return "[ERROR] No active serial port connection."

        try:
            self.serial.write(byte)
        except serial.SerialException as e:
            return f"[ERROR] Writing to port failed with message: {e.args[0]}"

    def read_byte(self) -> Union[bytes, str]:
        """Read a single byte from the serial port.

        Returns
        -------
        bytes | str
            Return the data read from the port.
            Return an error message if serial port is not open or the read
            fails.
        """
        if not self.serial.is_open:
            return "[ERROR] No active serial port connection."
        try:
            return self.serial.read()
        except serial.SerialException as e:
            msg = e.args[0]
            return f"[ERROR] Reading from port failed with message: {msg}"

    def read(self, num_bytes) -> Union[bytes, str]:
        """Read multiple bytes from the serial port.

        Parameters
        ----------
        num_bytes : int
            The number of bytes to read.

        Returns
        -------
        bytes | str
            Return the data read from the port.
            Return an error message if reading fails.
        """
        if not self.serial.is_open:
            return "[ERROR] No active serial port connection."
        try:
            return b''.join([self.serial.read() for _ in range(num_bytes)])
        except serial.SerialException as e:
            msg = e.args[0]
            return f"[ERROR] Reading from port failed with message: {msg}"

    def ping(self, timeout:float):
        """Ping the comport to check for USB transmission.

        Parameters
        ----------
        timeout : float
            Timeout for the ping.

        Returns
        -------
        str | tuple[float, int]
            Returns an error message or a tuple of ping time and response.
        """
        if not self.serial.is_open:
            return "[ERROR] No active serial port connection."

        self.timeout = timeout
        self.config_comport()

        opcode = 0x01
        ping_start = time.time()
        err = self.send_byte(opcode)
        if err:
            return err

        ping_data = self.serial.read()
        if not ping_data:
            return "[ERROR] Timeout expired. No device response recieved."

        ping_stop = time.time()
        ping_time = (ping_stop - ping_start)*1000
        return (ping_time, ord(ping_data))

    def connect(self, timeout:float):
        """Connect to the comport.

        Parameters
        ----------
        timeout : float
            Timeout for the ping.

        Returns
        -------
        str
            Returns an error message or the connect response.
        """
        if not self.serial.is_open:
            return "[ERROR] No active serial port connection."

        self.timeout = timeout
        self.config_comport()

        opcode = 0x02
        err = self.send_byte(opcode)
        if err:
            return err

        res = self.serial.read()
        if not res:
            return "[ERROR] Timeout expired. No device response recieved."

        return res

    def set_board(self, board_code:bytes):
        """Determine the SDR board that is connected.

        Parameters
        ----------
        board_code : bytes
            The code returned by the connect command on the connected board.
        """
        board_code = ord(board_code)
        if board_code not in self.codes:
            return f"[ERROR] {hex(board_code)} is not a recognized board code."

        controller = self.conf.controllers[board_code]

        # get firmware version if supported
        firmware = None
        if controller.firmware:
            res = self.serial.read()
            if res:
                firmware = self.conf.firmware.get(ord(res))

        firmware_desc = f" (Firmware: {firmware})" if firmware else ''

        self.board = controller
        self.firmware = firmware
        return f"Connection established with {self.board.name}{firmware_desc}"


@click.group(name="comports")
def comports():
    """Control comport connection"""
    ctx = click.get_current_context().obj
    if 'comport' not in ctx:
        ctx['comport'] = {'controller': SerialController(ctx['globals'])}

@comports.command(name="list")
def list_comports():
    """List available comports"""
    ctx = click.get_current_context().obj
    controller : SerialController
    controller = ctx['comport']['controller']

    msg = controller.list_comports()
    click.echo(msg)

@comports.command(name="open")
@click.argument('port')
@click.argument('baud')
@click.option('-t', '--timeout', help="Connection timeout on the port",
              type=float)
def open_(port:str, baud:int, timeout:float=None):
    """
    Connect to a serial device on PORT with baudrate set to BAUD.

    Supply a timeout value to set the timeout to something other than the
    default.
    """
    ctx = click.get_current_context().obj
    controller : SerialController
    controller = ctx['comport']['controller']

    if timeout == None:
        timeout = ctx['timeout']

    available_ports = serial.tools.list_ports.comports()
    devices = [p.device for p in available_ports]
    if port not in devices:
        click.echo(f"[ERROR] Invalid serial port\n{list_comports()}")

    controller.init_comport(baud, port, timeout)
    err = controller.open_comport()
    if err:
        click.echo(err)
        return
    else:
        click.echo(f"Connected to port {port} at {baud} baud.")

@comports.command(name="connect")
@click.argument('port')
@click.option('-t', '--timeout', help="Connection timeout on the port",
              type=float)
def connect(port:str, timeout:float=None):
    """
    Connect to the SDR board on PORT.

    Supply a timeout value to set the timeout to something other than the
    default.
    """
    ctx = click.get_current_context().obj
    controller : SerialController
    controller = ctx['comport']['controller']

    baud = 921600

    if timeout == None:
        timeout = ctx['timeout']

    available_ports = serial.tools.list_ports.comports()
    devices = [p.device for p in available_ports]
    if port not in devices:
        click.echo(f"[ERROR] Invalid serial port\n{list_comports()}")

    controller.init_comport(baud, port, timeout)
    err = controller.open_comport()
    if err:
        click.echo(err)
        return
    else:
        click.echo(f"Connected to port {port} at {baud} baud.")

    click.echo("Attempting to connect to board...")

    if connect:
        res = controller.connect(timeout)
        if isinstance(res, str):
            click.echo(res)
            return
        res = controller.set_board(res)
        click.echo(res)

@comports.command(name="disconnect")
def disconnect():
    """Disconnect from the active serial connection"""
    ctx = click.get_current_context().obj
    controller : SerialController
    controller = ctx['comport']['controller']

    err = controller.close_comport()
    if err:
        click.echo(err)
    else:
        click.echo(f"Disconnected from active serial port.")

@comports.command(name="ping")
@click.option('-t', '--timeout', type=float, default=1.0,
              help="Ping timeout in seconds")
def ping(timeout:float=1.0):
    """
    Ping the active serial connection to check for USB transmission.

    Supply a timeout value to set the timeout to something other than the
    default of 1 second.
    """
    ctx = click.get_current_context().obj
    controller : SerialController
    controller = ctx['comport']['controller']

    res = controller.ping(timeout)
    if isinstance(res, str): # error
        click.echo(res)
        return
    ping_time, ping_data = res
    board = controller.codes.get(ping_data, 'an unknown device')
    controller.code = ping_data
    controller.board = board
    click.echo(f"Response recieved in {ping_time:1.4f} ms from {board}")
