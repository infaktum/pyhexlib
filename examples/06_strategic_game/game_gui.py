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
import sys

import pygame

import pyguilib
from pyguilib import Size, Point, Rectangle
from pyguilib.components import Rim, Overlay, Button, Image
from pyguilib.decorators import rim_decorator
from pyguilib.layout import Container, VerticalLayouter
from pyguilib.render import GuiRenderer

map_window = Rectangle(16, 92, 1200, 720)

# ---------------------------------------- Logger ------------------------------------------------

LOGGER = pyguilib.get_logger(__name__)


def init(size: Size, startscreen):
    print(f"Initializing GUI with size {size}, {type(size)}")

    gui = Container("gui", size=size, decorator=rim_decorator)

    gui.add_component(Overlay("overlay", size=size, windows=[map_window]), pos=Point(0, 0))
    gui.add_component(Rim("map_rim", size=map_window.size), pos=map_window.topleft)

    gui.add_component(Rim("deco_top", size=Size(size.w - 32, 64)), pos=Point(16, 16))
    gui.add_component(Rim("deco_bottom", size=Size(size.w - 32, 228)), pos=Point(16, size.h - 16 - 228))

    # The Buttons on the right side

    button_labels = ["End Turn", "Load", "Save", "Quit"]
    button_size = Size(300, 80)
    button_box = Rectangle(size.w - (button_size.w + 64), map_window.y + 360, button_size.w + 20,
                           (button_size.h + 8) * len(button_labels))

    buttons = Container("buttons", layouter=VerticalLayouter(margin=2), decorator=rim_decorator)

    for label in button_labels:
        buttons.add_component(Button(f"b_{label}", size=button_size, text=label))

    gui.add_component(buttons, pos=button_box.topleft + Point(8, 8))

    # Another deco box

    image_box = Rectangle(button_box.x, 96, button_box.w, 320)

    gui.add_component(Image("startscreen", size=image_box.size, image=startscreen), pos=image_box.topleft)
    gui.add_component(Rim("deco_right", size=image_box.size), pos=image_box.topleft)
    return gui


def create_gui(size, assets):
    return init(size, assets)


# ---------------------------------------------------------------------------

SIZE = Size(1600, 1067)

if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode(SIZE)
    gui = init(SIZE)
    renderer = GuiRenderer(screen)
    renderer.render(gui)
    pygame.display.flip()
    while True:
        redraw = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

            # if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION or event.type == pygame.KEYDOWN:
            #    redraw = True

        if redraw:
            renderer.render(gui)
            # creen.blit(surface, (0, 0))
            pygame.display.flip()
