#!/usr/bin/env python3

import argparse
import sys

from pi_mcqueen_server.controller_server import ControllerServer
from pi_mcqueen_server.util.log          import set_debug

def main():
    parser = argparse.ArgumentParser(description='Pi McQueen Controller Server.')

    parser.add_argument("-d", "--debug",
        action = "store_const",
        const  = True,
        help   = 'Turn debug output on.'
    )

    parser.add_argument('n',
        type = float,
        help = 'The voltage of the battery powering on the HBridge in Volts.'
    )

    args = parser.parse_args()

    set_debug(args.debug)

    gl = ControllerServer("0.0.0.0", 5678, conn_limit = 1)
    gl.set_voltage(args.n)
    gl.start()


if __name__ == "__main__":
    main()
