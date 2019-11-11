"""Manager Module."""

import inspect

from ..exceptions import (DriverNotFound,
                          MissingContainerBindingNotFound,
                          UnacceptableDriverType)

from ..app import App
from ..helpers import config


class Manager:
    """Base Manager Class."""

    config = None
    driver_prefix = None

    def __init__(self, container: App):
        """Manager constructor.

        Keyword Arguments:
            container {masonite.app.App} -- The container class (default: {None})
        """
        self.manage_driver = None
        self.container = container

    def load_container(self, container):
        """Load the container into the class and creates the default driver.

        Arguments:
            container {masonite.app.App} -- The container class

        Returns:
            self
        """
        self.container = container
        self.create_driver()
        return self

    def driver(self, driver):
        """Create the driver specified and returns the driver instance.

        Arguments:
            driver {masonite.drivers.Driver} -- An instance of a Driver class.

        Returns:
            masonite.drivers.Driver -- Returns a driver which is an instance of the base Driver class.
        """
        self.create_driver(driver)
        print('manage?', self.manage_driver)
        return self.manage_driver.load_manager(self)

    def create_driver(self, driver=None):
        """Create the driver to be used.

        This could be used as the default driver when the manager is created or called internally on the fly
        to change to a specific driver

        Keyword Arguments:
            driver {string} -- The name of the driver to switch to (default: {None})

        Raises:
            UnacceptableDriverType -- Raised when a driver passed in is not a string or a class
            DriverNotFound -- Raised when the driver can not be found.
        """

        if driver in (None, 'default'):
            driver = config('{}.driver'.format(self.config)).capitalize()
        else:
            if isinstance(driver, str):
                driver = driver.capitalize()

        try:
            if isinstance(driver, str):
                driver = self.container.make(
                    '{0}{1}Driver'.format(self.driver_prefix, driver)
                )
                # return
            print('is driver a class?', driver)
            if inspect.isclass(driver):
                driver = self.container.resolve(driver)
                print('driver is now', driver)

            self.manage_driver = driver
            return
            raise UnacceptableDriverType(
                'String or class based driver required. {} driver recieved.'.format(driver))
        except MissingContainerBindingNotFound:
            raise DriverNotFound(
                'Could not find the {0}{1}Driver from the service container. Are you missing a service provider?'.format(self.driver_prefix, driver))
