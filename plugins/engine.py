from typing import Dict, Literal, Union

import click

from . import comport, valve


class EngineController():
    def __init__(self, serial_controller:comport.SerialController):
        self.serial_controller = serial_controller
        self.conf = self.serial_controller.conf.engine
        self.codes = self.serial_controller.codes
        self.allowed_codes = self.conf.controllers
        self.allowed_boards = [v for k, v in self.codes.items()
                               if k in self.allowed_codes]

        self.valve_controller = valve.ValveController(serial_controller)


@click.group(name="engine")
def engine():
    """Control engine functions"""
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

    if 'engine' not in ctx:
        ctx['engine'] = {'controller': EngineController(serial_controller)}
