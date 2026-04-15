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
from typing import Callable, Optional, TypeAlias

import pygame
from pygame import Surface, Vector2

import pyguilib
from pyguilib.basic import Point, Transparent
from pyguilib.components import VisibleComponent, Overlay, Rim, Button, Component, Image
from pyguilib.layout import Container
from pyguilib.widgets import Window

# ---------------------------------------- Logger ------------------------------------------------

LOGGER = pyguilib.get_logger(__name__)

# ---------------------------------- The GUI renderer  ----------------------------------


RenderFn: TypeAlias = Callable[[Component], Optional[Surface]]


class GuiRenderer:
    def __init__(self, surface: Surface):
        self.surface = surface

        self._render_functions = {
            Overlay.__name__: _render_overlay,
            Rim.__name__: _render_rim,
            Button.__name__: _render_button,
            Image.__name__: _render_image,
            Window.__name__: _render_window,
        }

    def render(self, component, pos: Point = Point(0, 0), offset: Point = Point(0, 0)) -> Surface:
        if isinstance(component, Container) and component.visible:  # Recursion over container content
            self.render_container(component, pos)

        elif isinstance(component, VisibleComponent) and component.visible and component.image:
            self.render_visible_component(component, offset, pos)

        component.dirty = False
        return self.surface

    def render_container(self, container: Container, pos: Vector2):
        size, layout = container.layout
        if container.background_image:
            self.surface.blit(container.background_image, Point(0, 0))

        for layout_item in layout:
            self.render(layout_item.component, layout_item.position, pos)

        if container.decorator:
            # container.decorator(surface=self.surface.subsurface(pygame.Rect(pos, size)))
            container.decorator(surface=self.surface.subsurface(pygame.Rect(*pos, *size)))

    def render_visible_component(self, component: VisibleComponent, offset: Vector2, pos: Vector2):
        render_fn = self.get_renderer(component)
        if render_fn is not None:
            surface = render_fn(component)
            if surface is not None:
                self.surface.blit(surface, pos + offset)

    # ----------------------------------- Rendering strategy -----------------------------------

    def get_renderer(self, component: Component) -> RenderFn:
        LOGGER.debug(f'Getting renderer for {type(component).__name__}')
        if component.id in self._render_functions:
            return self._render_functions[component.id]

        layer_type = type(component).__name__

        if layer_type in self._render_functions:
            return self._render_functions[layer_type]

        # If no renderer is found for the exact type, check the class hierarchy (MRO) for a compatible renderer.
        for cls in [c.__name__ for c in component.__class__.mro()]:
            if cls in self._render_functions:
                # Register the found renderer for the original layer type for faster future lookups.
                self._render_functions[layer_type] = self._render_functions[cls]
                return self._render_functions[cls]

        raise KeyError(
            f"No renderer registered for layer type {layer_type}, registered types: {list(self._render_functions.keys())}")

    def set_renderer(self, layer_type: type | str, render_fn: RenderFn) -> None:
        """Register a custom rendering function for a specific layer type."""
        register_name = layer_type.__name__ if type(layer_type) != str else layer_type
        self._render_functions[register_name] = render_fn
        LOGGER.log(LOGGER.INFO, f'Registering custom renderer "{render_fn}" for layer  "{register_name}"')

    # ------------------------------ --------------------------------------------

    def __repr__(self) -> str:
        """Return an English developer representation of the Renderer.

        Shows whether a surface is attached and the surface size when available.
        """
        try:
            size = self.surface.get_size() if self.surface is not None else None
        except Exception:
            size = None
        return f"{self.__class__.__name__}(surface_set={self.surface is not None!r}, surface_size={size!r})"


# ------------------------------------- Render Functions ----------------------------

def _render_overlay(overlay: Overlay):
    surface = pygame.Surface(overlay.size, flags=pygame.SRCALPHA)
    base_color = pyguilib.skin["color"]
    surface.fill(base_color)
    for window in overlay.windows:
        pygame.draw.rect(surface, Transparent, window)
    return surface


def _render_rim(rim: Rim, transparent: bool = False):
    surface = pygame.Surface(rim.size, flags=pygame.SRCALPHA)
    base_color = pyguilib.skin["color"]
    if transparent:
        base_color[3] = 0
    pyguilib.draw.draw_rim(surface, base_color=base_color, width=5)
    return surface


def _render_image(image: Image):
    return image.image.convert()


def _render_button(button: Button):
    return pyguilib.draw.draw_button(size=button.size, text=button.text)


def _render_window(window: Window):
    return pyguilib.draw.draw_window(size=window.size, text=window.text, title=window.title, btn_text=window.btn_ok)
