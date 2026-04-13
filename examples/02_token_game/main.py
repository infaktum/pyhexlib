import sys

import pygame

import pyhex
from assets import GameAssets
from controller import Controller
from game import Game
from pyhex import Orientation
from pyhex.hexagons import rectangle_map, HexagonalGrid
from pyhex.layers import HexGridManager, FillGridLayer, OutlineGridLayer, TokenGridLayer, SimpleImageGridLayer
from pyhex.render import HexGridRenderer

# ------------------------------- GameBoard -----------------------------------

COLOR_MARKER = (0, 255, 0)
COLOR_BG = (210, 170, 120)

# ----------------------------------- Main function -----------------------------------

ROWS, COLS, SIZE = 7, 10, 50

FIELDS = "fields"
GAME = "game"
OFFSET = (0, 20)


def main():
    pygame.init()

    pyhex.init(orientation=Orientation.FLAT)
    pygame.display.set_mode((1000, 1000))
    assets = GameAssets(SIZE)
    board, layers = create_layers(assets)
    renderer = HexGridRenderer(layers, SIZE, assets=assets)
    screen = pygame.display.set_mode((renderer.width + OFFSET[0], renderer.height + OFFSET[1]), pygame.SRCALPHA)
    pygame.display.set_caption("Hex Game")

    surface = pygame.Surface(renderer.screen_size, pygame.SRCALPHA)
    renderer.render()

    screen.blit(surface, (0, 0))
    pygame.display.flip()

    score_surface = pygame.Surface((renderer.screen_size[0], + OFFSET[1]), pygame.SRCALPHA)
    score_surface.fill((255, 255, 255))

    board.setup((0, 0), (ROWS - 1, COLS - 1))

    renderer.render()
    screen.blit(score_surface, (0, 0))
    screen.blit(renderer.surface, OFFSET)

    pygame.display.flip()

    controller = Controller(board, renderer)

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
                screen.blit(renderer.surface, (0, 20))
                render_score(score_surface, controller.score())
                screen.blit(score_surface, (0, 0))
                pygame.display.flip()
                controller.state = "IDLE"


def render_score(surface, score):
    (player0, player1), turn = score
    font = pygame.font.SysFont("Arial", 20)
    text = f"Red: Blue {player0} : {player1} - {["Red", "Blue"][turn]} moves"
    text_surf = font.render(text, True, (0, 0, 0))
    text_rect = text_surf.get_rect(center=(surface.get_width() // 2, surface.get_height() // 2))
    surface.fill((255, 255, 255))
    surface.blit(text_surf, text_rect)


def create_layers(assets):
    hexagons = rectangle_map(ROWS + 1, COLS + 1)
    hexagons = [rc for rc in hexagons if rc not in [(2, 2,), (2, 3), (3, 2), (4, 7), (4, 8), (5, 8)]]

    layers = HexGridManager(HexagonalGrid(hexagons))

    layers.add_layer(FillGridLayer("background", default_color=COLOR_BG))
    layers.add_layer((OutlineGridLayer("outline", default_color=(0, 0, 0,), default_width=2)))
    layers.add_layer(SimpleImageGridLayer("shadows"))
    tokens = TokenGridLayer("tokens")
    layers.add_layer(tokens)

    board = Game(tokens, assets)
    return board, layers


if __name__ == "__main__":
    main()
