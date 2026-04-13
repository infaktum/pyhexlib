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
from abc import ABC, abstractmethod

import pygame

import pyhex.graphic as g
from pyhex.hexagons import Direction, Hexagon


# ------------------------------ Tokens -----------------------------------

class Token(ABC):
    def __init__(self, token_id: int | str, image: pygame.Surface = None, rc: Hexagon = None, ) -> None:
        self.id = token_id
        self.rc = rc
        self._image = image

    @property
    @abstractmethod
    def angle(self) -> pygame.Surface:
        ...

    @angle.setter
    @abstractmethod
    def angle(self, angle) -> pygame.Surface:
        ...

    @property
    def image(self):

        if self.angle is None or self.angle == 0:
            return self._image
        else:
            return g.rotate_image(self._image, self.angle)

    def __repr__(self) -> str:
        """Return a concise developer representation for DirectionToken.

        Shows the token id, grid coordinate (rc), the direction name, the
        computed angle (degrees) and whether an image surface is present.
        """

        return (
            f"{self.__class__.__name__}(id={self.id!r}, rc={self.rc!r}, image_set={self._image is not None})"
        )


# ------------------------------     SimpleToken -----------------------------------

class SimpleToken(Token):
    def __init__(self, token_id: int | str, image: pygame.Surface = None, rc=None) -> None:
        super().__init__(token_id, image, rc)

    @property
    def angle(self):
        return 0

    @angle.setter
    def angle(self, angle: int) -> None:
        pass


# ------------------------------  FreeToken -----------------------------------

class FreeToken(Token):
    def __init__(self, token_id: int | str, image: pygame.Surface = None, rc=None, angle: int = None) -> None:
        super().__init__(token_id, image, rc)
        self._angle = angle

    @property
    def angle(self):
        return self._angle

    @angle.setter
    def angle(self, angle: int) -> None:
        self._angle = angle

    def __repr__(self) -> str:
        """Return a concise developer representation for DirectionToken.

        Shows the token id, grid coordinate (rc), the direction name, the
        computed angle (degrees) and whether an image surface is present.
        """
        dir_name = getattr(self.direction, "name", repr(self.direction))
        return (
            f"(id={self.id!r}, rc={self.rc!r}, direction={dir_name!r}, "
            f"angle={self.angle!r}, image_set={self._image is not None})"
        )


# ------------------------------  DirectionToken -----------------------------------

class DirectionToken(Token):
    def __init__(self, token_id: int | str, image: pygame.Surface = None, rc=None,
                 direction: Direction = Direction.NORTH) -> None:
        super().__init__(token_id, image, rc)
        self.direction = direction

    @property
    def angle(self):
        return g.direction_to_angle(self.direction)

    @angle.setter
    def angle(self, angle: int) -> None:
        pass

    def __repr__(self) -> str:
        """Return a concise developer representation for DirectionToken.

        Shows the token id, grid coordinate (rc), the direction name, the
        computed angle (degrees) and whether an image surface is present.
        """
        dir_name = getattr(self.direction, "name", repr(self.direction))
        return (
            f"{self.__class__.__name__}(id={self.id!r}, rc={self.rc!r}, direction={dir_name!r}, "
            f"angle={self.angle!r}, image_set={self._image is not None})"
        )
