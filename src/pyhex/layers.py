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

from abc import ABC, abstractmethod
from collections import namedtuple
from typing import List, TypeAlias, Tuple

import pygame

from pyhex.basic import AxialCoordinate, Direction, Hexagon
from pyhex.basic import axial_coordinates
from pyhex.graphic import Point, Offset
from pyhex.hexagons import HexagonalGrid
from pyhex.tokens import Token

__all__ = ["Border", "HexColor", "StyledGridLayer", "AxialCoordinateHexGridLayer", "OutlineGridLayer",
           "FillGridLayer", "TextGridLayer", "CoordinateGridLayer", "ImageGridLayer",
           "SimpleImageGridLayer", "TokenGridLayer", "PathGridLayer", "ValueGridLayer", "TerrainGridLayer",
           "HexGridLayer", "HexGridManager", "Token"]

# ------------------------------ Color Type Alias -------------------------------

HexColor: TypeAlias = Tuple[int, int, int] | Tuple[int, int, int, int] | pygame.Color

Font = namedtuple("Font", ["name", "size", "color"])

Bounds = namedtuple("Bounds", ["r_min", "c_min", "r_max", "c_max"])

Clipping = Bounds


# ------------------------------ Borders -------------------------------

class Border:
    """
    A border between two Hexagons, or the border of a HexGrid.
    """

    def __init__(self, rc: Hexagon, direction: Direction) -> None:
        self.rc = rc
        self.direction = direction


# -------------------------------- Grids -----------------------------

class HexGridLayer(ABC):
    """
    An abstract base class for all hexagon grids. It keeps track of the hexagons in the grid and whether the grid is visible.
    """

    def __init__(self, grid_id: str, hexagons: HexagonalGrid = None, visible: bool = True, comment: str = None) -> None:
        self.id = grid_id
        self.visible = visible
        self.dirty = True
        self.hexagons = hexagons if hexagons else {}
        self.comment = comment if comment else ""

    def clear(self):
        self.hexagons.clear()
        self.dirty = True

    def is_dirty(self) -> bool:
        return self.dirty

    def set_dirty(self) -> None:
        self.dirty = True

    def set_clean(self) -> None:
        self.dirty = False

    def __repr__(self) -> str:
        return f"Grid(id={self.id}, visible={self.visible} , hexagons={len(self.hexagons)}, comment={self.comment!r})"


# # ------------------------------ Coordinate Grids -------------------------------

class AxialCoordinateHexGridLayer(HexGridLayer):
    def __init__(self, grid_id: str, hexagons: HexagonalGrid = None, visible: bool = False,
                 comment: str = None) -> None:
        super().__init__(grid_id, hexagons, visible=visible, comment=comment)
        self.coord = axial_coordinates(hexagons)

    def convert(self, rc: Hexagon) -> AxialCoordinate:
        return self.coord.get(rc, None)


# ------------------------------ Value Grids -------------------------------

class ValueGridLayer(HexGridLayer):
    def __init__(self, grid_id: str, hexagons: HexagonalGrid = None, default_value=None, visible=False,
                 comment: str = None) -> None:
        super().__init__(grid_id, hexagons, visible=visible, comment=comment)
        self.default_value = default_value

    def set_value(self, rc: Hexagon, value: object) -> None:
        self.hexagons[rc] = value
        self.dirty = True

    def get_value(self, rc: Hexagon) -> object:
        return self.hexagons.get(rc, self.default_value)


# ------------------------------ Color Grids -------------------------------

class StyledGridLayer(HexGridLayer):
    """
    A grid that stores styles (color and width) for each hexagon.
    0 width means fill, >0 means outline with given width.
    """

    def __init__(self, grid_id: str, hexagons: List[Hexagon], visible: bool = True, default_color=None, default_width=1,
                 comment: str = None) -> None:
        super().__init__(grid_id, hexagons, visible=visible, comment=comment)
        self.default_style = default_color, default_width

    @property
    def default_color(self) -> HexColor | None:
        return self.default_style[0]

    @property
    def default_width(self) -> HexColor | None:
        return self.default_style[1]

    def set_color(self, rc, color: HexColor) -> None:
        if isinstance(rc, list):
            for rci in rc:
                self.hexagons[rci] = color, self.default_width
        else:
            self.hexagons[rc] = color, self.default_width

        self.dirty = True

    def get_color(self, rc):

        return self.get_style(rc)[0] if self.get_style(rc) else None

    def get_style(self, rc):
        return self.hexagons.get(rc, None)

    def set_style(self, rc: Hexagon, color: HexColor, width: int) -> None:
        if isinstance(rc, list):
            for rci in rc:
                self.hexagons[rci] = color, width
        else:
            self.hexagons[rc] = color, width

        self.dirty = True

    def remove_style(self, rc: Hexagon) -> None:
        del self.hexagons[rc]
        self.dirty = True

    def __repr__(self) -> str:
        hex_count = len(self.hexagons) if self.hexagons is not None else 0

        default_color = repr(self.default_color)
        default_width = repr(self.default_width)
        return (
            f"StyledGrid(if={self.id!r}, visible={self.visible}, "
            f"default_color={default_color}, default_width={default_width}, "
            f"hexagons={hex_count})"
        )


