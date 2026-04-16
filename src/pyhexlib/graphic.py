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
from collections import namedtuple
from math import pi, cos, sin, sqrt, atan2

import pygame
from pygame import Color

import pyhexlib
import pyhexlib.basic as b
from pyhexlib.basic import Orientation, Direction
from pyhexlib.hexagons import Hexagon

# ----------------------------------- Basic Types -----------------------------------

Offset = Point = pygame.Vector2

Rectangle = pygame.Rect

Size = namedtuple("Size", ["width", "height"])

# ----------------------------------- Constants --------------------------------------

TRANSPARENT = Color(0, 0, 0, 0)


# ----------------------------------- Hexagon Geometry -----------------------------------

def hex_corners(center: Point, radius: int) -> list[Point]:
    """Return the six corner points for a hexagon centered at ``center``.

    :param center: Pixel coordinates of the hexagon center as a
        :class:`pygame.Vector2`.
    :type center: pygame.Vector2
    :param radius: Outer radius of the hexagon in pixels.
    :type radius: int
    :return: List of six corner points as :class:`pygame.Vector2` objects.
    :rtype: list[pygame.Vector2]

    Chooses the flat- or pointy-top variant depending on the global
    orientation flag :data:`pyhexlib.is_flat`.
    """
    return hex_corners_flat(center, radius) if pyhexlib.is_flat else hex_corners_pointy(center, radius)


def hex_dimensions(radius: int) -> tuple[float, int, int]:
    """Return geometric hexagon metrics for the given radius.

    :param radius: Outer radius of the hexagon in pixels.
    :type radius: int
    :return: Tuple ``(inner_radius, x_dist, y_dist)`` where ``inner_radius``
        is the distance from center to a side, and ``x_dist``/``y_dist`` are
        the horizontal and vertical spacing between hexagon centers for the
        configured orientation.
    :rtype: tuple[float, int, int]
    """
    return _hex_dimensions_flat(radius) if pyhexlib.is_flat else _hex_dimensions_pointy(radius)


# ----------------------------------- Screen Size Calculation -----------------------------------

def compute_screen_size(rows: int, cols: int, radius: int) -> Size:
    """Compute the pixel size required to render a hex grid.

    :param rows: Number of rows in the grid.
    :type rows: int
    :param cols: Number of columns in the grid.
    :type cols: int
    :param radius: Hexagon outer radius in pixels.
    :type radius: int
    :return: Size object with attributes ``width`` and ``height``.
    :rtype: Size

    The computation differs between flat- and pointy-top hexagons and
    is delegated to internal helpers.
    """
    return _screen_size_flat(rows, cols, radius) if pyhexlib.is_flat else _screen_size_pointy(rows, cols, radius)


def compute_viewport_bounds(topleft: Hexagon) -> b.Bounds:
    """Compute an approximate :class:`pyhexlib.basic.Bounds` for a
    viewport starting at the supplied top-left hexagon.

    :param topleft: The top-left visible hexagon as a (row, col) tuple or
        :class:`pyhexlib.hexagons.Hexagon`.
    :type topleft: tuple[int, int] | Hexagon
    :return: A small bounds box starting at ``topleft``. This helper
        is intentionally approximate and currently returns a 20x20 box.
    :rtype: pyhexlib.basic.Bounds
    """
    return b.Bounds(*topleft, topleft[0] + 20, topleft[1] + 20)


# ----------------------------------- Pixel to Hex Conversion -----------------------------------

def xy_to_rc(x, y, radius: int) -> Hexagon:
    """Convert pixel coordinates to grid coordinates (row, col).

    :param x: X coordinate in pixels.
    :type x: float | int
    :param y: Y coordinate in pixels.
    :type y: float | int
    :param radius: Hexagon outer radius in pixels.
    :type radius: int
    :return: The corresponding :class:`pyhexlib.hexagons.Hexagon`.
    :rtype: Hexagon

    The conversion is delegated to orientation-specific helpers.
    """
    return xy_to_rc_flat(x, y, radius) if pyhexlib.is_flat else xy_to_rc_pointy(x, y, radius)


