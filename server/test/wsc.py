#!/usr/bin/env python3

import asyncio
import websockets
import random

from math import sin, cos, pi

running = True

OMEGA = 20.0

def log(msg):
    print("[client] {}".format(msg))

@asyncio.coroutine
def hello():
    websocket = yield from websockets.connect('ws://localhost:5678')
    t = 0
    try:
        while running:
            y = sin(2 * pi * t / 100 * OMEGA) * 127
            z = cos(2 * pi * t / 100 * OMEGA) * 127
            t   = (t + 1) % 100

            val = bytes([0, int(y if y >= 0 else y + 256), int(z if z >= 0 else z + 256)])

            yield from websocket.send(val)
            log("Sending {}".format(list(val)))

            # greeting = yield from websocket.recv()
            # log("< {}".format(greeting))

            yield from asyncio.sleep(10)

    except websockets.exceptions.ConnectionClosed:
        log("Connection Closed. Client shutting down.")

    except OSError:
        log("Unable to establish a connection. Is the server reachable and/or running?")

    finally:
        yield from websocket.close()
try:
    asyncio.get_event_loop().run_until_complete(hello())
except KeyboardInterrupt:
    print("")
    log("Received termination signal. Preparing to shutdown client.")

    running = False

    # Run loop until tasks done:
    log("Finishing with scheduled tasks.")
    # The client will return since running is now set to False.
    asyncio.get_event_loop().run_forever()
    log("Shutdown completed. Bye!")
