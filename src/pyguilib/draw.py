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

import pygame
from pygame import Color, Rect, Surface

import pyguilib
from pyguilib.basic import Size, Point


# ------------------------------------------ Component drawing primitives ----------------------------------


def draw_button(size: Size, text: str) -> pygame.Surface:
    surface = pygame.Surface((size.w, size.h))
    skin = pyguilib.skin["Button"]

    button_color, border_width = skin["color"], skin["border"]

    dark_color, light_color = darken_color(button_color, percentage=30), lighten_color(
        button_color, percentage=50
    )

    surface.fill(button_color)

    r = Rect(0, 0, *size)
    x_off, y_off = Point(border_width, 0), Point(0, border_width)

    # dark_color = (255, 0, 0, 255)

    pygame.draw.line(surface, light_color, r.bottomleft + x_off, r.topleft + x_off, width=border_width, )
    pygame.draw.line(surface, light_color, r.topleft + y_off, r.topright + y_off, width=border_width, )
    pygame.draw.line(surface, dark_color, r.bottomleft - 2 * y_off, r.bottomright - 2 * y_off, width=border_width, )
    pygame.draw.line(surface, dark_color, r.bottomright - 2 * x_off, r.topright - 2 * x_off, width=border_width, )

    # miter joins

    pygame.draw.line(surface, (0, 0, 0), r.topleft, r.topleft + Point(border_width, border_width), width=1, )

    pygame.draw.polygon(surface, light_color,
                        points=[r.bottomleft, r.bottomleft + 2 * (x_off - y_off), r.bottomleft - 2 * y_off, ], )
    pygame.draw.polygon(surface, light_color,
                        points=[r.topright, r.topright + 2 * (y_off - x_off), r.topright - 2 * x_off], )
    # black rim

    pygame.draw.rect(surface, color=(0, 0, 0), rect=r, width=2, )

    font, text_color, text_size = skin["font"], skin["text_color"], skin["text_size"]

    text_surface = draw_text_with_border(text, text_color, font, text_size)
    center_blit(surface, text_surface)

    return surface


def draw_rectangle_width_rim(size: Size, base_color: pygame.Color = Color(100, 100, 100),
                             border_width: int = 5) -> pygame.Surface:
    surface = pygame.surface.Surface(size)
    surface.fill(base_color)
    surface = draw_rim(surface, base_color=base_color, width=border_width)
    return surface


# -------------------------------- Blitting --------------------------------

def center_blit(surface_1, surface_2):
    surface_1.blit(surface_2, _center(surface_1=surface_1, surface_2=surface_2))


# -------------------------------------- Graphic primitives ------------------------------


def draw_rim(surface: pygame.Surface, base_color: Color, width: int = 10) -> pygame.Surface:
    rectangle = Rect(0, 0, *surface.get_size())

    dark_color, light_color = darken_color(base_color, percentage=50), lighten_color(base_color, percentage=50)

    pygame.draw.rect(surface, color=base_color, rect=rectangle, width=width, )
    pygame.draw.rect(surface, color=dark_color, rect=rectangle, width=2, )

    outer_rectangle = rectangle.move(1, 1)
    outer_rectangle.size = (rectangle.width - 2, rectangle.height - 2)

    pygame.draw.rect(surface, color=light_color, rect=outer_rectangle, width=1, )

    inner_rectangle = rectangle.move(width, width)
    inner_rectangle.size = (rectangle.width - 2 * width, rectangle.height - 2 * width)

    pygame.draw.rect(surface, color=dark_color, rect=inner_rectangle, width=1, )

    return surface


# ----------------------------------- Windows -----------------------------

def draw_window(size, text, title, btn_text):
    window = pygame.Surface((size.w, size.h))
    base_color = (200, 200, 200, 0)
    window.fill(base_color)
    draw_handle(window, base_color=(100, 100, 255, 255), size=Size(size.w, 30))
    draw_rim(window, base_color=base_color, width=2)

    return window


def draw_handle(surface: pygame.Surface, base_color: Color, size: Size) -> pygame.Surface:
    handle_surface = pygame.Surface((size.w, size.h), flags=pygame.SRCALPHA)

    dark_color, light_color = darken_color(base_color, percentage=50), lighten_color(base_color, percentage=50)
    handle_surface.fill(base_color)
    ys = int(size.h // 3)
    for y in range(ys):
        pygame.draw.line(handle_surface, color=dark_color, start_pos=(0, 3 * y + 2), end_pos=(size.w, 3 * y + 2),
                         width=1)
        pygame.draw.line(handle_surface, color=light_color, start_pos=(0, 3 * y), end_pos=(size.w, 3 * y), width=1)

    surface.blit(handle_surface, Point(0, 0))

    return surface


# ------------------------------------------ Color manipulation -----------------------------


def darken_color(base_color: pygame.Color, percentage) -> pygame.Color:
    return _shade_color_by_percentage(base_color, -percentage)


def lighten_color(base_color: pygame.Color, percentage) -> pygame.Color:
    return _shade_color_by_percentage(base_color, percentage)


# ------------------------------------------- Text rendering ----------------------------------


def draw_text_with_border(text: str, color: pygame.Color, font: str, size: int) -> pygame.Surface:
    font_obj = pygame.font.Font(font, size)
    # Text-Surface erzeugen
    text_surface = font_obj.render(text, True, color)
    # Neue Surface für Rand (1px auf jeder Seite)
    w, h = text_surface.get_width(), text_surface.get_height()
    border_surface = pygame.Surface((w + 2, h + 2), pygame.SRCALPHA)
    # Rand zeichnen: Text 8x in Schwarz um das Zentrum herum
    for dx in [-1, 0, 1]:
        for dy in [-1, 0, 1]:
            if dx != 0 or dy != 0:
                border_surface.blit(
                    font_obj.render(text, True, (0, 0, 0)), (1 + dx, 1 + dy)
                )
    # Text in Farbe in die Mitte
    border_surface.blit(text_surface, (1, 1))
    return border_surface


# -------------------------------- Helper Functions --------------------------

def _center(surface_1: Surface, surface_2: Surface) -> Point:
    w1, h1 = surface_1.get_size()
    w2, h2 = surface_2.get_size()

    x, y = (w1 - w2) // 2, (h1 - h2) // 2

    return Point(x, y)


def _shade_color_by_percentage(base_color: Color, percentage: float) -> Color:
    r, g, b, _ = base_color

    if percentage > 0:
        # Lighten: move towards white (255)
        r = int(r + (255 - r) * (percentage / 100))
        g = int(g + (255 - g) * (percentage / 100))
        b = int(b + (255 - b) * (percentage / 100))
    elif percentage < 0:
        # Darken: move towards black (0)
        r = int(r * (1 + percentage / 100))
        g = int(g * (1 + percentage / 100))
        b = int(b * (1 + percentage / 100))

    # Clamp values to valid range
    r = max(0, min(255, r))
    g = max(0, min(255, g))
    b = max(0, min(255, b))

    return Color(r, g, b)
