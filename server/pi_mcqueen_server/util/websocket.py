#!/usr/bin/env python3

import asyncio
import datetime
import random
import websockets

from .log import logger_factory


class Server:
    """
    Abstract WebSocket Server class with a support for limiting the number of
    simultaneous connections that can be accepted.

    Any subclass is required to implement the `handler` method, which defines
    how connections should be handled. The basic WebSocket Server
    functionalities are encapsulated in this class for ease of use.

    Once initialized, the server can be started with a call to `start`, and its
    status can be monitored with the attribute `is_running`.

    The general coding pattern in the implemented `handler` method looks like
    the following code snippet

    Example:

        @asyncio.coroutine
        def handler(self, websocket, path, connection_id):

            #
            # Initialization of local variables
            #

            while self.is_running:
                try:
                    data = yield from websocket.recv()

                    #
                    # do stuff with data
                    #

                except websockets.exceptions.ConnectionClosed:
                    break

            #
            # Cleanup
            #
    """
    __srv_limit = None
    __srv_cnt   = 0

    def __init__(self, address, port, conn_limit = None):
        """
        The constructor takes an IPv4 address and a port to listen to, and an
        optional connection limit.

        Args:
            address (str): The IPv4 address to bind the socket to.
            port (int): The port to listen to.
            conn_limit (int): The limit on the number of connections (defaults
                to `None`).
        """
        if Server.__srv_limit != None and Server.__srv_cnt >= Server.__srv_limit:
            raise RuntimeError("Maximum number of {} instances created.".format(self.__class__.__name__))

        self.__is_running = False
        self.__conn_cnt   = 0

        self.address    = address
        self.port       = port
        self.conn_limit = conn_limit

        Server.__srv_cnt += 1

        self.logger = logger_factory("{cls}@{address}:{port}".format(cls = self.__class__.__name__, address = address, port = port))

    def __del__(self):
        Server.__srv_cnt -= 1

    @staticmethod
    def set_limit(limit = None):
        # Precondition
        if limit is not None and not isinstance(limit, int):
            raise ValueError("Server limit must be an integer or None.")

        Server.__srv_limit = limit

    def __reserve_conn_id(self):
        ret = self.__conn_cnt
        self.__conn_cnt += 1
        return ret

    @asyncio.coroutine
    def __handler_wrapper(self, ws, p):
        # Precondition
        if self.conn_limit is not None and self.__conn_cnt >= self.conn_limit:
            self.logger.warning("Maximum number of connections reached. New request ignored.")
            yield from ws.send("MAXC")
            ws.close()
            return

        yield from self.handler(ws, p, self.__reserve_conn_id())

        self.__conn_cnt -= 1

    @asyncio.coroutine
    def handler(self, websocket, path, conn_id):
        """
        Any subclass must implement this method with the required logic.
        """
        raise NotImplementedError("Subclasses of Server must implement the handler coroutine.")

    @property
    def is_running(self):
        """
        Property to determine whether the server is still up and running.
        """
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
