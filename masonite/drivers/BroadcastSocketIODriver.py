"""Module for using the Ably websocket driver."""
import socketio
from masonite.exceptions import BroadcastException
from masonite.contracts.BroadcastContract import BroadcastContract
from masonite.drivers.BaseDriver import BaseDriver
from masonite.exceptions import DriverLibraryNotFound
from masonite.app import App


class BroadcastSocketioDriver(BroadcastContract, BaseDriver):
    """Class for the Ably Driver."""

    def __init__(self, app: App):
        """Ably driver constructor.

        Arguments:
            BroadcastConfig {config.broadcast} -- Broadcast configuration setting.
        """
        self.config = app.make('BroadcastConfig')
        self.ssl_message = True

    def connect(self, options):

        try:
            import socketio
        except ImportError:
            raise DriverLibraryNotFound(
                'Could not find the "ably" library. Please pip install this library running "pip install socketio"')

        # Setup Configuration
        host = self.config.DRIVERS['socketio']['host']
        port = self.config.DRIVERS['socketio']['port']

        if not host.endswith(':'):
            host = host + ':'
        url = host + str(port)

        # Create and connect to client
        sio = socketio.Client()
        sio.connect(
            url=url,
            headers=options['headers'],
            transports=options['transports'],
            namespaces=options['namespaces'],
            socketio_path=options['socketio_path'])
        return sio

    def ssl(self, boolean):
        pass

    def channel(self, event='message', data='', **kwargs):
        """Specify which channel(s) you want to send information to.

        Arguments:
            channels {string|list} -- Can be a string for the channel or a list of strings for the channels.
            message {string} -- The message you want to send to the channel(s)

        Keyword Arguments:
            event {string} -- The event you want broadcasted along with your data. (default: {'base-event'})

        Raises:
            DriverLibraryNotFound -- Thrown when ably is not installed.

        Returns:
            string -- Returns the message sent.
        """

        # Extra options for creating connection
        options = dict()
        options['headers'] = kwargs.get('headers', dict())
        options['transports'] = kwargs.get('transports', None)
        options['namespaces'] = kwargs.get('namespaces', None)
        options['socketio_path'] = kwargs.get('socketio_path', 'socket.io')
        options['callback'] = kwargs.get('callback', None)
        handler = kwargs.get('handler', None)

        # Either emit or send data
        sio = self.connect(options)

        # Register an event handler.
        if handler is not None:
            sio.on(event, handler)

        # Send message
        try:
            sio.emit(event, data, options['namespaces'], options['callback'])
            sio.disconnect()
            return {'event': event, 'data': data}
        except Exception:
            sio.disconnect()
            raise BroadcastException
