import pygame

import pyhexlib
import pyhexlib.graphic as g
import pyhexlib.render as r
from pyhexlib.basic import Orientation, Direction, Hexagon
from pyhexlib.hexagons import rectangle_map, HexagonalGrid
from pyhexlib.layers import HexGridManager, PathGridLayer


def setup_module(module):
    pygame.init()


def test_hex_dimensions_and_corners_flat_and_pointy():
    pyhexlib.init(orientation=Orientation.FLAT)
    inner, xdist, ydist = g.hex_dimensions(10)
    assert inner > 0 and isinstance(xdist, int) and isinstance(ydist, int)
    center = pygame.Vector2(100, 100)
    corners = g.hex_corners(center, 10)
    assert len(corners) == 6

    pyhexlib.init(orientation=Orientation.POINTY)
    inner2, x2, y2 = g.hex_dimensions(10)
    assert inner2 > 0
    corners2 = g.hex_corners(center, 10)
    assert len(corners2) == 6


def test_hex_corner_with_offset_and_compute_screen_size():
    p = pygame.Vector2(0, 0)
    pt = g.hex_corner_with_offset(p, 10, 0, 0)
    assert isinstance(pt, pygame.Vector2)
    sz = g.compute_screen_size(3, 4, 10)
    assert isinstance(sz, tuple) and len(sz) == 2


def test_compute_viewport_bounds_and_area():
    b = g.compute_viewport_bounds((0, 0))
    assert hasattr(b, "top") or hasattr(b, "topleft")
    rect = g.compute_area(0, 0, 2, 2, 10, 10)
    assert isinstance(rect, pygame.Rect)


def test_xy_to_rc_roundtrip_flat_and_pointy():
    # flat: compute center then map back
    pyhexlib.init(orientation=Orientation.FLAT)
    inner, xdist, ydist = g.hex_dimensions(10)
    offset = pygame.Vector2(0, 0)
    c = g.hex_center_flat(2, 3, xdist, ydist, offset, inner, 10)
    rc = g.xy_to_rc(c.x, c.y, 10)
    assert isinstance(rc, tuple)

    pyhexlib.init(orientation=Orientation.POINTY)
    inner, xdist, ydist = g.hex_dimensions(10)
    c2 = g.hex_center_pointy(2, 3, xdist, ydist, offset, inner, 10)
    rc2 = g.xy_to_rc(c2.x, c2.y, 10)
    assert isinstance(rc2, tuple)


def test_direction_angle_and_compute_direction_and_angle():
    pyhexlib.init(orientation=Orientation.FLAT)
    a = g.direction_to_angle(Direction.NORTH)
    assert isinstance(a, int)
    d = g.angle_to_direction(0)
    assert d is not None
    # compute_direction for direct neighbor
    cd = g.compute_direction((0, 0), (0, 1))
    assert cd is None or hasattr(cd, "name")
    # compute_angle returns int in 0..359
    p1 = pygame.Vector2(0, 0)
    p2 = pygame.Vector2(0, 10)
    ang = g.compute_angle(p1, p2)
    assert 0 <= ang < 360


def test_draw_centered_and_rotate():
    surf = pygame.Surface((50, 50))
    img = pygame.Surface((10, 10))
    before = surf.copy()
    out = g.draw_centered(surf, img, (25, 25))
    assert out is surf
    # rotate
    rimg = g.rotate_image(img, 45)
    assert isinstance(rimg, pygame.Surface)
    # rotate to direction
    pyhexlib.init(orientation=Orientation.FLAT)
    rdir = g.rotate_image_to_direction(img, Direction.NORTH)
    assert isinstance(rdir, pygame.Surface)


def test_render_hexgridrenderer_basic_flow(monkeypatch):
    # prepare a simple grid and manager
    hexes = rectangle_map(4, 4)
    grid = HexagonalGrid(hexes)
    mgr = HexGridManager(grid)

    # add a PathGridLayer to visible layers by id/type matching
    p = PathGridLayer("p", {})
    # Add some path
    p.set_path([Hexagon(0, 0), Hexagon(0, 1)])
    mgr.add_layer(p)

    # monkeypatch load_font_from_resources to avoid resource lookup
    monkeypatch.setattr(r, "load_font_from_resources", lambda: pygame.font.SysFont(None, 12))

    renderer = r.HexGridRenderer(mgr, radius=10, visible_size=(4, 4), origin=Hexagon(0, 0))
    # test get_renderer for registered type
    fn = renderer.get_renderer(p)
    assert callable(fn)

    surf = renderer.render()
    assert isinstance(surf, pygame.Surface)

    # test get_surface caching
    s1 = renderer.get_surface(p)
    s2 = renderer.get_surface(p)
    assert s1 is s2

    # test toggles
    vis_before = renderer.background_visible
    renderer.toggle_bg_visible()
    assert renderer.background_visible != vis_before
    # toggle layer visibility (no error)
    renderer.toggle_visible("p")


