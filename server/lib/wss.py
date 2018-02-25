#!/usr/bin/env python3

import asyncio
import datetime
import random
import websockets

from .utils import logger_factory


class WSServer:
    __srv_limit = None
    __srv_cnt   = 0

    @staticmethod
    def set_server_limit(limit = None):
        # Precondition
        if limit != None or not isinstance(limit, int):
            raise ValueError("Server limit must be an integer or None.")

        self.__srv_limit(limit)

    def __reserve_conn_id(self):
        ret = self.__conn_cnt
        self.__conn_cnt += 1
        return ret

    def __init__(self, address, port, conn_limit = None):
        if WSServer.__srv_limit != None and WSServer.__srv_cnt >= WSServer.__srv_limit:
            raise RuntimeError("Maximum number of {} instances created.".format(self.__class__.__name__))

        self.__is_running = False
        self.__conn_cnt   = 0

        self.address    = address
        self.port       = port
        self.conn_limit = conn_limit

        WSServer.__srv_cnt += 1

        self.logger = logger_factory("{cls}@{address}:{port}".format(cls = self.__class__.__name__, address = address, port = port))

    @asyncio.coroutine
    def __handler_wrapper(self, ws, p):
        # Precondition
        if self.__conn_cnt >= self.conn_limit:
            self.logger.warning("Maximum number of connections reached. New request ignored.")
            yield from ws.send("MAXC")
            ws.close()
            return

        yield from self.handler(ws, p, self.__reserve_conn_id())

        self.__conn_cnt -= 1

    @asyncio.coroutine
    def handler(self, websocket, path, conn_id):
        raise NotImplementedError("Subclasses of WSServer must implement the handler coroutine.")

    @property
    def is_running(self):
        return self.__is_running

    def start(self):
        loop = asyncio.get_event_loop()

        loop.run_until_complete(websockets.serve(self.__handler_wrapper, self.address, self.port))

        try:
            self.logger.info("WebSocket server started @ http://{address}:{port}.".format(address = self.address, port = self.port))
            self.logger.info("Press Ctrl+C to stop it.")
            self.__is_running = True
            loop.run_forever()

        except KeyboardInterrupt:
            self.__is_running = False
            print("")
            self.logger.info("Received termination signal. Preparing to shutdown ...")
            self.logger.info("Waiting for scheduled tasks to terminate normally ...")
            loop.run_until_complete(asyncio.gather(*asyncio.Task.all_tasks()))
            self.logger.info("Shutting down the WebSocket server. Bye!")
