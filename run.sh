#!/usr/bin/env bash
# Wrapper used by cron: activates the venv, runs the poster, logs the output.
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

source "$PROJECT_DIR/venv/bin/activate"
python "$PROJECT_DIR/newai.py" >> "$PROJECT_DIR/logs/run.log" 2>&1
