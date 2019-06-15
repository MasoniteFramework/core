""" Test Archer """
import unittest
import logging

from masonite.RouteTree import RouteTree
from masonite.exceptions import RouteTreeError


class TestRouteTree(unittest.TestCase):

    def setUp(self):
        self.routes = RouteTree()

    def tearDown(self):
        pass

    def test_match(self):
        """
        Should match an url to a registered pattern
        """
        self.routes.add(':foo/:bar/api/:baz', 'foo')
        route = self.routes.match('foo/bar/api/baz')
        self.assertDictEqual(
            route.params,
            {'foo': 'foo', 'bar': 'bar', 'baz': 'baz'})
        self.assertEqual(route.anything, 'foo')

    def test_match_nested(self):
        """
        Should support nested patterns
        """
        self.routes.add(':foo/:bar/api/:baz', 'foo')
        self.routes.add(':foo/:bar/api/:baz/books/:id', 'bar')
        route = self.routes.match('foo/bar/api/baz')
        route_b = self.routes.match('foo/bar/api/baz/books/id')
        self.assertDictEqual(
            route.params,
            {'foo': 'foo', 'bar': 'bar', 'baz': 'baz'})
        self.assertDictEqual(
            route_b.params,
            {'foo': 'foo', 'bar': 'bar', 'baz': 'baz', 'id': 'id'})
        self.assertEqual(route.anything, 'foo')
        self.assertEqual(route_b.anything, 'bar')

    def test_match_clashing(self):
        """
        Should resolve clashing
        """
        self.routes.add(':foo/:bar/:baz', 'foo')
        self.routes.add(':foo/api/:baz', 'bar')
        route = self.routes.match('foo/bar/baz')
        route_b = self.routes.match('foo/api/baz')
        self.assertDictEqual(
            route.params,
            {'foo': 'foo', 'bar': 'bar', 'baz': 'baz'})
        self.assertDictEqual(
            route_b.params,
            {'foo': 'foo', 'baz': 'baz'})
        self.assertEqual(route.anything, 'foo')
        self.assertEqual(route_b.anything, 'bar')

    def test_match_clashing_backtracking(self):
        """
        Should resolve clashing by doing backtracking
        """
        # match will walk up to the "api" part then realize
        # it needs one more part and then fallback to the previous
        # matched path (ie: all variables)
        self.routes.add(':bar/:baz', 'foo')
        self.routes.add('api', 'bar')
        route = self.routes.match('bar/baz')
        route_b = self.routes.match('api/baz')
        self.assertDictEqual(
            route.params,
            {'bar': 'bar', 'baz': 'baz'})
        self.assertDictEqual(
            route_b.params,
            {'bar': 'api', 'baz': 'baz'})
        self.assertEqual(route.anything, 'foo')
        self.assertEqual(route_b.anything, 'foo')

    def test_match_clashing_backtracking_deeper(self):
        """
        Should resolve clashing by doing backtracking
        """
        self.routes.add(':foo/:bar/:baz', 'foo')
        self.routes.add('api/:bar/:baz', 'bar')
        self.routes.add('api/id', 'baz')
        route = self.routes.match('api/id/baz')
        self.assertDictEqual(
            route.params,
            {'bar': 'id', 'baz': 'baz'})
        self.assertEqual(route.anything, 'bar')

    def test_match_clashing_last_part(self):
        """
        Should resolve clashing by doing backtracking
        """
        self.routes.add(':foo/last', 'foo')
        self.routes.add('api', 'baz')
        route = self.routes.match('api/last')
        self.assertDictEqual(
            route.params,
            {'foo': 'api'})
        self.assertEqual(route.anything, 'foo')

    def test_match_clashing_missing_part(self):
        """
        Should resolve clashing by doing backtracking
        """
        self.routes.add('foo/bar/:baz', 'foo')
        self.routes.add(':foo/:bar', 'foo')
        route = self.routes.match('foo/bar')
        self.assertDictEqual(
            route.params,
            {'foo': 'foo', 'bar': 'bar'})
        self.assertEqual(route.anything, 'foo')

    def test_match_not_found(self):
        """
        Should raise match error if there is no match
        """
        self.assertRaises(RouteTreeError, self.routes.match, 'foo')

    def test_match_not_found_missing_part(self):
        """
        Should raise match error if there is no match
        """
        self.routes.add(':foo/:bar/:baz', 'foo')
        self.assertRaises(RouteTreeError, self.routes.match, 'foo/bar')

    def test_match_case_sensitive(self):
        """
        Should be case sensitive (see HTTP URL spec)
        """
        self.routes.add('API', 'foo')
        route = self.routes.match('API')
        self.assertDictEqual(route.params, {})
        self.assertEqual(route.anything, 'foo')
        self.assertRaises(RouteTreeError, self.routes.match, 'api')

    def test_match_bail_early_on_deeper_urls(self):
        """
        Should not bother matching URLs larger than the largest registered URL
        """
        self.routes.add('foo/bar/baz', 'foo')
        self.routes.match('foo/bar/baz')
        self.routes._max_depth = 0
        self.assertRaises(RouteTreeError, self.routes.match, 'foo/bar/baz')
        self.routes._max_depth = 1
        self.assertRaises(RouteTreeError, self.routes.match, 'foo/bar/baz')
        self.routes._max_depth = 10
        self.routes.match('foo/bar/baz')

    def test_normalize_urls(self):
        """
        Should not care about leading/trailing slashes
        """
        self.routes.add('/foo/bar/baz/', 'foo')
        route = self.routes.match('foo/bar/baz')
        self.assertDictEqual(route.params, {})
        self.assertEqual(route.anything, 'foo')

        route = self.routes.match('/foo/bar/baz/')
        self.assertDictEqual(route.params, {})
        self.assertEqual(route.anything, 'foo')

        route = self.routes.match('/foo/bar/baz')
        self.assertDictEqual(route.params, {})
        self.assertEqual(route.anything, 'foo')

        route = self.routes.match('foo/bar/baz/')
        self.assertDictEqual(route.params, {})
        self.assertEqual(route.anything, 'foo')

    def test_match_var_any(self):
        """
        Should match unknown number of URL parts
        """
        self.routes.add(':*path', 'foo')
        self.routes.add('static/:*path', 'bar')
        self.routes.add('static/:*path/sub-path', 'baz')
        self.routes.add('static/:*path/sub-path/:file_name', 'qux')

        route = self.routes.match('foo/bar/baz')
        self.assertDictEqual(route.params, {'path': ('foo', 'bar', 'baz')})
        self.assertEqual(route.anything, 'foo')

        route = self.routes.match('static/foo/bar/baz')
        self.assertDictEqual(route.params, {'path': ('foo', 'bar', 'baz')})
        self.assertEqual(route.anything, 'bar')

        route = self.routes.match('static/foo/bar/baz/sub-path')
        self.assertDictEqual(route.params, {'path': ('foo', 'bar', 'baz')})
        self.assertEqual(route.anything, 'baz')

        route = self.routes.match('static/foo/bar/baz/sub-path/catz.jpg')
        self.assertDictEqual(route.params, {
            'file_name': 'catz.jpg',
            'path': ('foo', 'bar', 'baz')})
        self.assertEqual(route.anything, 'qux')

    def test_match_var_any_many(self):
        """
        Should match multiple any vars
        """
        self.routes.add(':*path/:*path_a/:*patch_b', 'foo')
        route = self.routes.match('foo/bar/baz/qux')
        self.assertDictEqual(route.params, {
            'patch_b': ('baz', 'qux'), 'path': ('foo',), 'path_a': ('bar',)})
        self.assertEqual(route.anything, 'foo')

    def test_match_var_any_precedence(self):
        """
        Should match in order: static > var > any-var
        """
        self.routes.add(':var1/:*path/:var2', 'foo')
        self.routes.add('static1/:*path/static2', 'bar')
        self.routes.add(':var1/:*path/static2', 'baz')
        self.routes.add('static2/:var1/:*path/:var2/:*path2', 'qux')

        # Never matches, since foo takes precedence
        self.routes.add(':*path/:var1/:*path2', 'bad')

        route = self.routes.match('foo/bar/baz/qux')
        self.assertDictEqual(route.params, {'path': ('bar', 'baz'), 'var2': 'qux', 'var1': 'foo'})
        self.assertEqual(route.anything, 'foo')

        route = self.routes.match('static1/bar/baz/static2')
        self.assertDictEqual(route.params, {'path': ('bar', 'baz')})
        self.assertEqual(route.anything, 'bar')

        route = self.routes.match('foo/bar/baz/static2')
        self.assertDictEqual(route.params, {'var1': 'foo', 'path': ('bar', 'baz')})
        self.assertEqual(route.anything, 'baz')

        route = self.routes.match('static2/foo/bar/baz/qux')
        self.assertDictEqual(route.params, {
            'var1': 'foo', 'path': ('bar',), 'var2': 'baz', 'path2': ('qux',)})
        self.assertEqual(route.anything, 'qux')

    def test_max_depth(self):
        """
        Should not match on max_depth < url length
        """
        rts = RouteTree(max_depth=3)
        rts.add(':*path', 'foo')
        self.assertEqual(rts.match('foo/bar/baz').anything, 'foo')

        rts = RouteTree(max_depth=1)
        rts.add(':*path', 'foo')
        self.assertRaises(archer.RouteError, rts.match, 'foo/bar/baz')

        # Changes max_depth
        rts.add(':var/bar/baz', 'bar')
        self.assertEqual(rts.match('foo/bar/baz').anything, 'bar')
