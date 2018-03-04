#!/usr/bin/env python3

import sys

from controller_server import ControllerServer

if __name__ == "__main__":
    """
    Bootstrap the controller server.

    Usage: main.py <n>V

    Example:
        main.py 9V

    The voltage argument is required to prevent damaging the DC motor.
    """

    n = None
    try:
        if len(sys.argv) != 2:
            raise RuntimeError

        n = int(sys.argv[1][:-1])

    except (RuntimeError, ValueError):
        print("Usage: main.py <n>V")
        print("")
        print("  n - The voltage of the battery used to power up the")
        print("      H-Bridge, in Volts.")
        exit(1)

    gl = ControllerServer("0.0.0.0", 5678, conn_limit = 1)
    gl.set_voltage(n)
    gl.start()
