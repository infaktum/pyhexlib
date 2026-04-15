import logging
from importlib import resources
from math import sqrt

import pygame
from pygame.font import Font

import pyhexlib
from pyhexlib import graphic as g
from pyhexlib.assets import Assets
from pyhexlib.graphic import Point, TRANSPARENT
from pyhexlib.hexagons import Hexagon
from pyhexlib.layers import OutlineGridLayer, FillGridLayer, ImageGridLayer, PathGridLayer, HexGridManager, \
    StyledGridLayer, HexColor, ValueGridLayer, HexGridLayer
from pyhexlib.viewport import HexGridViewport, Hexagons

# ---------------------------------------- Logger ------------------------------------------------

LOGGER = pyhexlib.get_logger(__name__)


# ----------------------------------------- HexGridRenderer -----------------------------------------------


class HexGridRenderer:

    def __init__(self, layers: HexGridManager, radius: int = 50, bg_color: HexColor = (100, 100, 100),
                 bg_image: pygame.Surface = None, assets: Assets = None, visible_size: g.Size = None,
                 origin: Hexagon = None) -> None:

        self.layers = layers
        self.radius = radius
        self.bg_color = bg_color
        self.assets = assets

        self.inner_radius = sqrt(3) * self.radius / 2

        _, self.x_dist, self.y_dist = g.hex_dimensions(self.radius)

        if visible_size is not None:
            self.visible_size = visible_size
            self.screen_size = self.width, self.height = g.compute_screen_size(*self.visible_size, self.radius)
        else:
            self.visible_size = self.layers.size
            self.screen_size = self.width, self.height = g.compute_screen_size(*self.layers.size, self.radius)

        self.origin = origin if origin is not None else self.layers.r_min, self.layers.c_min

        self.viewport = HexGridViewport(hexagonal_grid=self.layers.hexagons, radius=self.radius, origin=self.origin,
                                        visible_size=self.visible_size)

        self.viewport_offset = self._compute_viewport_offset()

        self.bg_image = bg_image if bg_image is not None else None
        self.background_visible = bg_image is not None

        self.surface = pygame.Surface(self.screen_size, pygame.SRCALPHA)

        self._render_functions = {
            OutlineGridLayer.__name__: _render_outline_layer,
            FillGridLayer.__name__: _render_fill_layer,
            ImageGridLayer.__name__: _render_image_layer,
            ValueGridLayer.__name__: _render_value_layer,
            PathGridLayer.__name__: _render_path_layer
        }

        self.surfaces = {}
        self.dirty = True

    # ----------------------------------- Internal Methods -----------------------------------

    def point_to_hex(self, p: Point) -> Hexagon:
        return g.xy_to_rc(*self._xy_with_offset(p), self.radius)

    def _xy_with_offset(self, p: Point):
        offset = self._compute_offset()
        return p + offset

    def _compute_offset(self) -> Point:
        return g.compute_offset(*self.origin, self.x_dist, self.y_dist, self.viewport_offset,
                                self.inner_radius, self.radius)

    def _compute_viewport_offset(self) -> Point:
        return -Point(self.viewport.origin.col * self.x_dist, self.viewport.origin.row * self.y_dist)

    # ----------------------------------- Scrolling Methods -----------------------------------

    def set_origin(self, origin: Hexagon):
        """Set the origin hex for rendering, which determines the clipping bounds."""
        self.origin = origin
        self.viewport.origin = origin
        self.viewport_offset = self._compute_viewport_offset()
        self.dirty = True

    def scroll(self, delta_r, delta_c):
        """Scroll the grid by changing the origin hex's row and column coordinates."""
        self.viewport.move_by(delta_r, delta_c)
        self.viewport_offset = self._compute_viewport_offset()
        self.dirty = True

    def scroll_h(self, delta_c: int):
        self.scroll(0, delta_c)

    def scroll_v(self, delta_r: int):
        self.scroll(delta_r, 0)

    # ----------------------------------- Public Methods -----------------------------------

    def get_layer(self, name) -> StyledGridLayer:
        """Retrieves a named grid from the grid's container."""
        return self.layers.get_layer(name)

    def hex_at(self, x, y) -> Hexagon:
        return self.point_to_hex(Point(x, y))

    def get_angle(self, h1: Hexagon, h2: Hexagon) -> int:
        """Return the angle in degrees from hex h1 to hex h2."""
        p1 = self.viewport.center(h1)
        p2 = self.viewport.center(h2)
        return g.compute_angle(p1, p2)

    # ----------------------------------- Rendering Methods -----------------------------------

    def render(self) -> pygame.Surface:
        self.surface.fill(self.bg_color)
        self.render_background()

        self.render_layers()
        self.dirty = False
        return self.surface

    def render_background(self):

        if self.bg_image is not None and self.background_visible:
            area = g.compute_area(*self.viewport.bounds.topleft, self.viewport.rows, self.viewport.cols,
                                  self.viewport.x_dist,
                                  self.viewport.y_dist)
            self.surface.blit(self.bg_image, dest=Point(0, 0), area=area)
        else:
            self.surface.fill(self.bg_color)

    def render_layers(self):
        for grid in self.layers.visible_layers:

            layer_surface = self.get_surface(grid)
            if self.dirty or grid.is_dirty():
                LOGGER.debug(f'Rendering layer {grid.id} of type {type(grid).__name__}')
                layer_surface.fill(TRANSPARENT)  # Clear the cached surface before re-rendering
                render_fn = self.get_renderer(grid)
                layer_surface = render_fn(layer_surface, grid, self.viewport.hexagons)
                grid.set_clean()

            y = self.y_dist // 2 if self.viewport.origin.col & 1 else 0
            self.surface.blit(layer_surface, (0, y))

    # ----------------------------------- Rendering strategy -----------------------------------

    def get_renderer(self, layer: HexGridLayer):
        LOGGER.debug(f'Getting renderer for {type(layer).__name__}')
        if layer.id in self._render_functions:
            return self._render_functions[layer.id]

        layer_type = type(layer).__name__

        if layer_type in self._render_functions:
            return self._render_functions[layer_type]

        # If no renderer is found for the exact type, check the class hierarchy (MRO) for a compatible renderer.
        for cls in [c.__name__ for c in layer.__class__.mro()]:
            if cls in self._render_functions:
                # Register the found renderer for the original layer type for faster future lookups.
                self._render_functions[layer_type] = self._render_functions[cls]
                return self._render_functions[cls]

        raise KeyError(
            f"No renderer registered for layer type {layer_type}, registered types: {list(self._render_functions.keys())}")

    def set_renderer(self, layer_type: type | str, render_fn) -> None:
        """Register a custom rendering function for a specific layer type."""
        register_name = layer_type.__name__ if type(layer_type) != str else layer_type
        self._render_functions[register_name] = render_fn
        logging.log(logging.INFO, f'Registering custom renderer "{render_fn}" for layer  "{register_name}"')

    # ------------------------------------ Caching Mechanism -----------------------------------

    def get_surface(self, layer: HexGridLayer) -> pygame.Surface:
        """Get the rendered surface for a given layer, using caching to optimize performance."""
        if layer.id in self.surfaces:
            return self.surfaces[layer.id]
        render_fn = self.get_renderer(layer)
        rendered_surface = render_fn(pygame.Surface(self.screen_size, pygame.SRCALPHA), layer, self.viewport.hexagons)
        self.surfaces[layer.id] = rendered_surface
        return rendered_surface

    # ----------------------------------- Visibility Methods -----------------------------------

    def set_layer_visible(self, grid_name: str, visible: bool) -> None:
        """
        Set visibility of a named grid in the grid's container.
        """
        self.layers.set_visible(grid_name, visible)

    def is_layer_visible(self, grid_name: str) -> bool:
        """
        Check visibility of a named grid in the grid's container.
        """
        return self.layers.is_visible(grid_name)

    def toggle_bg_visible(self) -> None:
        """
        Toggle between background image and solid color fill.
        """
        self.background_visible = not self.background_visible

    def toggle_visible(self, grid_name: str) -> None:
        """
        Toggle visibility of a named grid in the grid's container.
        """
        self.set_layer_visible(grid_name, not self.is_layer_visible(grid_name))

    # ----------------------------------- Developer Representation -----------------------------------

    def __repr__(self) -> str:
        """
        Return a concise developer representation showing:
        - hex size, surface size, background color,
        - grids container name, number of cached hexes, offsets, and whether assets are set.
        """
        grids_name = getattr(self.layers, "name", None) or type(self.layers).__name__
        hex_count = len(self.viewport.hexagons)
        return (f"<{HexGridRenderer.__name__} radius={self.radius!r} visible_size={self.visible_size!r} "
                f"bg_color={self.bg_color!r} grids={grids_name!r} "
                f"hexes={hex_count} offset={self.viewport_offset!r} assets_set={self.assets is not None}> ")