# ------------------------------ FillGrid -------------------------------

class FillGridLayer(StyledGridLayer):
    """
    A grid that stores fill colors for each hexagon.
    """

    def __init__(self, grid_id, hexagons=None, visible=True, default_color: HexColor = None, comment=None) -> None:
        super().__init__(grid_id, hexagons, visible=visible, default_color=default_color, default_width=0,
                         comment=comment)


# ------------------------------ OutlineGrid -------------------------------

class OutlineGridLayer(StyledGridLayer):
    """
    A grid that stores outline colors and widths for each hexagon.
    """

    def __init__(self, grid_id, hexagons=None, visible=True, default_color: HexColor = None, default_width=1,
                 comment=None) -> None:
        super().__init__(grid_id, hexagons, visible=visible, default_color=default_color, default_width=default_width,
                         comment=comment)
        if default_width < 1:
            raise ValueError("default_width must be at least 1 for an OutlineGrid")


# ------------------------------ Image Grids -------------------------------

class ImageGridLayer(HexGridLayer):
    def __init__(self, grid_id: str, hexagons=None, visible: bool = True, comment=None) -> None:
        super().__init__(grid_id=grid_id, hexagons=hexagons, visible=visible, comment=comment)

    @abstractmethod
    def get_image(self, rc: Hexagon) -> pygame.Surface:
        ...

    def get_offset(self, rc: Hexagon) -> Offset:
        return self.hexagons.get(rc, None)[1] if self.hexagons.get(rc, None) else (0, 0)


# ------------------------------- Simple Image Grids -------------------------------

class SimpleImageGridLayer(ImageGridLayer):
    def __init__(self, grid_id: str, hexagons=None, visible: bool = True, comment=None) -> None:
        super().__init__(grid_id=grid_id, hexagons=hexagons, visible=visible, comment=comment)

    def get_image(self, rc: Hexagon) -> pygame.Surface:
        return self.hexagons.get(rc, None)[0] if self.hexagons.get(rc, None) else None

    def get_offset(self, rc: Hexagon) -> Point:
        return self.hexagons.get(rc, None)[1] if self.hexagons.get(rc, None) else (0, 0)

    def set_image(self, rc: Hexagon, image: pygame.Surface, offset: Offset = Offset(0, 0)) -> None:
        self.hexagons[rc] = image, offset
        self.dirty = True

    def remove_image(self, rc: Hexagon) -> None:
        if rc in self.hexagons:
            del self.hexagons[rc]
            self.dirty = True

        # ------------------------------ Token Grids -------------------------------


class TokenGridLayer(ImageGridLayer):
    def __init__(self, grid_id: str, hexagons=None, visible: bool = True, comment: str = None) -> None:
        super().__init__(grid_id=grid_id, hexagons=hexagons, visible=visible, comment=comment)

    def set_token(self, rc: Hexagon, token: Token, offset=(0, 0)) -> None:
        self.hexagons[rc] = token, offset
        self.dirty = True

    def get_token(self, rc: Hexagon) -> Token:
        return self.hexagons.get(rc, None)[0] if self.hexagons.get(rc, None) else None

    def remove_token(self, rc: Hexagon) -> None:
        if rc in self.hexagons:
            del self.hexagons[rc]
        self.dirty = True

    def get_image(self, rc: Hexagon) -> pygame.Surface:
        token = self.get_token(rc)
        return token.image if token else None

    def get_token_id(self, rc):
        token = self.get_token(rc)
        return token.id if token else None


# ------------------------------ Path Grids -------------------------------

class PathGridLayer(HexGridLayer):
    def __init__(self, grid_id: str, hexagons: HexagonalGrid = None, visible=True, color: HexColor = (0, 0, 0),
                 width: int = 5, comment: str = None) -> None:
        super().__init__(grid_id=grid_id, hexagons=hexagons, visible=visible, comment=comment)
        self.color = color
        self.width = width

    def set_path(self, path: List[Hexagon]) -> None:
        for n, rc in enumerate(path):
            self.hexagons[rc] = n
        self.visible = True
        self.dirty = True

    def get_path(self) -> List[Hexagon]:
        return list(self.hexagons.keys())

    def remove_path(self) -> None:
        self.hexagons = {}
        self.visible = False
        self.dirty = True

    # ------------------------------ Text Grids -------------------------------


