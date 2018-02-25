import asyncio
import websockets

from lib.wss import WSServer
from lib.components import HBridge, DCMotor, PMWSignal, cleanup

import RPi.GPIO as G

FREQ = 50 # Hz
ENB1 = 15
ENB2 = 12
IN1 = 7
IN2 = 29
IN3 = 36
IN4 = 18

class GyroListener(WSServer):

    @asyncio.coroutine
    def handler(self, websocket, path, conn_id):

        hbridge = HBridge(PMWSignal(ENB1, FREQ)
                         ,PMWSignal(ENB2, FREQ)
                         ,DCMotor(IN1, IN2)
                         ,DCMotor(IN4, IN3)
                         )

        hbridge.start()

        while self.is_running:

            try:

                x, y, z = yield from websocket.recv()

                y, z = (y if y <= 127 else y - 256) * 100 / 128, (z if z <= 127 else z - 256) * 100 / 128

                self.logger.info("{} {}".format(y, z))

                hbridge.enable1.set_duty_cycle((y if y >= 0 else - y) * 100 / 128)
                hbridge.enable2.set_duty_cycle((z if z >= 0 else - z) * 100 / 128)

                hbridge.device1.set(y)
                hbridge.device2.set(z)

            except websockets.exceptions.ConnectionClosed:
                break

        hbridge.stop()
        cleanup()
