# Run the Flask app locally on Windows using waitress (works with venv)
# Usage: Open PowerShell in the repo root and run: .\scripts\run-local.ps1

$venv = Join-Path $PSScriptRoot '..\.venv\Scripts\Activate.ps1'
if (Test-Path $venv) {
    Write-Host ('Activating venv at ' + $venv)
    . $venv
} else {
    Write-Host ('No virtualenv found at ' + $venv + '. Make sure you have a Python venv or install dependencies globally')
}

# Ensure requirements are installed (safe no-op if already present)
pip install -r requirements.txt

Write-Host 'Starting waitress on :5000'
waitress-serve --listen='*:5000' wsgi:app
