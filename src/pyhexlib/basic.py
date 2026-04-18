#  MIT License
#
#  Copyright (c) 2026 Heiko Sippel
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
#
import heapq
import math
from collections import namedtuple
from dataclasses import dataclass
from enum import Enum
from typing import List, Tuple, Dict

import pyhexlib

"""Core utilities for hexagon coordinate systems and pathfinding.

This module provides lightweight helpers for converting between offset and
axial cube coordinates, computing neighbor directions for flat- and
pointy-top hex layouts, and implementations of common pathfinding
algorithms (Dijkstra and A*). Docstrings use Google/Napoleon style so they
are compatible with Sphinx autodoc + napoleon.
"""


# ------------------------------------ Types and Enums -----------------------------------

class Orientation(Enum):
    FLAT = "Flat Top"
    POINTY = "Pointy Top"


AxialCoordinate = namedtuple("AxialCoordinate", ["r", "q"])
OffsetCoordinate = namedtuple("OffsetCoordinate", ["row", "col"])

# --------------------------------------- Hexagon ---------------------------------------

Hexagon = namedtuple("Hexagon", ["row", "col"])


# --------------------------------------- Bounds -----------------------------

@dataclass
class Bounds:
    top: int
    left: int
    bottom: int
    right: int

    """Axis-aligned bounding box for a rectangular region of hexagons.

    The `Bounds` object stores the top/left and bottom/right coordinates and
    provides convenience properties and sequence-like access.

    Attributes:
        top (int): Top row index.
        left (int): Left column index.
        bottom (int): Bottom row index.
        right (int): Right column index.
    """

    @property
    def topleft(self) -> Hexagon:
        """Return the top-left corner as a (row, col) tuple."""
        return self.top, self.left

    @property
    def bottomright(self) -> Hexagon:
        """Return the bottom-right corner as a (row, col) tuple."""
        return self.bottom, self.right

    @property
    def size(self) -> Tuple[int, int]:
        """Return the size of the bounds as (height, width)."""
        return self.bottom - self.top, self.right - self.left

    def contains(self, rc: Hexagon) -> bool:
        """Return True if the given (row, col) is inside the bounds."""
        r, c = rc
        return self.top <= r <= self.bottom and self.left <= c <= self.right

    # ----------------------------------------- Packing, Unpacking --------------------------

    def __iter__(self):
        """Iterate over bounds as (top, left, bottom, right)."""
        yield self.top
        yield self.left
        yield self.bottom
        yield self.right

    def __len__(self) -> int:
        """Return number of elements when treated like a sequence (4)."""
        return 4

    def __getitem__(self, idx: int) -> int:
        if not isinstance(idx, int):
            raise TypeError('Indices must be integers')
        if idx == 0:
            return self.top
        if idx == 1:
            return self.left
        if idx == 2:
            return self.bottom
        if idx == 3:
            return self.right
        raise IndexError('Bounds index out of range')


# --------------------------------------- Neighborhood ---------------------------------------

class Neighborhood:
    def __init__(self, center: Hexagon, reachable: Dict[Hexagon, Tuple[int, int, Hexagon]]):
        """Container for reachable neighbors from a given hexagon.

        Args:
            center (Hexagon): The central hexagon coordinate.
            reachable (Dict[Hexagon, Tuple[int, int, Hexagon]]): Mapping from neighbor
                coordinate to a tuple (cost, ???, predecessor) used to reconstruct paths.
        """
        self.center = center
        self.reachable = reachable

    def neighbors(self):
        """Return a list of neighbor coordinates.

        Returns:
            List[Hexagon]: Neighbor coordinates reachable from the center.
        """
        return list(self.reachable.keys())

    def cost(self, neighbor: Hexagon):
        """Return the movement cost to the given neighbor.

        If the neighbor is not reachable, float('inf') is returned.
        """
        return self.reachable.get(neighbor, float('inf'))

    def direction(self, neighbor: Hexagon):
        """Return the Direction enum representing direction from center to neighbor.

        Args:
            neighbor (Hexagon): Neighbor coordinate.

        Returns:
            Direction | None: Direction enum or None if not a direct mapping.
        """
        return get_direction((self.center.row, self.center.col), (neighbor.row, neighbor.col))

    def path(self, target: Hexagon):
        """Reconstruct the path from center to the given target using predecessor links.

        The reachable mapping is expected to store tuples where the third element
        is the predecessor node. Returns the path as a list of hexagon coordinates
        starting with the center and ending with the target.

        Args:
            target (Hexagon): Destination coordinate.

        Returns:
            List[Hexagon]: Ordered list of coordinates from center to target.
        """
        path = []
        step = self.reachable.get(target)[2]

        while step != self.center:
            path.append(step)
            step = self.reachable.get(step)[2]

        path.append(self.center)

        path.reverse()
        return path

        # return dijkstra(self.reachable, (self.hexagons.row, self.hexagons.col), (neighbor.row, neighbor.col))


