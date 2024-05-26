from typing import Dict, Literal, Union

import click

from . import comport


class HardwareController():
    def __init__(self, serial_controller:comport.SerialController):
        self.serial_controller = serial_controller
        self.conf = self.serial_controller.conf.hardware
        self.codes = self.serial_controller.codes
        self.allowed_codes = self.conf.controllers
        self.allowed_boards = [v for k, v in self.codes.items()
                               if k in self.allowed_codes]


@click.group(name="hardware")
def hardware():
    """General hardware commands"""
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

    if 'hardware' not in ctx:
        ctx['hardware'] = {'controller': HardwareController(serial_controller)}

@hardware.command('test')
def test():
    ctx = click.get_current_context().obj
    controller : HardwareController
    controller = ctx['hardware']['controller']
    print(controller.allowed_codes)
