import asyncio
import pytest
import unittest.mock as mock

from pi_mcqueen_server.util.websocket import Server


loop = asyncio.get_event_loop()

@asyncio.coroutine
def mock_handler(self, ws, p, conn_id):
    assert conn_id not in self.conn_pool
    if self.depth > 0:
        self.depth -= 1
        yield from asyncio.wait([self._Server__handler_wrapper(ws, p)])


class MockSend(mock.Mock):
    @asyncio.coroutine
    def __call__(self, v):
        assert v == "MAXC"
        return super().__call__(self, v)


mock_ws = mock.Mock()
mock_ws.send = MockSend()


def simulate_connections(ws, limit, depth):
    s = Server("address", 1234, limit)
    s.depth = depth
    s.conn_pool = {}
    ws.reset()
    loop.run_until_complete(s._Server__handler_wrapper(ws, "/"))
    if limit < depth:
        assert s.depth == depth - limit
        assert ws.send.called
    else:
        assert s.depth == 0


@mock.patch.object(Server, "handler", mock_handler)
def test_conn_limit():
    simulate_connections(mock_ws, 1, 1)
    simulate_connections(mock_ws, 5, 5)
    simulate_connections(mock_ws, 10, 5)
    simulate_connections(mock_ws, 5, 10)


def test_no_handler():
    with pytest.raises(NotImplementedError):
        simulate_connections(mock_ws, 1, 1)
