#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────────────
#  ML Pipeline Template — Test Automation Entry Point
#
#  Usage:
#    ./run_tests.sh                   # run all suites
#    ./run_tests.sh --fast            # skip slow suites (no pip install)
#    ./run_tests.sh --suite bootstrap # run specific suite by keyword
#    ./run_tests.sh --suite 01        # run suite 01 by number
#
#  Requirements: Python 3.9+ (same as the template itself)
# ──────────────────────────────────────────────────────────────────────
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Check Python
if ! command -v python3 &>/dev/null; then
    echo "ERROR: python3 not found. Install Python 3.9+ from python.org"
    exit 1
fi

PY_VER=$(python3 -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
PY_MAJ=$(python3 -c "import sys; print(sys.version_info.major)")
PY_MIN=$(python3 -c "import sys; print(sys.version_info.minor)")

if [ "$PY_MAJ" -lt 3 ] || { [ "$PY_MAJ" -eq 3 ] && [ "$PY_MIN" -lt 9 ]; }; then
    echo "ERROR: Python 3.9+ required, found $PY_VER"
    exit 1
fi

# Create results dir if needed
mkdir -p "$SCRIPT_DIR/results"

# Run
exec python3 "$SCRIPT_DIR/test_runner.py" "$@"
