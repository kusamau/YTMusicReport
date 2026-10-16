"""Public API for extracting displayed YouTube Music playlist play counts."""

from importlib.metadata import version

from .playlist import PlaylistRetrievalError, fetch_playlist_plays

__version__ = version("ytmusic-report")

__all__ = ["PlaylistRetrievalError", "__version__", "fetch_playlist_plays"]
