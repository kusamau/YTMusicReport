from __future__ import annotations

import json
from pathlib import Path

import pytest

from ytmusic_report.playlist import (
    PlaylistRetrievalError,
    _fetch_playlist_plays,
    _parse_play_estimate,
    _playlist_id_from,
)


FIXTURES = Path(__file__).parent / "fixtures"


class FakeClient:
    def __init__(self, *responses: dict) -> None:
        self.responses = list(responses)
        self.calls: list[tuple[str, dict]] = []

    def _send_request(self, endpoint: str, body: dict) -> dict:
        self.calls.append((endpoint, body))
        return self.responses.pop(0)


def fixture(name: str) -> dict:
    return json.loads((FIXTURES / name).read_text())


def test_extracts_metadata_displayed_plays_and_continuations() -> None:
    client = FakeClient(fixture("playlist_page.json"), fixture("playlist_continuation.json"))

    rows = _fetch_playlist_plays(client, "OLAK-test", limit=None)

    assert client.calls == [
        ("browse", {"browseId": "VLOLAK-test"}),
        ("browse", {"continuation": "next-page"}),
    ]
    assert rows == [
        {
            "position": 1,
            "video_id": "video-1",
            "title": "Up556",
            "artists": [{"name": "layze", "id": "artist-1"}],
            "album": {"name": "Up556", "id": "album-1"},
            "duration": "3:42",
            "plays_display": "22M plays",
            "plays_estimate": 22_000_000,
        },
        {
            "position": 2,
            "video_id": "video-2",
            "title": "No count",
            "artists": [{"name": "layze", "id": "artist-1"}],
            "album": {"name": "Unknown", "id": None},
            "duration": None,
            "plays_display": None,
            "plays_estimate": None,
        },
        {
            "position": 3,
            "video_id": "video-3",
            "title": "You",
            "artists": [{"name": "Yung Deco", "id": "artist-2"}],
            "album": None,
            "duration": None,
            "plays_display": "3.3K plays",
            "plays_estimate": 3300,
        },
    ]


@pytest.mark.parametrize(
    ("display", "expected"),
    [
        ("334K plays", 334_000),
        ("2.8K plays", 2800),
        ("1,234 plays", 1234),
        ("1.2B plays", 1_200_000_000),
        ("Unknown", None),
        (None, None),
    ],
)
def test_parses_abbreviated_play_estimates(display: str | None, expected: int | None) -> None:
    assert _parse_play_estimate(display) == expected


def test_accepts_url_or_playlist_id() -> None:
    playlist_id = "OLAK5uy_example"
    assert _playlist_id_from(playlist_id) == playlist_id
    assert _playlist_id_from(f"https://music.youtube.com/playlist?list={playlist_id}") == playlist_id


@pytest.mark.parametrize("value", ["", "   ", "https://music.youtube.com/playlist", "bad id"])
def test_rejects_invalid_playlist_inputs(value: str) -> None:
    with pytest.raises(ValueError):
        _playlist_id_from(value)


def test_rejects_repeated_continuation_token() -> None:
    response = fixture("playlist_page.json")
    client = FakeClient(response, response)

    with pytest.raises(PlaylistRetrievalError, match="repeated continuation"):
        _fetch_playlist_plays(client, "OLAK-test", limit=None)
