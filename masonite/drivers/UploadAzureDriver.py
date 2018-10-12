""" Azure Upload Driver """

from masonite.contracts import UploadContract
from masonite.drivers import BaseUploadDriver
from masonite.exceptions import DriverLibraryNotFound
from masonite.helpers import random_string
from masonite.managers import UploadManager

from config import storage


class UploadAzureDriver(BaseUploadDriver, UploadContract):

    def __init__(self, upload: UploadManager):
        """Upload Azure Driver Constructor

        Arguments:
            UploadManager {masonite.managers.UploadManager} -- The Upload Manager object.
        """

        self.upload = upload
        self.config = storage

    def store(self, fileitem, location=None):
        """Store the file into Microsoft Azure server.

        Arguments:
            fileitem {cgi.Storage} -- Storage object.
        Keyword Arguments:
            location {string} -- The location on disk you would like to store the file. (default: {None})
        Raises:
            DriverLibraryNotFound -- Raises when the azure library is not installed.
        Returns:
            string -- Returns the file name just saved.
        """

        try:
            from azure.storage.blob import BlockBlobService
        except ImportError:
            raise DriverLibraryNotFound("Could not find the 'azure' driver")

        block_blob_service = BlockBlobService(
            account_name=self.config.DRIVERS['azure']['name'], account_key=self.config.DRIVERS['azure']['secret'])

        # Store temporarily on disk
        driver = self.upload.driver('disk')
        driver.store(fileitem, location)
        file_location = driver.file_location

        filename = random_string(25) + fileitem.filename

        block_blob_service.create_blob_from_path(
            self.config.DRIVERS['azure']['container'], filename, file_location)

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
