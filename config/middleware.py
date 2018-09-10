from app.http.middleware.MiddlewareTest import MiddlewareTest
from masonite.middleware import JsonResponseMiddleware
from masonite.middleware import CorsMiddleware
from app.http.middleware.AddAttributeMiddleware import AddAttributeMiddleware


ROUTE_MIDDLEWARE = {
    'test': MiddlewareTest,
    'middleware.test': [
        MiddlewareTest,
        AddAttributeMiddleware,
    ]
}

HTTP_MIDDLEWARE = [
    JsonResponseMiddleware,
    CorsMiddleware
]
