"""lungmask package metadata."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("lungmask")
except PackageNotFoundError:  # pragma: no cover - local source tree without installed metadata
    __version__ = "0+unknown"

__all__ = ["__version__"]
