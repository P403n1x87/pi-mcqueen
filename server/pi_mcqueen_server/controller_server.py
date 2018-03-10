import asyncio
import sys
import websockets

import pi_mcqueen_server.util.websocket  as websocket
import pi_mcqueen_server.util.components as comp

from pi_mcqueen_server.util.log import debug, bar, move_up


FREQ = 50  # Hz
ENB1 = 15
ENB2 = 12
IN1  = 29
IN2  = 7
IN3  = 36
IN4  = 18

VLIMIT = 6.0  # Volts


def normalize(value):
    """Normalize the given value from the byte range [0, 255] to [-100, 100]"""
    return (value - 256 if value & 128 else value) * 100 / 127


class ControllerServer(websocket.Server):
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

        comp.startup()

        hbridge = comp.HBridge(comp.PWMSignal(ENB1, FREQ)
                         ,comp.PWMSignal(ENB2, FREQ)
                         ,comp.DCMotor(IN1, IN2, threshold = 5)
                         ,comp.DCMotor(IN4, IN3, threshold = 20)
                         )

        hbridge.start()

        guard_factor = 1 if self._voltage <= VLIMIT else VLIMIT / self._voltage

        debug("RAW DATA")

        while self.is_running:
            try:
                x, y = yield from websocket.recv()

                debug(bar("X", x / 256.))
                debug(bar("Y", y / 256.))

                x, y = normalize(x), normalize(y)

                debug("PROCESSED DATA")
                debug(bar("X", abs(x) / 100.))
                debug(bar("Y", abs(y) / 100.))
                move_up(5)  # Up 5 lines

                hbridge.enable1.set_duty_cycle(abs(x) * guard_factor)
                hbridge.enable2.set_duty_cycle(abs(y) * guard_factor)

                hbridge.device1.set(x)
                hbridge.device2.set(y)

            except websockets.exceptions.ConnectionClosed:
                break

        hbridge.stop()
        comp.cleanup()
