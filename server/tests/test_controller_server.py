import asyncio
import mock

import pi_mcqueen_server.controller_server as cs

class MockWebSocket:

    def __init__(self, server):
        self.data = None
        self.server = server

    def send(self, data):
        self.data = data

    @asyncio.coroutine
    def recv(self):
        self.server._WSServer__is_running = False
        return self.data


server = cs.ControllerServer("0.0.0.0", 5678, conn_limit = 1)
server.set_voltage(6)
mock_socket = MockWebSocket(server)
loop = asyncio.get_event_loop()


def setup_module():
    pass


def teardown_module():
    pass


def send_value(value):
    server._WSServer__is_running = True
    mock_socket.send(bytes([0, 0]))
    loop.run_until_complete(server.handler(mock_socket, "/", 0))


@mock.patch.object(cs.comp.PWMSignal, 'set_duty_cycle')
@mock.patch('pi_mcqueen_server.controller_server.comp.G')
def test_server(mock_G, mock_dc):
    send_value(bytes([0, 0]))

    assert mock_G.setmode.called
    assert mock_G.cleanup.called
    mock_dc.assert_called_with(0)
