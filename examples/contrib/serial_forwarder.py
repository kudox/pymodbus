"""Pymodbus SerialRTU2TCP Forwarder

usage :
python3 serial_forwarder.py --log DEBUG --port "/dev/ttyUSB0" --baudrate 9600 --server_ip "192.168.1.27" --server_port 5020 --slaves 1 2 3
"""
import argparse
import asyncio
import logging
import signal

from pymodbus.client import ModbusSerialClient
from pymodbus.datastore import ModbusServerContext
from pymodbus.datastore.remote import RemoteSlaveContext
from pymodbus.server import ModbusTcpServer


_logger = logging.getLogger(__file__)


def raise_graceful_exit(*_args):
    """Enters shutdown mode"""
    _logger.info("receiving shutdown signal now")
    raise SystemExit


class SerialForwarderTCPServer:
    """SerialRTU2TCP Forwarder Server"""

    def __init__(self):
        """Initialize the server"""
        self.server = None

    async def run(self):
        """Run the server"""
        port, baudrate, server_port, server_ip, slaves = get_commandline()
        client = ModbusSerialClient(method="rtu", port=port, baudrate=baudrate)
        message = f"RTU bus on {port} - baudrate {baudrate}"
        _logger.info(message)
        store = {}
        for i in slaves:
            store[i] = RemoteSlaveContext(client, slave=i)
        context = ModbusServerContext(slaves=store, single=False)
        self.server = ModbusTcpServer(
            context,
            address=(server_ip, server_port),
        )
        message = f"serving on {server_ip} port {server_port}"
        _logger.info(message)
        message = f"listening to slaves {context.slaves()}"
        _logger.info(message)
        await self.server.serve_forever()

    async def stop(self):
        """Stop the server"""
        if self.server:
            await self.server.shutdown()
            _logger.info("TCP server is down")


def get_commandline():
    """Read and check command line arguments"""
    parser = argparse.ArgumentParser(description="Command line options")
    parser.add_argument(
        "--log",
        choices=["critical", "error", "warning", "info", "debug"],
        help="set log level, default is info",
        default="info",
        type=str,
    )
    parser.add_argument(
        "--port", help="RTU serial port", default="/dev/ttyUSB0", type=str
    )
    parser.add_argument("--baudrate", help="RTU baudrate", default=9600, type=int)
    parser.add_argument("--server_port", help="server port", default=5020, type=int)
    parser.add_argument("--server_ip", help="server IP", default="127.0.0.1", type=str)
    parser.add_argument(
        "--slaves", help="list of slaves to forward", type=int, nargs="+"
    )

    args = parser.parse_args()

    # set defaults
    _logger.setLevel(args.log.upper())
    if not args.slaves:
        args.slaves = {1, 2, 3}
    return args.port, args.baudrate, args.server_port, args.server_ip, args.slaves


if __name__ == "__main__":
    server = SerialForwarderTCPServer()
    try:
        signal.signal(signal.SIGINT, raise_graceful_exit)
        asyncio.run(server.run())
    finally:
        asyncio.run(server.stop())