# -----------------------------------Standard Layer Rendering Functions -------------------------------------------


# --------------------------------- Outline Layer Rendering Function -------------------------------------------

def _render_outline_layer(surface: pygame.Surface, grid: StyledGridLayer, hexagons: Hexagons) -> pygame.Surface:
    """
    Render an OutlineGrid.

    Procedure:
    - Fill all cached hexes with grid.default_color if provided.
    - Then draw per-hex fills using grid.get_color(h).
    """

    color, width = grid.default_style

    LOGGER.debug(f'Rendering outline grid {grid.id}: default color={color}, width={width}')
    if color is not None:
        for h in hexagons:
            pygame.draw.polygon(surface, color, hexagons.edges(h), width)

    for h in grid.hexagons:
        color, width = grid.get_style(h)

        pygame.draw.polygon(surface, color, hexagons.edges(h), width)

    return surface


# --------------------------------- Fill Layer Rendering Function -------------------------------------------
def _render_fill_layer(surface, grid: StyledGridLayer, hexagons) -> pygame.Surface:
    """
    Render a FillGrid.

    Procedure:
    - Fill all cached hexes with grid.default_color if provided.
    - Then draw per-hex fills using grid.get_color(h).
    """

    color = grid.default_color
    surface.fill((255, 0, 0, 0))  # Clear the surface with transparent fill

    LOGGER.debug(f'Rendering fill grid {grid.id}: default color={color}')
    if color is not None:
        for h in hexagons:
            pygame.draw.polygon(surface, color, hexagons.edges(h), 0)
            pass

    for h in grid.hexagons:
        color = grid.get_color(h)
        pygame.draw.polygon(surface, color, hexagons.edges(h), 0)

    return surface


