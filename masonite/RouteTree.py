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

import re
from string import punctuation


GLOB = '*'
SENTINEL = object()


def _get_position(i, n):
    if i == -1:
        return n
    return i


def _findinstr(source, word, start):
    return source.find(word, start)


def _append_no_conflict_handlers_if_any(root, method, nc_handlers):
    if root.no_conflict_methods.__contains__(method):
        nc_handlers.extend(root.no_conflict_methods[method])

class RouteTreeNode:

    def __init__(self, path=None, handler=None, methods=None, no_conflict=False):
        self.path_len = len(path) if path else 0
        self.path = path
        self.methods = dict()
        self.no_conflict_methods = dict()
        self.children = list()
        self.indices = ""
        self.indices_len = 0
        self.optimized_index = dict()
        self.index_zero_is_variable = 0
        self.index_zero_is_glob = 0

        if handler and methods:
            self.add_methods(methods, handler, no_conflict)

    def __repr__(self):
        return (
            "<RouteTreeNode path: {}, methods: {}, indices: \"{}\", children: "
            "{}>".format(
                "\"{}\"".format(self.path) if self.path else "None",
                self.methods,
                self.indices,
                self.children
            )
        )

    def add_methods(self, methods, handler, no_conflict=False):
        if not methods:
            return

        if no_conflict:
            for method in methods:
                if method in self.no_conflict_methods and handler in self.no_conflict_methods[method]:
                    continue

                if method in self.no_conflict_methods:
                    self.no_conflict_methods[method].append(handler)
                else:
                    self.no_conflict_methods[method] = [handler]
        else:
            for method in methods:
                if method in self.methods and self.methods[method] != handler:
                    raise KeyError(
                        "{} conflicts with existing handler "
                        "{}".format(handler, self.methods[method])
                    )

                self.methods[method] = handler

    def insert_child(self, index, child):
        return self._insert_child(index, child)

    def _insert_child(self, index, child):
        pos = self.get_index_position(index)
        self.indices = self.indices[:pos] + index + self.indices[pos:]
        self.indices_len = len(self.indices)
        self.children.insert(pos, child)
        return child

    def get_index_position(self, index):
        return _get_position(self.indices.find(index), 0)

    def get_child(self, index):
        i = self.get_index_position(index)
        if i < self.indices_len and self.indices[i] == index:
            return self.children[i]

    def optimize(self, tree):

        self.optimized_index.clear()  # if not already clean

        for index in self.indices:
            self.optimized_index[index] = self.get_child(index)

        if self.indices_len > 0:
            self.index_zero_is_variable = self.indices[0] == tree.VARIABLE
            self.index_zero_is_glob = self.indices[0] == GLOB
        else:
            self.index_zero_is_variable = 0
            self.index_zero_is_glob = 0

        for child in self.children:
            child.optimize(tree)

    def get_child_optimized(self, index):
        return self.optimized_index.get(index)


