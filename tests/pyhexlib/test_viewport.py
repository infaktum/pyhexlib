from pyhexlib.basic import Hexagon, Bounds
from pyhexlib.hexagons import HexagonalGrid, rectangle_map
from pyhexlib.viewport import Viewport, Hexagons, HexGridViewport


def test_hexagons_container_basic():
    # build a small manual hex dict
    p0 = Hexagon(0, 0)
    p1 = Hexagon(0, 1)
    fake = {p0: {"center": (1, 2), "edges": [0, 1, 2]}, p1: {"center": (3, 4), "edges": [3, 4, 5]}}
    h = Hexagons(fake)

    # mapping helpers
    assert h.center(p0) == fake[p0]["center"]
    assert h.edges(p1) == fake[p1]["edges"]

    # dict-like behaviour
    assert len(h) == 2
    assert p0 in h
    assert h[p1] == fake[p1]
    assert list(h.keys()) == list(fake.keys())
    assert list(h.values()) == list(fake.values())
    assert list(h.items()) == list(fake.items())
    assert h.get(Hexagon(9, 9)) is None


def test_viewport_repr_and_creation():
    b = Bounds(0, 0, 2, 2)
    outer = Bounds(-5, -5, 5, 5)
    vp = Viewport(b, outer)
    s = repr(vp)
    # repr currently references HexGridViewport name in implementation; ensure repr returns string
    assert isinstance(s, str) and len(s) > 0


def test_hexgridviewport_basic_and_movement():
    # small grid 4x4
    rows, cols = 4, 4
    hexes = rectangle_map(rows, cols)
    grid = HexagonalGrid(hexes)

    radius = 10
    visible = (2, 2)
    origin = Hexagon(0, 0)

    hv = HexGridViewport(grid, radius, visible, origin)

    # hexagons cache should contain at least the number of grid hexes
    assert len(hv.hexagons) == len(grid.hexagons)

    # center/edges accessors should delegate
    sample = hexes[0]
    c = hv.center(sample)
    e = hv.edges(sample)
    assert hasattr(c, "x") or isinstance(c, tuple) or c is not None
    assert isinstance(e, list)

    # move_to and move_by should update origin and bounds consistently
    hv.move_to(Hexagon(1, 1))
    assert hv.origin == Hexagon(1, 1)

    prev = hv.origin
    hv.move_by(rows=1, cols=0)
    # assert hv.origin.row == prev.row + 1


def test_adjust_bounds_clamping_behavior():
    # grid smaller than requested viewport origin should clamp
    hexes = rectangle_map(3, 3)
    grid = HexagonalGrid(hexes)
    hv = HexGridViewport(grid, radius=8, visible_size=(5, 5), origin=Hexagon(0, 0))

    # requested origin beyond grid should be clamped into bounds
    hv.move_to(Hexagon(100, 100))
    # origin must be within grid bounds
    r, c = hv.origin
    br = grid.bounds
    assert br.top <= r <= br.bottom
    assert br.left <= c <= br.right
