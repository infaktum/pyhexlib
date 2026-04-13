import sys

import pygame

import pyhex
from pyhex.hexagons import Orientation, HexagonalGrid
from pyhex.layers import HexGridManager, FillGridLayer, OutlineGridLayer
from pyhex.render import HexGridRenderer


# ------------------------------- Game Loop -----------------------------------

def run(screen, renderer):
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            sys.exit()

        if event.type == pygame.MOUSEBUTTONDOWN:
            x, y = event.pos
            rc = renderer.hex_at(x, y)
            switch_colors(renderer.layers, rc)
            renderer.render()
            screen.blit(renderer.surface, (0, 0))
            pygame.display.flip()

        # Pressing the key c will toggle the visibility of the coordinate grid
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_c:
                renderer.layers.toggle_coordinate_layer()
                renderer.render()
                screen.blit(renderer.surface, (0, 0))
                pygame.display.flip()


# ------------------------------ Event Handling -------------------------------

def switch_colors(grids: HexGridManager, rc):
    board = grids.get_layer("board")
    toggle_color(board, rc)
    for nbr in grids.hexagons._neighbors_without_cost(rc):
        toggle_color(board, nbr)


def toggle_color(board: FillGridLayer, rc):
    color = LIGHT if board.get_color(rc) == DARK else DARK
    board.set_color(rc, color)


# ------------------------------- Initialization -----------------------------------

def init(rows, cols):
    raw_hexagons = [(r, c) for r in range(rows) for c in range(cols)]

    print(pyhex.get_orientation())
    hexagons = HexagonalGrid(raw_hexagons)

    grids = HexGridManager(hexagons)

    board = FillGridLayer("board")
    for rc in hexagons:
        board.set_color(rc, DARK)
    grids.add_layer(board)
    grids.add_layer((OutlineGridLayer("outline", default_color=(0, 0, 0,), default_width=2)))

    return grids


# ------------------------------- CONSTANTS -----------------------------------

DARK, LIGHT = (50, 50, 150), (250, 250, 210)
ROWS, COLS, SIZE = 5, 7, 50

# ----------------------------------- Main function -----------------------------------

if __name__ == "__main__":
    pygame.init()
    pyhex.init(orientation=Orientation.FLAT)
    print(pyhex.get_config())
    pygame.display.set_caption("Simple Game")
    grids = init(ROWS, COLS)
    renderer = HexGridRenderer(grids, SIZE)
    screen = pygame.display.set_mode(renderer.screen_size, pygame.SRCALPHA)

    screen.blit(renderer.render(), (0, 0))
    pygame.display.flip()
    while True:
        run(screen, renderer)
