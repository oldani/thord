from thord.router import Route, Router


def test_route_regex():
    route = Route("/user/{id}/photo/{name}")

    assert route._regex.pattern == r"^/user/(?P<id>[^/]+?)/photo/(?P<name>[^/]+?)$"


def test_route_hash():
    route = Route("/user/{id}")
    route2 = Route("/user/{id}")
    assert hash(route) == hash(route2)


def test_route_match():
    route = Route("/user")
    assert route.match("/user") == True


def test_route_match_params():
    route = Route("/user/{id}")
    assert route.match("/user/1") == {"id": "1"}


def test_route_nomatch():
    route = Route("/user")
    assert route.match("/user/somethign") == None


def test_router_add():
    router = Router()

    handler = lambda x: x
    router.add_route("/user", handler)

    route = Route("/user")
    assert route in router.routes
    assert router.routes[route] == handler


def test_router_get():
    router = Router()

    handler = lambda x: x
    router.add_route("/user", handler)
    router.add_route("/user/{id}", handler)

    assert router.get("/user") == (handler, {})
    assert router.get("/user/1") == (handler, {"id": "1"})
    assert router.get("/photo") == (None, {})
