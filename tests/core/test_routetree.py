"""
MIT License

Copyright (c) 2018, Richard Kuesters

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

""" Test Route Tree """
import unittest
import logging

from masonite.RouteTree import RouteTree
from masonite.exceptions import RouteTreeError

from masonite.routes import Get, Post
import pytest

class Endpoint:
    def __init__(self, x):
        self.x = x

    def __repr__(self):
        return "<Endpoint {}>".format(self.x)

    __str__ = __repr__


class Middleware:
    def __init__(self, x):
        self.x = x

    def __repr__(self):
        return "<Middleware {}>".format(self.x)

    __str__ = __repr__


@pytest.fixture
def endpoint_factory():
    return Endpoint


@pytest.fixture
def middleware_factory():
    return Middleware

# Todo - Swap Webroutes for fixtures, change pytest to unittest

def test_tree():
    tree = RouteTree()
    assert tree is not None
    assert tree.root is not None
    assert len(tree.root.children) == 0
    assert tree.root.path is None
    assert tree.root.indices == ""
    assert tree.root.methods == {}
    assert tree.root.no_conflict_methods == {}

    r = tree.get("/foo", "BAR")
    assert r[0] is None
    assert r[1] == []
    assert r[2] == {}


def test_tree_repr(endpoint_factory):
    endpoint_1 = endpoint_factory(1)
    tree = RouteTree()
    assert repr(tree) == repr(tree.root)
    assert (
        repr(tree)
        == '<RouteTreeNode path: None, methods: {}, indices: "", children: []>'
    )
    assert (
        repr(tree.root)
        == '<RouteTreeNode path: None, methods: {}, indices: "", children: []>'
    )
    tree.insert("/foo", endpoint_1, ["BAR"])
    assert (
        repr(tree.root.children[0])
        == '<RouteTreeNode path: "/foo", methods: {\'BAR\': <Endpoint 1>}, indices: "", children: []>'
    )


def test_tree_validations(endpoint_factory):
    endpoint_1 = endpoint_factory(1)
    tree = RouteTree()

    with pytest.raises(ValueError):
        tree.insert(None, endpoint_1, ["BAR"])

    with pytest.raises(ValueError):
        tree.insert("", endpoint_1, ["BAR"])

    with pytest.raises(ValueError):
        tree.insert("     ", endpoint_1, ["BAR"])

    with pytest.raises(ValueError):
        tree.insert("foo", endpoint_1, ["BAR"])

    with pytest.raises(ValueError):
        tree.insert("   foo   ", endpoint_1, ["BAR"])

    with pytest.raises(ValueError):
        tree.insert("f/oo/", endpoint_1, ["BAR"])


def test_tree_config_1(endpoint_factory):
    endpoint_1 = endpoint_factory(1)
    tree = RouteTree()
    tree.VARIABLE = "$"
    tree.SEPARATOR = "."

    tree.insert(".foo", endpoint_1, ["BAR"])
    tree.insert(".foo.$bar", endpoint_1, ["BAR"])
    tree.insert(".bar", endpoint_1, ["BAR"])
    tree.insert(".bar.*rest", endpoint_1, ["BAR"])

    r = tree.get(".foo.hello", "BAR")
    assert r[0] == endpoint_1
    assert r[1] == []
    assert r[2] == {"bar": "hello"}

    r = tree.get(".bar.avra.cadavra.alacazam", "BAR")
    assert r[0] == endpoint_1
    assert r[1] == []
    assert r[2] == {"rest": "avra.cadavra.alacazam"}

    assert tree.config == {"variable": "$", "separator": "."}


def test_tree_config_2(endpoint_factory):
    endpoint_1 = endpoint_factory(1)
    tree = RouteTree(variable="$", separator=".")

    tree.insert(".foo", endpoint_1, ["BAR"])
    tree.insert(".foo.$bar", endpoint_1, ["BAR"])
    tree.insert(".bar", endpoint_1, ["BAR"])
    tree.insert(".bar.*rest", endpoint_1, ["BAR"])

    r = tree.get(".foo.hello", "BAR")
    assert r[0] == endpoint_1
    assert r[1] == []
    assert r[2] == {"bar": "hello"}

    r = tree.get(".bar.avra.cadavra.alacazam", "BAR")
    assert r[0] == endpoint_1
    assert r[1] == []
    assert r[2] == {"rest": "avra.cadavra.alacazam"}

    assert tree.config == {"variable": "$", "separator": "."}


def test_tree_config_error():
    tree = RouteTree()

    with pytest.raises(ValueError):
        tree.VARIABLE = "/"

    with pytest.raises(ValueError):
        tree.VARIABLE = "a"

    with pytest.raises(ValueError):
        tree.VARIABLE = "$$"

    with pytest.raises(ValueError):
        tree.VARIABLE = ""

    with pytest.raises(ValueError):
        tree.VARIABLE = None

    with pytest.raises(ValueError):
        tree.SEPARATOR = "@"

    with pytest.raises(ValueError):
        tree.SEPARATOR = "a"

    with pytest.raises(ValueError):
        tree.SEPARATOR = ".."

    with pytest.raises(ValueError):
        tree.SEPARATOR = ""

    with pytest.raises(ValueError):
        tree.SEPARATOR = None

    with pytest.raises(ValueError):
        RouteTree(variable="/")

    with pytest.raises(ValueError):
        RouteTree(separator="@")

    with pytest.raises(ValueError):
        RouteTree(variable=":", separator=":")

    with pytest.raises(ValueError):
        RouteTree(variable="a", separator="b")

    with pytest.raises(ValueError):
        RouteTree(separator="b")

    with pytest.raises(ValueError):
        RouteTree(variable="a")

    with pytest.raises(ValueError):
        RouteTree(variable="::", separator="//")

    with pytest.raises(ValueError):
        RouteTree(variable="::")

    with pytest.raises(ValueError):
        RouteTree(separator="//")

    # ----------------------------------------------------------------------- #
    # all tests bellow will assume defaults
    # ----------------------------------------------------------------------- #

    RouteTree(variable="", separator="")
    RouteTree(separator="")
    RouteTree(separator="")
    RouteTree(variable=None, separator=None)
    RouteTree(variable=None)
    RouteTree(separator=None)

    tree.insert("/", object(), ["BAR"])

    with pytest.raises(ValueError):
        tree.SEPARATOR = "."

    with pytest.raises(ValueError):
        tree.VARIABLE = "@"


def test_tree_single_endpoint(endpoint_factory):
    endpoint_1 = endpoint_factory(1)
    tree = RouteTree()

    tree.insert("/foo/@bar", endpoint_1, ["BAR"])

    r = tree.get("/foo/hello", "BAR")
    assert r[0] == endpoint_1
    assert r[1] == []
    assert r[2] == {"bar": "hello"}

    r = tree.get("/foooo", "BAR")
    assert r[0] is None
    assert r[1] == []
    assert r[2] == {}


def test_tree_methods_for(endpoint_factory):
    endpoint_1 = endpoint_factory(1)
    endpoint_2 = endpoint_factory(2)

    tree = RouteTree()

    tree.insert("/foo/@bar", endpoint_1, ["BAR"])
    tree.insert("/foo/@bar", endpoint_2, ["FOO"])

    r = tree.methods_for("/foo/hello")
    assert r == {"BAR", "FOO"}

    r = tree.methods_for("/foo/world")
    assert r == {"BAR", "FOO"}

    r = tree.methods_for("/foooo")
    assert r == set()


def test_tree_root_endpoint(endpoint_factory):
    endpoint_1 = endpoint_factory(1)
    tree = RouteTree()

    tree.insert("/", endpoint_1, ["BAR"])

    r = tree.get("/", "BAR")
    assert r[0] == endpoint_1
    assert r[1] == []
    assert r[2] == {}


def test_tree_full(endpoint_factory, middleware_factory):
    endpoint_1 = endpoint_factory(1)
    middleware_1 = middleware_factory(1)
    middleware_2 = middleware_factory(2)
    middleware_3 = middleware_factory(3)
    middleware_4 = middleware_factory(4)

    tree = RouteTree()

    tree.insert("/foo", endpoint_1, ["FOO"])
    tree.insert("/foo", middleware_1, ["FOO", "BAR"], no_conflict=True)
    tree.insert("/foo", middleware_1, ["BAR"], no_conflict=True)
    tree.insert("/foo/@name", endpoint_1, ["FOO", "BAR"])
    tree.insert(
        "/foo/@name/@x", middleware_2, ["FOO", "BAR"], no_conflict=True
    )
    tree.insert("/foo/@name/@x/@y", endpoint_1, ["FOO", "BAR"])
    tree.insert("/static/*path", endpoint_1, ["FOO"])

    with pytest.raises(ValueError):
        tree.insert("/foo/@bar", endpoint_1, ["FOO"])

    with pytest.raises(KeyError):
        tree.insert("/foo", middleware_2, ["FOO"])

    r = tree.get("/foo/hello", "FOO")
    assert r[0] == endpoint_1
    assert r[1] == [middleware_1]
    assert r[2] == {"name": "hello"}

    r = tree.get("/foo/hello/a/b", "BAR")
    assert r[0] == endpoint_1
    assert r[1] == [middleware_1, middleware_2]
    assert r[2] == {"name": "hello", "x": "a", "y": "b"}

    r = tree.get("/static/path/to/my/file.py", "FOO")
    assert r[0] == endpoint_1
    assert r[1] == []
    assert r[2] == {"path": "path/to/my/file.py"}

    tree.insert(
        "/foo/@name/@x", middleware_3, ["FOO", "BAR"], no_conflict=True
    )

    tree.insert("/foo/@name/@x/@y", middleware_4, ["FOO"], no_conflict=True)

    r = tree.get("/foo/hello/a/b", "FOO")
    assert r[0] == endpoint_1
    assert r[1] == [middleware_1, middleware_2, middleware_3, middleware_4]
    assert r[2] == {"name": "hello", "x": "a", "y": "b"}

    r = tree.get("/foo/hello/aa", "FOO")
    assert r[0] is None
    assert r[1] == []
    assert r[2] == {}

    r = tree.get("/foo/hello/a/b", "BAZ")
    assert r[0] is tree.sentinel
    assert r[1] == []
    assert r[2] == {}

    m = tree.methods_for("/foo/hello/aa")
    assert m == set()

    m = tree.methods_for("/foo/hello/a/b")
    assert m == {"BAR", "FOO"}

    m = tree.methods_for("/foo")
    assert m == {"FOO"}

    m = tree.methods_for("/static/abra/cadabra")
    assert m == {"FOO"}


def test_sentinel(endpoint_factory):
    endpoint_1 = endpoint_factory(1)
    tree = RouteTree()
    tree.insert("/hello/@bar", endpoint_1, ["BAR"])

    r = tree.get("/hello/world", "BAZ")
    assert r[0] is tree.sentinel
    assert r[1] == []
    assert r[2] == {}


def test_duplicate_parameters(endpoint_factory):
    endpoint_1 = endpoint_factory(1)
    tree = RouteTree()
    tree.insert("/hello/@bar", endpoint_1, ["BAR"])

    with pytest.raises(ValueError):
        tree.insert("/hello/@bar/@bar", endpoint_1, ["BAR"])

    with pytest.raises(ValueError):
        tree.insert("/hello/@bar/world/@bar", endpoint_1, ["BAR"])

    another_tree = RouteTree(variable=".", separator="|")
    another_tree.insert("|hello|.bar", endpoint_1, ["BAR"])

    with pytest.raises(ValueError):
        another_tree.insert("|hello|.bar|.bar", endpoint_1, ["BAR"])

    with pytest.raises(ValueError):
        another_tree.insert("|hello|.bar|world|.bar", endpoint_1, ["BAR"])

    with pytest.raises(ValueError):
        another_tree.insert("|hello|.bar|world|*bar", endpoint_1, ["BAR"])


def test_tree_middleware_first(endpoint_factory, middleware_factory):
    endpoint_1 = endpoint_factory(1)
    middleware_1 = middleware_factory(1)

    tree = RouteTree()

    tree.insert("/hello", middleware_1, ["BAR"], no_conflict=True)
    tree.insert("/hello/world", endpoint_1, ["BAR"])

    r = tree.get("/hello", "BAR")
    assert r[0] is None
    assert r[1] == []
    assert r[2] == {}

    r = tree.get("/hello/world", "BAR")
    assert r[0] == endpoint_1
    assert r[1] == [middleware_1]
    assert r[2] == {}
