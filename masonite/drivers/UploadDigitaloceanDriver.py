""" Upload DigitalOcean Driver """

from masonite.contracts.UploadContract import UploadContract
from masonite.drivers.BaseUploadDriver import BaseUploadDriver
from masonite.exceptions import DriverLibraryNotFound


class UploadDigitaloceanDriver(BaseUploadDriver, UploadContract):
    """
    Digital Ocean Upload driver
    """

    def __init__(self, UploadManager, StorageConfig):
        """Upload Disk Driver Constructor

        Arguments:
            UploadManager {masonite.managers.UploadManager} -- The Upload Manager object.
            StorageConfig {config.storage} -- Storage configuration.
        """

        self.upload = UploadManager
        self.config = StorageConfig

    def store(self, fileitem, location=None):
        """Store the file into a Digital Ocean Space.

        Arguments:
            fileitem {cgi.Storage} -- Storage object.

        Keyword Arguments:
            location {string} -- The location on disk you would like to store the file. (default: {None})

        Raises:
            DriverLibraryNotFound -- Raises when the boto3 library is not installed.

        Returns:
            string -- Returns the file name just saved.
        """

        driver = self.upload.driver('disk')
        driver.store(fileitem, location)
        file_location = driver.file_location

        # Check if is a valid extension
        self.validate_extension(fileitem.filename)

        try:
            import boto3
        except ImportError:
            raise DriverLibraryNotFound(
                'Could not find the "boto3" library. Please pip install this library '
                'by running "pip install boto3"')

        session = boto3.Session()
        client = session.client('s3',
                                region_name=self.config.DRIVERS['digitalocean']['region'],
                                endpoint_url=self.config.DRIVERS['digitalocean']['endpoint'],
                                aws_access_key_id=self.config.DRIVERS['digitalocean']['client'],
                                aws_secret_access_key=self.config.DRIVERS['digitalocean']['secret'])

        client.upload_file(
            file_location,
            self.config.DRIVERS['digitalocean']['space'],
            fileitem.filename
        )

        return fileitem.filename

    def store_prepend(self, fileitem, prepend, location=None):
        """Store the file onto a Digital Ocean Space but with a prepended file name.

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
