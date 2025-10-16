#!/usr/bin/env bash
set -euo pipefail

# run.sh - helper to create venv, install deps and run the Flask app
# Usage: ./run.sh [--no-install] [--port PORT]

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV_DIR="$ROOT_DIR/.venv"
REQUIREMENTS="$ROOT_DIR/requirements.txt"
APP_MODULE="$ROOT_DIR/src/main.py"
PORT=5000
NO_INSTALL=0

while [[ ${#} -gt 0 ]]; do
  case "$1" in
    --no-install) NO_INSTALL=1; shift ;;
    --port) PORT="$2"; shift 2 ;;
    -p) PORT="$2"; shift 2 ;;
    -h|--help)
      cat <<EOF
Usage: ./run.sh [--no-install] [--port PORT]

Options:
  --no-install    Skip installing dependencies from requirements.txt
  --port PORT     Port to run the Flask app on (default 5000)
  -h, --help      Show this help message
EOF
      exit 0
      ;;
    *) echo "Unknown argument: $1"; exit 2 ;;
  esac
done

if [[ ! -f "$APP_MODULE" ]]; then
  echo "Cannot find application entrypoint: $APP_MODULE" >&2
  exit 1
fi

python3_bin="$(command -v python3 || true)"
if [[ -z "$python3_bin" ]]; then
  echo "python3 not found on PATH" >&2
  exit 1
fi

if [[ ! -d "$VENV_DIR" ]]; then
  echo "Creating virtual environment at $VENV_DIR..."
  "$python3_bin" -m venv "$VENV_DIR"
fi

activate_script="$VENV_DIR/bin/activate"
if [[ ! -f "$activate_script" ]]; then
  echo "Virtualenv activate script not found: $activate_script" >&2
  exit 1
fi

# shellcheck disable=SC1091
source "$activate_script"

if [[ $NO_INSTALL -eq 0 && -f "$REQUIREMENTS" ]]; then
  echo "Ensuring dependencies are installed from $REQUIREMENTS..."
  pip install --upgrade pip
  pip install -r "$REQUIREMENTS"
fi

echo "Starting Flask app (port $PORT)..."
# Export port as environment variable (in case app uses it)
export FLASK_RUN_PORT="$PORT"

python3 "$APP_MODULE"
