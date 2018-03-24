import asyncio
import pytest
import unittest.mock as mock
import websockets

import pi_mcqueen_server.controller_server as cs


class MockWebSocket:

    def __init__(self, server):
        self.data = None
        self.server = server

    def send(self, data):
        self.data = data

    @asyncio.coroutine
    def recv(self):
        self.server._Server__is_running = False
        return self.data


server = cs.ControllerServer("0.0.0.0", 5678, conn_limit = 1)
mock_socket = MockWebSocket(server)
loop = asyncio.get_event_loop()


def send_value(value):
    server._Server__is_running = True
    mock_socket.send(value)
    loop.run_until_complete(server.handler(mock_socket, "/", 0))


@mock.patch('pi_mcqueen_server.controller_server.comp.G')
def test_server_no_voltage(mock_G):
    with pytest.raises(SystemExit):
        send_value(bytes([0, 0]))


class MockConnClosed(mock.Mock):
    def __call__(self, *args, **kwargs):
        super().__call__(*args, **kwargs)
        raise websockets.exceptions.ConnectionClosed(0, "TEST")


@mock.patch.object(cs, 'move_up', MockConnClosed())
@mock.patch('pi_mcqueen_server.controller_server.comp.G')
def test_conn_closed(mock_G):
    server.set_voltage(6)
    send_value(bytes([0, 0]))
    assert cs.move_up.called
    assert mock_G.setmode.called
    assert mock_G.cleanup.called


@mock.patch.object(cs.comp.PWMSignal, 'set_duty_cycle')
@mock.patch('pi_mcqueen_server.controller_server.comp.G')
def test_server(mock_G, mock_dc):
    server.set_voltage(6)

    send_value(bytes([0, 0]))
    assert mock_G.setmode.called
    assert mock_G.cleanup.called
    mock_dc.assert_called_with(0)

    mock_dc.reset_mock()
    send_value(bytes([0, 127]))
    mock_dc.assert_has_calls([
        mock.call(0),
        mock.call(100),
    ])

    mock_dc.reset_mock()
    send_value(bytes([0, 129]))
    mock_dc.assert_has_calls([
        mock.call(0),
        mock.call(100),
    ])

    mock_dc.reset_mock()
    send_value(bytes([127, 0]))
    mock_dc.assert_has_calls([
        mock.call(100),
        mock.call(0),
    ])

    mock_dc.reset_mock()
    send_value(bytes([129, 0]))
    mock_dc.assert_has_calls([
        mock.call(100),
        mock.call(0),
    ])
