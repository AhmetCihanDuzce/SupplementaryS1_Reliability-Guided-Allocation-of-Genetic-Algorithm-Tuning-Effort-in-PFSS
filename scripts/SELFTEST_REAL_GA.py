#!/usr/bin/env python3
"""Exact GA self-test: generate 10 runs from the matrix and compare to prespecified expected Cmax."""
from pathlib import Path
import csv, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]
out=ROOT/"outputs"/"SELFTEST_generated.csv"
cmd=[sys.executable,str(ROOT/"scripts"/"run_ga_experiments.py"),
     "--group","Ta50x5","--instance","1","--pop-mult","1","--pc","0.85","--pm","0.025",
     "--reps","10","--output",str(out)]
subprocess.run(cmd,check=True)
with out.open(newline="",encoding="utf-8") as f:
    got=[int(r["best_cmax"]) for r in csv.DictReader(f)]
expected=[2740,2752,2741,2735,2735,2735,2752,2735,2746,2735]
print("Generated:",got)
print("Expected: ",expected)
assert got==expected, "Exact historical reproduction failed"
print("PASS — the GA generated all 10 expected historical Cmax values from the processing-time matrix.")
