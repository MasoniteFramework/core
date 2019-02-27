"""Module for using the Socket.IO websocket driver."""
from masonite.app import App
from masonite.contracts.BroadcastContract import BroadcastContract
from masonite.drivers.BaseDriver import BaseDriver
from masonite.exceptions import BroadcastException, DriverLibraryNotFound


class BroadcastSocketioDriver(BroadcastContract, BaseDriver):
    """Class for the Socket.IO Driver."""

    def __init__(self, app: App):
        """Socket.IO driver constructor.

        Arguments:
            BroadcastConfig {config.broadcast} -- Broadcast configuration setting.
        """
        self.config = app.make('BroadcastConfig')
        self.ssl_message = True

    def connect(self, options):
        """Create Socket.IO connection

        Arguements:
            options {dict} -- Settings for Socket.IO connection
        """

        try:
            import socketio
        except ImportError:
            raise DriverLibraryNotFound(
                'Could not find the "socketio" library. Please pip install this library running "pip install socketio"')

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
        """ Socket.IO does not care about ssl """
        pass

    def channel(self, event='message', data='', **kwargs):
        """Specify which channel(s) you want to send information to.

        Keyword Arguments:
            event {string} -- The event you want broadcasted along with your data. (default: {'event'})
            data {string} -- Data that you want to push
            headers {dict} -- Custom set HTTP headers for websockets
            transports {string} -- The list of allowed transports. Valid transports are 'polling' and 'websocket'. (default: {'websockets})
            namespaces {string} --The Socket.IO namespace for the event. If this argument is omitted the event is emitted to the default namespace.
            callback {function} -- If given, this function will be called to acknowledge the the client has received the message.
            socketio_path {string} -- The endpoint where the Socket.IO server is installed.
            handler {function} -- The function that should be invoked to handle the event.

        Raises:
            DriverLibraryNotFound -- Thrown when socketio is not installed.
            BroadcastException -- Thrown when socket.io fails

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

        # Register an event handler if one exists
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
