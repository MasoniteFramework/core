""" Test Archer """
import unittest
import logging

from masonite.RouteTree import RouteTree
from masonite.exceptions import RouteTreeError


class TestRouteTree(unittest.TestCase):

    def setUp(self):
        self.tree = RouteTree()

    def tearDown(self):
        pass

    def test_match(self):
        """
        Should match an url to a registered pattern
        """
        self.tree.add(':foo/:bar/api/:baz', 'foo')
        router = self.tree.match('foo/bar/api/baz')
        self.assertDictEqual(
            router.params,
            {'foo': 'foo', 'bar': 'bar', 'baz': 'baz'})
        self.assertEqual(router.route, 'foo')

    def test_match_nested(self):
        """
        Should support nested patterns
        """
        self.tree.add(':foo/:bar/api/:baz', 'foo')
        self.tree.add(':foo/:bar/api/:baz/books/:id', 'bar')
        router = self.tree.match('foo/bar/api/baz')
        router_b = self.tree.match('foo/bar/api/baz/books/id')
        self.assertDictEqual(
            router.params,
            {'foo': 'foo', 'bar': 'bar', 'baz': 'baz'})
        self.assertDictEqual(
            router_b.params,
            {'foo': 'foo', 'bar': 'bar', 'baz': 'baz', 'id': 'id'})
        self.assertEqual(router.route, 'foo')
        self.assertEqual(router_b.route, 'bar')

    def test_match_clashing(self):
        """
        Should resolve clashing
        """
        self.tree.add(':foo/:bar/:baz', 'foo')
        self.tree.add(':foo/api/:baz', 'bar')
        router = self.tree.match('foo/bar/baz')
        router_b = self.tree.match('foo/api/baz')
        self.assertDictEqual(
            router.params,
            {'foo': 'foo', 'bar': 'bar', 'baz': 'baz'})
        self.assertDictEqual(
            router_b.params,
            {'foo': 'foo', 'baz': 'baz'})
        self.assertEqual(router.route, 'foo')
        self.assertEqual(router_b.route, 'bar')

    def test_match_clashing_backtracking(self):
        """
        Should resolve clashing by doing backtracking
        """
        # match will walk up to the "api" part then realize
        # it needs one more part and then fallback to the previous
        # matched path (ie: all variables)
        self.tree.add(':bar/:baz', 'foo')
        self.tree.add('api', 'bar')
        router = self.tree.match('bar/baz')
        router_b = self.tree.match('api/baz')
        self.assertDictEqual(
            router.params,
            {'bar': 'bar', 'baz': 'baz'})
        self.assertDictEqual(
            router_b.params,
            {'bar': 'api', 'baz': 'baz'})
        self.assertEqual(router.route, 'foo')
        self.assertEqual(router_b.route, 'foo')

    def test_match_clashing_backtracking_deeper(self):
        """
        Should resolve clashing by doing backtracking
        """
        self.tree.add(':foo/:bar/:baz', 'foo')
        self.tree.add('api/:bar/:baz', 'bar')
        self.tree.add('api/id', 'baz')
        router = self.tree.match('api/id/baz')
        self.assertDictEqual(
            router.params,
            {'bar': 'id', 'baz': 'baz'})
        self.assertEqual(router.route, 'bar')

    def test_match_clashing_last_part(self):
        """
        Should resolve clashing by doing backtracking
        """
        self.tree.add(':foo/last', 'foo')
        self.tree.add('api', 'baz')
        router = self.tree.match('api/last')
        self.assertDictEqual(
            router.params,
            {'foo': 'api'})
        self.assertEqual(router.route, 'foo')

    def test_match_clashing_missing_part(self):
        """
        Should resolve clashing by doing backtracking
        """
        self.tree.add('foo/bar/:baz', 'foo')
        self.tree.add(':foo/:bar', 'foo')
        router = self.tree.match('foo/bar')
        self.assertDictEqual(
            router.params,
            {'foo': 'foo', 'bar': 'bar'})
        self.assertEqual(router.route, 'foo')

    def test_match_not_found(self):
        """
        Should raise match error if there is no match
        """
        self.assertRaises(RouteTreeError, self.tree.match, 'foo')

    def test_match_not_found_missing_part(self):
        """
        Should raise match error if there is no match
        """
        self.tree.add(':foo/:bar/:baz', 'foo')
        self.assertRaises(RouteTreeError, self.tree.match, 'foo/bar')

    def test_match_case_sensitive(self):
        """
        Should be case sensitive (see HTTP URL spec)
        """
        self.tree.add('API', 'foo')
        router = self.tree.match('API')
        self.assertDictEqual(router.params, {})
        self.assertEqual(router.route, 'foo')
        self.assertRaises(RouteTreeError, self.tree.match, 'api')

    def test_match_bail_early_on_deeper_urls(self):
        """
        Should not bother matching URLs larger than the largest registered URL
        """
        self.tree.add('foo/bar/baz', 'foo')
        self.tree.match('foo/bar/baz')
        self.tree._max_depth = 0
        self.assertRaises(RouteTreeError, self.tree.match, 'foo/bar/baz')
        self.tree._max_depth = 1
        self.assertRaises(RouteTreeError, self.tree.match, 'foo/bar/baz')
        self.tree._max_depth = 10
        self.tree.match('foo/bar/baz')

    def test_normalize_urls(self):
        """
        Should not care about leading/trailing slashes
        """
        self.tree.add('/foo/bar/baz/', 'foo')
        router = self.tree.match('foo/bar/baz')
        self.assertDictEqual(router.params, {})
        self.assertEqual(router.route, 'foo')

        router = self.tree.match('/foo/bar/baz/')
        self.assertDictEqual(router.params, {})
        self.assertEqual(router.route, 'foo')

        router = self.tree.match('/foo/bar/baz')
        self.assertDictEqual(router.params, {})
        self.assertEqual(router.route, 'foo')

        router = self.tree.match('foo/bar/baz/')
        self.assertDictEqual(router.params, {})
        self.assertEqual(router.route, 'foo')

    def test_match_var_any(self):
        """
        Should match unknown number of URL parts
        """
        self.tree.add(':*path', 'foo')
        self.tree.add('static/:*path', 'bar')
        self.tree.add('static/:*path/sub-path', 'baz')
        self.tree.add('static/:*path/sub-path/:file_name', 'qux')

        router = self.tree.match('foo/bar/baz')
        self.assertDictEqual(router.params, {'path': ('foo', 'bar', 'baz')})
        self.assertEqual(router.route, 'foo')

        router = self.tree.match('static/foo/bar/baz')
        self.assertDictEqual(router.params, {'path': ('foo', 'bar', 'baz')})
        self.assertEqual(router.route, 'bar')

        router = self.tree.match('static/foo/bar/baz/sub-path')
        self.assertDictEqual(router.params, {'path': ('foo', 'bar', 'baz')})
        self.assertEqual(router.route, 'baz')

        router = self.tree.match('static/foo/bar/baz/sub-path/catz.jpg')
        self.assertDictEqual(router.params, {
            'file_name': 'catz.jpg',
            'path': ('foo', 'bar', 'baz')})
        self.assertEqual(router.route, 'qux')

    def test_match_var_any_many(self):
        """
        Should match multiple any vars
        """
        self.tree.add(':*path/:*path_a/:*patch_b', 'foo')
        router = self.tree.match('foo/bar/baz/qux')
        self.assertDictEqual(router.params, {
            'patch_b': ('baz', 'qux'), 'path': ('foo',), 'path_a': ('bar',)})
        self.assertEqual(router.route, 'foo')

    def test_match_var_any_precedence(self):
        """
        Should match in order: static > var > any-var
        """
        self.tree.add(':var1/:*path/:var2', 'foo')
        self.tree.add('static1/:*path/static2', 'bar')
        self.tree.add(':var1/:*path/static2', 'baz')
        self.tree.add('static2/:var1/:*path/:var2/:*path2', 'qux')

        # Never matches, since foo takes precedence
        self.tree.add(':*path/:var1/:*path2', 'bad')

        router = self.tree.match('foo/bar/baz/qux')
        self.assertDictEqual(router.params, {'path': ('bar', 'baz'), 'var2': 'qux', 'var1': 'foo'})
        self.assertEqual(router.route, 'foo')

        router = self.tree.match('static1/bar/baz/static2')
        self.assertDictEqual(router.params, {'path': ('bar', 'baz')})
        self.assertEqual(router.route, 'bar')

        router = self.tree.match('foo/bar/baz/static2')
        self.assertDictEqual(router.params, {'var1': 'foo', 'path': ('bar', 'baz')})
        self.assertEqual(router.route, 'baz')

        router = self.tree.match('static2/foo/bar/baz/qux')
        self.assertDictEqual(router.params, {
            'var1': 'foo', 'path': ('bar',), 'var2': 'baz', 'path2': ('qux',)})
        self.assertEqual(router.route, 'qux')

    def test_max_depth(self):
        """
        Should not match on max_depth < url length
        """
        rts = RouteTree(max_depth=3)
        rts.add(':*path', 'foo')
        self.assertEqual(rts.match('foo/bar/baz').route, 'foo')

        rts = RouteTree(max_depth=1)
        rts.add(':*path', 'foo')
        self.assertRaises(RouteTreeError, rts.match, 'foo/bar/baz')

        # Changes max_depth
        rts.add(':var/bar/baz', 'bar')
        self.assertEqual(rts.match('foo/bar/baz').route, 'bar')

    def test_match_custom_separator(self):
        """
        Should match an url to a registered pattern given a custom separator
        """
        self.tree.separator = '.'
        self.tree.add(':foo.:bar.api.:baz', 'foo')
        router = self.tree.match('foo.bar.api.baz')
        self.assertDictEqual(
            router.params,
            {'foo': 'foo', 'bar': 'bar', 'baz': 'baz'})
        self.assertEqual(router.route, 'foo')