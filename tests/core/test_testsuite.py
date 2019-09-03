import copy

from masonite.route import Route
from masonite.router import Router
from masonite.testsuite.TestSuite import TestSuite
import unittest


class TestTestSuite(unittest.TestCase):

    def setUp(self):
        self.suite = TestSuite().create_container()
        self.container = self.suite.get_container()
        
        router = Router()
        router.compilers = copy.deepcopy(Route.route_compilers)

        # Insert routes in tree
        for web_route in self.app.make("WebRoutes"):
            if web_route.required_domain:
                url = "{subdomain}.{url}".format(subdomain=web_route.required_domain, url=web_route.route_url)
            else:
                url = web_route.route_url
            router.insert(url, web_route, web_route.method_type)

        self.container.bind("Router", router)

    def test_testsuite_creates_container(self):
        self.assertTrue(self.container.make('Request'))

    def test_testsuite_should_return_route_exists(self):
        self.assertTrue(self.suite.route('/test').exists())

    def test_testsuite_route_should_return_bool_if_has_middleware(self):
        self.assertTrue(self.suite.route('/test').hasMiddleware('auth'))
        self.assertFalse(self.suite.route('/test').hasMiddleware('none'))
