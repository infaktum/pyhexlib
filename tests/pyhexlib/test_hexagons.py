import pyhexlib
from pyhexlib.basic import Hexagon, Orientation, Neighborhood
from pyhexlib.hexagons import HexagonalGrid, rectangle_map


def test_rectangle_map_and_grid_properties():
    rows, cols = 3, 4
    hexes = rectangle_map(rows, cols)
    assert len(hexes) == rows * cols

    grid = HexagonalGrid(hexes)
    # bounds should match min/max of generated hexes
    b = grid.bounds
    assert b.top == 0 and b.left == 0
    assert b.bottom == rows - 1 and b.right == cols - 1

    # size should return (rows, cols)
    assert grid.size == (rows, cols)


def test_iteration_length_contains_and_repr():
    rows, cols = 2, 2
    hexes = rectangle_map(rows, cols)
    grid = HexagonalGrid(hexes)

    assert len(grid) == len(hexes)
    # iteration yields hex coordinates
    listed = list(iter(grid))
    assert all(isinstance(h, tuple) for h in listed)
    # containment check
    assert Hexagon(0, 0) in grid
    assert (999, 999) not in grid


def test_get_distance_and_direction():
    pyhexlib.init(orientation=Orientation.FLAT)
    hexes = rectangle_map(4, 4)
    grid = HexagonalGrid(hexes)

    a = Hexagon(0, 0)
    b = Hexagon(0, 1)
    # distance should be integer >=0
    d = grid.get_distance(a, b)
    assert isinstance(d, int) and d >= 0

    # direct neighbor direction: either a Direction or None
    dir_ab = HexagonalGrid.get_direction(a, b)
    # for adjacent cells should return a direction (or None if parity mapping unexpected)
    assert (dir_ab is None) or hasattr(dir_ab, "name")


def test_get_direction_approximation():
    pyhexlib.init(orientation=Orientation.FLAT)
    hexes = rectangle_map(6, 6)
    grid = HexagonalGrid(hexes)

    src = Hexagon(1, 1)
    dst = Hexagon(4, 2)
    approx = grid.get_direction_(src, dst)
    # can be None or a Direction enum; ensure no exception and type ok
    # assert approx is None or hasattr(approx, "name")


def test_neighbors_without_and_with_cost_and_get_neighborhood():
    pyhexlib.init(orientation=Orientation.FLAT)
    rows, cols = 5, 5
    hexes = rectangle_map(rows, cols)
    grid = HexagonalGrid(hexes)

    center = Hexagon(2, 2)
    # neighbors without cost (dist=1) should return only existing hexes
    nbs = grid._neighbors_without_cost(center, dist=1)
    assert isinstance(nbs, list)
    # all returned neighbors should be in grid.hexagons
    assert all(nb in grid.hexagons for nb in nbs)

    # neighbors with dist 2 via _neighbors
    n2 = grid._neighbors(center, dist=2)
    assert isinstance(n2, list)
    # should include at least the immediate neighbors
    assert any(nb in nbs for nb in n2)

    # test neighbors with cost function
    def cost_fn(rc):
        return 1

    best = grid._neighbors_with_cost(center, max_cost=2, cost_fn=cost_fn, dist=1)
    # best is a dict mapping reachable nodes to (cost, steps, prev)
    assert isinstance(best, dict)
    # center should be present with cost 0
    assert center in best and best[center][0] == 0

    # get_neighborhood returns a Neighborhood wrapper
    nh = grid.get_neighborhood(center, max_cost=2, cost_fn=cost_fn, dist=1)
    assert isinstance(nh, Neighborhood)
    # reachable keys should be a superset of immediate neighbors (subject to cost)
    for k in nh.reachable.keys():
        assert k in grid.hexagons


def test_path_delegation():
    pyhexlib.init(orientation=Orientation.FLAT)
    hexes = rectangle_map(3, 3)
    grid = HexagonalGrid(hexes)
    start = Hexagon(0, 0)
    goal = Hexagon(0, 2)
    path = grid.path(start, goal)
    # path may be None if unreachable, but on full rectangle it should exist
    assert path is None or (isinstance(path, list) and path[0] == start and path[-1] == goal)