class Direction(Enum):
    NORTH = "North"
    NORTHEAST = "Northeast"
    EAST = "East"
    SOUTHEAST = "Southeast"
    SOUTH = "South"
    SOUTHWEST = "Southwest"
    WEST = "West"
    NORTHWEST = "Northwest"


DirectionMapping = Dict[Tuple[int, int], Direction]


# ----------------------------------- Coordinate Systems -----------------------------------

def offset_to_axial(row: int, col: int) -> Tuple[int, int]:
    """Convert offset coordinates (row, col) to axial coordinates (r, q).

    The conversion depends on the global orientation flag in `pyhexlib`.

    Args:
        row (int): Offset row coordinate.
        col (int): Offset column coordinate.

    Returns:
        Tuple[int, int]: Axial coordinates (r, q).
    """
    return _offset_to_axial_flat(row, col) if pyhexlib.is_flat else _offset_to_axial_pointy(
        row, col)


def axial_to_offset(ra: int, qa: int) -> Tuple[int, int]:
    """Convert axial coordinates (r, q) to offset coordinates (row, col).

    The exact formula depends on the global orientation flag in `pyhexlib`.

    Args:
        ra (int): Axial r coordinate.
        qa (int): Axial q coordinate.

    Returns:
        Tuple[int, int]: Offset coordinates (row, col).
    """
    return _axial_to_offset_flat(ra, qa) if pyhexlib.is_flat else _axial_to_offset_pointy(ra, qa)


# ----------------------------------- Internal specialized methods -----------------------------------

