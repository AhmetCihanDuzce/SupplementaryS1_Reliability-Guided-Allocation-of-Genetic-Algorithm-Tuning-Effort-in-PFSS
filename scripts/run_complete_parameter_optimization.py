#!/usr/bin/env python3
"""
Retained 50-job reproducibility workflow.

FULL mode:
  processing-time matrices -> actual C++ GA -> complete 125-configuration response surfaces
  -> descriptive 3-to-7 parameter-selection/holdout reconstruction.

The historical manuscript SAFE rates use prespecified independent fresh-validation records.
Therefore this script does NOT claim that rerunning the rebuilt 50-job main surfaces
will reproduce the already-prespecified historical SAFE counts or every Table-3 center.

QUICK mode is only a technical proof that:
  matrix -> C++ GA -> multiple parameter configurations -> parameter-selection utility
is executable without reading archived result CSV files.
"""
from pathlib import Path
import argparse, subprocess, sys
ROOT=Path(__file__).resolve().parents[1]

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--group",choices=["Ta50x5","Ta50x10","Ta50x20"],required=True)
    ap.add_argument("--quick-demo",action="store_true")
    args=ap.parse_args()
    outdir=ROOT/"outputs"/f"RETAINED_WORKFLOW_{args.group}"
    outdir.mkdir(parents=True,exist_ok=True)
    raw=outdir/"GA_raw_results.csv"

    if args.quick_demo:
        subprocess.run([sys.executable,str(ROOT/"scripts"/"04_quick_parameter_demo.py"),
                        "--group",args.group,"--output",str(raw)],check=True)
        subprocess.run([sys.executable,str(ROOT/"scripts"/"02_optimize_parameters.py"),
                        str(raw),"--group",args.group,
                        "--output-dir",str(outdir/"technical_selection_demo")],check=True)
        print("\nPASS — technical GA -> parameter-grid -> selection demonstration completed.")
        print("This quick demonstration is not a reproduction of a prespecified historical anchor.")
        return

    subprocess.run([sys.executable,str(ROOT/"scripts"/"run_ga_experiments.py"),
                    "--group",args.group,"--all-instances","--full-surface",
                    "--output",str(raw)],check=True)
    subprocess.run([sys.executable,str(ROOT/"scripts"/"03_historical_3to7_transfer.py"),
                    str(raw),"--group",args.group,
                    "--output",str(outdir/"descriptive_3to7_from_new_surfaces.csv")],check=True)
    print("\nPASS — retained 50-job main GA surfaces regenerated and descriptive 3->7 workflow completed.")
    print("For manuscript historical SAFE counts, use the prespecified independent-validation records in S2.")

if __name__=="__main__":
    main()
