#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
python3 "$ROOT/scripts/verify_all.py"
python3 "$ROOT/scripts/verify_prospective_matrices_exact.py"
