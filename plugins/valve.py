from typing import Dict, Literal, Union

import click
from omegaconf import DictConfig
import pandas as pd
from tabulate import tabulate

from . import comport


class Solenoid():
    def __init__(self, serial_controller:comport.SerialController, key:str,
                 active=False):
        self.serial_controller = serial_controller
        self.conf = serial_controller.conf.valve
        self.command = self.conf.opcodes.command.solenoid
        self.opcodes = self.conf.opcodes.solenoid
        self.key = key
        if key:
            self.name = self.conf.valves[key].name
            self.number = self.conf.valves[key].number
            self.on_state = self.conf.valves[key].on_state
            self.off_state = self.conf.valves[key].off_state
            self.off_open = self.off_state == "OPEN"
            self.active = active
        else:
            self.name = ''
            self.number = 0
            self.on_state = ''
            self.off_state = ''
            self.off_open = False
            self.active = False

    def __repr__(self) -> str:
        spaces = 4 - len(str(self.number))
        res = f"[{self.number}]{' '*spaces}{self.name}"
        return res

    def to_dict(self) -> dict:
        res = {
            'ID': self.number,
            'Name': self.name,
            'Expected Active': self.active,
            'Expected State': self.on_state if self.active else self.off_state,
        }
        return res

    def is_open(self):
        return self.off_open ^ self.active

    def turn_on(self):
        self.serial_controller.send_byte(self.command)
        code = self.opcodes.on + self.number
        res = self.serial_controller.send_byte(code)
        if not res:
            self.active = True
        return res

    def turn_off(self):
        self.serial_controller.send_byte(self.command)
        code = self.opcodes.off + self.number
        res = self.serial_controller.send_byte(code)
        if not res:
            self.active = False
        return res

    def toggle(self):
        self.serial_controller.send_byte(self.command)
        code = self.opcodes.toggle + self.number
        res = self.serial_controller.send_byte(code)
        if not res:
            self.active ^= True
        return res

    def open_(self):
        self.serial_controller.send_byte(self.command)
        code = self.opcodes.open + self.number
        res = self.serial_controller.send_byte(code)
        if not res:
            self.active = not self.off_open
        return res

    def close(self):
        self.serial_controller.send_byte(self.command)
        code = self.opcodes.close + self.number
        res = self.serial_controller.send_byte(code)
        if not res:
            self.active = self.off_open
        return res

    def reset(self):
        self.active = False

    def getstate(self, state:int):
        """Get the state of the solenoid.

        Pulls the state of this specific solenoid given it's number and a
        state variable containing the states of all solenoids.

        Parameters
        ----------
        state : int
            The one-byte state returned by the solenoid controller.
        """
        active = bool(state & (1 << self.number - 1))
        state = self.on_state if active else self.off_state
        return active, state


class SolenoidController():
    def __init__(self, serial_controller:comport.SerialController):
        self.serial_controller = serial_controller
        self.conf = serial_controller.conf.valve
        self.codes = serial_controller.codes
        self.allowed_codes = self.conf.controllers
        self.allowed_boards = [v for k, v in self.codes.items()
                               if k in self.allowed_codes]

        sols = [k for k, v in self.conf.valves.items() if v.solenoid]
        self.solenoids = [Solenoid(serial_controller, s) for s in sols]

    def __repr__(self) -> str:
        res = 'Solenoids:'
        for sol in self.solenoids:
            res += f"\n{sol}"
        return res

    def get_solenoid(self, search_field:str,
                     search_value) -> Union[Solenoid, None]:
        """Gets the solenoid meeting the given condition.

        Parameters
        ----------
        search_field : str
            The field on Solenoid to search in.
        search_value : str | int | float | bool
            The value of the search field that the solenoid must match.

        Returns
        -------
        Solenoid | None
            Returns the solenoid that meets the criterion or None if no
            Solenoid satisfies the condition. If multiple solenoids meet the
            criterion, return the first one.
        """
        dummy = Solenoid(self.serial_controller, '')
        if not search_field or not hasattr(dummy, search_field):
            return
        search = (lambda c: getattr(c, search_field) == search_value)
        channels = list(filter(search, self.solenoids))
        return channels[0] if len(channels) else None

    def turn_on(self, solenoid:int):
        sol = self.get_solenoid('number', solenoid)
        return sol.turn_on()

    def turn_off(self, solenoid:int):
        sol = self.get_solenoid('number', solenoid)
        return sol.turn_off()

    def toggle(self, solenoid:int):
        sol = self.get_solenoid('number', solenoid)
        return sol.toggle()

    def open_(self, solenoid:int):
        sol = self.get_solenoid('number', solenoid)
        return sol.open_()

    def close(self, solenoid:int):
        sol = self.get_solenoid('number', solenoid)
        return sol.close()

    def reset(self):
        self.serial_controller.send_byte(self.conf.opcodes.command.solenoid)
        code = self.conf.opcodes.solenoid.reset
        res = self.serial_controller.send_byte(code)
        for sol in self.solenoids:
            sol.reset()
        return res

    def getstate(self):
        self.serial_controller.send_byte(self.conf.opcodes.command.solenoid)
        code = self.conf.opcodes.solenoid.getstate
        res = self.serial_controller.send_byte(code)
        if res:
            return res
        state = self.serial_controller.read_byte()
        if not isinstance(state, bytes):
            return state
        state = ord(state)

        # example state for testing
        # state = 0b10100011

        data = [s.to_dict() for s in self.solenoids]
        df = pd.DataFrame(data)
        sol_states = [s.getstate(state) for s in self.solenoids]
        active = [s[0] for s in sol_states]
        states = [s[1] for s in sol_states]
        df.insert(2, 'Active', active, True)
        df.insert(3, 'State', states, True)
        return df


