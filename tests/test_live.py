from __future__ import annotations

import os

import pytest

from ytmusic_report import fetch_playlist_plays


@pytest.mark.live
@pytest.mark.skipif(os.getenv("YTMUSIC_LIVE_TEST") != "1", reason="set YTMUSIC_LIVE_TEST=1 to enable")
def test_public_playlist_contains_at_least_one_displayed_count() -> None:
    rows = fetch_playlist_plays("OLAK5uy_mGTAhnwAhzAT-1M52__jQqIGP-wc2sE_A", limit=25)
    assert rows
    assert any(row["plays_display"] is not None for row in rows)
