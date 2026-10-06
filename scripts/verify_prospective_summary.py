#!/usr/bin/env python3
# Backward-compatible entry point. The standalone verifier uses only files inside S1.
from pathlib import Path
import runpy
runpy.run_path(str(Path(__file__).with_name("verify_all.py")), run_name="__main__")
