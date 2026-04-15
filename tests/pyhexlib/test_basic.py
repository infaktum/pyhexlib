import pytest

import pyhexlib
from pyhexlib.basic import (
    Hexagon2,
    Bounds,
    offset_to_axial,
    axial_to_offset,
    axial_to_cube,
    axial_coordinates,
    neighborhood_basic,
    get_direction,
    distance,
    distance_axial,
    distance_axial_with_cube,
    dijkstra,
    astar,
    Orientation,
)


def test_hexagon2_pack_unpack_and_immutable():
    h = Hexagon2(1, 2)
    # iterable and length
    assert tuple(h) == (1, 2)
    assert len(h) == 2
    # indexing
    assert h[0] == 1
    assert h[1] == 2
    # frozen dataclass -> cannot assign
    with pytest.raises(Exception):
        h.row = 5


def test_bounds_properties_and_indexing():
    b = Bounds(top=0, left=0, bottom=2, right=3)
    assert b.topleft == (0, 0)
    assert b.bottomright == (2, 3)
    # size is bottom-top, right-left
    assert b.size == (2, 3)
    assert b.contains((1, 1)) is True
    assert b.contains((3, 0)) is False
    # iteration and indexing
    assert tuple(b) == (0, 0, 2, 3)
    assert b[0] == 0 and b[1] == 0 and b[2] == 2 and b[3] == 3


def test_coordinate_conversions_and_mappings():
    pyhexlib.init(orientation=Orientation.FLAT)
    # roundtrip offset <-> axial for a few samples
    samples = [(0, 0), (1, 0), (0, 1), (-2, 3)]
    for row, col in samples:
        ax = offset_to_axial(row, col)
        back = axial_to_offset(ax[0], ax[1])
        assert back == (row, col)

    # axial -> cube
    ax = (2, 1)
    x, y, z = axial_to_cube(ax)
    r, q = ax
    assert x == q and z == r and y == -x - z

    # axial_coordinates mapping
    hexes = [(0, 0), (1, 0), (2, 1)]
    mapping = axial_coordinates(hexes)
    for rc in hexes:
        assert mapping[rc] == offset_to_axial(rc[0], rc[1])


def test_neighborhood_basic_and_get_direction_and_distance():
    pyhexlib.init(orientation=Orientation.FLAT)
    # neighborhood_basic returns 6 offsets for a regular hex
    nb = neighborhood_basic(0, 0)
    assert len(nb) == 6

    # get_direction returns None for non-neighbor
    assert get_direction((0, 0), (2, 0)) is None

    # distance should match axial distance
    a = (0, 0)
    b = (2, 1)
    assert distance(a, b) == distance_axial(offset_to_axial(*a), offset_to_axial(*b))
    assert distance_axial_with_cube(offset_to_axial(*a), offset_to_axial(*b)) == distance(a, b)


def test_dijkstra_and_astar_basic():
    pyhexlib.init(orientation=Orientation.FLAT)
    # simple straight-line grid of three cells
    hexagons = {(0, 0), (0, 1), (0, 2)}
    # dijkstra should return a path that starts and ends correctly and
    # whose consecutive elements are neighbors (we don't assert a single
    # canonical route because the algorithm may traverse offset neighbors
    # that are still valid in the hex metric).
    path = dijkstra(hexagons, (0, 0), (0, 2))
    assert path is not None
    assert path[0] == (0, 0) and path[-1] == (0, 2)
    # consecutive nodes must be reachable neighbors according to neighborhood_basic
    for a, b in zip(path, path[1:]):
        assert b in neighborhood_basic(*a) or a in neighborhood_basic(*b)

    # astar: start==goal
    p2 = astar(hexagons, (0, 0), (0, 0))
    assert p2 == [(0, 0)]

    # astar: missing node returns None
    assert astar(hexagons, (0, 0), (10, 10)) is None
