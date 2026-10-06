#!/usr/bin/env python3
"""Generate a small REAL-GA multi-parameter surface for technical pipeline testing."""
from pathlib import Path
import argparse,csv,json,subprocess,sys,shutil
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/"config"/"prespecified_50job_main.json").read_text())
SRC=ROOT/"src"/"ga_single_exact_reference.cpp"
BIN=ROOT/"bin"/("ga_pfspan.exe" if sys.platform.startswith("win") else "ga_pfspan")
def main():
    ap=argparse.ArgumentParser();ap.add_argument("--group",required=True);ap.add_argument("--output",type=Path,required=True);a=ap.parse_args()
    g=CFG["groups"][a.group]; compiler=shutil.which("g++")
    if not compiler: raise SystemExit("g++ not found")
    BIN.parent.mkdir(exist_ok=True);subprocess.run([compiler,"-O3","-std=c++17",str(SRC),"-o",str(BIN)],check=True)
    matrix=ROOT/"instances"/"Taillard_50Job"/f"{a.group}_01.csv"
    configs=[(1,.85,.025),(1,.85,.125),(1,1.0,.025),(1,1.0,.125),
           (5,.85,.025),(5,.85,.125),(5,1.0,.025),(5,1.0,.125)]
    a.output.parent.mkdir(parents=True,exist_ok=True)
    fields=["experiment_id","group","instance","n","m","G","pop_mult","Ps","pc","pm","rep","seed","best_cmax","run_sec","matrix"]
    with a.output.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader()
        for config in configs:
            for rep in (1,2):
                pmul,pc,pm=config; seed=g["seed_base"]+100000+rep*1009
                tmp=a.output.parent/"._tmp.csv"
                subprocess.run([str(BIN),str(matrix),str(g["n"]),str(g["m"]),str(g["G"]),str(pmul),str(pc),str(pm),str(seed),str(tmp)],check=True)
                with tmp.open(newline="",encoding="utf-8") as q:r=next(csv.DictReader(q))
                tmp.unlink(missing_ok=True)
                w.writerow({"experiment_id":"QUICK_REAL_GA_DEMO","group":a.group,"instance":1,"n":g["n"],"m":g["m"],"G":g["G"],
                            "pop_mult":pmul,"Ps":pmul*g["n"],"pc":pc,"pm":pm,"rep":rep,"seed":seed,
                            "best_cmax":r["best_cmax"],"run_sec":r["run_sec"],"matrix":matrix.relative_to(ROOT).as_posix()})
                print(a.group,config,"rep",rep,"Cmax",r["best_cmax"])
    print("Generated real-GA demo surface:",a.output)
if __name__=="__main__":main()