# -------------------------------- Image Layer Rendering Function -------------------------------------------

def _render_image_layer(surface, grid: ImageGridLayer, hexagons) -> None:
    """
    Render images for an ImageGrid.

    For each hex with an image, draw the image centered at the hex center.
    """
    LOGGER.debug(f"Rendering image grid {grid.id} with {len(grid.hexagons)} hexes: {grid.hexagons}")
    for h in hexagons:
        image = grid.get_image(h)
        offset = grid.get_offset(h)
        if image is not None:
            g.draw_centered(surface, image, hexagons.center(h) + offset)
    return surface


# -------------------------------- Value Layer Rendering Function -------------------------------------------


def _render_value_layer(surface, grid: ValueGridLayer, hexagons) -> pygame.Surface:
    """
    Render text labels for a TextGrid.

    Uses a pygame font with grid.font_size and blits each text centered in the hex.
    """

    font_color = (100, 100, 100, 255)
    font = load_font_from_resources()

    for h in hexagons:
        value = str(grid.get_value(h))
        if value is not None:
            text_surf = font.render(value, True, font_color)
            text_rect = text_surf.get_rect(center=hexagons.center(h))
            surface.blit(text_surf, text_rect)
    return surface


def load_font_from_resources() -> Font:
    font_font, font_size = pyhexlib.font['name'], pyhexlib.font['size']
    font_file = resources.files("pyhex.fonts").joinpath(font_font)

    with resources.as_file(font_file) as font_path:
        font = pygame.font.Font(font_path, font_size)
    return font


# --------------------------------- Path Layer Rendering Function -------------------------------------------

def _render_path_layer(surface, grid: PathGridLayer, hexagons) -> pygame.Surface:
    """
    Render a path by connecting the centers of hexes returned by grid.get_path().

    Draws a polyline with grid.color and grid.width.
    """
    LOGGER.debug(f"Rendering path grid {grid.id} with {len(grid.hexagons)} hexes: {grid.hexagons}")
    points = [hexagons.center(rc) for rc in grid.get_path()]
    if len(points) > 1:
        color, width = grid.color, grid.width
        pygame.draw.lines(surface, color, False, points, width)
    return surface
