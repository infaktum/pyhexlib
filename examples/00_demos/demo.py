import pygame
from pyhexlib.grid import *
from pyhexlib.hexagon import rectangle

from pyhexlib.graphic import RenderEngine

# ----------------------------------- Main function -----------------------------------

ROWS, COLS, SIZE = 6, 8, 50

import sys


def main():
    pygame.init()
    screen = pygame.display.set_mode((1000, 1000), pygame.SRCALPHA)
    pygame.display.set_caption("Hexagons")

    grids = create_grids()
    renderer = RenderEngine(grids, SIZE)
    screen = pygame.display.set_mode(renderer.compute_screen_size, pygame.SRCALPHA)

    surface = renderer.render()

    screen.blit(surface, (0, 0))
    pygame.display.flip()

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                pygame.quit()
                sys.exit()


def create_grids():
    hexagons = rectangle(ROWS, COLS)
    hexagons = [(r, c) for r in range(-3, 3) for c in range(-4, 4)]
    grids = HexGridLayers(hexagons)

    grids.add_layer("background", FillGridLayer(default_color=(200, 200, 200)))
    grids.add_layer("grid", OutlineGridLayer(default_color=(0, 0, 0,), default_width=1))
    grids.add_layer("coordinates", CoordinateGridLayer(font="Courier", font_color=(0, 0, 0), font_size=20))

    return grids


if __name__ == "__main__":
    main()