class TextGridLayer(ValueGridLayer):
    def __init__(self, grid_id: str, hexagons: HexagonalGrid = None, font_family="Arial",
                 font_color: HexColor = (0, 0, 0),
                 font_size: int = 12, visible=True, comment: str = None) -> None:
        super().__init__(grid_id=grid_id, hexagons=hexagons, visible=visible, comment=comment)
        self.font = Font(font_family, font_color, font_size)


class CoordinateGridLayer(TextGridLayer):

    def __init__(self, grid_id: str, visible=False, font_family="Arial", font_color: HexColor = (0, 0, 0),
                 font_size: int = 12,
                 comment=None) -> None:
        super().__init__(grid_id=grid_id, visible=visible, comment=comment, font_family=font_family,
                         font_color=font_color,
                         font_size=font_size)

    def get_value(self, rc: Hexagon) -> str:
        return f"({rc.row},{rc.col})"


# ------------------------------ Terrain Grids -------------------------------

class TerrainGridLayer(FillGridLayer):
    def __init__(self, grid_id: str, hexagons=None, visible: bool = True, default_terrain=None, comment: str = None):
        super().__init__(grid_id=grid_id, hexagons=hexagons, visible=visible, default_color=None, comment=comment)
        self.terrain_colors = {}
        self.default_terrain = default_terrain

    def set_terrain_color(self, terrain, color):
        self.terrain_colors[terrain] = color

    def get_color(self, rc):
        terrain = self.hexagons.get(rc, self.default_terrain)
        return self.terrain_colors.get(terrain, None)


# ------------------------------ Trigger Grids -------------------------------

class TriggerGridLayer(HexGridLayer):
    def __init__(self, grid_id: str, hexagons: HexagonalGrid = None) -> None:
        super().__init__(grid_id, hexagons)


# ------------------------------ HexGridManager -------------------------------

class HexGridManager:
    def __init__(self, hexagons: HexagonalGrid) -> None:
        self.hexagons = hexagons
        self.size = self.hexagons.size
        self.r_min, self.c_min, self.r_max, self.c_max = self.hexagons.bounds

        self.axial_coordinates = self.hexagons.axial_coordinates
        self.layers = {}
        self.dirty_layers = set()

    # ---------------------------- Grid Properties -------------------------------

    @property
    def width(self) -> int:
        return self.size[0]

    @property
    def height(self) -> int:
        return self.size[1]

    @property
    def visible_layers(self) -> List[HexGridLayer]:
        return [grid for grid in self.layers.values() if grid.visible]

    # ---------------------------- Hexagon Selection -------------------------------

    def get_hexagons(self, clipping: Clipping = None) -> HexagonalGrid:
        """
        Return a HexagonalGrid containing only the hex coordinates from this manager
        that fall within the rectangular clipping area.

        Parameters:
        - clipping: either None (return full grid), or a pair (top_left, bottom_right),
          where each is an (r, c) tuple. Also accepts an object with attributes
          `top_left` and `bottom_right` (each an (r, c) tuple).

        The bounds are inclusive. The method is robust to the order of coordinates
        and will normalize min/max for each axis.
        """
        if clipping is None:
            return self.hexagons

        r_min, c_min, r_max, c_max = clipping
        r_min = min(r_min, r_max)
        r_max = max(r_min, r_max)
        c_min = min(c_min, c_max)
        c_max = max(c_min, c_max)

        selected = [h for h in self.hexagons if (r_min <= h[0] <= r_max and c_min <= h[1] <= c_max)]

        return HexagonalGrid(selected)

    # ---------------------------- Layer Management -------------------------------

    def add_layer(self, grid: HexGridLayer) -> HexGridLayer:
        self.layers[grid.id] = grid
        return self

    def get_layer(self, grid_id: str) -> HexGridLayer | None:
        return self.layers.get(grid_id, None)

    def remove_layer(self, grid_id: str) -> None:
        if grid_id in self.layers:
            del self.layers[grid_id]

    # ---------------------------- Layer Visibility -------------------------------

    def set_visible(self, name: str, visible: bool) -> None:
        grid = self.get_layer(name)
        if grid:
            grid.visible = visible

    def is_visible(self, grid_name):
        return self.get_layer(grid_name).visible if self.get_layer(grid_name) else False

    # ------------------------------ Representation -------------------------------

    def __repr__(self) -> str:
        visible = [name for name, g in self.layers.items() if getattr(g, "visible", False)]
        all_grids = list(self.layers.keys())
        return (
            f"Grids(size={self.size}, bounds=({self.hexagons.bounds}), "
            f"hexagons={len(self.hexagons)}, grids={all_grids}, visible={visible})"
        )
