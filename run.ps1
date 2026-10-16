[CmdletBinding()]
param(
    [Parameter(ValueFromRemainingArguments = $true)]
    [string[]]$CliArguments
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$projectDir = $PSScriptRoot
$venvDir = Join-Path $projectDir ".venv"
$venvPython = Join-Path $venvDir "Scripts\python.exe"
$venvCommand = Join-Path $venvDir "Scripts\ytmusic-report.exe"

if (-not (Test-Path -LiteralPath $venvPython -PathType Leaf)) {
    if (Test-Path -LiteralPath $venvDir -PathType Container) {
        throw "$venvDir is not a Windows virtual environment. Delete it, then run this script again."
    }

    if ($env:PYTHON) {
        & $env:PYTHON -m venv $venvDir
    }
    elseif (Get-Command python -ErrorAction SilentlyContinue) {
        & python -m venv $venvDir
    }
    elseif (Get-Command py -ErrorAction SilentlyContinue) {
        & py -3 -m venv $venvDir
    }
    else {
        throw "Python 3.10 or newer was not found. Set the PYTHON environment variable to its executable."
    }

    if ($LASTEXITCODE -ne 0) {
        exit $LASTEXITCODE
    }
}

& $venvPython -m pip install --quiet --editable $projectDir
if ($LASTEXITCODE -ne 0) {
    exit $LASTEXITCODE
}

& $venvCommand @CliArguments
exit $LASTEXITCODE
