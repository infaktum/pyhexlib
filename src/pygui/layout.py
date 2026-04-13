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
from abc import ABC
from dataclasses import dataclass
from typing import Dict, List, Optional, Any, Tuple

import pygame

from pygui import Point
from pygui.components import Component
from pyhex.graphic import Size


# ------------------------------------------------------------------------------------

# A single placed component produced by a Layouter
@dataclass(frozen=True)
class LayoutItem:
    component: Component
    position: Point


Layout = Tuple[Size, List[LayoutItem]]


# ------------------------------------- Layouter -----------------------------------------

class Layouter(ABC):

    def __init__(self):
        self.components = []

    def do_layout(self, components: Dict[Component, Any], border: int = 0) -> Layout:
        """Compute a layout from a mapping component -> metadata.

        The metadata is expected to be a dict with keys:
          - 'pos' (Optional[Point])
          - 'anchored' (bool)

        Implementations return a list of LayoutItem instances.
        """
        ...


#   -------------------------------------- Layouters --------------------------------------------

class NullLayouter(Layouter):
    def __init__(self):
        super().__init__()

    def do_layout(self, components: Dict[Component, Any], border: int = 0) -> Layout:
        # Accept both legacy values (Point|None) and new metadata dicts
        items: List[LayoutItem] = []
        for c, p in components.items():

            if p is not None and not isinstance(p, Point):
                p = Point(*p)
            items.append(LayoutItem(component=c, position=(p if p is not None else Point(0, 0))))
        return Size(0, 0), items


# --------------------------------- Layouter stacks components vertically with a margin --------------------------------------------

class VerticalLayouter(Layouter):
    def __init__(self, margin: int = 1):
        super().__init__()
        self.margin = margin

    def do_layout(self, components: Dict[Component, Point], border: int = 0) -> Layout:
        layout = []

        x = self.margin + border
        y = self.margin + border
        print(border)
        max_x = 0

        for component, _ in components.items():
            pos = Point(x, y)
            y += component.size.h + self.margin
            layout.append(LayoutItem(component=component, position=pos))
            max_x = max(max_x, x + component.size.w)

        layout_size = Size(max_x + 2 * self.margin, y + 2 * self.margin)

        return Size(layout_size.width, layout_size.height + border), layout

    def __repr__(self) -> str:
        """Return an English developer representation of the VerticalLayouter.

        Shows the layouter class name, the margin and how many components are stored.
        """
        return (
            f"{self.__class__.__name__}(margin={self.margin!r}, components={len(self.components)})"
        )


# -------------------------------------- Container --------------------------------------------


class Container(Component):
    def __init__(self, _id: int, size: Size = Size(0, 0), visible: bool = True, layouter: Layouter = NullLayouter(),
                 decorator=None, background_image: pygame.Surface = None):
        super().__init__(_id, size=size, visible=visible)
        self.layouter = layouter
        self.components: Dict[Component, Point] = {}
        self.decorator = decorator
        self.background_image = background_image
        self._layout = None

    def add_component(self, component: Component, pos: Optional[Point] = None):
        self.components[component] = pos
        self._layout = None

    def remove_component(self, component: Component) -> None:
        if component in self.components:
            del self.components[component]
            self._layout = None

    @property
    def layout(self) -> Layout:
        """Return the computed layout as a list of LayoutItem objects."""
        if self._layout is None:
            border = 10 if self.decorator is None else 0
            self._layout = self.layouter.do_layout(components=self.components, border=border)
        return self._layout

    def component_at(self, pos: Point) -> Component:

        pass

    def __repr__(self) -> str:
        """Return an English developer representation of the Container.

        Shows the container id, size, number of child components (not laid out) and
        the layouter class used for layout.
        """
        layouter_name = type(self.layouter).__name__ if self.layouter is not None else None
        return (
            f"{self.__class__.__name__}(id={self.id!r}, size={self.size!r}, "
            f"components={len(self.components)}, layouter={layouter_name!r}),"
            f"decorator={self.decorator!r}, background_image={self.background_image!r})"
        )


class Decorator:
    def __init__(self, border: int = 0):
        self.border = border


# ------------------------------------ Gui ---------------------------------------

class Gui():
    def __init__(self, ):
        self.components: Dict[Component, Point] = {}
        self.dirty = True
