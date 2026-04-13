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
from math import sqrt
from typing import Any, Dict

import pyhex
import pyhex.graphic as g
from pyhex.basic import Hexagon, Bounds
from pyhex.graphic import Point
from pyhex.hexagons import HexagonalGrid

# ---------------------------------------- Logger ------------------------------------------------

LOGGER = pyhex.get_logger(__name__)


# ----------------------------------------- HexGridViewport -----------------------------------------------

class Viewport(Bounds):
    def __init__(self, bounds: Bounds, outer_bounds: Bounds) -> None:
        super().__init__(*bounds)
        self.outer_bounds = outer_bounds

    # ------------------------- Properties for viewport configuration -------------------------------

    @property
    def origin(self) -> Hexagon:
        """Return the current origin hex for rendering."""
        return self.topleft

    @origin.setter
    def origin(self, origin: Hexagon) -> None:
        bounds = Bounds(origin.row, origin.col, origin.row + self.rows, origin.col + self.cols)
        self.bounds = self.adjust_bounds(bounds)
        self.hexagons = self._compute_hexagons()

    def adjust_bounds(self, bounds: Bounds) -> Bounds:
        # Ensure the viewport origin stays within the grid bounds.
        # `bounds` parameter contains a requested topleft (r_min, c_min) and an
        # implied size (we treat bottom/right as origin + rows/cols). The
        # grid bounds give the allowable area for the viewport origin.
        top, left, bottom, right = self.hexagonal_grid.bounds

        r_min, c_min, r_max, c_max = bounds

        # Compute the maximum allowed origin so that origin + (rows, cols)
        # does not exceed the grid's bottom/right. We use max(..., top)
        # to handle the case where the grid is smaller than the viewport.
        max_origin_row = max(top, bottom - self.rows)
        max_origin_col = max(left, right - self.cols)

        # Clamp requested origin to [top..max_origin_row] and [left..max_origin_col]
        r_min_temp = min(max(r_min, top), max_origin_row)
        c_min_temp = min(max(c_min, left), max_origin_col)

        # Set the adjusted origin and corresponding bounds (origin + size)
        self._origin = Hexagon(r_min_temp, c_min_temp)
        self.bounds = Bounds(r_min_temp, c_min_temp, r_min_temp + self.rows, c_min_temp + self.cols)

        return self.bounds

    # ----------------------------------- Moving the Viewport -----------------------------------

    def move_to(self, origin: Hexagon) -> None:
        """Move the viewport to a new origin hex."""
        self.origin = origin

    def move_by(self, rows: int = 0, cols: int = 0) -> None:
        """Move the viewport by a given amount."""
        row, col = self.origin
        self.origin = Hexagon(row + rows, col + cols)

    # ------------------------- Developer Representation -----------------------------------

    def __repr__(self) -> str:
        return (
            f"<{HexGridViewport.__name__}, bounds: top={self.top}, left={self.left}, bottom={self.bottom}, right={self.right}> "
            f"outer bounds={self.outer_bounds!r} >")


# ----------------------------------------- Hexagons Cache -----------------------------------------------

class Hexagons:
    def __init__(self, hexagons: Dict[Any, Any]) -> None:
        self._hexagons = hexagons

    # ----------------------------- Methods for accessing hexagon data -------------------------------

    def center(self, rc: Hexagon) -> Point:
        """Return cached pixel center for hex coordinate rc (r,c)."""
        return self._hexagons[rc]["center"]

    def edges(self, rc: Hexagon) -> list[Point]:
        """Return cached list of six corner points for hex key h (r,c)."""
        return self._hexagons[rc]["edges"]

    # ------------------------- Dictionary-like access to hexagon data -------------------------------

    def __iter__(self):
        return iter(self._hexagons)

    def __len__(self):
        return len(self._hexagons)

    def __contains__(self, item):
        return item in self._hexagons

    def __getitem__(self, key):
        return self._hexagons[key]

    def keys(self):
        return self._hexagons.keys()

    def items(self):
        return self._hexagons.items()

    def values(self):
        return self._hexagons.values()

    def get(self, key, default=None):
        return self._hexagons.get(key, default)

    # ------------------------- Developer Representation -----------------------------------

    def __repr__(self):
        return f"Hexagons(count={len(self)}: {self._hexagons})"


# ----------------------------------------- HexGridViewport -----------------------------------------------

