from typing import Dict, Tuple

import pygame

import pyhexlib
from pyhexlib.assets import Assets
from pyhexlib.basic import Orientation


# -------------------------------------------- Assets -------------------------------------------------

class SpaceAssets(Assets):
    def __init__(self, size, default_angle=None):
        super().__init__(size, default_angle=default_angle)
        self.size = size
        result = load_and_slice_images("images/StarWars.png", cols=4, rows=4)

        self.images = {n: pygame.transform.smoothscale(img, (3 * size // 2, 3 * size // 2)) for n, img in
                       enumerate(result)}
        self.shadows = {n: pygame.transform.smoothscale(pygame.transform.grayscale(self.get_image(n)), (size, size)) for
                        n in range(len(self.images))}
        self.background = pygame.image.load("images/starfield.png").convert()

        result = load_and_slice_images("images/Fadenkreuze.png", cols=2, rows=2)

        self.targets = {n: pygame.transform.smoothscale(img, (size, size)) for n, img in enumerate(result)}

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
            images.append(tile)
    return images


# -------------------------------------------- Main Test -------------------------------------------------

SIZE = 50

WINDOW_SIZE = 400, 400


def main():
    pygame.init()
    pyhexlib.init(orientation=Orientation.POINTY)
    screen = pygame.display.set_mode(WINDOW_SIZE)
    pygame.display.set_caption("Assets Preview")

    assets = SpaceAssets(SIZE)

    screen.blit(assets.background, (0, 0))

    pieces = [assets.shadows[n] for n in range(6)]

    screen.blit(pieces[0], (10, 20))
    screen.blit(pieces[1], (70, 20))
    screen.blit(pieces[2], (130, 20))
    screen.blit(pieces[3], (10, 100))
    screen.blit(pieces[4], (70, 100))
    screen.blit(pieces[5], (130, 100))

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