class Valve():
    def __init__(self, serial_controller:comport.SerialController, key:str,
                 active=False):
        self.serial_controller = serial_controller
        self.conf = serial_controller.conf.valve
        self.command = self.conf.opcodes.command.valve
        self.opcodes = self.conf.opcodes.valve
        self.key = key
        if key:
            self.name = self.conf.valves[key].name
            self.number = self.conf.valves[key].number
            self.on_state = self.conf.valves[key].on_state
            self.off_state = self.conf.valves[key].off_state
            self.off_open = self.off_state == "OPEN"
            self.active = active
        else:
            self.name = ''
            self.number = 0
            self.on_state = "OPEN"
            self.off_state = "CLOSED"
            self.off_open = False
            self.active = False

    def __repr__(self) -> str:
        spaces = 4 - len(str(self.number))
        res = f"[{self.number}]{' '*spaces}{self.name}"
        return res

    def is_open(self):
        return self.off_open ^ self.active

    def to_dict(self) -> dict:
        res = {
            'ID': self.number,
            'Name': self.name,
            'Expected Active': self.active,
            'Expected State': self.on_state if self.active else self.off_state,
        }
        return res

    def open_(self):
        self.serial_controller.send_byte(self.command)
        code = self.opcodes.open + self.number
        res = self.serial_controller.send_byte(code)
        if not res:
            self.active = not self.off_open
        return res

    def close(self):
        self.serial_controller.send_byte(self.command)
        code = self.opcodes.close + self.number
        res = self.serial_controller.send_byte(code)
        if not res:
            self.active = self.off_open
        return res

    def crack(self):
        self.serial_controller.send_byte(self.command)
        code = self.opcodes.crack + self.number
        res = self.serial_controller.send_byte(code)
        if not res:
            self.active = not self.off_open
        return res

    def enable(self):
        self.active = True
        return

    def disable(self):
        self.active = False
        return

    def reset(self):
        self.active = False
        return

    def openall(self):
        self.active = not self.off_open
        return

    def getstate(self, state:int):
        """Get the state of the valve.

        Pulls the state of this specific valve given it's number and a
        state variable containing the states of all valves.

        Parameters
        ----------
        state : int
            The one-byte state returned by the valve controller.
        """
        active = bool(state & (1 << self.number - 1))
        state = self.on_state if active else self.off_state
        return active, state