class HexGridViewport:
    def __init__(self, hexagonal_grid: HexagonalGrid, radius: int, visible_size: tuple[int, int],
                 origin: Hexagon = None, offset: Point = Point(0, 0)) -> None:
        self.hexagonal_grid = hexagonal_grid
        self.radius = radius
        self._origin = Hexagon(*origin)

        self.bounds = self.hexagonal_grid.bounds  # The real bounds, including non-visible hexagons

        self.offset = offset
        self.rows, self.cols = visible_size
        self.inner_radius = sqrt(3) * self.radius / 2
        _, self.x_dist, self.y_dist = g.hex_dimensions(self.radius)

        self.hexagons = self._compute_hexagons()

    # ---------------------------- Methods for accessing hexagon data -------------------------------

    def center(self, rc: Hexagon) -> Point:
        """Return cached pixel center for hex coordinate rc (r,c)."""
        return self.hexagons.center(rc)

    def edges(self, rc: Hexagon) -> list[Point]:
        """Return cached list of six corner points for hex key h (r,c)."""
        return self.hexagons.edges(rc)

    # ---------------------------- Methods dependent from Orientation -------------------------------

    def _compute_hex_center(self, r: int, c: int, offset: Point) -> Point:
        return g.hex_center(r, c, self.x_dist, self.y_dist, self.offset, self.inner_radius, self.radius) - offset

    def _compute_hex_corners(self, center) -> list[Point]:
        return g.hex_corners(center, self.radius)

    # ----------------------------------- Independent methods -----------------------------------

    def _compute_hexagons(self) -> Hexagons:
        hexes = {}
        offset = self._compute_offset()
        for (r, c) in self._get_hexagon_within_bounds():
            center = self._compute_hex_center(r, c, offset)
            edges = self._compute_hex_corners(center)
            hexes[Hexagon(r, c)] = {"center": center, "edges": edges}
        return Hexagons(hexes)

    def _compute_offset(self) -> Point:
        return g.compute_offset(*self.origin, self.x_dist, self.y_dist, self.offset, self.inner_radius, self.radius)

    def _get_hexagon_within_bounds(self) -> list[Hexagon]:
        hexagons = [rc for rc in self.hexagonal_grid if self.bounds.contains(rc)]
        return hexagons

    def _xy_with_offset(self, p: Point):
        return p.x + self.offset.x, p.y + self.offset.y

    # ------------------------- Properties for viewport configuration -------------------------------

    @property
    def origin(self) -> Hexagon:
        """Return the current origin hex for rendering."""
        return self._origin

    @origin.setter
    def origin(self, origin: Hexagon) -> None:
        bounds = Bounds(origin.row, origin.col, origin.row + self.rows, origin.col + self.cols)
        self.bounds = self.adjust_bounds(bounds)
        self.hexagons = self._compute_hexagons()

    def adjust_bounds(self, bounds: Bounds) -> Bounds:
        # Ensure the viewport origin stays within the grid bounds.
        # `bounds` parameter contains a requested topleft (r_min, c_min) and an
        # implied size (we treat bottom/right as origin + rows/cols). The
        # grid bounds give the allowable area for the viewport origin.
        top, left, bottom, right = self.hexagonal_grid.bounds

        r_min, c_min, r_max, c_max = bounds

        # Compute the maximum allowed origin so that origin + (rows, cols)
        # does not exceed the grid's bottom/right. We use max(..., top)
        # to handle the case where the grid is smaller than the viewport.
        max_origin_row = max(top, bottom - self.rows)
        max_origin_col = max(left, right - self.cols)

        # Clamp requested origin to [top..max_origin_row] and [left..max_origin_col]
        r_min_temp = min(max(r_min, top), max_origin_row)
        c_min_temp = min(max(c_min, left), max_origin_col)

        # Set the adjusted origin and corresponding bounds (origin + size)
        self._origin = Hexagon(r_min_temp, c_min_temp)
        self.bounds = Bounds(r_min_temp, c_min_temp, r_min_temp + self.rows, c_min_temp + self.cols)

        return self.bounds

    # ----------------------------------- Moving the Viewport -----------------------------------

    def move_to(self, origin: Hexagon) -> None:
        """Move the viewport to a new origin hex."""
        self.origin = origin

    def move_by(self, rows: int = 0, cols: int = 0) -> None:
        """Move the viewport by a given amount."""
        row, col = self.origin
        self.origin = Hexagon(row + rows, col + cols)

    # ------------------------- Developer Representation -----------------------------------

    def __repr__(self) -> str:
        return (f"<{HexGridViewport.__name__}, origin={self.origin!r}, rows={self.rows!r}, cols = {self.cols!r}, "
                f"bounds={self.bounds!r} hex_count={len(self.hexagons)}>")
