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
    return hex_corners_flat(center, radius) if pyhexlib.is_flat else hex_corners_pointy(center, radius)


def hex_dimensions(radius: int) -> tuple[float, int, int]:
    return _hex_dimensions_flat(radius) if pyhexlib.is_flat else _hex_dimensions_pointy(radius)


# ----------------------------------- Screen Size Calculation -----------------------------------

def compute_screen_size(rows: int, cols: int, radius: int) -> Size:
    return _screen_size_flat(rows, cols, radius) if pyhexlib.is_flat else _screen_size_pointy(rows, cols, radius)


def compute_viewport_bounds(screen_size: Size, radius: int, topleft: Hexagon) -> b.Bounds:
    return b.Bounds(*topleft, topleft[0] + 20, topleft[1] + 20)


# ----------------------------------- Pixel to Hex Conversion -----------------------------------

def xy_to_rc(x, y, radius: int) -> Hexagon:
    return xy_to_rc_flat(x, y, radius) if pyhexlib.is_flat else xy_to_rc_pointy(x, y, radius)


# ----------------------------------- Internal methods -----------------------------------

def hex_corner_with_offset(center: Point, size: int, i: int, angle_offset) -> Point:
    """Return a corner point for a hexagon centered at `center`.
    """

    angle_deg = 60 * i + angle_offset
    angle_rad = pi / 180 * angle_deg
    x = center.x + size * cos(angle_rad) * pyhexlib.sx
    y = center.y + size * sin(angle_rad) * pyhexlib.sy
    return Point(round(x), round(y))


def hex_corners_pointy(center: Point, size: int) -> list[Point]:
    return [hex_corner_with_offset(center, size, j, 30) for j in range(6)]


def hex_corners_flat(center: Point, size: int) -> list[Point]:
    return [hex_corner_with_offset(center, size, j, 0) for j in range(6)]


# --------------------------------------------------------------------------------------

def hex_center(r, c, x_dist, y_dist, offset, inner_radius, radius: int) -> Point:
    if pyhexlib.is_flat:
        return hex_center_flat(r, c, x_dist, y_dist, offset, inner_radius, radius)
    else:
        return hex_center_pointy(r, c, x_dist, y_dist, offset, inner_radius, radius)


def hex_center_flat(r, c, x_dist, y_dist, offset, inner_radius, radius):
    x = int(x_dist * c + radius) - offset.x
    y = int(y_dist * (r + (c & 1) / 2) + inner_radius) - offset.y
    return Point(x, y)


def hex_center_pointy(r, c, x_dist, y_dist, offset, inner_radius, radius):
    x = int(x_dist * (c + (r & 1) / 2) + inner_radius) - offset.x
    y = int(y_dist * r + radius) - offset.y
    return Point(x, y)


def compute_offset(r, c, x_dist, y_dist, offset, inner_radius, radius) -> Point:
    """Compute the pixel offset to left top corner the viewport around the origin hex."""
    origin_center = hex_center(r, c, x_dist, y_dist, offset, inner_radius, radius)
    if pyhexlib.is_flat:
        offset = origin_center - Point(radius, y_dist // 2)
    else:
        offset = origin_center - Point(x_dist // 2, radius)
    return Point(offset)


def compute_area(top, left, rows, cols, x_dist, y_dist) -> Rectangle:
    return Rectangle(left * x_dist, top * y_dist, (left + cols) * x_dist, (top + rows) * y_dist)


# ----------------------------------- Hexagon Geometry -----------------------------------

def _hex_dimensions_flat(radius: int) -> tuple[float, int, int]:
    inner_radius = sqrt(3) * radius / 2
    x_dist, y_dist = round(3 * radius // 2 * pyhexlib.sx), round(2 * inner_radius * pyhexlib.sy)
    return inner_radius, x_dist, y_dist


def _hex_dimensions_pointy(radius: int) -> tuple[float, int, int]:
    inner_radius = sqrt(3) * radius / 2
    x_dist, y_dist = round(2 * inner_radius * pyhexlib.sx), round(3 * radius // 2 * pyhexlib.sy)
    return inner_radius, x_dist, y_dist


# ----------------------------------- Screen Size Calculation -----------------------------------

def _screen_size_flat(rows: int, cols: int, radius: int) -> tuple[int, int]:
    inner_radius, xdist, ydist = _hex_dimensions_flat(radius)
    width = round(xdist * (cols - 1) + radius * 2)
    height = round(ydist * rows + ydist // 2)
    return width, height


def _screen_size_pointy(rows: int, cols: int, radius: int) -> tuple[int, int]:
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
    angle = ANGLES[pyhexlib.get_orientation()].get(direction, None)
    return angle


def angle_to_direction(angle: int) -> Direction:
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
    def to_rc(p):
        try:
            return int(p[0]), int(p[1])
        except Exception:
            return int(getattr(p, "row")), int(getattr(p, "col"))

    r1, c1 = to_rc(p1)
    r2, c2 = to_rc(p2)
    d = (r2 - r1, c2 - c1)

    parity = c1 & 1 if pyhexlib.is_flat else r1 & 1

    mapping = b._nb_dir_mapping(parity)

    return mapping.get(d, None)


def compute_angle(start: Point, target: Point) -> int:
    dx, dy = target - start
    radians = atan2(dy, dx)
    degrees = - radians * 180 / pi  # absolute angle from to positive x-axis (math standard) to clockwise angle from positive x-axis (pygame standard)
    if pyhexlib.is_flat:
        degrees -= 90  # adjust so that 0° points to the top (NORTH)
    return round((degrees + 360) % 360)


def draw_centered(surface: pygame.Surface, image: pygame.Surface, position: tuple[int, int]) -> pygame.Surface:
    """
    Blit an image such that its center matches the given position.

    position: (x,y) pixel coordinates for the image center.
    """
    surface.blit(image, (int(position[0] - image.get_width() / 2), int(position[1] - image.get_height() / 2)))


# ------------------------------ Rotation Helpers -----------------------------------

def rotate_image_to_direction(image, direction: Direction):
    angle = ANGLES[pyhexlib.get_orientation()].get(direction, 0)
    return pygame.transform.rotate(image, angle)


def rotate_image(image, angle: int = 0):
    return pygame.transform.rotate(image, angle)