# ----------------------------------- Internal methods -----------------------------------

def hex_corner_with_offset(center: Point, size: int, i: int, angle_offset) -> Point:
    """Return a single corner point for a hexagon.

    :param center: Center position as :class:`pygame.Vector2`.
    :type center: pygame.Vector2
    :param size: Hexagon outer radius in pixels.
    :type size: int
    :param i: Corner index in range 0..5.
    :type i: int
    :param angle_offset: Angle offset in degrees applied to the base
        corner angles (0 for flat, 30 for pointy).
    :type angle_offset: int
    :return: Corner point as :class:`pygame.Vector2`.
    :rtype: pygame.Vector2
    """

    angle_deg = 60 * i + angle_offset
    angle_rad = pi / 180 * angle_deg
    x = center.x + size * cos(angle_rad) * pyhexlib.sx
    y = center.y + size * sin(angle_rad) * pyhexlib.sy
    return Point(round(x), round(y))


def hex_corners_pointy(center: Point, size: int) -> list[Point]:
    """Return the six corner points for a pointy-top hexagon.

    :param center: Center position in pixels as :class:`pygame.Vector2`.
    :type center: pygame.Vector2
    :param size: Hexagon outer radius in pixels.
    :type size: int
    :return: List of six corner points.
    :rtype: list[pygame.Vector2]
    """
    return [hex_corner_with_offset(center, size, j, 30) for j in range(6)]


def hex_corners_flat(center: Point, size: int) -> list[Point]:
    """Return the six corner points for a flat-top hexagon.

    :param center: Center position in pixels as :class:`pygame.Vector2`.
    :type center: pygame.Vector2
    :param size: Hexagon outer radius in pixels.
    :type size: int
    :return: List of six corner points.
    :rtype: list[pygame.Vector2]
    """
    return [hex_corner_with_offset(center, size, j, 0) for j in range(6)]


# --------------------------------------------------------------------------------------

def hex_center(r, c, x_dist, y_dist, offset, inner_radius, radius: int) -> Point:
    if pyhexlib.is_flat:
        return hex_center_flat(r, c, x_dist, y_dist, offset, inner_radius, radius)
    else:
        return hex_center_pointy(r, c, x_dist, y_dist, offset, inner_radius, radius)


def hex_center_flat(r, c, x_dist, y_dist, offset, inner_radius, radius):
    """Compute the pixel center for a flat-top hexagon at grid
    coordinates (r, c).

    :param r: Row index.
    :type r: int
    :param c: Column index.
    :type c: int
    :param x_dist: Horizontal spacing between hex centers.
    :type x_dist: int
    :param y_dist: Vertical spacing between hex centers.
    :type y_dist: int
    :param offset: Pixel offset applied to the resulting center.
    :type offset: pygame.Vector2
    :param inner_radius: Distance from center to side.
    :type inner_radius: float
    :param radius: Outer radius in pixels.
    :type radius: int
    :return: Pixel coordinates of the hex center.
    :rtype: pygame.Vector2
    """
    x = int(x_dist * c + radius) - offset.x
    y = int(y_dist * (r + (c & 1) / 2) + inner_radius) - offset.y
    return Point(x, y)


def hex_center_pointy(r, c, x_dist, y_dist, offset, inner_radius, radius):
    """Compute the pixel center for a pointy-top hexagon at grid
    coordinates (r, c).

    :param r: Row index.
    :type r: int
    :param c: Column index.
    :type c: int
    :param x_dist: Horizontal spacing between hex centers.
    :type x_dist: int
    :param y_dist: Vertical spacing between hex centers.
    :type y_dist: int
    :param offset: Pixel offset applied to the resulting center.
    :type offset: pygame.Vector2
    :param inner_radius: Distance from center to side.
    :type inner_radius: float
    :param radius: Outer radius in pixels.
    :type radius: int
    :return: Pixel coordinates of the hex center.
    :rtype: pygame.Vector2
    """
    x = int(x_dist * (c + (r & 1) / 2) + inner_radius) - offset.x
    y = int(y_dist * r + radius) - offset.y
    return Point(x, y)


