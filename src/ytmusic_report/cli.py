"""Command-line entry point for the playlist play-count extractor."""

from __future__ import annotations

import argparse
import json
from collections.abc import Sequence
from pathlib import Path

from . import __version__
from .playlist import PlaylistRetrievalError, fetch_playlist_plays


def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="ytmusic-report",
        description="Return displayed YouTube Music playlist play counts as JSON.",
    )
    parser.add_argument("playlist", help="YouTube Music playlist URL or playlist ID")
    parser.add_argument(
        "-v",
        "--version",
        action="version",
        version=_version_line(),
        help="show version and license information",
    )
    parser.add_argument(
        "--limit",
        type=_positive_int,
        metavar="N",
        help="maximum number of playlist rows to retrieve",
    )
    parser.add_argument(
        "-o",
        "--output",
        type=Path,
        metavar="PATH",
        help="write formatted JSON to PATH instead of standard output",
    )
    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="replace an existing output file (requires --output)",
    )
    return parser


def _version_line() -> str:
    return f"ytmusic-report {__version__} - MIT License (c) 2026 Maurizio Nagni"


def _positive_int(value: str) -> int:
    try:
        result = int(value)
    except ValueError as exc:
        raise argparse.ArgumentTypeError("must be a positive integer") from exc
    if result < 1:
        raise argparse.ArgumentTypeError("must be a positive integer")
    return result


def main(argv: Sequence[str] | None = None) -> int:
    """Run the extractor and write JSON to standard output."""

    parser = _parser()
    arguments = parser.parse_args(argv)
    if arguments.force and arguments.output is None:
        parser.error("--force requires --output")
    if arguments.output is not None:
        _validate_output_path(parser, arguments.output, force=arguments.force)

    try:
        rows = fetch_playlist_plays(arguments.playlist, limit=arguments.limit)
    except (PlaylistRetrievalError, ValueError) as exc:
        parser.exit(2, f"ytmusic-report: error: {exc}\n")

    output = json.dumps(rows, indent=2, ensure_ascii=False) + "\n"
    if arguments.output is None:
        print(output, end="")
    else:
        try:
            _write_output(arguments.output, output, force=arguments.force)
        except OSError as exc:
            parser.exit(2, f"ytmusic-report: error: could not write {arguments.output}: {exc}\n")
        print(f"Saved {len(rows)} rows to {arguments.output}")
    return 0


def _validate_output_path(parser: argparse.ArgumentParser, path: Path, *, force: bool) -> None:
    if not path.parent.is_dir():
        parser.exit(2, f"ytmusic-report: error: output directory does not exist: {path.parent}\n")
    if path.is_dir():
        parser.exit(2, f"ytmusic-report: error: {path} is a directory\n")
    if path.exists() and not force:
        parser.exit(
            2,
            f"ytmusic-report: warning: {path} already exists; use --force (-f) to overwrite it\n",
        )


def _write_output(path: Path, output: str, *, force: bool) -> None:
    mode = "w" if force else "x"
    with path.open(mode, encoding="utf-8") as destination:
        destination.write(output)


if __name__ == "__main__":  # pragma: no cover
    raise SystemExit(main())
