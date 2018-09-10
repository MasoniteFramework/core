from masonite.request import Request
from masonite.view import View
from masonite.app import App
from masonite.middleware import CorsMiddleware
from masonite.testsuite.TestSuite import generate_wsgi
import pytest
from masonite.exceptions import InvalidCSRFToken

class TestCSRFMiddleware:

    def setup_method(self):
        self.app = App()
        self.request = Request(generate_wsgi())    
        self.view = View(self.app)
        self.app.bind('Request', self.request)

        self.request = self.app.make('Request')

        self.middleware = CorsMiddleware(self.request)

    def test_cors_headers(self):
        self.middleware.after()

        cors = {"Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"}

        