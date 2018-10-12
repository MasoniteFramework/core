""" Upload Rackspace Driver """

from masonite.contracts import UploadContract
from masonite.drivers import BaseUploadDriver
from masonite.exceptions import DriverLibraryNotFound
from masonite.helpers import random_string
from masonite.managers import UploadManager

from config import storage


class UploadRackspaceDriver(BaseUploadDriver, UploadContract):

    def __init__(self, upload: UploadManager):
        """Upload Rackspace Driver Constructor

        Arguments:
            UploadManager {masonite.managers.UploadManager} -- The Upload Manager object.
        """

        self.upload = upload
        self.config = storage

    def store(self, fileitem, location=None):
        """Store the file into Rackspace server.

        Arguments:
            fileitem {cgi.Storage} -- Storage object.
        Keyword Arguments:
            location {string} -- The location on disk you would like to store the file. (default: {None})
        Raises:
            DriverLibraryNotFound -- Raises when the rackspace library is not installed.
        Returns:
            string -- Returns the file name just saved.
        """

        try:
            from rackspace import connection
        except ImportError:
            raise DriverLibraryNotFound(
                "Could not find the required 'rackspace' driver")

        conn = connection.Connection(username=self.config.DRIVERS['rackspace']['username'],
                                     api_key=self.config.DRIVERS['rackspace']['secret'],
                                     region=self.config.DRIVERS['rackspace']['region'])

        filename = random_string(25) + fileitem.filename

        self.validate_extension(filename)

        conn.object_store.upload_object(container=self.config.DRIVERS['rackspace']['container'],
                                        name=filename,
                                        data=fileitem.file.read())
        return filename

    def store_prepend(self, fileitem, prepend, location=None):
        """Store the file onto the Rackspace server but with a prepended file name.

        Arguments:
            fileitem {cgi.Storage} -- Storage object.
            prepend {string} -- The prefix you want to prepend to the file name.
        Keyword Arguments:
            location {string} -- The location on disk you would like to store the file. (default: {None})
        Returns:
            string -- Returns the file name just saved.
        """

        fileitem.filename = prepend + fileitem.filename

        return self.store(fileitem, location=location)
