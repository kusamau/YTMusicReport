"""Raw YouTube Music playlist parsing.

``ytmusicapi`` intentionally normalizes playlist rows and currently omits the
play-count flex column used by the YouTube Music web UI.  This module uses its
unauthenticated request transport, then parses that column from the raw browse
response before it is discarded.
"""

from __future__ import annotations

from collections.abc import Iterator
from decimal import Decimal, InvalidOperation
import re
from typing import Any, Protocol
from urllib.parse import parse_qs, urlparse

JsonDict = dict[str, Any]

_PLAY_RE = re.compile(
    r"^\s*(?P<number>[0-9][0-9,]*(?:\.[0-9]+)?|[0-9]+,[0-9]+)\s*(?P<suffix>[KMB])?\s+plays?\s*$",
    re.IGNORECASE,
)
_DURATION_RE = re.compile(r"^\d{1,2}:\d{2}(?::\d{2})?$")


class PlaylistRetrievalError(RuntimeError):
    """Raised when YouTube Music cannot supply a usable playlist response."""


class _RawClient(Protocol):
    def _send_request(self, endpoint: str, body: JsonDict) -> JsonDict: ...


def fetch_playlist_plays(playlist: str, *, limit: int | None = None) -> list[JsonDict]:
    """Return displayed play counts and metadata for a public Music playlist.

    ``playlist`` may be a YouTube Music playlist URL or its ``list`` ID.  A
    value of ``None`` for ``limit`` retrieves every available page.
    """

    if limit is not None and limit < 1:
        raise ValueError("limit must be a positive integer or None")

    playlist_id = _playlist_id_from(playlist)

    try:
        from ytmusicapi import YTMusic

        client: _RawClient = YTMusic(language="en")
    except Exception as exc:  # pragma: no cover - dependency/environment failure
        raise PlaylistRetrievalError("Could not initialize the YouTube Music client") from exc

    return _fetch_playlist_plays(client, playlist_id, limit=limit)


def _fetch_playlist_plays(client: _RawClient, playlist_id: str, *, limit: int | None) -> list[JsonDict]:
    """Fetch using an injectable client; kept separate for deterministic tests."""

    browse_id = playlist_id if playlist_id.startswith("VL") else f"VL{playlist_id}"
    try:
        response = client._send_request("browse", {"browseId": browse_id})
    except Exception as exc:
        raise PlaylistRetrievalError(f"Could not retrieve playlist {playlist_id!r}") from exc

    rows: list[JsonDict] = []
    seen_tokens: set[str] = set()
    while True:
        for renderer in _playlist_renderers(response):
            row = _parse_renderer(renderer, position=len(rows) + 1)
            if row is not None:
                rows.append(row)
                if limit is not None and len(rows) >= limit:
                    return rows

        token = _continuation_token(response)
        if not token:
            return rows
        if token in seen_tokens:
            raise PlaylistRetrievalError("YouTube Music returned a repeated continuation token")
        seen_tokens.add(token)

        try:
            response = client._send_request("browse", {"continuation": token})
        except Exception as exc:
            raise PlaylistRetrievalError("Could not retrieve the next playlist page") from exc


def _playlist_id_from(playlist: str) -> str:
    if not isinstance(playlist, str) or not playlist.strip():
        raise ValueError("playlist must be a non-empty playlist URL or ID")

    candidate = playlist.strip()
    parsed = urlparse(candidate)
    if parsed.scheme or parsed.netloc:
        values = parse_qs(parsed.query).get("list", [])
        if len(values) != 1 or not values[0]:
            raise ValueError("playlist URL must contain exactly one non-empty list parameter")
        return values[0]
    if any(character.isspace() for character in candidate):
        raise ValueError("playlist ID must not contain whitespace")
    return candidate


def _playlist_renderers(value: Any) -> Iterator[JsonDict]:
    """Yield list-item renderers in source order from one raw API response."""

    if isinstance(value, dict):
        renderer = value.get("musicResponsiveListItemRenderer")
        if isinstance(renderer, dict) and isinstance(renderer.get("flexColumns"), list):
            yield renderer
        for child in value.values():
            yield from _playlist_renderers(child)
    elif isinstance(value, list):
        for child in value:
            yield from _playlist_renderers(child)


def _continuation_token(value: Any) -> str | None:
    """Find the playlist continuation token carried by a list's trailing item."""

    if isinstance(value, dict):
        continuation = value.get("continuationItemRenderer")
        if isinstance(continuation, dict):
            token = (
                continuation.get("continuationEndpoint", {})
                .get("continuationCommand", {})
                .get("token")
            )
            if isinstance(token, str) and token:
                return token
        for child in value.values():
            token = _continuation_token(child)
            if token:
                return token
    elif isinstance(value, list):
        for child in value:
            token = _continuation_token(child)
            if token:
                return token
    return None


def _parse_renderer(renderer: JsonDict, *, position: int) -> JsonDict | None:
    columns = [_column_text(item) for item in renderer.get("flexColumns", [])]
    if not columns:
        return None

    title_index = _title_index(renderer)
    title = columns[title_index] if title_index is not None else columns[0]
    if not title or title == "Song deleted":
        return None

    artist_indexes = _artist_indexes(renderer)
    artists = _artists(renderer, artist_indexes)
    play_index = next((index for index, text in enumerate(columns) if _PLAY_RE.match(text or "")), None)
    album_index = _album_index(renderer)
    if album_index is None:
        excluded = {index for index in (title_index, play_index) if index is not None} | artist_indexes
        album_index = next(
            (index for index, text in enumerate(columns) if index not in excluded and text and not _DURATION_RE.match(text)),
            None,
        )

    plays_display = columns[play_index] if play_index is not None else None
    return {
        "position": position,
        "video_id": _video_id(renderer),
        "title": title,
        "artists": artists,
        "album": _album(renderer, album_index),
        "duration": _duration(renderer),
        "plays_display": plays_display,
        "plays_estimate": _parse_play_estimate(plays_display),
    }


