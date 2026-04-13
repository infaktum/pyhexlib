import pygame

from pyhex.hexagons import Hexagon, Direction, HexagonalGrid, rectangle_map
from pyhex.layers import TokenGridLayer, HexGridManager, OutlineGridLayer, ValueGridLayer, FillGridLayer, \
    SimpleImageGridLayer
from pyhex.tokens import Token, FreeToken, DirectionToken


# ------------------------------  DirectionToken Fighter -----------------------------------

class Fighter(DirectionToken):

    def __init__(self, token_id, image, movement: int = None, hp: int = None, rc: Hexagon = None,
                 direction: Direction = Direction.NORTH) -> None:
        super().__init__(token_id, image, rc, direction)
        self.movement = movement
        self.hp = hp

    def __repr__(self) -> str:
        """Return a concise developer representation for Fighter.

        Shows the token id, grid coordinate (rc), direction name, speed, hp and
        whether an image surface is present.
        """
        image_set = getattr(self, "_image", None) is not None
        dir_obj = getattr(self, "direction", None)
        dir_name = getattr(dir_obj, "name", dir_obj)
        return (
            f"{self.__class__.__name__}(id={self.id!r}, rc={self.rc!r}, direction={dir_name!r}, "
            f"movement={self.movement!r}, hp={self.hp!r}, image_set={image_set})"
        )


class Turret(DirectionToken):

    def __init__(self, token_id, image, firing_range: int = None, hp: int = None, rc: Hexagon = None,
                 direction: Direction = Direction.NORTH) -> None:
        super().__init__(token_id, image, rc, direction)
        self.firing_range = firing_range
        self.hp = hp

    def __repr__(self) -> str:
        """Return a concise developer representation for Turret.

        Shows the token id, grid coordinate (rc), direction name, firing_range, hp and
        whether an image surface is present.
        """
        image_set = getattr(self, "_image", None) is not None
        dir_obj = getattr(self, "direction", None)
        dir_name = getattr(dir_obj, "name", dir_obj)
        return (
            f"{self.__class__.__name__}(id={self.id!r}, rc={self.rc!r}, direction={dir_name!r}, "
            f"firing_range={self.firing_range!r}, hp={self.hp!r}, image_set={image_set})"
        )


# ------------------------------  GameBoard -----------------------------------

class GameBoard:

    def __init__(self, token_layer: TokenGridLayer, target_layer: TokenGridLayer, assets):
        self.marker = None
        self.assets = assets = assets
        self.token_layer = token_layer
        self.target_layer = target_layer
        self.renderer = None

        self.images = {"xwing": assets.get_image(5), "tie": assets.get_image(0), "turret": assets.get_image(15)}
        self.shadows = {"xwing": assets.get_shadow_token(5), "tie": assets.get_shadow_token(0),
                        "turret": assets.get_shadow_token(15)}

        self.targets = {"xwing": assets.targets[0], "tie": assets.targets[2]}

        self.tokens = {}
        self.shadow_tokens = {"xwing1": DirectionToken("xwing_shadow", self.shadows["xwing"], None, None),
                              "tie1": DirectionToken("tie_shadow", self.shadows["tie"], None, None)}

        self.target_tokens = {"xwing": DirectionToken("xwing_target", self.targets["xwing"], None, None),
                              "tie": DirectionToken("tie_target", self.targets["tie"], None, None)}

        self.turrets = [(3, 2), (4, 9)]

    def setup(self):

        xwing1 = Fighter("xwing1", movement=3, hp=4, image=self.images["xwing"], rc=(5, 8))
        tie1 = Fighter("tie1", movement=5, hp=5, image=self.images["tie"], rc=(1, 1))
        turret1 = FreeToken("turret1", self.images["turret"], (3, 2), None)
        turret2 = FreeToken("turret2", self.images["turret"], (4, 9), None)

        self.tokens["xwing1"] = xwing1
        self.tokens["tie1"] = tie1
        self.tokens["turret1"] = turret1
        self.tokens["turret2"] = turret2

        for token in self.tokens.values():
            self.set_token(token.rc, token)

        self.turrets = [turret1.rc, turret2.rc]

    def get_shadow_token(self, token_id):
        shadow = self.shadow_tokens.get(token_id, None)
        return DirectionToken(shadow.id, shadow.image, None, None) if shadow else None

    def set_token(self, rc: Hexagon, token: Token, direction: Direction = None):
        token.rc = rc
        token.direction = direction
        self.token_layer.set_token(rc, token)

    def get_token(self, rc) -> Token:
        return self.token_layer.get_token(rc)

    def remove_token(self, rc: Hexagon) -> None:
        token = self.get_token(rc)
        if token:
            self.token_layer.remove_token(rc)

    def is_player_token(self, token: Token) -> bool:
        return token.id in ["xwing1", "tie1"]

    def turn_turrets(self, rc):
        for turret in self.turrets:
            self.turn_turret(turret, rc)

    def turn_turret(self, rc: Hexagon, target: Hexagon) -> None:
        token = self.get_token(rc)
        angle = self.renderer.get_angle(rc, target)

        token.angle = angle
        self.token_layer.set_token(rc, token)

    def put_marker(self, rc):
        self.marker = rc

    def remove_marker(self):
        self.marker = None

    def put_target(self, rc):
        self.target_layer.set_token(rc, self.target_tokens["xwing"] if self.get_token(rc) == self.tokens["xwing1"] else
        self.target_tokens["tie"])

    def remove_target(self, rc):
        self.target_layer.remove_token(rc)


# ----------------------------------- Setup function -----------------------------------

def setup(rows, cols, assets):
    hexagons = HexagonalGrid(rectangle_map(rows, cols))
    grids = HexGridManager(hexagons)

    terrain_grid = ValueGridLayer("terrain", default_value=1)
    grids.add_layer(terrain_grid)
    grids.add_layer(FillGridLayer("neighbors"))
    background = SimpleImageGridLayer("background")
    grids.add_layer(background)

    asteroid = pygame.image.load("images/Asteroid.png").convert_alpha()
    planet = pygame.image.load("images/Planet.png").convert_alpha()

    asteroid_hexes = [(3, 2), (4, 9)]
    for rc in asteroid_hexes:
        terrain_grid.set_value(rc, 1000)
        background.set_image(rc, asteroid)

    pos_planet = (5, 6)
    background.set_image(pos_planet, planet)
    terrain_grid.set_value(pos_planet, 1000)
    for rc in hexagons._neighbors_without_cost(pos_planet):
        terrain_grid.set_value(rc, 1000)

    grids.add_layer(TokenGridLayer("shadows"))

    tokens = TokenGridLayer("tokens")

    grids.add_layer(tokens)
    targets = TokenGridLayer("targets")
    grids.add_layer(targets)
    game_board = GameBoard(tokens, targets, assets)

    grids.add_layer(OutlineGridLayer("outline", default_color=(255, 255, 255,), default_width=1))
    return grids, game_board
