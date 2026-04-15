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

import pyhexlib
import pyhexlib.graphic as g
from pyhexlib.basic import Orientation
from pyhexlib.hexagons import HexagonalGrid
from pyhexlib.layers import HexGridManager, FillGridLayer, OutlineGridLayer, CoordinateGridLayer
from pyhexlib.render import HexGridRenderer


# ------------------------------ Event loop and handlers -------------------------------

def run(grids, renderer):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            rc = renderer.hex_at(x, y)
            print(rc)
            surface = renderer.render()
            screen.blit(surface, (0, 0))

            pygame.display.flip()

        if event.type in [pygame.KEYDOWN]:
            if event.key == pygame.K_UP:
                renderer.scroll_v(-1)
            elif event.key == pygame.K_DOWN:
                renderer.scroll_v(+1)
            elif event.key == pygame.K_LEFT:
                renderer.scroll_h(-1)
            elif event.key == pygame.K_RIGHT:
                renderer.scroll_h(+1)

            surface = renderer.render()
            screen.blit(surface, (0, 0))
            pygame.display.flip()


# ------------------------------ Grid creation and styling -------------------------------

def init(rows, cols, radius):
    # raw_hexagons = [(r, c) for r in range(-rows, rows + 1) for c in range(-cols, cols + 1)]
    raw_hexagons = [(r, c) for r in range(2 * rows + 1) for c in range(2 * cols + 1)]

    hexagons = HexagonalGrid(raw_hexagons)

    grids = HexGridManager(hexagons)

    grids.add_layer(FillGridLayer("background", default_color=(200, 200, 150)))
    grids.add_layer(OutlineGridLayer("outline", default_color=(0, 0, 0,), default_width=1))
    grids.add_layer(CoordinateGridLayer("coordinates", visible=True))
    grids.set_visible("coordinates", True)
    renderer = HexGridRenderer(grids, radius=radius, visible_size=(6, 10))
    # renderer.set_origin((0, 0))
    return grids, renderer


# ----------------------------------- Main function -----------------------------------

ROWS, COLS, SIZE = 10, 15, 40

if __name__ == "__main__":

    pygame.init()

    pyhexlib.init(orientation=Orientation.FLAT)
    pygame.display.set_caption("Demo: Scrolling")

    grids, renderer = init(ROWS, COLS, SIZE)

    screen_size = g.compute_screen_size(6, 10, SIZE)

    screen = pygame.display.set_mode(screen_size, pygame.SRCALPHA)

    surface = renderer.render()
    screen.blit(surface, (0, 0))
    pygame.display.flip()

    while True:
        run(grids, renderer)
