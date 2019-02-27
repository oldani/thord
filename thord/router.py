import re
from functools import lru_cache

from thord.types import Union, Callable, Tuple


class Route:
    _pattern = re.compile("{([^{}]*)}")

    def __init__(self, route: str) -> None:
        self._route = route
        self.setup_route()

    def __eq__(self, other):
        if isinstance(other, Route):
            return self._route == other._route
        else:
            return self.match(other)

    def __hash__(self):  # To allow dict storage
        return hash(self._regex)

    def setup_route(self) -> None:
        """ Create a regex for matching incoming routes.
            _pattern: is a regex for matching {fields} in views patterns.
            _pattner.sub calls Route.replace_field in each field match
                and replace it for group capturing rx. 
                E.g:
                    /test/{id} will be compile to ^/test/(?P<id>[^/]+?)$ 
        """
        self._regex = re.compile(
            f"^{self._pattern.sub(self.replace_field, self._route)}$"
        )

    @staticmethod
    def replace_field(match) -> str:
        """ Takes field name and put in inside a regex group. """
        return f"(?P<{match.group(1)}>[^/]+?)"

    def match(self, path: str) -> Union[dict, bool, None]:
        """ Match a path with this routes.
            @return:
                - dict {field: value} for routes with fields. E.g:
                    route: /user/{id} will return {id: 1}
                - True if matched but no field
                - None for no matches.
        """
        result = self._regex.match(path)
        if result:
            return result.groupdict() or True
        return None


class Router:
    def __init__(self) -> None:
        self.routes: dict = {}

    def add_route(self, pattern: str, handler: Callable) -> None:
        """ Create Route obj and store in a dict as the key for a given handler. """
        self.routes[Route(pattern)] = handler

    @lru_cache(maxsize=65536)  # If we already saw this path cache it
    def get(self, path: str) -> Tuple[Union[Callable, None], dict]:
        """ Retrieve view and params (if any) for a given path. """
        _view, params = None, {}
        for route, view in self.routes.items():
            match = route.match(path)
            if not match:
                continue
            if match and isinstance(match, dict):  # Means route have parameters
                _view, params = view, match
            else:
                _view = view
            break
        return _view, params
