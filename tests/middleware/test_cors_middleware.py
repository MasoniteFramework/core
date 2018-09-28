""" Test CORS Middleware """
from masonite.request import Request
from masonite.middleware import CorsMiddleware
from masonite.testsuite.TestSuite import generate_wsgi

class TestCORSMiddleware:

   def setup_method(self):
        self.request = Request(generate_wsgi())
        self.middleware = CorsMiddleware(self.request)

   def test_cors_middleware(self):
        self.middleware.before()

        # Demo CORS values - Cope your CORS values from CorsMiddleware.py
        cors = {"Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"}
        
        for key, value in cors.items():
            assert self.request.header(key) == value

