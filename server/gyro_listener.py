import asyncio
import websockets

from lib.wss import WSServer

import RPi.GPIO as G

CHR  = 12
CHL  = 15
FREQ = 50 # Hz

class GyroListener(WSServer):

    @asyncio.coroutine
    def handler(self, websocket, path, conn_id):
        self.logger.info("Connection ID {} established [path {}]".format(conn_id, path))

        G.setmode(G.BOARD)
        G.setup(CHR, G.OUT)
        G.setup(CHL, G.OUT)

        pr = G.PWM(CHR, FREQ)
        pl = G.PWM(CHL, FREQ)
        pr.start(0)
        pl.start(0)

        while self.is_running:
            try:
                gyro_data = yield from websocket.recv()
                g         = gyro_data.split()
                val       = int(float(g[1]))

                self.logger.debug("Received datum {}".format(val))
                if val > 0:
                    pr.ChangeDutyCycle(val)
                    pl.ChangeDutyCycle(0)
                else:
                    pr.ChangeDutyCycle(0)
                    pl.ChangeDutyCycle(-val)
                # yield from websocket.send("ACK " + gyro_data)

            except websockets.exceptions.ConnectionClosed:
                self.logger.info("Connection ID {} closed.".format(conn_id))
                pr.stop()
                return

        G.cleanup()
