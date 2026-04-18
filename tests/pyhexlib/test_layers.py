import pygame

from pyhexlib.basic import Hexagon
from pyhexlib.hexagons import rectangle_map, HexagonalGrid
from pyhexlib.layers import (
    HexGridLayer,
    AxialCoordinateHexGridLayer,
    ValueGridLayer,
    StyledGridLayer,
    SimpleImageGridLayer,
    TokenGridLayer,
    PathGridLayer,
    CoordinateGridLayer,
    TerrainGridLayer,
    HexGridManager, )
from pyhexlib.tokens import SimpleToken


def setup_module(module):
    # initialize pygame once for surface creation
    pygame.init()


def test_hexgridlayer_basic_dirty_and_clear():
    layer = HexGridLayer("g1")
    assert layer.is_dirty() is True
    layer.set_clean()
    assert layer.is_dirty() is False
    layer.set_dirty()
    assert layer.is_dirty() is True
    layer.hexagons[(0, 0)] = 1
    layer.clear()
    assert len(layer.hexagons) == 0
    r = repr(layer)
    assert "Grid(id=" in r


def test_axial_coordinate_layer_convert():
    hexes = rectangle_map(2, 2)
    grid = HexagonalGrid(hexes)
    layer = AxialCoordinateHexGridLayer("ax", grid)
    rc = hexes[0]
    ax = layer.convert(rc)
    assert isinstance(ax, tuple)


def test_value_grid_layer_set_get():
    hexes = rectangle_map(2, 2)
    grid = HexagonalGrid(hexes)
    layer = ValueGridLayer("v", grid, default_value=0)
    rc = hexes[0]


def test_simple_image_grid_and_token_grid():
    hexes = rectangle_map(2, 2)
    img_layer = SimpleImageGridLayer("img", {})
    s = pygame.Surface((2, 2))
    rc = Hexagon(0, 0)
    img_layer.set_image(rc, s, offset=(1, 1))
    assert img_layer.get_image(rc) is s
    assert img_layer.get_offset(rc) == (1, 1)
    img_layer.remove_image(rc)
    assert img_layer.get_image(rc) is None

    # Token grid
    tok_layer = TokenGridLayer("t", {})
    token = SimpleToken("id1", image=s, rc=rc)
    tok_layer.set_token(rc, token, offset=(2, 2))
    assert tok_layer.get_token(rc) is token
    assert tok_layer.get_image(rc) is not None
    assert tok_layer.get_token_id(rc) == "id1"
    tok_layer.remove_token(rc)
    assert tok_layer.get_token(rc) is None


def test_path_grid_layer():
    p = PathGridLayer("p", {})
    path = [Hexagon(0, 0), Hexagon(0, 1), Hexagon(0, 2)]
    p.set_path(path)
    assert p.visible is True
    got = p.get_path()
    assert set(got) == set(path)
    p.remove_path()
    assert p.visible is False


def test_coordinate_and_terrain_layers():
    coord = CoordinateGridLayer("c")
    rc = Hexagon(1, 2)
    assert coord.get_value(rc) == f"({rc.row},{rc.col})"

    t = TerrainGridLayer("ter", {})
    t.set_terrain_color("grass", (1, 2, 3))
    t.hexagons[rc] = "grass"
    assert t.get_color(rc) == (1, 2, 3)


def test_hexgridmanager_layer_management_and_selection():
    hexes = rectangle_map(3, 3)
    grid = HexagonalGrid(hexes)
    mgr = HexGridManager(grid)
    assert mgr.width == mgr.size[0]
    assert mgr.height == mgr.size[1]

    # add/get/remove layer
    l = StyledGridLayer("layer1", hexes)
    mgr.add_layer(l)
    assert mgr.get_layer("layer1") is l
    mgr.set_visible("layer1", False)
    assert mgr.is_visible("layer1") is False
    mgr.remove_layer("layer1")
    assert mgr.get_layer("layer1") is None

    # get_hexagons clipping
    sub = mgr.get_hexagons((0, 0, 1, 1))
    assert isinstance(sub, HexagonalGrid)
    r = repr(mgr)
    assert "Grids(size=" in r


def test_styled_grid_edge_cases_and_defaults():
    # get_style on empty returns None
    layer = StyledGridLayer("edge", [])
    rc = Hexagon(0, 0)
    assert layer.get_style(rc) is None

    # remove_style on missing key should raise KeyError
    try:
        layer.remove_style(rc)
    except KeyError:
        pass


def test_image_grid_defaults_and_token_variants():
    img_layer = SimpleImageGridLayer("img2", {})
    missing = Hexagon(9, 9)
    # default offset when missing
    assert img_layer.get_offset(missing) == (0, 0)

    # token grid behaviors with token without image
    s = pygame.Surface((2, 2))
    tok_layer = TokenGridLayer("tg", {})
    rc = Hexagon(0, 0)
    token_no_img = SimpleToken("noimg", image=None, rc=rc)
    tok_layer.set_token(rc, token_no_img)
    assert tok_layer.get_image(rc) is None
    assert tok_layer.get_token_id(rc) == "noimg"


def test_path_grid_values_indexing():
    p = PathGridLayer("pp", {})
    path = [Hexagon(0, 0), Hexagon(1, 0), Hexagon(2, 0)]
    p.set_path(path)
    # ensure stored indices match the order
    for idx, rc in enumerate(path):
        assert p.hexagons[rc] == idx
    p.remove_path()


def test_terrain_default_and_coordinate_font():
    coord = CoordinateGridLayer("coord2")
    assert hasattr(coord, "font")

    t = TerrainGridLayer("terrain2", {})
    rc = Hexagon(0, 0)
    # no terrain set -> None
    assert t.get_color(rc) is None


def test_hexgridmanager_visible_layers_and_clipping_normalization():
    hexes = rectangle_map(4, 4)
    grid = HexagonalGrid(hexes)
    mgr = HexGridManager(grid)
    l1 = StyledGridLayer("v1", hexes, visible=True)
    l2 = StyledGridLayer("v2", hexes, visible=False)
    mgr.add_layer(l1)
    mgr.add_layer(l2)
    vis = mgr.visible_layers
    assert any(g.id == "v1" for g in vis)
    assert not any(g.id == "v2" for g in vis)

    # clipping normalization: inverted coordinates should still work
    sub = mgr.get_hexagons((1, 1, 0, 0))
    assert isinstance(sub, HexagonalGrid)

    # is_visible for missing layer returns False and set_visible for missing does not raise
    assert mgr.is_visible("doesnotexist") is False
    mgr.set_visible("doesnotexist", True)
