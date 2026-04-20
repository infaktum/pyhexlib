from pyhexlib.hexagons import Hexagon, Direction, HexagonalGrid, rectangle_map
from pyhexlib.layers import TokenGridLayer, HexGridManager, OutlineGridLayer, FillGridLayer, \
    SimpleImageGridLayer, PathGridLayer, TerrainGridLayer
from pyhexlib.tokens import Token, SimpleToken


# ------------------------------  DirectionTokens -----------------------------------

class Unit(SimpleToken):
    def __init__(self, token_id, image, unit_type=0, unit_range: int = None, hp: int = None,
                 rc: Hexagon = None) -> None:
        super().__init__(token_id, image, rc)
        self.unit_type = unit_type
        self._range = unit_range
        self._hp = hp

    @property
    def range(self) -> int:
        return self._range

    @property
    def hp(self) -> int:
        return self._hp

    def __repr__(self) -> str:
        """Return a concise developer representation for Fighter.

        Shows the token id, grid coordinate (rc), direction name, speed, hp and
        whether an image surface is present.
        """
        image_set = getattr(self, "_image", None) is not None
        return (
            f"{self.__class__.__name__}(id={self.id!r}, rc={self.rc!r}, "
            f"range={self.range!r}, hp={self.hp!r}, image_set={image_set})"
        )


class Infantry(Unit):

    def __init__(self, token_id, image, rc: Hexagon = None) -> None:
        super().__init__(token_id, image, 0, unit_range=2, hp=3, rc=rc)


class Armor(Unit):

    def __init__(self, token_id, image, rc: Hexagon = None) -> None:
        super().__init__(token_id, image, 0, 5, 10, rc)


class Artillery(Unit):

    def __init__(self, token_id, image, rc: Hexagon = None) -> None:
        super().__init__(token_id, image, 0, 2, 6, rc)


class Plane(Unit):

    def __init__(self, token_id, image, rc: Hexagon = None) -> None:
        super().__init__(token_id, image, 2, 8, 4, rc)


class Battleship(Unit):

    def __init__(self, token_id, image, rc: Hexagon = None) -> None:
        super().__init__(token_id, image, 1, 2, 20, rc)


# ------------------------------  GameBoard -----------------------------------

class Map:

    def __init__(self, token_layer: TokenGridLayer, target_layer: TokenGridLayer, cities_layer, assets):
        self.token_layer = token_layer
        self.target_layer = target_layer
        self.cities_layer = cities_layer
        self.assets = assets
        self.marker = None

        self.cities_layer.set_image(Hexagon(11, 10), self.assets.cities[2])
        self.cities_layer.set_image(Hexagon(14, 11), self.assets.cities[2])
        self.cities_layer.set_image(Hexagon(10, 8), self.assets.cities[0])
        self.cities_layer.set_image(Hexagon(8, 10), self.assets.cities[0])
        self.cities_layer.set_image(Hexagon(10, 12), self.assets.cities[1])
        self.cities_layer.set_image(Hexagon(12, 4), self.assets.cities[1])
        self.cities_layer.set_image(Hexagon(4, 10), self.assets.cities[5])
        self.images = {
            "US": {"infantry": assets.get_unit("US", "Infantry"), "armor": assets.get_unit("US", "Armor"),
                   "artillery": assets.get_unit("US", "Artillery"), "plane": assets.get_unit("US", "AirForce"),
                   "ship": assets.get_unit("US", "Navy"),
                   },
            "Axis": {"infantry": assets.get_unit("Axis", "Infantry"), "armor": assets.get_unit("Axis", "Armor"),
                     "artillery": assets.get_unit("Axis", "Artillery"), "plane": assets.get_unit("Axis", "AirForce"),
                     "ship": assets.get_unit("Axis", "Navy"),
                     },
        }

        self.tokens = {"US": {
            "infantry": Infantry("us_infantry", self.images["US"]["infantry"], rc=Hexagon(4, 9)),
            "armor": Armor("us_armor", self.images["US"]["armor"], rc=Hexagon(4, 11)),
            "artillery": Artillery("us_artillery", self.images["US"]["artillery"]),
            "plane": Plane("us_plane", self.images["US"]["plane"]),
            "ship": Battleship("us_ship", self.images["US"]["ship"]),

        }, "Axis": {
            "infantry": Infantry("axis_infantry", self.images["Axis"]["infantry"], rc=Hexagon(4, 9)),
            "armor": Armor("axis_armor", self.images["Axis"]["armor"], rc=Hexagon(4, 11)),
            "artillery": Artillery("axis_artillery", self.images["Axis"]["artillery"]),
            "plane": Plane("axis_plane", self.images["Axis"]["plane"]),
            "ship": Battleship("axis_ship", self.images["Axis"]["ship"]),

        }, "UK": {}}

    def setup(self):
        self.set_token(Hexagon(7, 9), self.tokens["US"]["infantry"])
        self.set_token(Hexagon(7, 12), self.tokens["US"]["armor"])
        self.set_token(Hexagon(10, 11), self.tokens["US"]["plane"])
        self.set_token(Hexagon(1, 1), self.tokens["US"]["ship"])

        self.set_token(Hexagon(10, 15), self.tokens["Axis"]["infantry"])
        self.set_token(Hexagon(5, 23), self.tokens["Axis"]["armor"])
        self.set_token(Hexagon(9, 15), self.tokens["Axis"]["plane"])
        self.set_token(Hexagon(3, 9), self.tokens["Axis"]["ship"])

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
        return True  # return token.id in ["xwing1", "tie1"]

    def put_marker(self, rc):
        self.marker = rc

    def remove_marker(self):
        self.marker = None

    def put_target(self, rc):
        pass

    def remove_target(self, rc):
        self.target_layer.remove_token(rc)


# ----------------------------------- Setup function -----------------------------------

def setup(rows, cols, assets):
    hexagons = HexagonalGrid(rectangle_map(rows, cols))
    grids = HexGridManager(hexagons)

    token_layer = TokenGridLayer("tokens")
    location_layer = SimpleImageGridLayer("locations")
    target_layer = TokenGridLayer("targets")
    board = Map(token_layer, target_layer, location_layer, assets)

    grids.add_layer(SimpleImageGridLayer("background"))
    grids.add_layer(location_layer)
    grids.add_layer(setup_terrain("terrain"))
    grids.add_layer(FillGridLayer("neighbors"))
    grids.add_layer(PathGridLayer("path"))
    grids.add_layer(token_layer)
    grids.add_layer(target_layer)
    grids.add_layer(OutlineGridLayer("outline", default_color=(255, 255, 255,), default_width=1))
    return grids, board


def setup_terrain(name: str):
    terrain = TerrainGridLayer(name, default_value=(1, 1, 1))
    land = [Hexagon(4, 9)]
    water = [(19, 0), (11, 0), (12, 0), (11, 1), (10, 2), (9, 3), (9, 4), (8, 5), (8, 6), (7, 6), (6, 7), (5, 7),
             (5, 8), (4, 9), (4, 10),
             (3, 11), (3, 12), (3, 13), (2, 13), (1, 13), (0, 13), (0, 12), ]
    for rc in land:
        terrain.set_value(rc, (1, 100, 1))
    for rc in water:
        terrain.set_value(rc, (1000, 1, 1))
    return terrain
