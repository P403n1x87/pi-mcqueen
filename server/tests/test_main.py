import pytest
import sys
import unittest.mock as mock

import pi_mcqueen_server.__init__ as init


def test_main_with_invalid_no_of_args():
    with mock.patch.object(sys, "argv", ["bla"]):
        with pytest.raises(SystemExit):
            init.main()


def test_main_with_invalid_type_of_args():
    with mock.patch.object(sys, "argv", ["bla", "bla"]):
        with pytest.raises(SystemExit):
            init.main()


@mock.patch('pi_mcqueen_server.__init__.cs.websocket.asyncio.get_event_loop')
def test_main(mock_asyncio):
    with mock.patch.object(sys, "argv", ["bla", "6"]):
        mock_loop = mock.Mock()
        mock_loop.run_forever = mock.Mock()

        def keyboard_interrupt():
            raise KeyboardInterrupt

        mock_loop.run_forever.side_effect = keyboard_interrupt
        mock_asyncio.return_value = mock_loop
        init.main()
        assert mock_asyncio.called
        assert mock_loop.run_until_complete.called
        assert mock_loop.run_forever
