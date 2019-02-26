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

            # Extra options for creating connection
            self.options = dict()
            self.options['headers'] = dict()
            self.options['transports'] = None
            self.options['namespaces'] = None
            self.options['socketio_path'] = 'socket.io'
            self.options['callback'] = None

        def test_broadcast_loads_into_container_with_socketio(self):
            self.app.bind('Broadcast', self.app.make('BroadcastManager').driver('socketio'))

            assert self.app.make('BroadcastManager')
            assert self.app.make('Broadcast').channel('hi', 'hola') == {'event': 'hi', 'data': 'hola'}
            assert self.app.make('Broadcast').channel(data=('bonjour')) == {'event': 'message', 'data': 'bonjour'}
            assert self.app.make('Broadcast').channel(event='hi') == {'event': 'hi', 'data': ''}
            # assert self.app.make('Broadcast').ssl(True).ssl_message is True

        def test_socketio_broadcast_exception(self):
            self.app.bind('Broadcast', self.app.make('BroadcastManager').driver('socketio'))
            with pytest.raises(BroadcastException):
                # Throw in something that the driver is not expecting, like a class
                self.app.make('Broadcast').channel(event=BroadcastException, data='hello')

        def test_socketio_handles_message_handle(self):
            self.app.bind('Broadcast', self.app.make('BroadcastManager').driver('socketio'))

            # Test Message Handler
            def message_handler():
                print('I like computers!')
                return None

            assert self.app.make('Broadcast').channel(handler=message_handler())

        def test_socketio_headers(self):
            self.app.bind('Broadcast', self.app.make('BroadcastManager').driver('socketio'))
            self.options['headers'] = {'Access-Control-Allow-Origin': '*'}
            assert self.app.make('Broadcast').channel(event='event', data='hola', **self.options) == {'event': 'event', 'data': 'hola'}
