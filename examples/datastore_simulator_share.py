#!/usr/bin/env python3
"""Pymodbus datastore simulator Example.

An example of using simulator datastore with json interface.

Detailed description of the device definition can be found at:

    https://pymodbus.readthedocs.io/en/latest/source/library/simulator/config.html#device-entries

usage::

    datastore_simulator_share.py [-h]
                        [--log {critical,error,warning,info,debug}]
                        [--port PORT]
                        [--test_client]

    -h, --help
        show this help message and exit
    -l, --log {critical,error,warning,info,debug}
        set log level
    -p, --port PORT
        set port to use
    --test_client
        starts a client to test the configuration

The corresponding client can be started as:
    python3 client_sync.py

.. tip:: This is NOT the pymodbus simulator, that is started as pymodbus.simulator.
"""
import argparse
import asyncio
import logging

from pymodbus import pymodbus_apply_logging_config
from pymodbus.datastore import ModbusServerContext, ModbusSimulatorContext
from pymodbus.device import ModbusDeviceIdentification
from pymodbus.server import StartAsyncTcpServer


_logger = logging.getLogger(__file__)

demo_config = {
    "setup": {
        "co size": 100,
        "di size": 150,
        "hr size": 200,
        "ir size": 250,
        "shared blocks": True,
        "type exception": False,
        "defaults": {
            "value": {
                "bits": 0x0708,
                "uint16": 1,
                "uint32": 45000,
                "float32": 127.4,
                "string": "X",
            },
            "action": {
                "bits": None,
                "uint16": None,
                "uint32": None,
                "float32": None,
                "string": None,
            },
        },
    },
    "invalid": [
        1,
        [6, 6],
    ],
    "write": [
        3,
        [7, 8],
        [16, 18],
        [21, 26],
        [31, 36],
    ],
    "bits": [
        [7, 9],
        {"addr": 2, "value": 0x81},
        {"addr": 3, "value": 17},
        {"addr": 4, "value": 17},
        {"addr": 5, "value": 17},
        {"addr": 10, "value": 0x81},
        {"addr": [11, 12], "value": 0x04342},
        {"addr": 13, "action": "reset"},
        {"addr": 14, "value": 15, "action": "reset"},
    ],
    "uint16": [
        {"addr": 16, "value": 3124},
        {"addr": [17, 18], "value": 5678},
        {"addr": [19, 20], "value": 14661, "action": "increment"},
    ],
    "uint32": [
        {"addr": [21, 22], "value": 3124},
        {"addr": [23, 26], "value": 5678},
        {"addr": [27, 30], "value": 345000, "action": "increment"},
    ],
    "float32": [
        {"addr": [31, 32], "value": 3124.17},
        {"addr": [33, 36], "value": 5678.19},
        {"addr": [37, 40], "value": 345000.18, "action": "increment"},
    ],
    "string": [
        {"addr": [41, 42], "value": "Str"},
        {"addr": [43, 44], "value": "Strx"},
    ],
    "repeat": [{"addr": [0, 45], "to": [46, 138]}],
}


def custom_action1(_inx, _cell):
    """Test action."""


def custom_action2(_inx, _cell):
    """Test action."""


demo_actions = {
    "custom1": custom_action1,
    "custom2": custom_action2,
}


def get_commandline(cmdline=None):
    """Read and check command line arguments."""
    parser = argparse.ArgumentParser(description="Run datastore simulator example.")
    parser.add_argument(
        "--log",
        choices=["critical", "error", "warning", "info", "debug"],
        help="set log level, default is info",
        default="info",
        type=str,
    )
    parser.add_argument("--port", help="set port", type=str, default="5020")
    parser.add_argument("--host", help="set interface", type=str, default="localhost")
    parser.add_argument("--test_client", help="start client to test", action="store_true")
    args = parser.parse_args(cmdline)
    return args


def setup_simulator(setup=None, actions=None, cmdline=None):
    """Run server setup."""
    if not setup:
        setup=demo_config
    if not actions:
        actions=demo_actions
    args = get_commandline(cmdline=cmdline)
    pymodbus_apply_logging_config(args.log.upper())
    _logger.setLevel(args.log.upper())
    args.port = int(args.port)

    context = ModbusSimulatorContext(setup, actions)
    args.context = ModbusServerContext(slaves=context, single=True)
    args.identity = ModbusDeviceIdentification(
        info_name={
            "VendorName": "Pymodbus",
            "ProductCode": "PM",
            "VendorUrl": "https://github.com/pymodbus-dev/pymodbus/",
            "ProductName": "Pymodbus Server",
            "ModelName": "Pymodbus Server",
            "MajorMinorRevision": "test",
        }
    )
    return args


async def run_server_simulator(args):
    """Run server."""
    _logger.info("### start server simulator")

    await StartAsyncTcpServer(
        context=args.context,
        address=(args.host, args.port),
    )


async def main(cmdline=None):
    """Combine setup and run."""
    run_args = setup_simulator(cmdline=cmdline)
    await run_server_simulator(run_args)


if __name__ == "__main__":
    asyncio.run(main(), debug=True)
