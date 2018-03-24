import argparse

import pi_mcqueen_server.controller_server as cs

from pi_mcqueen_server.util.log import set_debug

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

    server = cs.ControllerServer("0.0.0.0", 5678, conn_limit = 1)
    server.set_voltage(args.n)
    server.start()
