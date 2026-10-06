#!/usr/bin/env bash
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
CXX="${CXX:-g++}"
CXXFLAGS="${CXXFLAGS:--O3 -std=c++17}"
$CXX $CXXFLAGS "$ROOT/src/ga_single_exact_reference.cpp" -o "$TMP/ga_ref"
"$TMP/ga_ref" "$ROOT/examples/Ta50x5_01.csv" 50 5 2000 1 0.85 0.025 2250101210 "$TMP/out.csv"
OBS="$(awk -F, 'NR==2 {print $7}' "$TMP/out.csv")"
if [[ "$OBS" != "2740" ]]; then
  echo "Smoke test FAILED: expected best_cmax=2740, observed $OBS" >&2
  exit 1
fi
echo "Smoke test PASS: Ta50x5 instance 1, seed 2250101210 -> best_cmax=2740"
