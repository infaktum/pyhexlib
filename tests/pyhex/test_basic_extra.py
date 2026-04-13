import pyhex
from pyhex.basic import (
    compute_direction,
    Orientation,
    Direction,
)


def test_compute_direction_flat():
    pyhex.init(orientation=Orientation.FLAT)
    assert compute_direction((0, 0), (-1, 0)) == Direction.NORTH
    assert compute_direction((0, 0), (0, 1)) == Direction.SOUTHEAST
    assert compute_direction((0, 0), (-1, -1)) == Direction.NORTHWEST

    # approximate directions
    assert compute_direction((0, 0), (2, 0)) == Direction.SOUTH
    assert compute_direction((0, 0), (1, 2)) == Direction.SOUTHEAST