def _offset_to_axial_flat(row: int, col: int) -> Tuple[int, int]:
    """Flat-top offset -> axial conversion (even-q vertical layout).

    Args:
        row (int): Offset row.
        col (int): Offset column.

    Returns:
        Tuple[int, int]: Axial coordinates (r, q).
    """
    q = int(col)
    parity = col & 1
    r = int(row - (col - parity) // 2)
    return r, q


def _axial_to_offset_flat(r: int, q: int) -> Tuple[int, int]:
    """Axial -> flat-top offset conversion (even-q vertical layout)."""
    col = int(q)
    parity = col & 1
    row = int(r + (col - parity) // 2)
    return row, col


def _offset_to_axial_pointy(row: int, col: int) -> Tuple[int, int]:
    """Pointy-top offset -> axial conversion (odd-r horizontal layout)."""
    r = int(row)
    parity = r & 1
    q = int(col - (r - parity) // 2)
    return r, q


def _axial_to_offset_pointy(r: int, q: int) -> Tuple[int, int]:
    """Axial -> pointy-top offset conversion (odd-r horizontal layout)."""
    row = int(r)
    parity = row & 1
    col = int(q + (row - parity) // 2)
    return row, col


def axial_to_cube(ax: Tuple[int, int]) -> Tuple[int, int, int]:
    """Convert axial coordinates (r, q) to cube coordinates (x, y, z).

    Cube coordinates are useful for computing hex distances and rotations.

    Args:
        ax (Tuple[int, int]): Axial coordinates (r, q).

    Returns:
        Tuple[int, int, int]: Cube coordinates (x, y, z).
    """
    r, q = ax
    x = q
    z = r
    y = -x - z
    return x, y, z


def axial_coordinates(hexagons: List[tuple[int, int]]):
    """Map a collection of offset coordinates to axial coordinates.

    Args:
        hexagons (List[tuple[int, int]]): Iterable of (row, col) coordinates.

    Returns:
        Dict[tuple[int,int], tuple[int,int]]: Mapping from (row,col) -> (r,q).
    """
    return {(r, c): offset_to_axial(r, c) for (r, c) in hexagons}


# Predefined direction mappings for direct neighbors based on orientation and parity.

_direction_mappings: DirectionMapping = \
    {
        Orientation.FLAT:
            [{(-1, 0): Direction.NORTH, (-1, +1): Direction.NORTHEAST, (0, +1): Direction.SOUTHEAST,
              (+1, 0): Direction.SOUTH, (0, -1): Direction.SOUTHWEST, (-1, -1): Direction.NORTHWEST},

             {(-1, 0): Direction.NORTH, (0, +1): Direction.NORTHEAST, (+1, +1): Direction.SOUTHEAST,
              (+1, 0): Direction.SOUTH, (+1, -1): Direction.SOUTHWEST, (0, -1): Direction.NORTHWEST}
             ],

        Orientation.POINTY:
            [{(0, +1): Direction.EAST, (+1, 0): Direction.SOUTHEAST, (+1, -1): Direction.SOUTHWEST,
              (0, -1): Direction.WEST, (-1, -1): Direction.NORTHWEST, (-1, 0): Direction.NORTHEAST},

             {(0, +1): Direction.EAST, (+1, +1): Direction.SOUTHEAST, (+1, 0): Direction.SOUTHWEST,
              (0, -1): Direction.WEST, (-1, 0): Direction.NORTHWEST, (-1, +1): Direction.NORTHEAST}
             ]
    }


# ----------------------------------- Neighborhoods and Directions -----------------------------------

def nb_dir_mapping(parity: int) -> DirectionMapping:
    """Return the neighbor-direction mapping for the current orientation and parity.

    Args:
        parity (int): Parity (0 or 1) of the relevant coordinate (col for flat, row for pointy).

    Returns:
        DirectionMapping: A dict mapping neighbor offsets to Direction enums.
    """
    return _direction_mappings[pyhexlib.get_orientation()][parity]


def neighborhood_basic(row, col) -> List[tuple[int, int]]:
    """Return the 6 immediate neighboring coordinates for a hex at (row, col).

    The neighbor offsets depend on whether the layout is flat- or pointy-top
    and on the parity of the relevant coordinate (column or row).

    Args:
        row (int): Row index of the center hex.
        col (int): Column index of the center hex.

    Returns:
        List[tuple[int,int]]: List of six (row, col) neighbor coordinates.
    """
    if pyhexlib.is_flat:
        return [(row + drow, col + dcol) for drow, dcol in nb_dir_mapping(col & 1)]
    else:
        return [(row + drow, col + dcol) for drow, dcol in nb_dir_mapping(row & 1)]


def get_direction(rc1, rc2) -> Direction:
    # parity depends on orientation: FLAT uses column parity, POINTY uses row parity
    """Return the Direction from rc1 to rc2 if they are direct neighbors.

    The function checks the parity appropriate for the configured orientation
    and looks up the simple neighbor mapping. If the pair is not a direct
    neighbor, None is returned.

    Args:
        rc1 (tuple[int,int]): Source coordinate (row, col).
        rc2 (tuple[int,int]): Target coordinate (row, col).

    Returns:
        Direction | None: Direction enum if rc2 is an immediate neighbor of rc1.
    """
    parity = rc1[1] & 1 if pyhexlib.is_flat else rc1[0] & 1
    directions = nb_dir_mapping(parity)

    drow = rc2[0] - rc1[0]
    dcol = rc2[1] - rc1[1]

    return directions.get((drow, dcol), None)


def compute_direction(rc1, rc2):
    """Compute a Direction between two coordinates, approximating if necessary.

    If the two coordinates are direct neighbors the precise direction is
    returned. Otherwise, the function falls back to computing an approximate
    direction based on axial/vector geometry.

    Args:
        rc1 (tuple[int,int]): Source (row, col).
        rc2 (tuple[int,int]): Target (row, col).

    Returns:
        Direction | None: Best matching Direction or None if same cell.
    """
    return _compute_direction_flat(rc1, rc2) if pyhexlib.is_flat else _compute_direction_pointy(rc1, rc2)


def _compute_direction_flat(rc1, rc2):
    """Compute direction for flat-top layout, approximate if not direct neighbor.

    Args:
        rc1 (tuple[int,int]): Source coordinate (row, col).
        rc2 (tuple[int,int]): Target coordinate (row, col).

    Returns:
        Direction | None: Computed direction or None if same cell.
    """
    if rc1 == rc2:
        return None

    # direct neighbor lookup using parity of column (base = rc1)
    parity = rc1[1] & 1
    d = (rc2[0] - rc1[0], rc2[1] - rc1[1])
    mapping = _direction_mappings[Orientation.FLAT][parity]
    if d in mapping:
        return mapping[d]

    # approximate: compute axial difference
    ax1 = offset_to_axial(rc1[0], rc1[1])
    ax2 = offset_to_axial(rc2[0], rc2[1])
    delta_ax = (ax2[0] - ax1[0], ax2[1] - ax1[1])

    # build canonical axial direction vectors from parity 0 neighbor offsets
    canon_map = _direction_mappings[Orientation.FLAT][0]
    base_ax = offset_to_axial(0, 0)

    def axial_to_2d_flat(ax):
        # convert axial (r, q) to 2D cartesian coordinates for flat-top hex layout
        r, q = ax
        x = 1.5 * q
        y = math.sqrt(3) * (r + q / 2.0)
        return x, y

    target_xy = axial_to_2d_flat(delta_ax)
    target_angle = math.degrees(math.atan2(target_xy[1], target_xy[0]))

    best = None
    best_diff = 1e9
    for off, direction in canon_map.items():
        nb_ax = offset_to_axial(off[0], off[1])
        vec_ax = (nb_ax[0] - base_ax[0], nb_ax[1] - base_ax[1])
        vec_xy = axial_to_2d_flat(vec_ax)
        ang = math.degrees(math.atan2(vec_xy[1], vec_xy[0]))
        diff = abs((ang - target_angle + 180) % 360 - 180)
        if diff < best_diff:
            best_diff = diff
            best = direction
    return best


def _compute_direction_pointy(rc1, rc2):
    """Compute direction for pointy-top layout, approximate if not direct neighbor.

    Args:
        rc1 (tuple[int,int]): Source coordinate (row, col).
        rc2 (tuple[int,int]): Target coordinate (row, col).

    Returns:
        Direction | None: Computed direction or None if same cell.
    """
    if rc1 == rc2:
        return None

    # direct neighbor lookup using parity of row
    parity = rc1[0] & 1
    d = (rc2[0] - rc1[0], rc2[1] - rc1[1])
    mapping = _direction_mappings[Orientation.POINTY][parity]
    if d in mapping:
        return mapping[d]

    # approximate: compute axial difference
    ax1 = offset_to_axial(rc1[0], rc1[1])
    ax2 = offset_to_axial(rc2[0], rc2[1])
    delta_ax = (ax2[0] - ax1[0], ax2[1] - ax1[1])

    # canonical directions from parity 0
    canon_map = _direction_mappings[Orientation.POINTY][0]
    base_ax = offset_to_axial(0, 0)

    def axial_to_2d_pointy(ax):
        # convert axial (r, q) to 2D cartesian coordinates for pointy-top hex layout
        r, q = ax
        x = math.sqrt(3) * (q + r / 2.0)
        y = 1.5 * r
        return x, y

    target_xy = axial_to_2d_pointy(delta_ax)
    target_angle = math.degrees(math.atan2(target_xy[1], target_xy[0]))

    best = None
    best_diff = 1e9
    for off, direction in canon_map.items():
        nb_ax = offset_to_axial(off[0], off[1])
        vec_ax = (nb_ax[0] - base_ax[0], nb_ax[1] - base_ax[1])
        vec_xy = axial_to_2d_pointy(vec_ax)
        ang = math.degrees(math.atan2(vec_xy[1], vec_xy[0]))
        diff = abs((ang - target_angle + 180) % 360 - 180)
        if diff < best_diff:
            best_diff = diff
            best = direction
    return best


# ------------------------------------------- Distances -----------------------------------

def distance(rc1, rc2) -> int:
    """Compute hex distance between two offset coordinates.

    Args:
        rc1 (tuple[int,int]): First coordinate (row, col).
        rc2 (tuple[int,int]): Second coordinate (row, col).

    Returns:
        int: Hex distance (number of steps between cells).
    """
    ax1 = offset_to_axial(rc1[0], rc1[1])
    ax2 = offset_to_axial(rc2[0], rc2[1])
    return distance_axial(ax1, ax2)


def distance_axial(ax1, ax2):
    """Compute hex distance between two axial coordinates.

    Uses the common axial distance formula.
    """
    return int((abs(ax1[0] - ax2[0]) + abs(ax1[0] + ax1[1] - ax2[0] - ax2[1]) + abs(ax1[1] - ax2[1])) / 2)


def distance_axial_with_cube(ax1, ax2):
    # ax1, ax2 sind (r, q)
    """Compute axial distance using cube coordinates conversion.

    This variant converts axial coords to cube coordinates and returns the
    maximum absolute difference among cube axes.
    """
    r1, q1 = int(ax1[0]), int(ax1[1])
    r2, q2 = int(ax2[0]), int(ax2[1])

    # axial -> cube: x = q, z = r, y = -x - z
    x1, y1, z1 = q1, -(q1 + r1), r1
    x2, y2, z2 = q2, -(q2 + r2), r2

    return int(max(abs(x1 - x2), abs(y1 - y2), abs(z1 - z2)))


# ------------------------------ Dijkstra Pathfinding -------------------------------


def dijkstra(hexagons, start, goal, cost_fn=None) -> List[tuple[int, int]] | None:
    """Dijkstra shortest-path algorithm over hexagon graph.

    The `hexagons` parameter may be a mapping providing cost information for
    each cell or an iterable container of coordinates. When it is a mapping,
    the default cost lookup tries to read either `.cost` or `.move_cost` from
    the stored value; otherwise costs default to 1.

    Args:
        hexagons (Mapping|Iterable): Graph representation or container of nodes.
        start (tuple[int,int]): Start coordinate.
        goal (tuple[int,int]): Goal coordinate.
        cost_fn (callable, optional): Optional function cost_fn(rc) -> numeric cost.

    Returns:
        List[tuple[int,int]] | None: The shortest path from start to goal as a list
        of coordinates, or None if no path exists.
    """
    if start == goal:
        return [start] if start in hexagons else None

    if start not in hexagons or goal not in hexagons:
        return None

    def _default_cost(rc):
        if isinstance(hexagons, dict):
            v = hexagons.get(rc)
            if v is None:
                return float('inf')
            return getattr(v, "cost", getattr(v, "move_cost", 1))
        else:
            return 1

    cost = cost_fn or _default_cost

    dist_so_far = {start: 0}
    prev = {}
    heap = [(0, start)]

    while heap:
        cur_cost, cur = heapq.heappop(heap)
        if cur_cost != dist_so_far.get(cur, float('inf')):
            continue
        if cur == goal:
            # reconstruct path
            path = []
            node = goal
            while node in prev:
                path.append(node)
                node = prev[node]
            path.append(start)
            path.reverse()
            return path

        for nb in neighborhood_basic(*cur):
            step_cost = cost(nb)
            if step_cost is None or step_cost == float('inf'):
                continue
            new_cost = cur_cost + step_cost
            if new_cost < dist_so_far.get(nb, float('inf')):
                dist_so_far[nb] = new_cost
                prev[nb] = cur
                heapq.heappush(heap, (new_cost, nb))

    return None


# ------------------------------- A-Star Algorithm for path finding --------------------------------

def astar(hexagons, start, goal, cost_fn=None) -> List[tuple[int, int]] | None:
    """A* pathfinding on the same interface as dijkstra.

    hexagons can be a dict or any container. cost_fn behaves like in dijkstra
    (if omitted, a default cost lookup is used).

    This implementation supports an optional preference-based penalty that
    biases the search to keep one of the offset coordinates ('row' or 'col')
    close to the start coordinate. This can be used to force a more
    'zigzag' style horizontal movement instead of the usual straight/triangular
    shortest path. The parameters are:

    - prefer_coord: 'none' (default), 'row' or 'col'. If not 'none', the
      heuristic adds a penalty proportional to the absolute difference
      between the current node's chosen coordinate and the start node's
      chosen coordinate.
    - penalty: a non-negative float multiplier controlling how strongly
      deviations are penalized. Default 0.0 (no penalty) preserves original
      behavior.

    Note: adding a penalty can make the heuristic inadmissible (i.e. no
    longer guaranteed to be optimistic) and therefore may sacrifice optimality
    for the desired path shape.
    """
    if start == goal:
        return [start] if start in hexagons else None

    if start not in hexagons or goal not in hexagons:
        return None

    prefer_coord = 'row' if pyhexlib.is_flat else 'col'
    penalty = 1.0

    def _default_cost(rc):
        if isinstance(hexagons, dict):
            v = hexagons.get(rc)
            if v is None:
                return float('inf')
            return getattr(v, "cost", getattr(v, "move_cost", 1))
        else:
            return 1

    cost = cost_fn or _default_cost

    # validate prefer_coord
    prefer = prefer_coord.lower() if isinstance(prefer_coord, str) else 'none'
    if prefer not in ('none', 'row', 'col'):
        raise ValueError("prefer_coord must be one of 'none', 'row', 'col' or 'auto'")

    if penalty is None:
        penalty = 0.0
    try:
        penalty = float(penalty)
    except Exception:
        raise ValueError('penalty must be a number')

    def heuristic(rc):
        # base heuristic: hex distance (offset coords)
        try:
            h = distance(rc, goal)
        except Exception:
            return 0

        # if preference is active, add a penalty based on deviation from the
        # start coordinate along the chosen axis (row -> index 0, col -> index 1)
        if prefer != 'none' and penalty > 0.0:
            idx = 0 if prefer == 'row' else 1
            # absolute deviation from the start coordinate
            dev = abs(rc[idx] - start[idx])
            h = h + penalty * dev

        return h

    # g-score: cost from start to node
    g_score = {start: 0}
    # came_from map for path reconstruction
    came_from = {}

    # open set as heap of (f_score, g_score, node)
    heap = []
    start_f = g_score[start] + heuristic(start)
    heapq.heappush(heap, (start_f, g_score[start], start))

    while heap:
        f_cur, g_cur, cur = heapq.heappop(heap)

        # stale entry check
        if g_cur != g_score.get(cur, float('inf')):
            continue

        if cur == goal:
            # reconstruct path
            path = []
            node = goal
            while node in came_from:
                path.append(node)
                node = came_from[node]
            path.append(start)
            path.reverse()
            return path

        for nb in neighborhood_basic(*cur):
            step_cost = cost(nb)
            if step_cost is None or step_cost == float('inf'):
                continue
            tentative_g = g_score.get(cur, float('inf')) + step_cost
            if tentative_g < g_score.get(nb, float('inf')):
                came_from[nb] = cur
                g_score[nb] = tentative_g
                f = tentative_g + heuristic(nb)
                heapq.heappush(heap, (f, tentative_g, nb))

    return None