class ValveController():
    def __init__(self, serial_controller:comport.SerialController):
        self.serial_controller = serial_controller
        self.conf = serial_controller.conf.valve
        self.codes = serial_controller.codes
        self.allowed_codes = self.conf.controllers
        self.allowed_boards = [v for k, v in self.codes.items()
                               if k in self.allowed_codes]

        valves = [k for k, v in self.conf.valves.items() if not v.solenoid]
        self.valves = [Valve(serial_controller, v) for v in valves]

    def __repr__(self) -> str:
        res = 'Valves:'
        for valve in self.valves:
            res += f"\n{valve}"
        return res

    def get_valve(self, search_field:str,
                  search_value) -> Union[Valve, None]:
        """Gets the valve meeting the given condition.

        Parameters
        ----------
        search_field : str
            The field on Valve to search in.
        search_value : str | int | float | bool
            The value of the search field that the valve must match.

        Returns
        -------
        Valve | None
            Returns the valve that meets the criterion or None if no
            Valve satisfies the condition. If multiple valves meet the
            criterion, return the first one.
        """
        dummy = Valve(self.serial_controller, '')
        if not search_field or not hasattr(dummy, search_field):
            return
        search = (lambda c: getattr(c, search_field) == search_value)
        channels = list(filter(search, self.valves))
        return channels[0] if len(channels) else None

    def open_(self, valve:int):
        val = self.get_valve('number', valve)
        return val.open_()

    def close(self, valve:int):
        val = self.get_valve('number', valve)
        return val.close()

    def crack(self, valve:int):
        val = self.get_valve('number', valve)
        return val.crack()

    def enable(self):
        self.serial_controller.send_byte(self.conf.opcodes.command.valve)
        code = self.conf.opcodes.valve.enable
        res = self.serial_controller.send_byte(code)
        for valve in self.valves:
            valve.enable()
        return res

    def disable(self):
        self.serial_controller.send_byte(self.conf.opcodes.command.valve)
        code = self.conf.opcodes.valve.disable
        res = self.serial_controller.send_byte(code)
        for valve in self.valves:
            valve.disable()
        return res

    def calibrate(self):
        self.serial_controller.send_byte(self.conf.opcodes.command.valve)
        code = self.conf.opcodes.valve.calibrate
        res = self.serial_controller.send_byte(code)
        return res

    def reset(self):
        self.serial_controller.send_byte(self.conf.opcodes.command.valve)
        code = self.conf.opcodes.valve.reset
        res = self.serial_controller.send_byte(code)
        for valve in self.valves:
            valve.reset()
        return res

    def openall(self):
        self.serial_controller.send_byte(self.conf.opcodes.command.valve)
        code = self.conf.opcodes.valve.openall
        res = self.serial_controller.send_byte(code)
        for valve in self.valves:
            valve.openall()
        return res

    def getstate(self):
        self.serial_controller.send_byte(self.conf.opcodes.command.valve)
        code = self.conf.opcodes.valve.getstate
        res = self.serial_controller.send_byte(code)
        if res:
            return res
        state = self.serial_controller.read_byte()
        if not isinstance(state, bytes):
            return state
        state = ord(state)

        # example state for testing
        # state = 0b10100011

        data = [v.to_dict() for v in self.valves]
        df = pd.DataFrame(data)
        valve_states = [v.getstate(state) for v in self.valves]
        active = [v[0] for v in valve_states]
        states = [v[1] for v in valve_states]
        df.insert(2, 'Active', active, True)
        df.insert(3, 'State', states, True)
        return df


@click.group(name="sol")
def solenoid():
    """Control solenoid actuation"""
    ctx = click.get_current_context().obj

    # check for properly configured and active serial port
    if 'comport' not in ctx or 'controller' not in ctx['comport']:
        raise click.ClickException("No comport has been selected.")
    serial_controller = ctx['comport']['controller']
    serial_controller : comport.SerialController
    if not serial_controller.configured:
        raise click.ClickException("No comport has been selected.")
    if not serial_controller.serial.is_open:
        raise click.ClickException("Selected comport is not open.")

    if 'solenoid' not in ctx:
        ctx['solenoid'] = {'controller': SolenoidController(serial_controller)}

@solenoid.command(name="on")
@click.argument('num', type=int)
def sol_on(num):
    """Turn on solenoid NUM on the connected board."""
    ctx = click.get_current_context().obj
    controller : SolenoidController
    controller = ctx['solenoid']['controller']

    msg = controller.turn_on(num)
    click.echo(msg)

@solenoid.command(name="off")
@click.argument('num', type=int)
def sol_off(num):
    """Turn off solenoid NUM on the connected board."""
    ctx = click.get_current_context().obj
    controller : SolenoidController
    controller = ctx['solenoid']['controller']

    msg = controller.turn_off(num)
    click.echo(msg)

@solenoid.command(name="toggle")
@click.argument('num', type=int)
def sol_toggle(num):
    """Toggle solenoid NUM on the connected board."""
    ctx = click.get_current_context().obj
    controller : SolenoidController
    controller = ctx['solenoid']['controller']

    msg = controller.toggle(num)
    click.echo(msg)

@solenoid.command(name="reset")
def sol_reset():
    """Reset solenoids on the connected board."""
    ctx = click.get_current_context().obj
    controller : SolenoidController
    controller = ctx['solenoid']['controller']

    msg = controller.reset()
    click.echo(msg)

@solenoid.command(name="list")
def sol_list():
    """List the solenoids on the connected board."""
    ctx = click.get_current_context().obj
    controller : SolenoidController
    controller = ctx['solenoid']['controller']

    click.echo(f"{controller}")

