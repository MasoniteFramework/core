"""A RouterProvider Service Provider."""
import copy
import re

from masonite.provider import ServiceProvider
from masonite.routes import Route
from masonite.router import Router

class RouterProvider(ServiceProvider):
    """Load Masonite router with routes"""
    wsgi = False

    def boot(self, route: Route):
        router = Router()
        router.compilers = copy.deepcopy(route.route_compilers)

        # Insert routes in tree
        for web_route in self.app.make("WebRoutes"):
            if web_route.required_domain:
                url = "{subdomain}.{url}".format(subdomain=web_route.required_domain, url=web_route.route_url)
            else:
                url = web_route.route_url
            router.insert(url, web_route, web_route.method_type)

        self.app.bind("Router", router)
