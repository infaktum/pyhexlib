"""Top-level package for pyhex.
"""
__version__ = "0.1.0"
__author__ = "Heiko Sippel"

import logging
from typing import Optional, Dict, Any

from pygame import Color

from .basic import (
    Size,
    Point,
    Rectangle,
)

__all__ = [
    "init",
    "Size",
    "Point"
]

_initialized: bool = False
_config: Dict[str, Any] = {}

navy_skin = {
    "color": Color(28, 61, 90),  # Color(79, 109, 122),
    "Button": {"color": Color(28, 61, 90, 255), "border": 2, "font": "Mono.ttf",
               "text_color": Color(150, 150, 200, 255), "text_size": 20}
}

metal_skin = {
    "color": Color(109, 115, 122),
    "Button": {"color": Color(109, 115, 122), "border": 2, "font": "Mono.ttf",
               "text_color": Color(150, 150, 200, 255), "text_size": 20}
}

default_skin = {
    "color": Color(150, 150, 150, 255),
    # "color": Color(88, 89, 68, 255),
    "Button": {"color": Color(150, 150, 150, 255), "border": 2, "font": "Mono.ttf",
               "text_color": Color(200, 200, 200, 255), "text_size": 20}
}

# ------------------------------- Logging ---------------------------------------


_pyhex_logger = logging.getLogger("pyhex")
# Libraries should not configure I/O handlers by default. Attach a NullHandler
# so that logging calls do nothing unless the application configures logging.
if not _pyhex_logger.handlers:
    _pyhex_logger.addHandler(logging.NullHandler())


def get_logger(name: str):
    if isinstance(name, str) and name.startswith("pyhex"):
        return logging.getLogger(name)
    return logging.getLogger(f"pyhex.{name}")


# -------------------------------- Initialization -------------------------------

def init(settings: Optional[Dict[str, Any]] = None,
         *,
         skin: Optional[Dict[str, Any]] = None,
         log_level: Optional[int] = None) -> Dict[str, Any]:
    global _initialized, _config

    if settings is None:
        settings = {}

    _skin = skin if skin else default_skin
    cfg = {"skin": _skin, **settings}

    if log_level is not None:
        _pyhex_logger.setLevel(log_level)
        cfg["log_level"] = log_level

    _config = cfg
    _initialized = True
    logging.getLogger(__name__).debug("pyhex initialized: %s", _config)
    return _config


def is_initialized() -> bool:
    return _initialized


def get_config() -> Dict[str, Any]:
    return dict(_config)


def get_skin() -> dict:
    return _config.get("skin", default_skin)


def set_skin(skin: dict) -> None:
    global _config, _initialized
    if not is_initialized():
        init(skin=skin)
        return
    _config["skin"] = skin


# -------------- Convenience access methods for orientation and scale -------------------

def __getattr__(name: str):
    if name == "skin" and _initialized:
        return _config["skin"]
    else:
        return default_skin
    # raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list:
    # include the dynamic convenience attributes in dir(pyhex)
    names = list(globals().keys())
    names.extend(["skin"])
    return sorted(set(names))
