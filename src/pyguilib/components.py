from abc import ABC

import pygame

import pyguilib
import pyguilib.draw
from pyguilib import Size
from pyhexlib.graphic import Rectangle


def rimmed(cls):
    # Wrap the existing instance method `draw` so we can run extra logic
    # (e.g. draw a rim) and then call the original method. Store the
    # original method to avoid recursion.
    orig_draw = getattr(cls, 'draw', None)

    def draw(self, *args, **kwargs):
        if orig_draw:
            return orig_draw(self, *args, **kwargs)

    cls.draw = draw
    return cls


# ------------------------------------ Base Classes -----------------------------------

class Component(ABC):
    def __init__(self, _id: str, size: Size = Size(0, 0), visible: bool = True, active: bool = True):
        self.id = _id

        self.size = size if isinstance(size, Size) else Size(*size)
        self.visible = visible
        self.active = active
        self.dirty = True

    @property
    def width(self):
        return self.size.w

    @property
    def height(self):
        return self.size.h

    def toggle_visible(self) -> None:
        """Toggle the visibility of the component."""
        self.visible = not self.visible
        self.dirty = True

    def __repr__(self) -> str:
        """Return an English developer representation of the Component.

        Shows id, size, visibility and active state.
        """
        return (
            f"{self.__class__.__name__}(id={self.id!r}, size={self.size!r}, "
            f"visible={self.visible!r}, active={self.active!r})"
        )


# ---------------------------------------- Visible Components --------------------------------------------

class VisibleComponent(Component):
    def __init__(self, _id: str, size: Size):
        super().__init__(_id, size=size, visible=True, active=True)
        self.image = pygame.Surface(self.size, flags=pygame.SRCALPHA)

    def __repr__(self) -> str:
        """Return an English developer representation of the VisibleComponent.

        Shows id, size and whether an image surface exists.
        """
        return (
            f"{self.__class__.__name__}(id={self.id!r}, size={self.size!r}, image_set={self.image is not None})"
        )


# ------------------------------------- Overlay --------------------------------------------


class Overlay(VisibleComponent):
    def __init__(self, _id: str, size: Size, windows: list[Rectangle]):
        super().__init__(_id, size=size)
        self.windows = windows

    def __repr__(self) -> str:
        """Return an English developer representation of the Overlay.

        Shows id, size and number of transparent windows.
        """
        return (
            f"{self.__class__.__name__} (id={self.id!r}, size={self.size!r}, windows={len(self.windows)})"
        )


# ---------------------------------------- Rim ------------------------------------------------

class Rim(VisibleComponent):
    def __init__(self, _id: str, size: Size):
        super().__init__(_id, size=size)

    def __repr__(self) -> str:
        """Return an English developer representation of the Rim.

        Shows id and size.
        """
        return f"{self.__class__.__name__} (id={self.id!r}, size={self.size!r})"


class TransparentComponent(VisibleComponent):
    def __init__(self, _id: str, size: Size):
        super().__init__(_id, size=size)
        self.image = pygame.Surface(self.size, flags=pygame.SRCALPHA)
        self.image.fill((0, 0, 0, 0))

    def __repr__(self) -> str:
        """Return an English developer representation of the TransparentComponent.

        Shows id, size and that the image is transparent.
        """
        return (
            f"{self.__class__.__name__} (id={self.id!r}, size={self.size!r}, transparent_image=True)"
        )


# ------------------------------------------ Image -------------------------------------

class Image(VisibleComponent):
    def __init__(self, _id: str, size: Size = None, image: pygame.Surface = None):
        super().__init__(_id, size=Size(0, 0))

        if size is not None:
            self.image = pygame.transform.smoothscale(image, size)
        else:
            self.image = image
        self.size = image.get_size()


# --------------------------------------------- Button ----------------------------------


class Button(VisibleComponent):
    def __init__(self, button_id, size: Size, text: str = ''):
        super().__init__(button_id, size=size)
        self.text = text
        self.state = False

        self.image = pyguilib.draw.draw_button(size=size, text=text)

    def __repr__(self) -> str:
        """Return a developer representation of the Button.

        Shows id, text label, size and current state.
        """
        return (
            f"{self.__class__.__name__} (id={self.id!r}, text={self.text!r}, size={self.size!r}, state={self.state!r})"
        )
