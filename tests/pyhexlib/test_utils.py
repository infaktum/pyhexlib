import pygame
import pytest

from pyhexlib.utils import (
    toggle_layer,
    toggle_coordinate_layer,
    toggle_background,
    handle_scrolling_event,
    round_edges,
    shadow_image,
    outline_layer_imprinted_renderer,
)

from pyhexlib.layers import HexGridManager, StyledGridLayer, OutlineGridLayer
from pyhexlib.hexagons import rectangle_map, HexagonalGrid
from pyhexlib.basic import Hexagon
from pyhexlib.render import HexGridRenderer
import pyhexlib


def setup_module(module):
    # pygame surfaces used in tests require initialization
    pygame.init()


def make_manager():
    hexes = rectangle_map(3, 3)
    grid = HexagonalGrid(hexes)
    mgr = HexGridManager(grid)
    return mgr


def test_toggle_layer_visibility_and_return_value():
    mgr = make_manager()
    layer = StyledGridLayer("l1", [])
    layer.visible = True
    mgr.add_layer(layer)

    # toggle_layer sets the visibility flag; function does not return a value
    ret = toggle_layer(mgr, "l1")
    assert mgr.is_visible("l1") is False
    assert ret is None

    # toggle again
    toggle_layer(mgr, "l1")
    assert mgr.is_visible("l1") is True


def test_toggle_coordinate_layer_add_and_remove():
    mgr = make_manager()
    # ensure removed first
    if mgr.get_layer("_coordinates"):
        mgr.remove_layer("_coordinates")

    added = toggle_coordinate_layer(mgr, font_color=(1, 2, 3), font_size=10)
    assert added is True
    assert mgr.get_layer("_coordinates") is not None

    removed = toggle_coordinate_layer(mgr)
    assert removed is False
    assert mgr.get_layer("_coordinates") is None


def test_toggle_background_property():
    mgr = make_manager()
    renderer = HexGridRenderer(mgr, bg_image=None)
    # initial background_visible should be False when no bg_image
    assert renderer.background_visible is False
    toggle_background(renderer)
    assert renderer.background_visible is True
    toggle_background(renderer)
    assert renderer.background_visible is False


def test_handle_scrolling_event_moves_renderer_and_returns_tuple():
    mgr = make_manager()
    renderer = HexGridRenderer(mgr)

    # initial dirty is True after construction
    ev_up = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_UP)
    res = handle_scrolling_event(ev_up, renderer)
    assert res == (0, -1)
    assert renderer.dirty is True

    ev_right = pygame.event.Event(pygame.KEYDOWN, key=pygame.K_RIGHT)
    res = handle_scrolling_event(ev_right, renderer)
    assert res == (1, 0) or res == (+1, 0)

    # non-handled event -> None
    ev = pygame.event.Event(pygame.MOUSEBUTTONDOWN, button=1)
    assert handle_scrolling_event(ev, renderer) is None


def test_round_edges_behaviour_and_masking():
    s = pygame.Surface((20, 20), pygame.SRCALPHA)
    s.fill((255, 0, 0, 255))

    # radius <=0: identity for in_place True
    same = round_edges(s, 0, in_place=True)
    assert same is s

    # radius <=0 and in_place False -> copy
    copy = round_edges(s, 0, in_place=False)
    assert copy is not s

    # rounding with positive radius should make corners transparent
    rounded = round_edges(s, 6, in_place=False)
    # corner pixel at (0,0) should be transparent (alpha == 0)
    a = rounded.get_at((0, 0))[3]
    assert a == 0


def test_shadow_image_applies_color_and_alpha():
    s = pygame.Surface((4, 4), pygame.SRCALPHA)
    s.fill((255, 255, 255, 255))
    sh = shadow_image(s, shadow_color=(0, 0, 0), alpha=128)
    # With white original surface, multiplied by (0,0,0,128) should yield (0,0,0,~128)
    px = sh.get_at((1, 1))
    assert px[0] == 0 and px[1] == 0 and px[2] == 0
    # alpha should be approximately 128
    assert abs(px[3] - 128) <= 1


def test_outline_layer_imprinted_renderer_runs_without_error_and_draws():
    # prepare a small surface and a fake hexagon helper
    surf = pygame.Surface((60, 60), pygame.SRCALPHA)

    class FakeHexagons:
        def __init__(self):
            self._hexes = [(0, 0)]

        def __iter__(self):
            return iter(self._hexes)

        def edges(self, h):
            # return a small hex-like polygon inside the surface
            return [(10, 20), (20, 10), (40, 10), (50, 20), (40, 40), (20, 40)]

    fake_hexes = FakeHexagons()

    grid = OutlineGridLayer("o", {})
    # add one styled hexagon entry so the renderer draws per-hex style
    rc = Hexagon(0, 0)
    grid.hexagons[rc] = ((10, 10, 10), 1)

    renderer_factory = outline_layer_imprinted_renderer(color_dark=(5, 5, 5), color_light=(200, 200, 200))
    out = renderer_factory(surf, grid, fake_hexes)
    assert out is surf
    # ensure that something was drawn by checking bounding rect of non-transparent pixels
    bbox = surf.get_bounding_rect()
    assert bbox.width > 0 and bbox.height > 0

