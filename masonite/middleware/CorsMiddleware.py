""" CORS Middleware """
from masonite.request import Request


class CorsMiddleware:

    def __init__(self, request: Request):
        self.request = request

    def before(self):
        '''
        |--------------------------------------------------------------------------
        | Appends CORS Headers to HTTP response
        |--------------------------------------------------------------------------
        |
        '''

        # Demo CORS values - Modify for your own CORS values
        cors = {"Access-Control-Allow-Origin": "*",
                "Access-Control-Allow-Headers": "Content-Type",
                "Access-Control-Allow-Methods": "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"}

        for key, value in cors.items():
            self.request.header(key, value, http_prefix=None)
