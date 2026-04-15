import logging

import pygame
from pyhexlib.palette import COLOR_WATER

import pyhexlib
from assets import GameAssets
from controller import Controller
from game import GameBoard
from pyhexlib import Orientation
from pyhexlib.hexagons import HexagonalGrid
from pyhexlib.layers import ValueGridLayer, HexGridManager, FillGridLayer, PathGridLayer, \
    OutlineGridLayer, TokenGridLayer
from pyhexlib.render import HexGridRenderer

COLOR_OLIVE = (75, 87, 62)
COLOR_MOUNTAINS = {"dark": (70, 60, 50), "normal": (120, 110, 100), "light": (200, 190, 180)}

# ----------------------------------- Main function -----------------------------------


# orientation, default_angle = Orientation.POINTY, -90

orientation, default_angle = Orientation.FLAT, 0

ROWS, COLS, SIZE = 20, 30, 30

FIELDS = "fields"

import sys


def main():
    pygame.init()
    # Application configures logging for the examples
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    logging.getLogger("pyhex").setLevel(logging.DEBUG)

    pyhexlib.init(orientation=orientation, log_level=logging.DEBUG)
    pygame.display.set_caption("Wargame")

    pygame.display.set_mode((1000, 1000))
    # Source - https://stackoverflow.com/a/31538680
    # Posted by muddyfish, modified by community. See post 'Timeline' for change history
    # Retrieved 2026-04-03, License - CC BY-SA 3.0

    assets = GameAssets(SIZE, default_angle=default_angle)
    grids = create_grids()

    bg_image = pygame.image.load("images/terrain3.png").convert()
    renderer = HexGridRenderer(grids, SIZE, bg_image=bg_image, assets=assets)
    print(renderer.screen_size)
    screen = pygame.display.set_mode(renderer.screen_size, pygame.SRCALPHA)
    # screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    board = GameBoard(grids.get_layer("tokens"), assets)

    renderer.render()
    screen.blit(renderer.surface, (0, 0))
    pygame.display.flip()

    controller = Controller(board, renderer)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                running = False
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION or event.type == pygame.KEYDOWN:
                controller.handle_event(event)

            if controller.state == "UPDATE":
                screen.fill((0, 0, 0))
                surface = renderer.render()
                screen.blit(surface, (0, 0))
                pygame.display.flip()
                controller.state = "IDLE"


def create_grids():
    hexagons = HexagonalGrid([(r, c) for r in range(ROWS) for c in range(COLS)])
    grids = HexGridManager(hexagons)

    terrain_grid = ValueGridLayer("terrain")
    for h in hexagons:
        terrain_grid.set_value(h, 1)
    grids.add_layer(terrain_grid)

    terrain = {}
    for rc in [(2, 2,), (2, 3), (3, 2)]:
        terrain[rc] = 1000, COLOR_WATER["dark"]

    terrain[(2, 4)] = terrain[(2, 6)] = terrain[(1, 7)] = terrain[(1, 8)] = terrain[(1, 9)] = 100, COLOR_WATER["normal"]
    terrain[(1, 5)] = 1, COLOR_MOUNTAINS["dark"]

    for rc in [(4, 7), (4, 8), (5, 8)]:
        terrain[rc] = 1000, COLOR_MOUNTAINS["normal"]

    color = FillGridLayer("colored", default_color=COLOR_OLIVE)
    # grids.add_grid("background", color)
    for rc in terrain:
        cost, col = terrain[rc]
        terrain_grid.set_value(rc, cost)
        color.set_color(rc, col)

    grids.add_layer(FillGridLayer("neighbors"))
    grids.add_layer(PathGridLayer("path"))
    grids.add_layer(TokenGridLayer("shadows"))
    grids.add_layer(TokenGridLayer("tokens"))
    grids.add_layer(OutlineGridLayer("outline", default_color=(200, 200, 200), default_width=1))

    return grids


if __name__ == "__main__":
    main()
