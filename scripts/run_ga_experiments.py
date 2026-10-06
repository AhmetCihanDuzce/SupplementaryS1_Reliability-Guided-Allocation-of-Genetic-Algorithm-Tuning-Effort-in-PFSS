#!/usr/bin/env python3
"""
Run the actual prespecified GA from processing-time matrices.

This is an experiment generator, not a result reader.
It compiles src/ga_single_exact_reference.cpp, executes the GA, and writes NEW results.

Examples
--------
Fast exact reproduction of the first historical parameter configuration (10 independent GA runs):
  python scripts/run_ga_experiments.py --group Ta50x5 --instance 1 --pop-mult 1 --pc 0.85 --pm 0.025

One complete 125-configuration surface for one instance (1250 GA runs):
  python scripts/run_ga_experiments.py --group Ta50x5 --instance 1 --full-surface

All 10 instances of one 50-job group (12,500 GA runs):
  python scripts/run_ga_experiments.py --group Ta50x5 --all-instances --full-surface

Full 50-job main experiment (37,500 GA runs):
  python scripts/run_ga_experiments.py --all-50job --full-surface

Output is generated from scratch under outputs/.
"""
from pathlib import Path
import argparse, csv, json, subprocess, sys, time, shutil

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT/"config"/"prespecified_50job_main.json").read_text(encoding="utf-8"))
SRC = ROOT/"src"/"ga_single_exact_reference.cpp"
BIN = ROOT/"bin"/("ga_pfspan.exe" if sys.platform.startswith("win") else "ga_pfspan")

def compile_engine():
    BIN.parent.mkdir(exist_ok=True)
    compiler = shutil.which("g++")
    if compiler is None:
        raise RuntimeError("g++ was not found. Install a C++17 compiler (GCC/g++) and rerun.")
    cmd=[compiler,"-O3","-std=c++17",str(SRC),"-o",str(BIN)]
    subprocess.run(cmd,check=True)

def configurations(args):
    g=CFG["grid"]
    if args.full_surface:
        return [(pmul,pc,pm) for pmul in g["pop_mult"] for pc in g["pc"] for pm in g["pm"]]
    if args.pop_mult is None or args.pc is None or args.pm is None:
        raise SystemExit("For a single parameter configuration, provide --pop-mult, --pc and --pm, or use --full-surface.")
    return [(args.pop_mult,args.pc,args.pm)]

def jobs(args):
    if args.all_50job:
        groups=list(CFG["groups"])
    elif args.group:
        groups=[args.group]
    else:
        raise SystemExit("Choose --group GROUP or --all-50job.")
    out=[]
    for group in groups:
        if group not in CFG["groups"]:
            raise SystemExit(f"Unknown group {group}")
        instances=range(1,11) if (args.all_instances or args.all_50job) else [args.instance]
        for inst in instances:
            out.append((group,inst))
    return out

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--group",choices=list(CFG["groups"]))
    ap.add_argument("--instance",type=int,default=1)
    ap.add_argument("--all-instances",action="store_true")
    ap.add_argument("--all-50job",action="store_true")
    ap.add_argument("--full-surface",action="store_true")
    ap.add_argument("--pop-mult",type=int)
    ap.add_argument("--pc",type=float)
    ap.add_argument("--pm",type=float)
    ap.add_argument("--reps",type=int,default=10,help="Default 10; use smaller only for a quick technical test.")
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    if not 1 <= args.reps <= 10: raise SystemExit("--reps must be 1..10")
    compile_engine()
    selected_configurations=configurations(args)
    selected_jobs=jobs(args)
    total=len(selected_configurations)*len(selected_jobs)*args.reps
    stamp=time.strftime("%Y%m%d_%H%M%S")
    out=args.output or ROOT/"outputs"/f"GA_generated_{stamp}.csv"
    out.parent.mkdir(parents=True,exist_ok=True)
    fields=["experiment_id","group","instance","n","m","G","pop_mult","Ps","pc","pm","rep","seed","best_cmax","run_sec","matrix"]
    done=0
    with out.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for group,inst in selected_jobs:
            spec=CFG["groups"][group]
            matrix=ROOT/"instances"/"Taillard_50Job"/f"{group}_{inst:02d}.csv"
            if not matrix.exists(): raise FileNotFoundError(matrix)
            for pmul,pc,pm in selected_configurations:
                for rep in range(1,args.reps+1):
                    seed=spec["seed_base"] + inst*100000 + rep*1009
                    tmp=out.parent/"._single_ga_result.csv"
                    cmd=[str(BIN),str(matrix),str(spec["n"]),str(spec["m"]),str(spec["G"]),
                         str(pmul),str(pc),str(pm),str(seed),str(tmp)]
                    subprocess.run(cmd,check=True,stdout=subprocess.DEVNULL)
                    with tmp.open(newline="",encoding="utf-8") as sf:
                        r=next(csv.DictReader(sf))
                    tmp.unlink(missing_ok=True)
                    w.writerow({
                        "experiment_id":CFG["experiment_id"],"group":group,"instance":inst,
                        "n":spec["n"],"m":spec["m"],"G":spec["G"],
                        "pop_mult":pmul,"Ps":pmul*spec["n"],"pc":pc,"pm":pm,
                        "rep":rep,"seed":seed,"best_cmax":r["best_cmax"],
                        "run_sec":r["run_sec"],"matrix":matrix.relative_to(ROOT).as_posix()
                    })
                    f.flush()
                    done+=1
                    print(f"[{done}/{total}] {group} inst={inst} configuration=({pmul},{pc},{pm}) rep={rep} Cmax={r['best_cmax']}")
    print(f"\nDONE — {total} GA runs generated from scratch")
    print(out)

if __name__=="__main__":
    main()
