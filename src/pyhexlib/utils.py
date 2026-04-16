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
from typing import Callable

import pygame

from pyhexlib.layers import HexGridManager, CoordinateGridLayer, HexColor, OutlineGridLayer
from pyhexlib.render import HexGridRenderer


# ------------------------------ Coordinate Grid Toggle -----------------------------------


def toggle_layer(layers: HexGridManager, layer: str | int) -> bool:
    layers.set_visible(layer, not layers.is_visible(layer))


def toggle_coordinate_layer(layers: HexGridManager, font_color: HexColor = (0, 0, 0), font_size: int = 12) -> bool:
    coordinate_layer = layers.get_layer("_coordinates")
    if coordinate_layer:
        layers.remove_layer("_coordinates")
        return False
    else:
        coordinate_grid = CoordinateGridLayer("_coordinates", visible=True, font_family="Courier",
                                              font_color=font_color, font_size=font_size)
        layers.add_layer(coordinate_grid)
        return True


def toggle_background(renderer):
    renderer.background_visible = not renderer.background_visible


# ------------------------------ Scrolling Handler -----------------------------------


def handle_scrolling_event(event: pygame.event.Event, renderer: HexGridRenderer) -> tuple[int, int] | None:
    if event.type in [pygame.KEYDOWN]:
        if event.key == pygame.K_UP:
            renderer.scroll_v(-1)
            return 0, -1
        elif event.key == pygame.K_DOWN:
            renderer.scroll_v(+1)
            return 0, +1
        elif event.key == pygame.K_LEFT:
            renderer.scroll_h(-1)
            return -1, 0
        elif event.key == pygame.K_RIGHT:
            renderer.scroll_h(+1)
            return +1, 0

    return None


# ------------------------------ Rounded Corners Utility --------------------------------


def round_edges(surface: pygame.Surface, radius: int, in_place: bool = True) -> pygame.Surface:
    if radius <= 0:
        return surface if in_place else surface.copy()

    # Falls nicht in_place: erstelle eine Kopie mit SRCALPHA und arbeite auf dieser
    if not in_place:
        target = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        # Blit die originale Surface auf die neue, so bleibt die Originaloberfläche unverändert
        target.blit(surface, (0, 0))
    else:
        # Versuche, direkte Modifikation: stelle sicher, dass die Surface per-pixel-Alpha unterstützt
        if not surface.get_flags() & pygame.SRCALPHA:
            # convert_alpha erzeugt eine neue Surface; wir weisen sie zu und geben sie zurück.
            surface = surface.convert_alpha()
        target = surface

    w, h = target.get_size()
    # radius darf nicht größer als die halbe kleinere Seite sein
    max_radius = min(w, h) // 2
    if radius > max_radius:
        radius = max_radius

    # Maske erzeugen: transparente Fläche, gefülltes weißes Rechteck mit border_radius
    mask = pygame.Surface((w, h), pygame.SRCALPHA)
    mask.fill((0, 0, 0, 0))
    rect = mask.get_rect()
    pygame.draw.rect(mask, (255, 255, 255, 255), rect, border_radius=radius)

    # Maske auf die Surface anwenden: Multiplikation von RGBA-Kanälen
    target.blit(mask, (0, 0), special_flags=pygame.BLEND_RGBA_MULT)

    return target


def shadow_image(surface: pygame.Surface, shadow_color: HexColor = (0, 0, 0), alpha: int = 128) -> pygame.Surface:
    shadow = surface.copy()
    shadow.fill((*shadow_color, alpha), special_flags=pygame.BLEND_RGBA_MULT)
    return shadow


# ---------------------------------- Fancy renderers -----------------------------------

# ------------------------------- Outline Layer Renderer -----------------------------------


def _render_outline_layer_imprinted(surface, grid: OutlineGridLayer, hexagons, color_dark: HexColor,
                                    color_light: HexColor) -> pygame.Surface:
    for h in hexagons:
        pygame.draw.polygon(surface, color_dark, hexagons.edges(h), 2)
        edges = [(edge[0] + 1, edge[1] + 2) for edge in hexagons.edges(h)[3:]]
        pygame.draw.lines(surface, color_light, False, edges, 2, )
    for h in grid.hexagons:
        color, width = grid.get_style(h)
        pygame.draw.polygon(surface, color, hexagons.edges(h), width)

    return surface


def outline_layer_imprinted_renderer(color_dark: HexColor = (50, 50, 50),
                                     color_light: HexColor = (200, 200, 200)) -> Callable:
    """Factory: returns a renderer function that calls
    `render_outline_layer_imprinted` with the provided default colors bound.

    The returned function has the same call signature as
    `render_outline_layer_imprinted(surface, grid, hexagons, ...) -> pygame.Surface`.
    """

    def renderer(surface: pygame.Surface, grid: OutlineGridLayer, hexagons) -> pygame.Surface:
        # Forward to the main implementation while binding the colors
        return _render_outline_layer_imprinted(surface, grid, hexagons,
                                               color_dark=color_dark, color_light=color_light)

    return renderer
