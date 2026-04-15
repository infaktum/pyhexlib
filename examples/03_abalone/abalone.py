import pygame
from pyhexlib.grid import CoordinateGridLayer, HexGridLayers, FillGridLayer, OutlineGridLayer, ImageGridLayer
from pyhexlib.hexagon import rectangle, HexType

from assets import GameAssets
from board import GameBoard
from controller import Controller
from pyhexlib.graphic import RenderEngine

# ------------------------------- GameBoard -----------------------------------

COLOR_MARKER = (0, 255, 0)
COLOR_WOOD = (245, 222, 179)  # (139,90,43)
COLOR_BG = COLOR_WOOD

# ----------------------------------- Main function -----------------------------------

ROWS, COLS, SIZE = 7, 10, 50

FIELDS = "fields"
GAME = "game"

import sys


def main():
    pygame.init()
    pygame.display.set_mode((1000, 1000))
    assets = GameAssets(SIZE)
    grids = create_grids(assets)
    renderer = RenderEngine(grids, SIZE, assets=assets, hex_type=HexType.POINTY)
    print(renderer)
    screen = pygame.display.set_mode((renderer.width, renderer.height), pygame.SRCALPHA)
    pygame.display.set_caption("Hex Game")

    surface = pygame.Surface(renderer.compute_screen_size, pygame.SRCALPHA)
    renderer.render()

    screen.blit(surface, (0, 0))
    pygame.display.flip()

    score_surface = pygame.Surface(renderer.compute_screen_size, pygame.SRCALPHA)
    score_surface.fill((255, 255, 255))

    new_game(grids.get_layer(GAME))

    renderer.render()
    screen.blit(score_surface, (0, 0))
    screen.blit(renderer.surface, (0, 0))

    pygame.display.flip()

    controller = Controller(renderer)

    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION or event.type == pygame.KEYDOWN:
                controller.handle_event(event)

            if controller.state == "UPDATE":
                renderer.render()
                screen.blit(renderer.surface, (0, 0))
                pygame.display.flip()
                controller.state = "IDLE"


def new_game(board):
    board.set_token((0, 0), 0)


COLOR_WOOD = (245, 222, 179)


def create_grids(assets):
    hexagons = [(row, col) for col in range(-4, 5) for row in range(-4, 5)]
    invalid = [(-4, -4), (-4, -3), (-4, 3), (-4, 4), (4, -4), (4, -3), (4, 3), (4, 4)]
    invalid += [(-3, -4), (-3, 4), (-3, 3), (3, -4), (3, 3), (3, 4)]
    invalid += [(-2, -4), (-2, 4), (2, -4), (2, 4)]
    invalid += [(-1, 4), (1, 4)]
    for rc in invalid:
        hexagons.remove(rc)

    grids = HexGridLayers(hexagons)

    grids.add_layer("background", FillGridLayer(default_color=COLOR_WOOD))
    grids.add_layer("outline", (OutlineGridLayer(default_color=(0, 0, 0,), default_width=2)))
    grids.add_layer("shadows", ImageGridLayer())
    grids.add_layer(GAME, GameBoard(assets))

    return grids


if __name__ == "__main__":
    main()