def _column_text(column: Any) -> str | None:
    if not isinstance(column, dict):
        return None
    return _text(column.get("musicResponsiveListItemFlexColumnRenderer", {}).get("text"))


def _text(value: Any) -> str | None:
    if not isinstance(value, dict):
        return None
    simple = value.get("simpleText")
    if isinstance(simple, str):
        return simple
    runs = value.get("runs")
    if isinstance(runs, list):
        text = "".join(run.get("text", "") for run in runs if isinstance(run, dict))
        return text or None
    return None


def _column_runs(renderer: JsonDict, index: int) -> list[JsonDict]:
    columns = renderer.get("flexColumns", [])
    if not isinstance(columns, list) or index >= len(columns):
        return []
    try:
        runs = columns[index]["musicResponsiveListItemFlexColumnRenderer"]["text"].get("runs", [])
    except (KeyError, TypeError):
        return []
    return [run for run in runs if isinstance(run, dict)] if isinstance(runs, list) else []


def _page_type(run: JsonDict) -> str | None:
    endpoint = run.get("navigationEndpoint", {}).get("browseEndpoint", {})
    config = endpoint.get("browseEndpointContextSupportedConfigs", {}).get("browseEndpointContextMusicConfig", {})
    page_type = config.get("pageType")
    return page_type if isinstance(page_type, str) else None


def _title_index(renderer: JsonDict) -> int | None:
    for index in range(len(renderer.get("flexColumns", []))):
        if any("watchEndpoint" in run.get("navigationEndpoint", {}) for run in _column_runs(renderer, index)):
            return index
    return None


def _artist_indexes(renderer: JsonDict) -> set[int]:
    indexes: set[int] = set()
    for index in range(len(renderer.get("flexColumns", []))):
        if any(_page_type(run) == "MUSIC_PAGE_TYPE_ARTIST" for run in _column_runs(renderer, index)):
            indexes.add(index)
    return indexes


def _artists(renderer: JsonDict, indexes: set[int]) -> list[JsonDict]:
    artists: list[JsonDict] = []
    for index in indexes:
        for run in _column_runs(renderer, index):
            if _page_type(run) != "MUSIC_PAGE_TYPE_ARTIST":
                continue
            endpoint = run["navigationEndpoint"]["browseEndpoint"]
            name = run.get("text")
            artist_id = endpoint.get("browseId")
            if isinstance(name, str) and name:
                artists.append({"name": name, "id": artist_id if isinstance(artist_id, str) else None})
    return artists


def _album_index(renderer: JsonDict) -> int | None:
    for index in range(len(renderer.get("flexColumns", []))):
        if any(_page_type(run) == "MUSIC_PAGE_TYPE_ALBUM" for run in _column_runs(renderer, index)):
            return index
    return None


def _album(renderer: JsonDict, index: int | None) -> JsonDict | None:
    if index is None:
        return None
    name = _column_text(renderer.get("flexColumns", [])[index])
    if not name:
        return None
    album_id = next(
        (
            run.get("navigationEndpoint", {}).get("browseEndpoint", {}).get("browseId")
            for run in _column_runs(renderer, index)
            if _page_type(run) == "MUSIC_PAGE_TYPE_ALBUM"
        ),
        None,
    )
    return {"name": name, "id": album_id if isinstance(album_id, str) else None}


def _video_id(renderer: JsonDict) -> str | None:
    for value in _walk(renderer):
        if not isinstance(value, dict):
            continue
        video_id = value.get("playNavigationEndpoint", {}).get("watchEndpoint", {}).get("videoId")
        if isinstance(video_id, str):
            return video_id
        video_id = value.get("watchEndpoint", {}).get("videoId")
        if isinstance(video_id, str):
            return video_id
    return None


def _duration(renderer: JsonDict) -> str | None:
    fixed_columns = renderer.get("fixedColumns", [])
    if isinstance(fixed_columns, list):
        for column in fixed_columns:
            try:
                text = _text(column["musicResponsiveListItemFixedColumnRenderer"]["text"])
            except (KeyError, TypeError):
                text = None
            if text:
                return text
    for column in renderer.get("flexColumns", []):
        text = _column_text(column)
        if text and _DURATION_RE.match(text):
            return text
    return None


def _walk(value: Any) -> Iterator[Any]:
    yield value
    if isinstance(value, dict):
        for child in value.values():
            yield from _walk(child)
    elif isinstance(value, list):
        for child in value:
            yield from _walk(child)


def _parse_play_estimate(value: str | None) -> int | None:
    if value is None:
        return None
    match = _PLAY_RE.match(value)
    if not match:
        return None
    number = match.group("number")
    suffix = match.group("suffix")
    try:
        if suffix:
            parsed = Decimal(number.replace(",", "."))
            multiplier = {"K": 1_000, "M": 1_000_000, "B": 1_000_000_000}[suffix.upper()]
            return int(parsed * multiplier)
        return int(number.replace(",", ""))
    except (InvalidOperation, ValueError):
        return None
