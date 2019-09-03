""" Masonite Radix Tree Router

Special thanks to: Richard Kuesters and the XRTR project. (https://github.com/vltr/xrtr)
"""
import re
from string import punctuation

from masonite.exceptions import RouterError, InvalidRouteCompileException

GLOB = "*"
SENTINEL = object()


def get_position(i, n):
    """Return position

    Arguments:
        i {int}
        n {int}
    Returns:
        position {int}
    """
    if i == -1:
        return n
    return i


class RouteTreeNode:
    __slots__ = (
        "path_len",
        "path",
        "methods",
        "no_conflict_methods",
        "children",
        "indices",
        "indices_len",
        "optimized_index",
        "index_zero_is_variable",
        "index_zero_is_glob",
    )

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
        return '<RouteTreeNode path: {}, methods: {}, indices: "{}", children: ' "{}>".format(
            '"{}"'.format(self.path) if self.path else "None", self.methods, self.indices, self.children
        )

    def add_methods(self, methods, handler, no_conflict=False):
        """Add methods

        Arguments:
            root {RouteTreeNode} -- Tree node
            method {str} -- HTTP methods

        Keyword Arguments:
            no_conflict {bool} -- Used when wanting to associate extra objects to a route

        Returns:
            None

        Raises:
            KeyError -- Arises when there is a conflicting handler
        """
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
                    raise KeyError("{} conflicts with existing handler " "{}".format(handler, self.methods[method]))

                self.methods[method] = handler

    def insert_child(self, index, child):
        """Wrapper for insert child method

        Arguments:
            index {str} -- Index where child should be inserted
            child {RouteTreeNode} -- Child node

        Returns:
            child {RouteTreeNode} -- Child node
        """
        return self._insert_child(index, child)

    def _insert_child(self, index, child):
        """Insert object into tree

        Arguments:
            index {str} -- Index where child should be inserted
            child {RouteTreeNode} -- Child node

        Returns:
            child {RouteTreeNode} -- Child node
        """
        pos = self.get_index_position(index)
        self.indices = self.indices[:pos] + index + self.indices[pos:]
        self.indices_len = len(self.indices)
        self.children.insert(pos, child)
        return child

    def get_index_position(self, index):
        """Get index

        Arguments:
            index {str} -- Index of child node

        Returns:
            position {int} -- Position of child node
        """
        return get_position(self.indices.find(index), 0)

    def get_child(self, index):
        """Get child

        Arguments:
            index {str} -- Index of child node

        Returns:
            child {RouteTreeNode} -- Child Node
        """
        i = self.get_index_position(index)
        if i < self.indices_len and self.indices[i] == index:
            return self.children[i]

    def optimize(self, tree):
        """Optimize tree

        Radix trees can take up a lot of memory. Optimization occurs so that
        the tree can be compressed and use less RAM.

        Arguments:
            tree {Router} -- Route Tree

        Returns:
            None
        """

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
        """Get value from optimized tree

        Arguments:
            index {str} -- Index of child node

        Returns:
            child {RouteTreeNode} -- Child Node
        """
        return self.optimized_index.get(index)


