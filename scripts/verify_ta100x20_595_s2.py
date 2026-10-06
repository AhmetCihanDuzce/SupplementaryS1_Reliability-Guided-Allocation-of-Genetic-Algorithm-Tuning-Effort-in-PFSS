#!/usr/bin/env python3
from pathlib import Path
import argparse, zipfile, tempfile, subprocess, sys

ap=argparse.ArgumentParser(description="Run the S2 canonical Ta100x20 595/840 verifier")
ap.add_argument("--s2", required=True, help="Path to the revised S2 ZIP or extracted S2 root/directory")
a=ap.parse_args(); p=Path(a.s2).resolve()

def locate(root):
    candidates=[root, root/"Supplementary_S2_Data_Results_and_Quality_Assurance"]
    for c in candidates:
        v=c/"03_Quality_Assurance_and_Integrity"/"scripts"/"verify_all.py"
        if v.exists(): return v
    for v in root.rglob("verify_all.py"):
        if "03_Quality_Assurance_and_Integrity" in str(v): return v
    raise FileNotFoundError("S2 verify_all.py not found")

if p.is_file() and p.suffix.lower()==".zip":
    with tempfile.TemporaryDirectory() as td:
        with zipfile.ZipFile(p) as z: z.extractall(td)
        v=locate(Path(td))
        raise SystemExit(subprocess.call([sys.executable,str(v)]))
elif p.is_dir():
    v=locate(p); raise SystemExit(subprocess.call([sys.executable,str(v)]))
else:
    raise SystemExit(f"Unsupported --s2 path: {p}")
