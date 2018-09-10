""" CORS Middleware """
from masonite.request import Request

class CorsMiddleware:

    def __init__(self, request: Request):
        self.request = request

    def after(self):                          
        '''
        |--------------------------------------------------------------------------
        | Create Dictionary of CORS headers
        |--------------------------------------------------------------------------
        |
        | Appends CORS headers to HTTP response
        |
        | Ex. cors = {"Access-Control-Allow-Origin": "*",
        |             "Access-Control-Allow-Headers": "Content-Type",
        |             "Access-Control-Allow-Methods": "DELETE, GET, HEAD, OPTIONS, PATCH, POST, PUT"}
        |
        '''

        cors = dict()
        
        for key, value in cors.items():
            self.request.header(key, value, http_prefix=None)
