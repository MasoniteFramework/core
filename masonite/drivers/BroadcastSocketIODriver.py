"""Module for using the Ably websocket driver."""
import socketio
from masonite.exceptions import BroadcastException
from masonite.contracts.BroadcastContract import BroadcastContract
from masonite.drivers.BaseDriver import BaseDriver
from masonite.exceptions import DriverLibraryNotFound
from masonite.app import App


class SocketIO:
    """ Context manager for SocketIO """

    try:
        import socketio
    except ImportError:
        raise DriverLibraryNotFound(
            'Could not find the "ably" library. Please pip install this library running "pip install socketio"')

    def __init__(self, config):
        self.config = config

    def __enter__(self, **options):
        """ Establish connection """

        # Setup Configuration
        host = self.config['host']
        port = self.config['port']
        url = host + str(port)

        # Create and connect to client
        client = socketio.Client
        self.sio = client.connect(url=url, **options)

        return self.io

    def __exit__(self):
        self.sio.disconnect()


class BroadcastSocketIODriver(BroadcastContract, BaseDriver):
    """Class for the Ably Driver."""

    def __init__(self, app: App):
        """Ably driver constructor.

        Arguments:
            BroadcastConfig {config.broadcast} -- Broadcast configuration setting.
        """
        self.config = app.make('BroadcastConfig')
        self.ssl_message = True

    def ssl(self, boolean):
        pass

    def channel(self, event=None, data='', **kwargs):
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
        options['namespaces'] =  kwargs.get('namespaces', None)
        options['socketio_path']= kwargs.get('socketio_path', 'socket.io')
        options['callback'] = kwargs.get('callback', None)

        # Either emit or send data
        with SocketIO(self.config, options) as sio:
            if options['handler'] is not None:
                sio.on(event, options['handler'])
            
            if event is not None:
                sio.emit(event, data, options['namespaces'], options['callback'])
            elif event is None:
                sio.send(data, options['namespaces'], options['callback'])
            else:
                raise BroadcastException

        return {'event': event, 'data': data}
