import asyncio
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

                y, z = y if y <= 127 else y - 256, z if z <= 127 else z - 256

                self.logger.info("{} {}".format((y if y >= 0 else -y) * 100 / 127 * guard_factor, (z if z >= 0 else -z) * 100 / 127 * guard_factor))

                hbridge.enable1.set_duty_cycle((y if y >= 0 else -y) * 100 / 127 * guard_factor)
                hbridge.enable2.set_duty_cycle((z if z >= 0 else -z) * 100 / 127 * guard_factor)

                hbridge.device1.set(y)
                hbridge.device2.set(z)

            except websockets.exceptions.ConnectionClosed:
                break

        hbridge.stop()
        cleanup()
