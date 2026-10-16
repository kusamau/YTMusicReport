from __future__ import annotations

import json
from importlib.metadata import version

import pytest

from ytmusic_report import __version__, cli
from ytmusic_report.playlist import PlaylistRetrievalError


def test_prints_json_and_forwards_limit(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    expected = [{"title": "Up556", "plays_display": "22M plays", "plays_estimate": 22_000_000}]
    received: dict[str, object] = {}

    def fetch(playlist: str, *, limit: int | None) -> list[dict[str, object]]:
        received["playlist"] = playlist
        received["limit"] = limit
        return expected

    monkeypatch.setattr(cli, "fetch_playlist_plays", fetch)

    assert cli.main(["playlist-id", "--limit", "25"]) == 0
    assert received == {"playlist": "playlist-id", "limit": 25}
    assert json.loads(capsys.readouterr().out) == expected


@pytest.mark.parametrize("flag", ["-v", "--version"])
def test_prints_version_and_license_without_fetching(
    monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], flag: str
) -> None:
    monkeypatch.setattr(cli, "fetch_playlist_plays", lambda playlist, *, limit: pytest.fail("must not fetch"))

    with pytest.raises(SystemExit) as exit_info:
        cli.main([flag])

    assert exit_info.value.code == 0
    assert capsys.readouterr().out == "ytmusic-report 0.1.0 - MIT License (c) 2026 Maurizio Nagni\n"


def test_public_version_matches_distribution_metadata() -> None:
    assert __version__ == version("ytmusic-report")


def test_writes_json_to_new_output_file(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path) -> None:
    expected = [{"title": "Up556", "plays_display": "22M plays", "plays_estimate": 22_000_000}]
    output_path = tmp_path / "top-songs.json"

    monkeypatch.setattr(cli, "fetch_playlist_plays", lambda playlist, *, limit: expected)

    assert cli.main(["playlist-id", "--output", str(output_path)]) == 0
    assert json.loads(output_path.read_text()) == expected
    assert capsys.readouterr().out == f"Saved 1 rows to {output_path}\n"


def test_retains_existing_file_without_force(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path) -> None:
    output_path = tmp_path / "top-songs.json"
    output_path.write_text("existing JSON\n")
    monkeypatch.setattr(cli, "fetch_playlist_plays", lambda playlist, *, limit: pytest.fail("must not fetch"))

    with pytest.raises(SystemExit) as exit_info:
        cli.main(["playlist-id", "--output", str(output_path)])

    assert exit_info.value.code == 2
    assert output_path.read_text() == "existing JSON\n"
    assert f"{output_path} already exists; use --force (-f)" in capsys.readouterr().err


def test_force_replaces_existing_file(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str], tmp_path) -> None:
    output_path = tmp_path / "top-songs.json"
    output_path.write_text("old JSON\n")
    expected = [{"title": "Up556"}]
    monkeypatch.setattr(cli, "fetch_playlist_plays", lambda playlist, *, limit: expected)

    assert cli.main(["playlist-id", "--output", str(output_path), "--force"]) == 0
    assert json.loads(output_path.read_text()) == expected
    assert capsys.readouterr().out == f"Saved 1 rows to {output_path}\n"


def test_force_requires_output(capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["playlist-id", "--force"])

    assert exit_info.value.code == 2
    assert "--force requires --output" in capsys.readouterr().err


def test_rejects_missing_output_directory(capsys: pytest.CaptureFixture[str], tmp_path) -> None:
    output_path = tmp_path / "missing" / "top-songs.json"

    with pytest.raises(SystemExit) as exit_info:
        cli.main(["playlist-id", "--output", str(output_path)])

    assert exit_info.value.code == 2
    assert "output directory does not exist" in capsys.readouterr().err


def test_reports_retrieval_error(monkeypatch: pytest.MonkeyPatch, capsys: pytest.CaptureFixture[str]) -> None:
    def fetch(playlist: str, *, limit: int | None) -> list[dict[str, object]]:
        raise PlaylistRetrievalError("playlist unavailable")

    monkeypatch.setattr(cli, "fetch_playlist_plays", fetch)

    with pytest.raises(SystemExit) as exit_info:
        cli.main(["playlist-id"])

    assert exit_info.value.code == 2
    assert "playlist unavailable" in capsys.readouterr().err


@pytest.mark.parametrize("value", ["0", "-1", "not-a-number"])
def test_rejects_invalid_limit(value: str, capsys: pytest.CaptureFixture[str]) -> None:
    with pytest.raises(SystemExit) as exit_info:
        cli.main(["playlist-id", "--limit", value])

    assert exit_info.value.code == 2
    assert "positive integer" in capsys.readouterr().err
