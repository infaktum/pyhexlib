import logging
from typing import Optional, Dict, Any, Tuple

from .basic import (
    Orientation,
    Direction,
    AxialCoordinate,
)

__version__ = "0.1.0"
__author__ = "Heiko Sippel"

__all__ = [
    "init",
    "is_initialized",
    "get_config",
    "Orientation",
    "Direction",
    "AxialCoordinate",
]

_initialized: bool = False
_config: Dict[str, Any] = {}

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


# ------------------------------- Standard font -----------------------------

font = {'name': 'Mono.ttf', 'size': 12}


# -------------------------------- Initialization -------------------------------

def init(settings: Optional[Dict[str, Any]] = None,
         *,
         orientation: Orientation = Orientation.FLAT,
         scale: Tuple[float, float] = (1.0, 1.0),
         log_level: Optional[int] = None) -> Dict[str, Any]:
    global _initialized, _config

    if settings is None:
        settings = {}

    cfg = {"orientation": orientation, "scale": scale, **settings}

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


def get_orientation() -> Orientation:
    cfg = get_config()
    return cfg.get("orientation", Orientation.FLAT)


def set_orientation(orientation: Orientation) -> None:
    global _config, _initialized
    if not is_initialized():
        init(orientation=orientation)
        return
    _config["orientation"] = orientation


def get_scale() -> Tuple[float, float,]:
    cfg = get_config()
    # scale is stored under the key "scale" in the config
    return cfg.get("scale", (1.0, 1.0))


def set_scale(scale: Tuple[float, float]) -> None:
    """Set the global scale (sx, sy). If module not initialized yet, call init.

    The signature expects a (sx, sy) tuple.
    """
    global _config, _initialized
    if not is_initialized():
        init(scale=scale)
        return
    _config["scale"] = scale


# -------------- Convenience access methods for orientation and scale -------------------

def __getattr__(name: str):
    if name == "sx":
        return get_scale()[0]
    if name == "sy":
        return get_scale()[1]
    if name == "is_flat":
        return get_orientation() == Orientation.FLAT
    if name == "is_pointy":
        return get_orientation() == Orientation.POINTY
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


def __dir__() -> list:
    # include the dynamic convenience attributes in dir(pyhex)
    names = list(globals().keys())
    names.extend(["sx", "sy", "is_flat", "is_pointy"])
    return sorted(set(names))
