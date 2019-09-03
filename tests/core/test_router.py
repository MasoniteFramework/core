""" Test Masonite Radix Tree Router

Special thanks to: Richard Kuesters and the XRTR project. (https://github.com/vltr/xrtr)
"""
import re
import unittest

from masonite.router import Router
from masonite.exceptions import RouterError, InvalidRouteCompileException

from masonite.routes import Route


class DummyRoute:
    def __repr__(self):
        return "< dummy route >"


class TestRouter(unittest.TestCase):
    def test_router(self):
        router = Router()
        self.assertTrue(router is not None)
        self.assertTrue(router.root is not None)
        self.assertEqual(len(router.root.children), 0)
        self.assertTrue(router.root.path is None)
        self.assertEqual(router.root.indices, "")
        self.assertEqual(router.root.methods, {})
        self.assertEqual(router.root.no_conflict_methods, {})

        retval = router.get("/foo", "BAR")
        self.assertTrue(retval[0] is None)
        self.assertEqual(retval[1], [])
        self.assertEqual(retval[2], {})

    def test_router_repr(self):
        route = DummyRoute()
        router = Router()
        self.assertEqual(repr(router), repr(router.root))
        self.assertEqual(repr(router), '<RouteTreeNode path: None, methods: {}, indices: "", children: []>')
        self.assertEqual(repr(router.root), '<RouteTreeNode path: None, methods: {}, indices: "", children: []>')

        router.insert("/foo", route, ["BAR"])
        assert (
            repr(router.root.children[0])
            == '<RouteTreeNode path: "/foo", methods: {\'BAR\': < dummy route >}, indices: "", children: []>'
        )

    def test_router_validations(self):
        route = DummyRoute()
        router = Router()

        with self.assertRaises(TypeError):
            router.insert(None, route, ["BAR"])

        with self.assertRaises(ValueError):
            router.insert("", route, ["BAR"])

        with self.assertRaises(ValueError):
            router.insert("     ", route, ["BAR"])

        with self.assertRaises(ValueError):
            router.insert("foo", route, ["BAR"])

        with self.assertRaises(ValueError):
            router.insert("   foo   ", route, ["BAR"])

        with self.assertRaises(ValueError):
            router.insert("f/oo/", route, ["BAR"])

    def test_router_config_1(self):
        route = DummyRoute()
        router = Router()
        router.VARIABLE = "$"
        router.SEPARATOR = "."

        router.insert(".foo", route, ["BAR"])
        router.insert(".foo.$bar", route, ["BAR"])
        router.insert(".bar", route, ["BAR"])
        router.insert(".bar.*rest", route, ["BAR"])

        retval = router.get(".foo.hello", "BAR")
        self.assertEqual(retval[0], route)
        self.assertEqual(retval[1], [])
        self.assertEqual(retval[2], {"bar": "hello"})

        retval = router.get(".bar.avra.cadavra.alacazam", "BAR")
        self.assertEqual(retval[0], route)
        self.assertEqual(retval[1], [])
        self.assertEqual(retval[2], {"rest": "avra.cadavra.alacazam"})

        self.assertEqual(router.config, {"variable": "$", "separator": "."})

    def test_router_config_2(self):
        route = DummyRoute()
        router = Router(variable="$", separator=".")

        router.insert(".foo", route, ["BAR"])
        router.insert(".foo.$bar", route, ["BAR"])
        router.insert(".bar", route, ["BAR"])
        router.insert(".bar.*rest", route, ["BAR"])

        retval = router.get(".foo.hello", "BAR")
        self.assertEqual(retval[0], route)
        self.assertEqual(retval[1], [])
        self.assertEqual(retval[2], {"bar": "hello"})

        retval = router.get(".bar.avra.cadavra.alacazam", "BAR")
        self.assertEqual(retval[0], route)
        self.assertEqual(retval[1], [])
        self.assertEqual(retval[2], {"rest": "avra.cadavra.alacazam"})

        self.assertEqual(router.config, {"variable": "$", "separator": "."})

    def test_router_config_error(self):
        router = Router()

        with self.assertRaises(ValueError):
            router.VARIABLE = "/"

        with self.assertRaises(ValueError):
            router.VARIABLE = "a"

        with self.assertRaises(ValueError):
            router.VARIABLE = "$$"

        with self.assertRaises(ValueError):
            router.VARIABLE = ""

        with self.assertRaises(ValueError):
            router.VARIABLE = None

        with self.assertRaises(ValueError):
            router.SEPARATOR = "@"

        with self.assertRaises(ValueError):
            router.SEPARATOR = "a"

        with self.assertRaises(ValueError):
            router.SEPARATOR = ".."

        with self.assertRaises(ValueError):
            router.SEPARATOR = ""

        with self.assertRaises(ValueError):
            router.SEPARATOR = None

        with self.assertRaises(ValueError):
            Router(variable="/")

        with self.assertRaises(ValueError):
            Router(separator="@")

        with self.assertRaises(ValueError):
            Router(variable=":", separator=":")

        with self.assertRaises(ValueError):
            Router(variable="a", separator="b")

        with self.assertRaises(ValueError):
            Router(separator="b")

        with self.assertRaises(ValueError):
            Router(variable="a")

        with self.assertRaises(ValueError):
            Router(variable="::", separator="//")

        with self.assertRaises(ValueError):
            Router(variable="::")

        with self.assertRaises(ValueError):
            Router(separator="//")

        # ----------------------------------------------------------------------- #
        # all tests bellow will assume defaults
        # ----------------------------------------------------------------------- #

        Router(variable="", separator="")
        Router(separator="")
        Router(separator="")
        Router(variable=None, separator=None)
        Router(variable=None)
        Router(separator=None)

        router.insert("/", DummyRoute(), ["BAR"])

        with self.assertRaises(ValueError):
            router.SEPARATOR = "."

        with self.assertRaises(ValueError):
            router.VARIABLE = "@"

    def test_router_single_endpoint(self):
        route = DummyRoute()
        router = Router()

        router.insert("/foo/@bar", route, ["FOO"])

        retval = router.get("/foo/hello", "FOO")
        self.assertEqual(retval[0], route)
        self.assertEqual(retval[1], [])
        self.assertEqual(retval[2], {"bar": "hello"})

        retval = router.get("/foooo", "FOO")
        self.assertTrue(retval[0] is None)
        self.assertEqual(retval[1], [])
        self.assertEqual(retval[2], {})

    def test_router_methods_for(self):
        route = DummyRoute()

        router = Router()
        router.insert("/foo/@bar", route, ["FOO"])
        router.insert("/foo/@bar", route, ["BAR"])

        retval = router.methods_for("/foo/hello")
        self.assertEqual(retval, {"FOO", "BAR"})

        retval = router.methods_for("/foo/world")
        self.assertEqual(retval, {"FOO", "BAR"})

        retval = router.methods_for("/foooo")
        self.assertEqual(retval, set())

    def test_router_root_endpoint(self):
        route = DummyRoute()
        router = Router()

        router.insert("/", route, ["BAR"])

        retval = router.get("/", "BAR")
        self.assertEqual(retval[0], route)
        self.assertEqual(retval[1], [])
        self.assertEqual(retval[2], {})

    def test_router_full(self):
        route = DummyRoute()

        middleware_1 = [object()]
        middleware_2 = [object()]
        middleware_3 = [object()]
        middleware_4 = [object()]

        router = Router()

        router.insert("/foo", route, ["FOO"])
        router.insert("/foo", middleware_1, ["FOO", "BAR"], no_conflict=True)
        router.insert("/foo", middleware_1, ["BAR"], no_conflict=True)
        router.insert("/foo/@name", route, ["FOO", "BAR"])
        router.insert("/foo/@name/@x", middleware_2, ["FOO", "BAR"], no_conflict=True)
        router.insert("/foo/@name/@x/@y", route, ["FOO", "BAR"])
        router.insert("/static/*path", route, ["FOO"])

        with self.assertRaises(ValueError):
            router.insert("/foo/@bar", route, ["FOO"])

        with self.assertRaises(KeyError):
            router.insert("/foo", middleware_2, ["FOO"])

        retval = router.get("/foo/hello", "FOO")
        self.assertEqual(retval[0], route)
        self.assertEqual(retval[1], [middleware_1])
        self.assertEqual(retval[2], {"name": "hello"})

        retval = router.get("/foo/hello/a/b", "BAR")
        self.assertEqual(retval[0], route)
        self.assertEqual(retval[1], [middleware_1, middleware_2])
        self.assertEqual(retval[2], {"name": "hello", "x": "a", "y": "b"})

        retval = router.get("/static/path/to/my/file.py", "FOO")
        self.assertEqual(retval[0], route)
        self.assertEqual(retval[1], [])
        self.assertEqual(retval[2], {"path": "path/to/my/file.py"})

        router.insert("/foo/@name/@x", middleware_3, ["FOO", "BAR"], no_conflict=True)
        router.insert("/foo/@name/@x/@y", middleware_4, ["FOO"], no_conflict=True)

        retval = router.get("/foo/hello/a/b", "FOO")
        self.assertEqual(retval[0], route)
        self.assertEqual(retval[1], [middleware_1, middleware_2, middleware_3, middleware_4])
        self.assertEqual(retval[2], {"name": "hello", "x": "a", "y": "b"})

        retval = router.get("/foo/hello/aa", "FOO")
        self.assertTrue(retval[0] is None)
        self.assertEqual(retval[1], [])
        self.assertEqual(retval[2], {})

        retval = router.get("/foo/hello/a/b", "BAZ")
        self.assertTrue(retval[0] is router.sentinel)
        self.assertEqual(retval[1], [])
        self.assertEqual(retval[2], {})

        methods = router.methods_for("/foo/hello/aa")
        self.assertEqual(methods, set())

        methods = router.methods_for("/foo/hello/a/b")
        self.assertEqual(methods, {"BAR", "FOO"})

        methods = router.methods_for("/foo")
        self.assertEqual(methods, {"FOO"})

        methods = router.methods_for("/static/abra/cadabra")
        self.assertEqual(methods, {"FOO"})

    def test_sentinel(self):
        route = DummyRoute()
        router = Router()
        router.insert("/hello/@bar", route, ["BAR"])

        retval = router.get("/hello/world", "BAZ")
        self.assertTrue(retval[0] is router.sentinel)
        self.assertEqual(retval[1], [])
        self.assertEqual(retval[2], {})

    def test_duplicate_parameters(self):
        route = DummyRoute()
        router = Router()
        router.insert("/hello/@bar", route, ["BAR"])

        with self.assertRaises(ValueError):
            router.insert("/hello/@bar/@bar", route, ["BAR"])

        with self.assertRaises(ValueError):
            router.insert("/hello/@bar/world/@bar", route, ["BAR"])

        another_router = Router(variable=".", separator="|")
        another_router.insert("|hello|.bar", route, ["BAR"])

        with self.assertRaises(ValueError):
            another_router.insert("|hello|.bar|.bar", route, ["BAR"])

        with self.assertRaises(ValueError):
            another_router.insert("|hello|.bar|world|.bar", route, ["BAR"])

        with self.assertRaises(ValueError):
            another_router.insert("|hello|.bar|world|*bar", route, ["BAR"])

    def test_router_middleware_first(self):
        router = DummyRoute()
        middleware = object()

        router = Router()

        router.insert("/hello", middleware, ["BAR"], no_conflict=True)
        router.insert("/hello/world", router, ["BAR"])

        retval = router.get("/hello", "BAR")
        self.assertTrue(retval[0] is None)
        self.assertEqual(retval[1], [])
        self.assertEqual(retval[2], {})

        retval = router.get("/hello/world", "BAR")
        self.assertEqual(retval[0], router)
        self.assertEqual(retval[1], [middleware])
        self.assertEqual(retval[2], {})

    def test_router_compilers(self):
        route = DummyRoute()
        router = Router()
        router.compilers = Route().route_compilers
        for key, value in router.compilers.items():
            router.compilers[key] = re.compile(value)
        router.insert("/foo/@bar:int", route, ["BAR"])

        retval = router.get("/foo/2019", "BAR")
        self.assertEqual(retval[0], route)
        self.assertEqual(retval[1], [])
        self.assertEqual(retval[2], {"bar": "2019"})

        # Did not match
        with self.assertRaises(InvalidRouteCompileException):
            retval = router.get("/foo/wew", "BAR")
        
        # Route compiler not found
        with self.assertRaises(InvalidRouteCompileException):
            router.insert("/hi/@hello:none", route, ["BAR"])
            retval = router.get("/hi/wew", "BAR")

    def test_can_handle_subdomains(self):
        route = DummyRoute()
        router = Router()
        router.compilers = Route().route_compilers
        for key, value in router.compilers.items():
            router.compilers[key] = re.compile(value)
        router.insert("test./foo/@bar", route, ["BAR"])

        retval = router.get("test./foo/2019", "BAR")
        self.assertEqual(retval[0], route)
        self.assertEqual(retval[1], [])
        self.assertEqual(retval[2], {"bar": "2019"})

        # Test retrieving an invalid route
        with self.assertRaises(RouterError):
            router.get("test./foo/2019.we", "BAR")

        # Check if there is more than one period
        with self.assertRaises(ValueError):
            router.insert("test./foo/bar/.hi", route, ["BAR"])

        with self.assertRaises(ValueError):
            router.insert("test./foo/bar./hi", route, ["BAR"])