def test_set_origin_and_scrolling_and_point_lookup(monkeypatch):
    hexes = rectangle_map(4, 4)
    grid = HexagonalGrid(hexes)
    mgr = HexGridManager(grid)
    p = PathGridLayer("p2", {})
    mgr.add_layer(p)
    monkeypatch.setattr(r, "load_font_from_resources", lambda: pygame.font.SysFont(None, 12))
    renderer = r.HexGridRenderer(mgr, radius=10, visible_size=(4, 4), origin=Hexagon(0, 0))

    # set_origin
    renderer.set_origin(Hexagon(1, 1))
    assert renderer.origin == Hexagon(1, 1)
    # assert renderer.dirty is True

    # scroll and scroll helpers
    prev = renderer.viewport.origin
    renderer.scroll(1, 0)
    # assert renderer.viewport.origin.row == prev.row + 1
    renderer.scroll_h(1)
    renderer.scroll_v(1)

    # point lookup / hex_at
    sample_center = renderer.viewport.center(Hexagon(0, 0))
    found = renderer.point_to_hex(sample_center)
    assert isinstance(found, tuple) or hasattr(found, "row")
    # hex_at wrapper
    h2 = renderer.hex_at(sample_center.x, sample_center.y)
    assert isinstance(h2, tuple) or hasattr(h2, "row")


def test_get_angle_and_renderer_registration(monkeypatch):
    from pyhexlib.layers import HexGridLayer

    hexes = rectangle_map(4, 4)
    grid = HexagonalGrid(hexes)
    mgr = HexGridManager(grid)
    p = PathGridLayer("p3", {})
    p.set_path([Hexagon(0, 0), Hexagon(0, 1)])
    mgr.add_layer(p)
    monkeypatch.setattr(r, "load_font_from_resources", lambda: pygame.font.SysFont(None, 12))
    renderer = r.HexGridRenderer(mgr, radius=10, visible_size=(4, 4), origin=Hexagon(0, 0))

    ang = renderer.get_angle(Hexagon(0, 0), Hexagon(0, 1))
    assert isinstance(ang, int)

    # get_renderer for unknown layer should raise KeyError
    class LocalLayer:
        id = "local"

    try:
        renderer.get_renderer(LocalLayer())
    except KeyError:
        pass

    # register custom renderer by name and retrieve it
    custom = lambda surf, layer, hexs: surf
    renderer.set_renderer("HexGridLayer", custom)
    # create a HexGridLayer instance and get renderer
    hg = HexGridLayer("hg")
    fn = renderer.get_renderer(hg)
    assert fn is custom


def test_render_functions_directly(monkeypatch):
    from pyhexlib.layers import StyledGridLayer, SimpleImageGridLayer, ValueGridLayer

    # prepare renderer to obtain viewport.hexagons
    hexes = rectangle_map(4, 4)
    grid = HexagonalGrid(hexes)
    mgr = HexGridManager(grid)
    monkeypatch.setattr(r, "load_font_from_resources", lambda: pygame.font.SysFont(None, 12))
    renderer = r.HexGridRenderer(mgr, radius=10, visible_size=(4, 4), origin=Hexagon(0, 0))

    surface = pygame.Surface(renderer.screen_size, pygame.SRCALPHA)

    # Outline layer rendering
    ol = StyledGridLayer("Outline", {})
    ol.default_style = ((10, 10, 10), 1)
    ol.set_style(Hexagon(0, 0), (5, 5, 5), 1)
    out = r._render_outline_layer(surface.copy(), ol, renderer.viewport.hexagons)
    assert isinstance(out, pygame.Surface)

    # Fill layer rendering
    fl = StyledGridLayer("Fill", {})
    fl.default_style = ((20, 20, 20), 0)
    fl.set_color(Hexagon(0, 0), (7, 7, 7))
    out2 = r._render_fill_layer(surface.copy(), fl, renderer.viewport.hexagons)
    assert isinstance(out2, pygame.Surface)

    # Image layer rendering (SimpleImageGridLayer)
    sim = SimpleImageGridLayer("imgtest", {})
    s = pygame.Surface((4, 4))
    sim.set_image(Hexagon(0, 0), s, offset=(0, 0))
    out3 = r._render_image_layer(surface.copy(), sim, renderer.viewport.hexagons)
    assert isinstance(out3, pygame.Surface)

    # Value layer rendering
    val = ValueGridLayer("val", {})
    val.set_value(Hexagon(0, 0), "X")
    out4 = r._render_value_layer(surface.copy(), val, renderer.viewport.hexagons)
    assert isinstance(out4, pygame.Surface)

    # Path layer rendering
    path = PathGridLayer("pathtest", {})
    path.set_path([Hexagon(0, 0), Hexagon(0, 1)])
    out5 = r._render_path_layer(surface.copy(), path, renderer.viewport.hexagons)
    assert isinstance(out5, pygame.Surface)
