import sys

import pygame
from pygame import Color

import pygui
import pyhex
from assets import GameAssets as Assets
from controller import Controller
from game import setup
from game_gui import map_window
from pyhex import Orientation
from pyhex.render import HexGridRenderer
from pyhex.utils import outline_layer_imprinted_renderer

# ----------------------------------- Initialization -----------------------------------

# orientation, default_angle = Orientation.POINTY, -90


orientation, default_angle = Orientation.FLAT, 0


def init(rows, cols, radius):
    pygame.init()
    pyhex.init(orientation=orientation, scale=(1, 0.8), log_level="INFO")
    pygame.display.set_mode((1600, 1067), pygame.SRCALPHA)
    # screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    assets = Assets(size=radius, default_angle=default_angle)

    pygame.display.set_icon(assets.icon)

    layers, map = setup(rows, cols, assets)
    map.setup()
    renderer = HexGridRenderer(layers, radius, bg_image=assets.background, assets=assets, visible_size=(15, 20))
    renderer.set_renderer("outline", render_fn=outline_layer_imprinted_renderer(color_dark=(0, 0, 0)))
    map.renderer = renderer
    screen_surface = pygame.display.set_mode((1600, 1067), pygame.SRCALPHA and pygame.RESIZABLE)
    # screen_surface = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    pygame.display.set_caption("Strategic Command Demo")

    gui = assets.gui

    controller = Controller(map, renderer, gui)
    controller.new_game()
    return controller, renderer, screen_surface, gui


# ----------------------------------- Main loop -----------------------------------


def run(screen, controller, renderer, gui_render):
    for event in pygame.event.get():
        if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.MOUSEMOTION or event.type == pygame.KEYDOWN:
            controller.handle_event(event, map_window)

        if controller.state == "UPDATE":
            screen.fill((0, 0, 0, 0))
            renderer.render()
            screen.blit(renderer.surface, map_window.topleft)
            gui_renderer.render(gui)
            pygame.display.flip()
            controller.state = "IDLE"


# ----------------------------------- Main function -----------------------------------

military_skin = {
    "color": Color(88, 89, 68, 255),
    "Button": {"color": Color(88, 89, 68, 255), "border": 2, "font": "Mono.ttf",
               "text_color": Color(150, 200, 150, 255), "text_size": 20}
}

if __name__ == "__main__":
    pygui.init(skin=military_skin)
    controller, renderer, screen, gui = init(25, 30, 40)
    gui_renderer = pygui.render.GuiRenderer(screen)
    while True:
        run(screen, controller, renderer, gui_renderer)
