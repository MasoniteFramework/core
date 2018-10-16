"""Maintainance Mode Middleware."""
import os
from masonite.request import Request
from config import application


class MaintenanceModeMiddleware:
    """ Class that initiates maintance mode """

    def __init__(self, request: Request):
        self.request = request

    def before(self):
        down = os.path.exists(os.path.join(application.BASE_DIRECTORY, 'bootstrap/down'))
        if down is True:
            self.request.status(503)
