#  MIT License
#
#  Copyright (c) 2026 Heiko Sippel
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to deal
#  in the Software without restriction, including without limitation the rights
#  to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#  copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in all
#  copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#  OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#  SOFTWARE.
#
#
from pyhex import Direction
from pyhex.tokens import DirectionToken, Token


class Plane(DirectionToken):
    def __init__(self, name, image, movement, hp, position, direction):
        super().__init__(name, image, position, direction)
        self.movement = movement
        self.hp = hp

    def __repr__(self):
        return f"{Plane.__name__} (name={self.id}, movement={self.movement}, hp={self.hp}, position={self.rc}, direction={self.direction})"


class Tank(DirectionToken):
    def __init__(self, name, image, movement, hp, position, direction):
        super().__init__(name, image, position, direction)
        self.movement = movement
        self.hp = hp

    def __repr__(self):
        return f"{Tank.__name__} (name={self.id}, movement={self.movement}, hp={self.hp}, position={self.rc}, direction={self.direction})"


# ------------------------------- GameBoard -----------------------------------

class GameBoard:

    def __init__(self, token_layer, assets=None):
        self.assets = assets
        self.token_layer = token_layer
        self.marker = None
        self.shadow = None

        self.images = {"tank": assets.get_image(0), "plane": assets.get_image(1), "soldier": assets.get_image(2),
                       "tank_shadow": assets.get_shadow(0), "plane_shadow": assets.get_shadow(1),
                       "soldier_shadow": assets.get_shadow(2)
                       }

        self.tokens = {
            "tank": Tank("tank", self.images["tank"], movement=3, hp=12, position=(10, 20),
                         direction=Direction.SOUTH),
            "plane": Plane("plane", self.images["plane"], movement=7, hp=4, position=(6, 3),
                           direction=Direction.NORTHWEST)}

        self.shadow_tokens = {"tank": DirectionToken("tank", self.images["tank_shadow"], None, None),
                              "plane": DirectionToken("plane_shadow", self.images["plane_shadow"], None, None)}

        self.tank = self.tokens["tank"]
        self.plane = self.tokens["plane"]

        self.set_token((5, 20), self.tank, direction=Direction.SOUTHWEST)
        self.set_token((6, 3), self.plane)

    def set_token(self, rc, token: Token, direction: Direction = None):
        token.direction = direction
        self.token_layer.set_token(rc, token)

    def get_token(self, rc):
        return self.token_layer.get_token(rc)

    def remove_token(self, rc):
        self.token_layer.remove_token(rc)

    def put_marker(self, rc):
        self.marker = rc

    def remove_marker(self):
        self.marker = None

    def check_game_over(self, player):
        pass

    def compute_score(self):
        pass
