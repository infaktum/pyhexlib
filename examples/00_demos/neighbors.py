import sys

import pygame

import pyhexlib
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

            toggle_neighbors(grids, rc)
            surface = renderer.render()
            screen.blit(surface, (0, 0))
            pygame.display.flip()

        if event.type == pygame.MOUSEMOTION:
            ...
            # x, y = event.pos
            # rc = renderer.hex_at(x, y)
            # print(x,y,rc)


# ------------------------------ Neighbor toggling logic -------------------------------


def toggle_neighbors(grids, rc):
    grid = grids.get_layer("neighbors")
    grid.clear()
    # for nbr in grids.hexagons._neighbors_without_cost(rc, 3):
    #    grid.set_color(nbr, (240, 240, 200))

    for nbr in grids.hexagons._neighbors_without_cost(rc, 1):
        grid.set_color(nbr, (220, 220, 180))


# ------------------------------ Grid creation and styling -------------------------------

def init(rows, cols, size):
    raw_hexagons = [(r, c) for r in range(-rows, rows + 1) for c in range(-cols, cols + 1)]
    # raw_hexagons = [ (r,c) for r in range(2 * rows + 1) for c in range(2 * cols + 1)]

    hexagons = HexagonalGrid(raw_hexagons)

    grids = HexGridManager(hexagons)

    grids.add_layer(FillGridLayer("background", default_color=(100, 100, 200)))
    grids.add_layer(FillGridLayer("neighbors", default_color=(100, 100, 200)))
    grids.add_layer(OutlineGridLayer("outline", default_color=(0, 0, 0,), default_width=1))
    grids.add_layer(CoordinateGridLayer("coordinates", visible=True))
    grids.set_visible("coordinates", True)
    renderer = HexGridRenderer(grids, size)
    return grids, renderer


# ----------------------------------- Main function -----------------------------------

ROWS, COLS = 2, 3

if __name__ == "__main__":

    pygame.init()

    pyhexlib.init(orientation=Orientation.POINTY)
    pygame.display.set_caption("Test: Negative Coordinates, Neighbors")

    grids, renderer = init(ROWS, COLS, 60)
    screen = pygame.display.set_mode(renderer.screen_size, pygame.SRCALPHA)

    surface = renderer.render()
    screen.blit(surface, (0, 0))
    pygame.display.flip()

    while True:
        run(grids, renderer)
