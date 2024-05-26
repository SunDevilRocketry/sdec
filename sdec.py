"""
SDEC
====
Main terminal program. Contains main program loop and global objects.

---

Sun Devil Rocketry Avionics
Author: Colton Acosta
Date: 4/16/2022

Updated: 3/3/2024
Author: Christian Thompson
Purpose: Improve API and CLI interfaces.
"""

from typing import Callable, Dict, List

import click
from omegaconf import OmegaConf
import prompt_toolkit.shortcuts
import serial
import serial.tools.list_ports
from click_repl import ExitReplException, repl
from plugins import comport, engine, flight, hardware, valve
from prompt_toolkit.history import FileHistory

CONTEXT_SETTINGS = dict(
    help_option_names=['-h', '--help'],
    obj = {}
)

PLUGIN_COMMANDS = {
    "comports": comport.comports,
    "sol": valve.solenoid,
    "valve": valve.valve,
    "hardware": hardware.hardware,
    # "power": engineController.power,
    # "ignite": hw_commands.ignite,
    # "flash": hw_commands.flash,
    # "sensor": hw_commands.sensor,
    # "abort": engineController.hotfire_abort,
    # "telreq": engineController.telreq,
    # "pfpurge": engineController.pfpurge,
    # "fillchill": engineController.fillchill,
    # "standby": engineController.standby,
    # "hotfire": engineController.hotfire,
    # "getstate": engineController.hotfire_getstate,
    # "stophotfire": engineController.stop_hotfire,
    # "stoppurge": engineController.stop_purge,
    # "loxpurge": engineController.lox_purge,
    # "dual-deploy": flightComputer.dual_deploy,
}

GLOBALS = "globals.yaml"

@click.group(context_settings=CONTEXT_SETTINGS)
@click.option('--debug/--no-debug', '-d/', default=False,
              help="Enter debug mode")
def main(debug=False):
    ctx = click.get_current_context()
    ctx.obj['debug'] = debug

    # load globals from yaml file
    globs = OmegaConf.load(GLOBALS)
    ctx.obj['globals'] = globs

    # set timeout in seconds
    timeout = globs.timeout.debug if debug else globs.timeout.default
    ctx.obj['timeout'] = timeout

@main.command(name="term")
def terminal():
    """Open the command terminal"""
    prompt_kwargs = {
        'history': FileHistory('./.myrepl-history'),
        'message': 'SDR> ',
    }
    ctx = click.get_current_context()
    repl(ctx, prompt_kwargs=prompt_kwargs)

# register plugin commands
for name, command in PLUGIN_COMMANDS.items():
    main.add_command(command, name=name)

@main.command(name="quit")
def q():
    """Quit the terminal and exit the app"""
    raise ExitReplException()

@main.command(name="clear")
def clear():
    """Clear the console"""
    prompt_toolkit.shortcuts.clear()

if __name__ == '__main__':
    main()
