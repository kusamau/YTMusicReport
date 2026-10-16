#!/usr/bin/env bash
set -euo pipefail

project_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
venv_dir="$project_dir/.venv"
python_bin="${PYTHON:-python3}"

if [[ ! -x "$venv_dir/bin/python" ]]; then
    "$python_bin" -m venv "$venv_dir"
fi

"$venv_dir/bin/python" -m pip install --quiet --editable "$project_dir"
exec "$venv_dir/bin/ytmusic-report" "$@"