def compute_offset(r, c, x_dist, y_dist, offset, inner_radius, radius) -> Point:
    """Compute the pixel offset to position the viewport so that the
    specified origin hexagon appears near the top-left of the visible
    area.

    :param r: Origin row index.
    :type r: int
    :param c: Origin column index.
    :type c: int
    :param x_dist: Horizontal spacing between hex centers.
    :type x_dist: int
    :param y_dist: Vertical spacing between hex centers.
    :type y_dist: int
    :param offset: Current offset or anchor point (unused semantic,
        passed through to helpers).
    :type offset: pygame.Vector2
    :param inner_radius: Distance from center to side.
    :type inner_radius: float
    :param radius: Outer radius in pixels.
    :type radius: int
    :return: Pixel offset as :class:`pygame.Vector2` to apply to world
        coordinates.
    :rtype: pygame.Vector2
    """
    origin_center = hex_center(r, c, x_dist, y_dist, offset, inner_radius, radius)
    if pyhexlib.is_flat:
        offset = origin_center - Point(radius, y_dist // 2)
    else:
        offset = origin_center - Point(x_dist // 2, radius)
    return Point(offset)


def compute_area(top, left, rows, cols, x_dist, y_dist) -> Rectangle:
    """Return a :class:`pygame.Rect` covering the pixel area for a
    grid region.

    :param top: Top row index of the region.
    :type top: int
    :param left: Left column index of the region.
    :type left: int
    :param rows: Number of rows in the region.
    :type rows: int
    :param cols: Number of columns in the region.
    :type cols: int
    :param x_dist: Horizontal spacing between centers in pixels.
    :type x_dist: int
    :param y_dist: Vertical spacing between centers in pixels.
    :type y_dist: int
    :return: Rectangle in pixel coordinates covering the region.
    :rtype: pygame.Rect
    """
    return Rectangle(left * x_dist, top * y_dist, (left + cols) * x_dist, (top + rows) * y_dist)


# ----------------------------------- Hexagon Geometry -----------------------------------

def _hex_dimensions_flat(radius: int) -> tuple[float, int, int]:
    """Internal helper: compute hex geometry for flat-top hexagons.

    :param radius: Hexagon outer radius in pixels.
    :type radius: int
    :return: (inner_radius, x_dist, y_dist)
    :rtype: tuple[float, int, int]
    """
    inner_radius = sqrt(3) * radius / 2
    x_dist, y_dist = round(3 * radius // 2 * pyhexlib.sx), round(2 * inner_radius * pyhexlib.sy)
    return inner_radius, x_dist, y_dist


def _hex_dimensions_pointy(radius: int) -> tuple[float, int, int]:
    """Internal helper: compute hex geometry for pointy-top hexagons.

    :param radius: Hexagon outer radius in pixels.
    :type radius: int
    :return: (inner_radius, x_dist, y_dist)
    :rtype: tuple[float, int, int]
    """
    inner_radius = sqrt(3) * radius / 2
    x_dist, y_dist = round(2 * inner_radius * pyhexlib.sx), round(3 * radius // 2 * pyhexlib.sy)
    return inner_radius, x_dist, y_dist


# ----------------------------------- Screen Size Calculation -----------------------------------

def _screen_size_flat(rows: int, cols: int, radius: int) -> tuple[int, int]:
    """Internal helper: compute screen pixel size for a flat-top grid.

    :param rows: Number of rows.
    :type rows: int
    :param cols: Number of columns.
    :type cols: int
    :param radius: Hexagon outer radius.
    :type radius: int
    :return: Width and height in pixels.
    :rtype: tuple[int, int]
    """
    inner_radius, xdist, ydist = _hex_dimensions_flat(radius)
    width = round(xdist * (cols - 1) + radius * 2)
    height = round(ydist * rows + ydist // 2)
    return width, height


def _screen_size_pointy(rows: int, cols: int, radius: int) -> tuple[int, int]:
    """Internal helper: compute screen pixel size for a pointy-top grid.

    :param rows: Number of rows.
    :type rows: int
    :param cols: Number of columns.
    :type cols: int
    :param radius: Hexagon outer radius.
    :type radius: int
    :return: Width and height in pixels.
    :rtype: tuple[int, int]
    """
    inner_radius, x_dist, y_dist = _hex_dimensions_pointy(radius)
    width = round(x_dist * cols + (rows > 1) * inner_radius)
    height = round(y_dist * rows + y_dist // 3)
    return width, height


# ----------------------------------------- Directions and Angles -----------------------------------------

ANGLES = {
    Orientation.FLAT: {Direction.NORTH: 0, Direction.NORTHWEST: 60, Direction.SOUTHWEST: 120, Direction.SOUTH: 180,
                       Direction.SOUTHEAST: 240, Direction.NORTHEAST: 300},
    Orientation.POINTY: {Direction.EAST: 0, Direction.NORTHEAST: 60, Direction.NORTHWEST: 120, Direction.WEST: 180,
                         Direction.SOUTHWEST: 240, Direction.SOUTHEAST: 300}
}


def direction_to_angle(direction: Direction) -> int:
    """Return the rotation angle (degrees) for a hex :class:`Direction`.

    :param direction: Direction enum value.
    :type direction: pyhexlib.basic.Direction
    :return: Angle in degrees, or ``None`` if the direction is unknown.
    :rtype: int | None
    """
    angle = ANGLES[pyhexlib.get_orientation()].get(direction, None)
    return angle


def angle_to_direction(angle: int) -> Direction:
    """Map an absolute angle (degrees) to the nearest hex :class:`Direction`.

    :param angle: Angle in degrees.
    :type angle: int
    :return: Nearest :class:`pyhexlib.basic.Direction` value.
    :rtype: pyhexlib.basic.Direction | None
    """
    angle = angle % 360
    mapping = ANGLES[pyhexlib.get_orientation()]
    best_dir = None
    best_diff = 360.0
    for direction, dir_angle in mapping.items():

        diff = abs(((angle - dir_angle + 180) % 360) - 180)
        if diff < best_diff:
            best_diff = diff
            best_dir = direction
    return best_dir


# ----------------------------------- Pixel to Hex Conversion -----------------------------------

def xy_to_rc_flat(x, y, radius) -> Hexagon:
    """Convert pixel coordinates to hex grid coordinates for flat-top hexagons.

    :param x: X coordinate in pixels.
    :type x: float | int
    :param y: Y coordinate in pixels.
    :type y: float | int
    :param radius: Hexagon outer radius in pixels.
    :type radius: int
    :return: The corresponding :class:`pyhexlib.hexagons.Hexagon`.
    :rtype: Hexagon

    The algorithm first estimates the column and row and then corrects
    the result by inspecting the triangular regions near hex edges.
    """
    inner_radius, x_dist, y_dist = _hex_dimensions_flat(radius)
    col_estimate = int(x // x_dist)
    y_shifted = y - (col_estimate % 2) * inner_radius
    row_estimate = int(round(y_shifted // y_dist))
    local_x = x - col_estimate * x_dist
    local_y = y_shifted - row_estimate * y_dist

    threshold = radius * abs((0.5 - local_y / y_dist))

    if local_x > threshold:
        col = col_estimate
        row = row_estimate
    else:
        col = col_estimate - 1
        row = row_estimate - (col & 1) + int(local_y > inner_radius)

    return Hexagon(row, col)


def xy_to_rc_pointy(x, y, radius) -> Hexagon:
    """Convert pixel coordinates to hex grid coordinates for pointy-top hexagons.

    :param x: X coordinate in pixels.
    :type x: float | int
    :param y: Y coordinate in pixels.
    :type y: float | int
    :param radius: Hexagon outer radius in pixels.
    :type radius: int
    :return: The corresponding :class:`pyhexlib.hexagons.Hexagon`.
    :rtype: Hexagon
    """
    inner_radius, x_dist, y_dist = _hex_dimensions_pointy(radius)

    row_estimate = int(y // y_dist)
    x_shifted = x - (row_estimate % 2) * inner_radius

    col_estimate = int(round(x_shifted // x_dist))

    local_y = y - row_estimate * y_dist
    local_x = x_shifted - col_estimate * x_dist
    threshold = radius * abs((0.5 - local_x / x_dist))

    if local_y > threshold:
        col = col_estimate
        row = row_estimate
    else:
        row = row_estimate - 1
        col = col_estimate - (row & 1) + int(local_x > inner_radius)

    return Hexagon(row, col)


# ----------------------------------- Direction Calculation -----------------------------------

def compute_direction(p1, p2):
    """Compute the hex :class:`pyhexlib.basic.Direction` from ``p1`` to ``p2``.

    :param p1: Starting hex as a (row, col) tuple or an object with
        ``row`` and ``col`` attributes.
    :type p1: tuple[int, int] | object
    :param p2: Target hex as a (row, col) tuple or an object with
        ``row`` and ``col`` attributes.
    :type p2: tuple[int, int] | object
    :return: A direction enum value or ``None`` if the cells are not
        direct neighbors.
    :rtype: pyhexlib.basic.Direction | None
    """
    def to_rc(p):
        try:
            return int(p[0]), int(p[1])
        except Exception:
            return int(getattr(p, "row")), int(getattr(p, "col"))

    r1, c1 = to_rc(p1)
    r2, c2 = to_rc(p2)
    d = (r2 - r1, c2 - c1)

    parity = c1 & 1 if pyhexlib.is_flat else r1 & 1

    mapping = b.nb_dir_mapping(parity)

    return mapping.get(d, None)


def compute_angle(start: Point, target: Point) -> int:
    """Compute the angle in degrees from ``start`` to ``target``.

    :param start: Start point as :class:`pygame.Vector2`.
    :type start: pygame.Vector2
    :param target: Target point as :class:`pygame.Vector2`.
    :type target: pygame.Vector2
    :return: Angle in degrees (0..359), adjusted for the current
        hex orientation so that 0 points 'up' for flat-top grids.
    :rtype: int
    """
    dx, dy = target - start
    radians = atan2(dy, dx)
    degrees = - radians * 180 / pi  # absolute angle from to positive x-axis (math standard) to clockwise angle from positive x-axis (pygame standard)
    if pyhexlib.is_flat:
        degrees -= 90  # adjust so that 0° points to the top (NORTH)
    return round((degrees + 360) % 360)


def draw_centered(surface: pygame.Surface, image: pygame.Surface, position: tuple[int, int]) -> pygame.Surface:
    """Blit ``image`` onto ``surface`` so its center matches ``position``.

    :param surface: Destination surface.
    :type surface: pygame.Surface
    :param image: Source image surface to blit.
    :type image: pygame.Surface
    :param position: Pixel coordinates (x, y) where the image center
        should be placed.
    :type position: tuple[int, int]
    :return: The destination surface (same object passed in).
    :rtype: pygame.Surface
    """
    surface.blit(image, (int(position[0] - image.get_width() / 2), int(position[1] - image.get_height() / 2)))
    return surface


# ------------------------------ Rotation Helpers -----------------------------------

def rotate_image_to_direction(image, direction: Direction):
    """Rotate an image surface to match a hex grid direction.

    :param image: Image surface to rotate.
    :type image: pygame.Surface
    :param direction: Hex direction to rotate to.
    :type direction: pyhexlib.basic.Direction
    :return: Rotated surface.
    :rtype: pygame.Surface
    """
    angle = ANGLES[pyhexlib.get_orientation()].get(direction, 0)
    return pygame.transform.rotate(image, angle)


def rotate_image(image, angle: int = 0):
    """Rotate an image surface by an absolute angle in degrees.

    :param image: Image surface to rotate.
    :type image: pygame.Surface
    :param angle: Rotation angle in degrees (clockwise).
    :type angle: int
    :return: Rotated surface.
    :rtype: pygame.Surface
    """
    return pygame.transform.rotate(image, angle)