@solenoid.command(name="getstate")
def sol_getstate():
    """Get the state of the solenoids."""
    ctx = click.get_current_context().obj
    controller : SolenoidController
    controller = ctx['solenoid']['controller']

    df = controller.getstate()
    if isinstance(df, pd.DataFrame):
        vals = df[['ID', 'Name', 'Active', 'State', 'Expected State']]
        msg = tabulate(vals, headers='keys', tablefmt='psql', showindex=False)
        click.echo(msg)
    else:
        click.echo(df)

@solenoid.command(name="open")
@click.argument('num', type=int)
def sol_open(num):
    """Open solenoid NUM on the connected board."""
    ctx = click.get_current_context().obj
    controller : SolenoidController
    controller = ctx['solenoid']['controller']

    msg = controller.open_(num)
    click.echo(msg)

@solenoid.command(name="close")
@click.argument('num', type=int)
def sol_close(num):
    """Close solenoid NUM on the connected board."""
    ctx = click.get_current_context().obj
    controller : SolenoidController
    controller = ctx['solenoid']['controller']

    msg = controller.close(num)
    click.echo(msg)

@click.group(name="valve")
def valve():
    """Control valve actuation"""
    ctx = click.get_current_context().obj

    # check for properly configured and active serial port
    if 'comport' not in ctx or 'controller' not in ctx['comport']:
        raise click.ClickException("No comport has been selected.")
    serial_controller = ctx['comport']['controller']
    serial_controller : comport.SerialController
    if not serial_controller.configured:
        raise click.ClickException("No comport has been selected.")
    if not serial_controller.serial.is_open:
        raise click.ClickException("Selected comport is not open.")

    if 'valve' not in ctx:
        ctx['valve'] = {'controller': ValveController(serial_controller)}

@valve.command(name="open")
@click.argument('num', type=int)
def valve_open(num):
    """Open valve NUM on the connected board."""
    ctx = click.get_current_context().obj
    controller : ValveController
    controller = ctx['valve']['controller']

    msg = controller.open_(num)
    click.echo(msg)

@valve.command(name="close")
@click.argument('num', type=int)
def valve_close(num):
    """Close valve NUM on the connected board."""
    ctx = click.get_current_context().obj
    controller : ValveController
    controller = ctx['valve']['controller']

    msg = controller.close(num)
    click.echo(msg)

@valve.command(name="crack")
@click.argument('num', type=int)
def valve_crack(num):
    """Crack valve NUM on the connected board."""
    ctx = click.get_current_context().obj
    controller : ValveController
    controller = ctx['valve']['controller']

    msg = controller.crack(num)
    click.echo(msg)

@valve.command(name="enable")
def valve_enable():
    """Enable valve control on the connected board."""
    ctx = click.get_current_context().obj
    controller : ValveController
    controller = ctx['valve']['controller']

    msg = controller.enable()
    click.echo(msg)

@valve.command(name="disable")
def valve_disable():
    """Disable valve control on the connected board."""
    ctx = click.get_current_context().obj
    controller : ValveController
    controller = ctx['valve']['controller']

    msg = controller.disable()
    click.echo(msg)

@valve.command(name="calibrate")
def valve_calibrate():
    """Calibrate valves on the connected board."""
    ctx = click.get_current_context().obj
    controller : ValveController
    controller = ctx['valve']['controller']

    msg = controller.calibrate()
    click.echo(msg)

@valve.command(name="reset")
def valve_reset():
    """Reset all valves on the connected board."""
    ctx = click.get_current_context().obj
    controller : ValveController
    controller = ctx['valve']['controller']

    msg = controller.reset()
    click.echo(msg)

@valve.command(name="openall")
def valve_enable():
    """Open all valves on the connected board."""
    ctx = click.get_current_context().obj
    controller : ValveController
    controller = ctx['valve']['controller']

    msg = controller.openall()
    click.echo(msg)

@valve.command(name="list")
def valve_list():
    """List the valves on the connected board."""
    ctx = click.get_current_context().obj
    controller : ValveController
    controller = ctx['valve']['controller']

    click.echo(f"{controller}")

@valve.command(name="getstate")
def valve_getstate():
    """Get the state of the valves."""
    ctx = click.get_current_context().obj
    controller : ValveController
    controller = ctx['valve']['controller']

    df = controller.getstate()
    if isinstance(df, pd.DataFrame):
        vals = df[['ID', 'Name', 'Active', 'State', 'Expected State']]
        msg = tabulate(vals, headers='keys', tablefmt='psql', showindex=False)
        click.echo(msg)
    else:
        click.echo(df)
