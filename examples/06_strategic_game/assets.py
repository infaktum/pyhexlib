from typing import Dict, Tuple

import pygame

import pyhexlib
from game_gui import create_gui
from pyhexlib.assets import Assets
from pyhexlib.basic import Orientation
from pyhexlib.utils import round_edges
from pylightgui import Size

COUNTRIES = ["US", "Axis"]  # ,"UK"]
UNIT_TYPES = ["Infantry", "Armor", "Artillery", "Airborne", "Navy", "AirForce"]


# -------------------------------------------- Assets -------------------------------------------------

class GameAssets(Assets):
    def __init__(self, size, default_angle=None):
        super().__init__(size, default_angle=default_angle)
        self.size = size
        result = load_and_slice_images("images/Units.png", cols=6, rows=2)

        self.images = {n: pygame.transform.smoothscale(img, (1.2 * size, size)) for n, img in
                       enumerate(result)}

        self.units = {}
        counter = 0
        for country in COUNTRIES:
            for unit_type in UNIT_TYPES:
                self.units[(country, unit_type)] = self.images[counter]
                counter += 1
        self.background = pygame.image.load("images/europe.png").convert()

        result = load_and_slice_images("images/cities.png", cols=3, rows=2)
        self.cities = {n: pygame.transform.smoothscale(img, (2 * size, 2 * size)) for n, img in
                       enumerate(result)}

        self.icon = pygame.image.load("images/icon.png").convert()
        self.startscreen = pygame.image.load("images/startscreen_2.jpg").convert()

        self.gui = create_gui(Size(1600, 1067), self.startscreen)

    def get_unit(self, country: str, unit_type: str) -> pygame.Surface:
        return self.units[(country, unit_type)]

    def get_shadow_token(self, number: int) -> pygame.Surface:
        return self.shadows[number]


# -------------------------------------------- Helper Functions-------------------------------------------------


def load_and_slice_images(path: str, cols: int = 3, rows: int = 1) -> Dict[str, Dict[Tuple[int, int], pygame.Surface]]:
    img = pygame.image.load(path).convert_alpha()

    w, h = img.get_width(), img.get_height()
    tile_w = w // max(1, cols)
    tile_h = h // max(1, rows)

    images = []

    for row in range(rows):
        for col in range(cols):
            rect = pygame.Rect(col * tile_w, row * tile_h, tile_w, tile_h)
            tile = pygame.Surface((tile_w, tile_h), pygame.SRCALPHA)
            tile.blit(img, (0, 0), rect)
            images.append(round_edges(tile, 10))
    return images


# -------------------------------------------- Main Test -------------------------------------------------

SIZE = 50

WINDOW_SIZE = 600, 400


def main():
    pygame.init()
    pyhexlib.init(orientation=Orientation.POINTY)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Assets Preview")

    assets = GameAssets(SIZE)

    screen.blit(assets.background, (0, 0))

    pieces = [assets.get_unit("America", t) for t in UNIT_TYPES]

    screen.blit(pieces[0], (10, 20))
    screen.blit(pieces[1], (270, 20))
    screen.blit(pieces[2], (400, 20))
    screen.blit(pieces[3], (10, 100))
    screen.blit(pieces[4], (70, 100))
    # screen.blit(pieces[5], (130, 100))

    clock = pygame.time.Clock()
    running = True

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        pygame.display.flip()
        clock.tick(30)

    pygame.quit()


if __name__ == '__main__':
    main()
