import pygame

Point = pygame.Vector2
Rectangle = pygame.Rect

Transparent = pygame.Color(0, 0, 0, 0)


class Size(pygame.Vector2):
    @property
    def w(self):
        return self.x

    @property
    def h(self):
        return self.y

    @property
    def width(self):
        return self.x

    @property
    def height(self):
        return self.y

    def __iter__(self):
        """Allow unpacking: w, h = size"""
        yield self.x
        yield self.y

    def to_tuple(self):
        """Return (w, h) as a plain tuple."""
        return (self.x, self.y)

    @classmethod
    def from_tuple(cls, tup):
        """Create a Size from a (w, h) tuple or list."""
        return cls(tup[0], tup[1])

    def __repr__(self):
        return f"Size(w={self.x}, h={self.y})"

