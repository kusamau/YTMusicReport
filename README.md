# ytmusic-report

[![Python 3.10+](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python&logoColor=white)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-4CAF50)](LICENSE)

Retrieve the per-track play values displayed on a public YouTube Music playlist
and export the results as structured JSON. `ytmusic-report` accepts a playlist
URL or ID, keeps the exact value shown by YouTube Music, and includes useful
track metadata such as artists, album, duration, and video ID.

## Features

- Query public YouTube Music playlist URLs and playlist IDs.
- Extract the displayed **Plays** column alongside track metadata.
- Return formatted JSON to the terminal or save it to a file.
- Protect existing output files unless `--force` is explicitly supplied.
- Start quickly with macOS/Linux Bash or Windows PowerShell launchers.
- Use the extractor from the command line or directly from Python.

## Quick start

### Requirements

- Python 3.10 or newer.
- Internet access to reach YouTube Music.

### macOS and Linux

From a project checkout, `run.sh` creates a local `.venv`, installs the project,
and runs the command:

```bash
./run.sh 'https://music.youtube.com/playlist?list=OLAK5uy_mGTAhnwAhzAT-1M52__jQqIGP-wc2sE_A'
```

Save the result to a file:

```bash
./run.sh OLAK5uy_mGTAhnwAhzAT-1M52__jQqIGP-wc2sE_A --output top-songs.json
```

### Windows PowerShell

```powershell
.\run.ps1 'https://music.youtube.com/playlist?list=OLAK5uy_mGTAhnwAhzAT-1M52__jQqIGP-wc2sE_A'
.\run.ps1 OLAK5uy_mGTAhnwAhzAT-1M52__jQqIGP-wc2sE_A --output top-songs.json
```

If PowerShell prevents script execution, run:

```powershell
powershell -ExecutionPolicy Bypass -File .\run.ps1 OLAK5uy_mGTAhnwAhzAT-1M52__jQqIGP-wc2sE_A
```

The virtual environment is operating-system-specific. Remove `.venv` before
using the same checkout on a different operating system.

## Command-line interface

After installation, use the command directly:

```bash
python -m pip install .
ytmusic-report PLAYLIST [--limit N] [--output PATH] [--force]
```

| Option | Description |
| --- | --- |
| `PLAYLIST` | Required YouTube Music playlist URL or playlist ID. |
| `--limit N` | Return at most `N` tracks. |
| `-o PATH`, `--output PATH` | Save formatted JSON to `PATH` instead of printing it. |
| `-f`, `--force` | Replace an existing output file; requires `--output`. |
| `-v`, `--version` | Print version and MIT License information. |
| `-h`, `--help` | Show command help. |

Examples:

```bash
# Print the first 25 tracks as JSON.
./run.sh OLAK5uy_mGTAhnwAhzAT-1M52__jQqIGP-wc2sE_A --limit 25

# Save results without overwriting an existing file.
./run.sh OLAK5uy_mGTAhnwAhzAT-1M52__jQqIGP-wc2sE_A --output top-songs.json

# Replace an existing output file deliberately.
./run.sh OLAK5uy_mGTAhnwAhzAT-1M52__jQqIGP-wc2sE_A --output top-songs.json --force

# Display version and license information.
./run.sh -v
```

Set `PYTHON` when a specific interpreter should create the virtual environment:

```bash
PYTHON=python3.12 ./run.sh OLAK5uy_mGTAhnwAhzAT-1M52__jQqIGP-wc2sE_A
```

```powershell
$env:PYTHON = 'C:\Python312\python.exe'
.\run.ps1 OLAK5uy_mGTAhnwAhzAT-1M52__jQqIGP-wc2sE_A
```

## Output

Each result is a JSON-ready track record:

```json
{
  "position": 1,
  "video_id": "1JIKMsO_CZc",
  "title": "Up556",
  "artists": [
    {
      "name": "Iayze",
      "id": "UCgIltsJc_3itretxv5oma2g"
    }
  ],
  "album": {
    "name": "Up556",
    "id": "MPREb_B3E8GMJF7I1"
  },
  "duration": "3:42",
  "plays_display": "22M plays",
  "plays_estimate": 22000000
}
```

`plays_display` preserves the text shown by YouTube Music. `plays_estimate` is
a numeric conversion of that abbreviated text and is therefore an estimate, not
an exact underlying count. When YouTube Music does not display a count for a
track, both fields are `null`.

## Python API

Install the package from this checkout:

```bash
python -m pip install .
```

Then call `fetch_playlist_plays()`:

```python
from ytmusic_report import fetch_playlist_plays

rows = fetch_playlist_plays(
    "https://music.youtube.com/playlist?list=OLAK5uy_mGTAhnwAhzAT-1M52__jQqIGP-wc2sE_A",
    limit=25,
)

for row in rows:
    print(row["title"], row["plays_display"])
```

The function returns a list of the same dictionaries shown in the JSON output.
It raises `PlaylistRetrievalError` when YouTube Music cannot return a usable
playlist response and `ValueError` for an invalid playlist input.

## Limitations

This project uses YouTube Music's undocumented web interface. It is not an
official Google or YouTube API, and upstream response changes can require
maintenance. Displayed play values are abbreviated by YouTube Music and may be
unavailable for some tracks.

## Testing

Install the development dependencies, then run the offline test suite:

```bash
python -m pip install -e ".[dev]"
python -m pytest
```

Run the optional live check against a public playlist:

```bash
YTMUSIC_LIVE_TEST=1 python -m pytest -m live
```

## License

Distributed under the [MIT License](LICENSE). Copyright © 2026 Maurizio Nagni.
