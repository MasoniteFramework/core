"""A RouteProvider Service Provider."""

from masonite.helpers.routes import create_matchurl
from masonite.provider import ServiceProvider
from masonite.request import Request
from masonite.response import Response
from masonite.routes import Route
from masonite.RouteTree import RouteTree


class RouteProvider(ServiceProvider):

    def register(self):
        # Todo - Create tree and bind it
        routes = self.app.make("WebRoutes")
        tree = RouteTree()

        # Put routes in tree
        for route in routes:
            method = route.method_type
            url = route.route_url
            tree.insert(url, route, method)

        self.app.bind("RouteTree", tree)

    def boot(self, router: Route, request: Request, response: Response):
        # Todo - Tree based lookup
        # All routes joined
        from config import application

        tree = self.app.make("RouteTree")
        route, _, url_params = tree.get(router.url, request.get_request_method())

        # No Response was found in the for loop so let's set an arbitrary response now.
        if route is None:
            return response.view('Route not found. Error 404', status=404)

        # If the route exists but not the method is incorrect
        if route is tree.sentinel: 
            return response.view('Method not allowed', status=405)

        """Houston, we've got a match
            Check to see if a route matches the corresponding router url. If a match
            is found, execute that route and break out of the loop. We only need
            one match. Routes are executed on a first come, first serve basis
        """
        route.load_request(request)

        """Check if subdomains are active and if the route matches on the subdomain
            It needs to match to.
        """

        if request.has_subdomain():
            # Check if the subdomain matches the correct routes domain
            if not route.has_required_domain():
                response.view('Route not found. Error 404')

        """Get URL Parameters
            This will create a dictionary of parameters given. This is sort of a short
            but complex way to retrieve the url parameters.
            This is the code used to convert /url/@firstname/@lastname
            to {'firstmane': 'joseph', 'lastname': 'mancuso'}.
        """

        request.set_params(url_params)

        """Excute HTTP before middleware
            Only those middleware that have a "before" method are ran.
        """

        for http_middleware in self.app.make('HttpMiddleware'):
            located_middleware = self.app.resolve(
                http_middleware
            )
            if hasattr(located_middleware, 'before'):
                located_middleware.before()

        """Execute Route Before Middleware
            This is middleware that contains a before method.
        """

        route.run_middleware('before')

        # Show a helper in the terminal of which route has been visited
        if application.DEBUG:
            print(request.get_request_method() + ' Route: ' + router.url)

        # If no routes have been found and no middleware has changed the status code
        if not request.get_status():

            """Get the response from the route and set it on the 'Response' key.
                This data is typically the output of the controller method depending
                on the type of route.
            """

            response.view(route.get_response(), status=200)

        """Execute Route After Route Middleware
            This is middleware that contains an after method.
        """

        route.run_middleware('after')

        """Excute HTTP after middleware
            Only those middleware that have an "after" method are ran.
            Check here if the middleware even has the required method.
        """

        for http_middleware in self.app.make('HttpMiddleware'):
            located_middleware = self.app.resolve(http_middleware)

            if hasattr(located_middleware, 'after'):
                located_middleware.after()
