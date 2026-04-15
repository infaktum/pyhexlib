import logging
import sys

import pygame

import pyhexlib
from assets import SpaceAssets
from controller import Controller
from game import setup
from pyhexlib import Orientation
from pyhexlib.render import HexGridRenderer

# ----------------------------------- Initialization -----------------------------------

# orientation, default_angle = Orientation.POINTY, -90


orientation, default_angle = Orientation.FLAT, 0


def init(rows, cols, radius):
    pygame.init()
    # Application logging configuration
    logging.basicConfig(level=logging.INFO,
                        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s")
    logging.getLogger("pyhex").setLevel(logging.DEBUG)

    pyhexlib.init(orientation=orientation, log_level=logging.DEBUG)
    pygame.display.set_mode((1000, 1000))
    info = pygame.display.Info()
    size = info.current_w, info.current_h
    pygame.display.set_mode(size)
    assets = SpaceAssets(size=radius, default_angle=default_angle)
    layers, game_board = setup(rows, cols, assets)
    renderer = HexGridRenderer(layers, radius, bg_image=assets.background, assets=assets)
    game_board.renderer = renderer
    screen_surface = pygame.display.set_mode(renderer.screen_size, pygame.SRCALPHA)
    pygame.display.set_caption("Space Fighter Game Demo")

    renderer.render()
    screen_surface.blit(renderer.surface, (0, 0))
    pygame.display.flip()

    controller = Controller(game_board, renderer)
    controller.new_game()
    return controller, renderer, screen_surface


# ----------------------------------- Main loop -----------------------------------

def run(screen, controller, renderer):
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION or event.type == pygame.KEYDOWN:
            controller.handle_event(event)

        if controller.state == "UPDATE":
            renderer.render()
            screen.blit(renderer.surface, (0, 0))
            pygame.display.flip()
            controller.state = "IDLE"


# ----------------------------------- Main function -----------------------------------

if __name__ == "__main__":
    controller, renderer, screen = init(10, 16, 60)

    while True:
        run(screen, controller, renderer)
