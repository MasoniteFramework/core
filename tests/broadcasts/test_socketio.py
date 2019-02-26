import os
import pytest
from masonite.exceptions import BroadcastException
from masonite.drivers.BroadcastSocketioDriver import BroadcastSocketioDriver
from masonite.managers.BroadcastManager import BroadcastManager
from masonite.testsuite.TestSuite import TestSuite

from config import broadcast

if os.getenv('SOCKETIO_HOST'):

    class TestSockets:

        def setup_method(self):
            self.app = TestSuite().create_container().container
            self.app.bind('BroadcastConfig', broadcast)
            self.app.bind('BroadcastSocketioDriver', BroadcastSocketioDriver)
            self.app.bind('BroadcastManager', BroadcastManager().load_container(self.app))

        def test_broadcast_loads_into_container_with_socketio(self):
            self.app.bind('Broadcast', self.app.make('BroadcastManager').driver('socketio'))

            assert self.app.make('BroadcastManager')
            assert self.app.make('Broadcast').channel('event', 'hola') == {'event': 'event', 'data': 'hola'}
            assert self.app.make('Broadcast').channel(data=('hola')) == {'event': 'event', 'data': 'bonjour'}
            assert self.app.make('Broadcast').channel(event='hi') == {'event': 'hi', 'data': ''}
            # assert self.app.make('Broadcast').ssl(True).ssl_message is True

        def test_socketio_broadcast_exception(self):
            self.app.bind('Broadcast', self.app.make('BroadcastManager').driver('socketio'))
            with pytest.raises(BroadcastException):
                # Throw in something that the driver is not expecting, like a class
                self.app.make('Broadcast').channel(event=BroadcastException, data='hello')