class Router:
    _VARIABLE = ""
    _SEPARATOR = ""

    def __init__(self, variable=None, separator=None):
        self.root = RouteTreeNode()
        self.VARIABLE = variable or "@"
        self.SEPARATOR = separator or "/"
        self._VAR_PATTERN = re.compile(r"(?:[{}\*])([a-zA-Z0-9\_]+)".format(re.escape(self._VARIABLE)))
        self._compilers = dict()

    def __repr__(self):
        return repr(self.root)

    @property
    def compilers(self):
        """Get route compilers associated with the tree

        Returns:
            compilers {dict} -- Route compilers
        """
        return self._compilers

    @compilers.setter
    def compilers(self, value):
        """Add route compilers

        Arguments:
            value {dict} -- Route compilers

        Returns:
            None
        """
        if not self._compilers:
            self._compilers = value
        else:
            # If we already have compilers, extend our collection of compilers.
            self._compilers = {**self._compilers, **value}

        for key, value in self._compilers.items():
            self._compilers[key] = re.compile(value)

    @property
    def config(self):
        """Config for route tree

        Returns:
            config {dict} -- Reserved characters for route tree
        """
        return {"variable": self.VARIABLE, "separator": self.SEPARATOR}

    @property
    def SEPARATOR(self):
        """Return separator character

        Returns:
            separator {str} -- character used to parse URI
        """
        return self._SEPARATOR

    @SEPARATOR.setter
    def SEPARATOR(self, value):
        """Set seperator character

        Arguments:
            separator {str} -- character used to parse URI

        Returns:
            None
        """
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
        """Return variable character

        Returns:
            variable {str} -- character used to declare varaiable in URI
        """
        return self._VARIABLE

    @VARIABLE.setter
    def VARIABLE(self, value):
        """ Set variable character

        Arguments:
            variable {str} -- character used to declare varaiable in URI

        Returns:
            None
        """
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
        """Return sentinel value

        This is used to determine if route is found or not.
        """
        return SENTINEL

    def insert(self, path, handler, methods, no_conflict=False):
        """ Wrapper for insert a route into tree

        Arguments:
            path {str} -- URI path
            handler {object} -- Handler associated with route
            methods {list} -- HTTP Methods

        Keyword Arguments:
            no_conflict {bool} -- Used when wanting to associate extra objects to a route

        Returns:
            None

        Raises:
            ValueError -- Raised for invalid pahs, duplicate variable names, or path conflicts
        """
        # Suppress error when subdomain
        if "./" in path:
            split = path.split(".")
            if len(split) > 2:
                raise ValueError("path cannot be None, empty or invalid")
        else:
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
        """Traverse tree

        Arguments:
            root {RouteTreeNode} -- Tree node

        Returns:
            retval {list} -- Parts of URI
        """
        retval = list()
        child = RouteTreeNode()

        if len(root.indices) != 0:
            for i, c in enumerate(root.indices):
                child = root.children[i]
                path = "{}{}".format(c if c in [self._VARIABLE, GLOB] else "", child.path)

                if child.methods and child.indices:
                    retval.append(path)

                retval.extend([path + p for p in self.traverse(child) or [""]])
        return retval

    def _c_insert(self, path, handler, methods, no_conflict):
        """Insert route into tree

        Arguments:
            path {str} -- URI path
            handler {object} -- Handler associated with route
            methods {list} -- HTTP Methods
            no_conflict {bool} -- Used when wanting to associate extra objects to a route

        Returns:
            retval {tuple} -- Response from insertion

        Raises:
            ValueError -- Raised for invalid pahs, duplicate variable names, or path conflicts
        """
        i = 0
        n = len(path)
        code = 0
        root = self.root

        while i < n:
            if not no_conflict:
                if len(root.indices) != 0 and (
                    root.indices[0] == GLOB
                    or path[i] == GLOB
                    and len(root.indices) != 0
                    or path[i] != self._VARIABLE
                    and root.indices[0] == self._VARIABLE
                    or path[i] == self._VARIABLE
                    and root.indices[0] != self._VARIABLE
                    or path[i] == self._VARIABLE
                    and root.indices[0] == self._VARIABLE
                    and path[i + 1 : get_position(self._findinstr(path, self._SEPARATOR, i), n)]
                    != root.children[0].path
                ):

                    return i, root

            child = root.get_child(path[i])

            if child is None:
                p = get_position(path.find(self._VARIABLE, i), n)
                if p == n:
                    p = get_position(path.find(GLOB, i), n)
                    if p == n:
                        root.insert_child(path[i], RouteTreeNode(path[i:], handler, methods, no_conflict))
                        return code, None

                    root = root.insert_child(path[i], RouteTreeNode(path[i:p]))
                    root.insert_child(GLOB, RouteTreeNode(path[p + 1 :], handler, methods, no_conflict))
                    return code, None

                root = root.insert_child(path[i], RouteTreeNode(path[i:p]))
                i = get_position(path.find(self._SEPARATOR, p), n)
                root = root.insert_child(self._VARIABLE, RouteTreeNode(path[p + 1 : i]))

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
        """Wrapper for get route

        Arguments:
            path {str} -- URI path
            method {str} -- HTTP method

        Returns:
            handler {object} -- Handler associated with route
            nc_handlers {list}  -- List of no-conflict handlers
            params {dict} -- URL params
        """
        # Check if there are more than period
        if "./" in path:
            split = path.split(".")
            if len(split) > 2:
                raise RouterError("Invalid path")

        params = dict()
        handler, nc_handlers = self._c_get(path, method, params)
        if handler is None:
            return None, list(), dict()
        elif handler == SENTINEL:
            return SENTINEL, list(), dict()
        return handler, nc_handlers, params

    def _c_get(self, path, method, params):
        """Get route

        Arguments:
            path {str} -- URI path
            method {str} -- HTTP method
            params {dict} -- URL params

        Returns:
            handler {object} -- Handler associated with route
            nc_handlers {list}  -- List of no-conflict handlers

        Raises:
            RouterError -- Failed to match route
        """
        i = 0
        n = len(path)
        handler = None
        nc_handlers = list()

        root = self.root

        while i < n:
            if root.indices_len == 0:
                return None, None

            nc_handlers = self._append_no_conflict_handlers_if_any(root, method, nc_handlers)

            if root.index_zero_is_variable:
                root = root.children[0]
                pos = get_position(self._findinstr(path, self._SEPARATOR, i), n)
                # Specifc param is assigned
                path_parts = root.path.split(":")
                param = path[i:pos]

                # Check route compile
                if len(path_parts) > 1:
                    route = root.methods.get(method)
                    compiler = self._compilers.get(path_parts[1])
                    if not compiler:
                        raise InvalidRouteCompileException(f"Compiler not found")
                    matched = compiler.match(param)
                    if not matched:
                        raise InvalidRouteCompileException(f"'{param}' failed to match route compiler: {path_parts[1]}")

                params[path_parts[0]] = param
                i = pos

            elif root.index_zero_is_glob:
                root = root.children[0]
                # glob variables are assigned
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

        nc_handlers = self._append_no_conflict_handlers_if_any(root, method, nc_handlers)

        return root.methods.get(method), nc_handlers

    def methods_for(self, path):
        """Wrapper for finding methods for a path

        Arguments:
            path {str} -- URI path

        Returns:
            methods {set} -- Set of HTTP methods
        """
        methods = self._c_methods_for(path)
        return set() if methods is None else methods

    def _c_methods_for(self, path):
        """Find methods for a path

        Arguments:
            path {str} -- URI path

        Returns:
            methods {set} -- Set of HTTP methods
        """
        i = 0
        n = len(path)

        root = self.root

        while i < n:
            if root.indices_len == 0:
                return None

            if root.index_zero_is_variable:
                root = root.children[0]
                pos = get_position(self._findinstr(path, self._SEPARATOR, i), n)
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

    @staticmethod
    def _append_no_conflict_handlers_if_any(root, method, nc_handlers):
        """Append no-conflict handers

        Arguments:
            root {RouteTreeNode} -- Tree node
            method {str} -- HTTP methods
            nc_handlers {list}  -- List of no-conflict handlers

        Returns:
            nc_handlers {list}  -- List of no-conflict handlers
        """
        if root.no_conflict_methods.__contains__(method):
            nc_handlers.extend(root.no_conflict_methods[method])
        return nc_handlers

    @staticmethod
    def _findinstr(source, word, start):
        """Helper function to find word in string

        Arguments:
            source {str} -- Text to search against
            word {str} -- -- Text to search
            start {int} -- Index to start search
        """
        return source.find(word, start)
