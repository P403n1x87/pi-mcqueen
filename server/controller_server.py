import asyncio
import sys
import websockets

from lib.wss import WSServer
from lib.components import HBridge, DCMotor, PMWSignal, cleanup, startup

import RPi.GPIO as G

FREQ = 50  # Hz
ENB1 = 15
ENB2 = 12
IN1  = 29
IN2  = 7
IN3  = 18
IN4  = 36

VLIMIT = 6.0  # Volts


def bar(label, value, m = 32):
    size = int(value * m)
    bar_string = "█" * size + "░" * (m - size)
    return "{label} {bar} {value:>3}".format(label = label, bar = bar_string, value = int(value * 100))


def steering_mapping(value):
    return (value - 256 if value >= 128 else value) / 64.0 * 100


def pedal_mapping(value):
    if 128 <= value < 256:
        return ((192 - value) * 25) >> 4
    return 0


class ControllerServer(WSServer):
    """
    Controller WebSocket Server for accepting a single incoming connection from
    a controlling device.
    """

    def set_voltage(self, v):
        """
        Sets the voltate the H-Bridge is being operated at. This method must be
        called at least once before running the server to make sure that no
        voltage higher than the maximum allowed is sent to the DC motors.

        Args:
            v (int): The voltage the H-Bridge is being operated at.
        """
        self._voltage = v


    @asyncio.coroutine
    def handler(self, websocket, path, conn_id):
        try:
            self._voltage
        except AttributeError:
            self.logger.critical("No voltage set. Server not started to avoid damage.")
            exit(2)

        startup()

        hbridge = HBridge(PMWSignal(ENB1, FREQ)
                         ,PMWSignal(ENB2, FREQ)
                         ,DCMotor(IN1, IN2)
                         ,DCMotor(IN4, IN3)
                         )

        hbridge.start()

        guard_factor = 1 if self._voltage <= VLIMIT else VLIMIT / self._voltage

        while self.is_running:
            try:
                x, y, z = yield from websocket.recv()

                # Y axis - Steering Wheel       range: [-1/4, +1/4] * 256
                # Z axis - Accelerate / Break   range: [1/4, 0] U [1/4, 1/2] * 256
                # y, z = y if y <= 127 else y - 256, z if z <= 127 else z - 256

                # self.logger.info("A {} {}".format(y, z))

                print(bar("Y", y / 256.))
                print(bar("Z", z / 256.))

                y = steering_mapping(y)
                z = pedal_mapping(z)

                # self.logger.info("B {} {}".format(y, z))
                print()
                print(bar("Y", abs(y) / 100.))
                print(bar("Z", abs(z) / 100.))
                sys.stdout.write("\033[5A")

                hbridge.enable1.set_duty_cycle(abs(y) * guard_factor)
                hbridge.enable2.set_duty_cycle(abs(z) * guard_factor)

                hbridge.device1.set(y)
                hbridge.device2.set(z)

            except websockets.exceptions.ConnectionClosed:
                break

        hbridge.stop()
        cleanup()
