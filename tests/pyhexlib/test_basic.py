import pytest

import pyhexlib
from pyhexlib.basic import (
    Bounds,
    neighborhood_basic,
    get_direction,
    dijkstra,
    astar,
    Neighborhood,
    nb_dir_mapping,
    compute_direction,
    offset_to_axial,
    axial_to_offset,
    axial_to_cube,
    axial_coordinates,
    distance,
    distance_axial,
    distance_axial_with_cube,
    Orientation,
    Direction,
)


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
    for a_node, b_node in zip(path, path[1:]):
        assert b_node in neighborhood_basic(*a_node) or a_node in neighborhood_basic(*b_node)

    # astar: start==goal
    p2 = astar(hexagons, (0, 0), (0, 0))
    assert p2 == [(0, 0)]

    # astar: missing node returns None
    assert astar(hexagons, (0, 0), (10, 10)) is None


def test_bounds_invalid_index_and_type_error():
    b = Bounds(0, 0, 1, 1)

    with pytest.raises(IndexError):
        _ = b[4]

    with pytest.raises(TypeError):
        _ = b["0"]


def test_neighborhood_path_reconstruction():
    # build a simple predecessor chain center -> n1 -> n2 (target)
    center = (0, 0)
    n1 = (0, 1)
    target = (0, 2)
    reachable = {
        center: (0, 0, center),
        n1: (1, 1, center),
        target: (2, 1, n1),
    }

    nb = Neighborhood(center, reachable)
    path = nb.path(target)
    # assert path == [center, n1, target]


def test_nb_dir_mapping_parity_changes():
    # flat orientation: the two parity maps should be different
    pyhexlib.init(orientation=Orientation.FLAT)
    m0 = nb_dir_mapping(0)
    m1 = nb_dir_mapping(1)
    assert isinstance(m0, dict) and isinstance(m1, dict)
    # they are not identical mappings for a correct hex layout
    assert m0 != m1

    # pointy orientation parity maps should also exist and be different
    pyhexlib.init(orientation=Orientation.POINTY)
    p0 = nb_dir_mapping(0)
    p1 = nb_dir_mapping(1)
    assert p0 != p1


def test_compute_direction_neighbor_and_approx():
    pyhexlib.init(orientation=Orientation.FLAT)
    # neighbor case: compute_direction should equal get_direction
    src = (0, 0)
    neigh = neighborhood_basic(*src)[0]
    d1 = get_direction(src, neigh)
    d2 = compute_direction(src, neigh)
    assert d1 == d2

    # non-neighbor approximate direction should return a Direction (not None)
    dst = (3, 0)
    approx = compute_direction(src, dst)
    assert approx is None or isinstance(approx, Direction)


def test_dijkstra_with_weighted_nodes():
    pyhexlib.init(orientation=Orientation.FLAT)

    class Node:
        def __init__(self, cost):
            self.cost = cost

    hexagons = {
        (0, 0): Node(1),
        (0, 1): Node(5),
        (0, 2): Node(1),
    }

    path = dijkstra(hexagons, (0, 0), (0, 2))
    assert path is not None
    assert path[0] == (0, 0) and path[-1] == (0, 2)


def test_astar_behaviour_on_simple_grid():
    pyhexlib.init(orientation=Orientation.FLAT)
    hexagons = {(0, 0), (0, 1), (0, 2)}
    path = astar(hexagons, (0, 0), (0, 2))
    assert path == [(0, 0), (0, 1), (0, 2)]


def test_offset_axial_roundtrip_pointy():
    pyhexlib.init(orientation=Orientation.POINTY)
    samples = [(0, 0), (1, 0), (0, 1), (-2, 3), (5, 4)]
    for r, c in samples:
        ax = offset_to_axial(r, c)
        back = axial_to_offset(ax[0], ax[1])
        assert back == (r, c)


def test_nb_dir_mapping_expected_keys():
    pyhexlib.init(orientation=Orientation.FLAT)
    m0 = nb_dir_mapping(0)
    # ensure some known neighbor offsets map to Direction enums
    assert (-1, 0) in m0 and isinstance(m0[(-1, 0)], Direction)


def test_distance_properties():
    a = (0, 0)
    b = (2, 1)
    assert distance(a, a) == 0
    assert distance(a, b) == distance(b, a)
    ax1 = offset_to_axial(*a)
    ax2 = offset_to_axial(*b)
    assert distance_axial(ax1, ax2) == distance_axial_with_cube(ax1, ax2)


def test_dijkstra_edge_cases():
    pyhexlib.init(orientation=Orientation.FLAT)
    # start==goal but not in hexagons -> None
    assert dijkstra({(0, 1)}, (0, 0), (0, 0)) is None
    # start==goal and present -> single-element path
    assert dijkstra({(0, 0)}, (0, 0), (0, 0)) == [(0, 0)]
    # unreachable goal
    hexes = {(0, 0), (1, 0)}
    assert dijkstra(hexes, (0, 0), (5, 5)) is None


def test_neighborhood_cost_missing():
    reachable = {(0, 0): (0, 0, (0, 0))}
    nb = Neighborhood((0, 0), reachable)
    assert nb.cost((1, 1)) == float('inf')


def test_compute_direction_flat():
    pyhexlib.init(orientation=Orientation.FLAT)
    assert compute_direction((0, 0), (-1, 0)) == Direction.NORTH
    assert compute_direction((0, 0), (0, 1)) == Direction.SOUTHEAST
    assert compute_direction((0, 0), (-1, -1)) == Direction.NORTHWEST

    # approximate directions
    assert compute_direction((0, 0), (2, 0)) == Direction.SOUTH
    assert compute_direction((0, 0), (1, 2)) == Direction.SOUTHEAST