class RouteTree:
    _VARIABLE = ""
    _SEPARATOR = ""

    def __init__(self, variable=None, separator=None):
        self.root = RouteTreeNode()
        self.VARIABLE = variable or '@'
        self.SEPARATOR = separator or '/'
        self._VAR_PATTERN = re.compile(r"(?:[{}\*])([a-zA-Z0-9\_]+)".format(re.escape(self._VARIABLE)))

    def __repr__(self):
        return repr(self.root)

    @property
    def config(self):
        return {
            'variable': self.VARIABLE,
            'separator': self.SEPARATOR
        }

    @property
    def SEPARATOR(self):
        return self._SEPARATOR

    @SEPARATOR.setter
    def SEPARATOR(self, value):
        if self.root.children:
            raise ValueError("You can't change the separator character after routes have been inserted")
        if value is not None and value in punctuation and len(value) == 1:
            if value == self._VARIABLE:
                raise ValueError("The separator character must not equal the variable character")
            self._SEPARATOR = value
        else:
            raise ValueError("The separator character must be of length one and a valid punctuation")

    @property
    def VARIABLE(self):
        return self._VARIABLE

    @VARIABLE.setter
    def VARIABLE(self, value):
        if self.root.children:
            raise ValueError("You can't change the variable character after routes have been inserted")
        if value is not None and value in punctuation and len(value) == 1:
            if value == self._SEPARATOR:
                raise ValueError("The variable character must not equal the separator character")
            self._VARIABLE = value
        else:
            raise ValueError("The variable character must be of length one and a valid punctuation")

    @property
    def sentinel(self):
        return SENTINEL

    def insert(self, path, handler, methods, no_conflict=False):
        if path is None or len(path.strip()) == 0 or path.strip()[0] != self._SEPARATOR:
            raise ValueError("path cannot be None, empty or invalid")

        parts = path.strip(self.SEPARATOR).split(self.SEPARATOR)
        matches = [self._VAR_PATTERN.match(p) for p in parts]
        all_matches = [m.group(1) for m in matches if m is not None]

        if len(all_matches) != len(set(all_matches)):
            raise ValueError('"{}" has at least one duplicate variable name'.format(path))

        i, node = self._c_insert(path, handler, methods, no_conflict)

        if node is not None:
            conflict = [path[:i] + p for p in self.traverse(node)]
            raise ValueError('"{}" conflicts with {}'.format(path, conflict))

        self.root.optimize(self)

    def traverse(self, root):
        r = list()
        child = RouteTreeNode()

        if len(root.indices) != 0:
            for i, c in enumerate(root.indices):
                child = root.children[i]
                path = "{}{}".format(c if c in [self._VARIABLE, GLOB] else "", child.path)

                if child.methods and child.indices:
                    r.append(path)

                r.extend([path + p for p in self.traverse(child) or [""]])
        return r

    def _c_insert(self, path, handler, methods, no_conflict):
        i = 0
        n = len(path)
        code = 0        
        root = self.root

        while i < n:
            if not no_conflict:
                if len(root.indices) != 0 and (root.indices[0] == GLOB or
                    path[i] == GLOB and len(root.indices) != 0 or
                    path[i] != self._VARIABLE and root.indices[0] == self._VARIABLE or
                    path[i] == self._VARIABLE and root.indices[0] != self._VARIABLE or
                    path[i] == self._VARIABLE and root.indices[0] == self._VARIABLE and
                    path[i + 1: _get_position(_findinstr(path, self._SEPARATOR, i), n)] != root.children[0].path):

                    return i, root

            child = root.get_child(path[i])

            if child is None:
                p = _get_position(path.find(self._VARIABLE, i), n)
                if p == n:
                    p = _get_position(path.find(GLOB, i), n)
                    if p == n:
                        root.insert_child(path[i], RouteTreeNode(path[i:], handler, methods, no_conflict))
                        return code, None

                    root = root.insert_child(path[i], RouteTreeNode(path[i:p]))
                    root.insert_child(GLOB, RouteTreeNode(path[p + 1:], handler, methods, no_conflict))
                    return code, None

                root = root.insert_child(path[i], RouteTreeNode(path[i:p]))
                i = _get_position(path.find(self._SEPARATOR, p), n)
                root = root.insert_child(self._VARIABLE, RouteTreeNode(path[p + 1: i]))

                if i == n:
                    root.add_methods(methods, handler, no_conflict)
            else:
                root = child
                if path[i] == self._VARIABLE:
                    i += len(root.path) + 1
                    if i == n:
                        root.add_methods(methods, handler, no_conflict)
                else:
                    j = 0
                    m = len(root.path)

                    while i < n and j < m and path[i] == root.path[j]:
                        i += 1
                        j += 1

                    if j < m:
                        child = RouteTreeNode(root.path[j:])
                        child.methods = root.methods
                        child.no_conflict_methods = root.no_conflict_methods
                        child.children = root.children
                        child.indices = root.indices
                        child.indices_len = len(child.indices)

                        root.path = root.path[:j]
                        root.path_len = len(root.path)
                        root.methods = {}
                        root.no_conflict_methods = {}
                        root.children = [child]
                        root.indices = child.path[0]
                        root.indices_len = len(root.indices)

                    if i == n:
                        root.add_methods(methods, handler, no_conflict)

        return code, None

    def get(self, path, method):
        params = {}

        handler, nc_handlers = self._c_get(path, method, params)
        if handler is None:
            return None, [], {}
        elif handler == SENTINEL:
            return SENTINEL, [], {}
        return handler, nc_handlers, params

    def _c_get(self, path, method, params):
        i = 0
        n = len(path)
        handler = None
        nc_handlers = []

        root = self.root

        while i < n:
            if root.indices_len == 0:
                return None, None

            _append_no_conflict_handlers_if_any(root, method, nc_handlers)

            if root.index_zero_is_variable:
                root = root.children[0]
                pos = _get_position(_findinstr(path, self._SEPARATOR, i), n)
                params[root.path] = path[i:pos]
                i = pos

            elif root.index_zero_is_glob:
                root = root.children[0]
                params[root.path] = path[i:]
                break
            else:
                root = root.get_child_optimized(path[i])

                if root is None:
                    return None, None

                pos = i + root.path_len

                if path[i:pos] != root.path:
                    return None, None

                i = pos

        handler = root.methods.get(method)

        if handler is None:
            if root.methods:
                return SENTINEL, None
            return None, None

        _append_no_conflict_handlers_if_any(root, method, nc_handlers)

        return root.methods.get(method), nc_handlers

    def methods_for(self, path):
        methods = self._c_methods_for(path)
        return set() if methods is None else methods

    def _c_methods_for(self, path):
        i = 0
        n = len(path)

        root = self.root

        while i < n:
            if root.indices_len == 0:
                return None

            if root.index_zero_is_variable:
                root = root.children[0]
                pos = _get_position(_findinstr(path, self._SEPARATOR, i), n)
                i = pos

            elif root.index_zero_is_glob:
                root = root.children[0]
                break
            else:
                root = root.get_child_optimized(path[i])

                if root is None:
                    return None

                pos = i + root.path_len

                if path[i:pos] != root.path:
                    return None

                i = pos

        return set(root.methods.keys())
