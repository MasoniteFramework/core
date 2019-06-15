""" Route Tree """

from .exceptions import RouteTreeError


class RouteNode:
    __slots__ = ["key_parts", "anything"]

    def __init__(self, key_parts, anything):
        """
        Route Node

        Arguments:
            key_parts {dict} -- Pattern variables to URL parts
            anything {object} -- Literally anything. This is attached to the
                URL pattern when registering it.
        """
        self.key_parts = key_parts
        self.anything = anything


class RouteResolved:
    __slots__ = ["params", "anything"]

    def __init__(self, params, anything):
        """
        Resolved route

        Arguments:
            params {dict} -- Pattern variables to URL parts
            anything {object} -- Literally anything. This is attached to the
                URL pattern when registering it.
        """
        self.params = params
        self.anything = anything


class RouteTree:
    """
    Route URLs to registered URL patterns.

    Thread safety: adding routes is not thread-safe,
    it should be done on import time, everything else is.

    URL matcher supports ``:var`` for matching dynamic
    path parts and ``:*var`` for matching one or more parts.

    Path parts are matched in the following order: ``static > var > any-var``.
    """

    _VAR_NODE = ":var"
    _VAR_ANY_NODE = ":*var"
    _ROUTE_NODE = ":route"

    _VAR_ANY_BREAK = ":*break"

    def __init__(self, max_depth: int = 40):
        self._max_depth_custom = max_depth  # The maximum URL depth
        self._routes = {}
        self._max_depth = 0

    def _deconstruct_url(self, url: str):
        """
        Split a regular URL into parts

        Arguments:
            url {string} -- A normalized URL
        
        Returns:
            parts {list} -- Parts of the URL

        Raises:
            {masonite.exceptions.RouteTreeError} -- If the depth of the URL exceeds
            the max depth of the deepest registered pattern.
        """
        parts = url.split("/", self._max_depth + 1)

        if self.depth_of(parts) > self._max_depth:
            raise RouteTreeError("No match")

        return parts

    def _match(self, parts):
        """
        Match URL parts to a registered pattern.

        This function is basically where all
        the CPU-heavy work is done.

        Arguments:
            parts {list} -- URL parts

        Returns:
            {RouteResolved} -- Matched route

        Raises: 
            {masonite.exceptions.RouteTreeError} -- If there is no match
        """
        route_match = None
        route_variable_parts = tuple()
        to_visit = [(self._routes, tuple(), 0)]  # (route_partial, variable_parts, depth)

        # Walk through the graph, and keep track of all possible
        # matching branches. Do backtracking if needed.
        while to_visit:
            curr, curr_variable_parts, depth = to_visit.pop()

            try:
                part = parts[depth]
            except IndexError:
                if self._ROUTE_NODE in curr:
                    route_match = curr[self._ROUTE_NODE]
                    route_variable_parts = curr_variable_parts
                    break
                else:
                    continue

            if self._VAR_ANY_NODE in curr:
                to_visit.append(
                    (
                        {self._VAR_ANY_NODE: curr[self._VAR_ANY_NODE]},
                        (curr_variable_parts, (self._VAR_ANY_NODE, part)),
                        depth + 1,
                    )
                )
                to_visit.append(
                    (curr[self._VAR_ANY_NODE], (curr_variable_parts, (self._VAR_ANY_BREAK, part)), depth + 1)
                )

            if self._VAR_NODE in curr:
                to_visit.append((curr[self._VAR_NODE], (curr_variable_parts, (self._VAR_NODE, part)), depth + 1))

            if part in curr:
                to_visit.append((curr[part], curr_variable_parts, depth + 1))

        if not route_match:
            raise RouteTreeError("No match")

        return RouteResolved(
            params=self.make_params(key_parts=route_match.key_parts, variable_parts=route_variable_parts),
            anything=route_match.anything,
        )

    def match(self, url):
        """
        Match a URL to a registered pattern.

        Arguments:
            parts {list} -- URL parts

        Returns:
            {RouteResolved} -- Matched route

        Raises: 
            {masonite.exceptions.RouteTreeError} -- If there is no match
        """
        url = self.normalize_url(url)
        parts = self._deconstruct_url(url)
        return self._match(parts)

    def add(self, url, anything):
        """ Register a URL pattern into the routes for later matching.

        It's possible to attach any kind of object to the pattern for later
        retrieving. A dict with methods and callbacks, for example. Anything really.

        Registration order does not matter.
        Adding a URL first or last makes no difference.

        Arguments:
            url {string} -- URL
            anything {Any} -- Literally anything.
        
        Returns:
            None
        """
        url = self.normalize_url(url)
        parts = url.split("/")
        curr_partial_routes = self._routes
        curr_key_parts = list()

        for part in parts:
            if part.startswith(":*"):
                curr_key_parts.append(part[2:])
                part = self._VAR_ANY_NODE
                self._max_depth = self._max_depth_custom

            elif part.startswith(":"):
                curr_key_parts.append(part[1:])
                part = self._VAR_NODE

            curr_partial_routes = curr_partial_routes.setdefault(part, {})

        curr_partial_routes[self._ROUTE_NODE] = RouteNode(key_parts=curr_key_parts, anything=anything)

        self._max_depth = max(self._max_depth, self.depth_of(parts))

    def make_params(self, key_parts, variable_parts):
        """
        Map keys to variables.
        
        This map URL-pattern variables to a URL related parts

        Arguments:
            key_parts {list} -- A list of URL parts
            variable_parts {VariablePartsType} -- Nested tuples of URL parts

        Returns:
            {ParameterDictType} -- The param dict with the values assigned to the keys
        """
        # The unwrapped variable parts are in reverse order.
        # Instead of reversing those we reverse the key parts
        # and avoid the O(n) space required for reversing the vars
        return dict(zip(reversed(key_parts), self._unwrap(variable_parts)))

    @staticmethod
    def depth_of(parts):
        """
        Calculate the depth of URL parts

        Arguments:
            parts {list} -- A list of URL parts
        
        Returns:
            {int} -- Depth of the list
        """
        return len(parts) - 1

    def _unwrap(self, variable_parts):
        """
        Yield URL parts. The given parts are usually in reverse order.

        Arguments:
            variable_parts {VariablePartsType} -- parts of url
        
        Returns:
            variable_parts {VariablePartsType} -- parts of url 
        """
        curr_parts = variable_parts
        var_any = list()

        while curr_parts:
            curr_parts, (var_type, part) = curr_parts

            if var_type == self._VAR_ANY_NODE:
                var_any.append(part)
                continue

            if var_type == self._VAR_ANY_BREAK:
                if var_any:
                    yield tuple(reversed(var_any))
                    var_any.clear()

                var_any.append(part)
                continue

            if var_any:
                yield tuple(reversed(var_any))
                var_any.clear()
                yield part
                continue

            yield part

        if var_any:
            yield tuple(reversed(var_any))

    @staticmethod
    def normalize_url(url: str) -> str:
        """
        Remove leading and trailing slashes from a URL

        Arguments:
            url {string} -- URL
        
        Return:
            url {string} -- URL with no leading and trailing slashes
        """
        if url.startswith("/"):
            url = url[1:]

        if url.endswith("/"):
            url = url[:-1]

        return url
