#!/usr/bin/env python3
from pathlib import Path
import argparse,csv,json,subprocess,sys,time,shutil
ROOT=Path(__file__).resolve().parents[1]
CFG=json.loads((ROOT/"config"/"multisize_groups.json").read_text(encoding="utf-8"))
SRC=ROOT/"src"/"ga_single_exact_reference.cpp"
BIN=ROOT/"bin"/("ga_pfspan.exe" if sys.platform.startswith("win") else "ga_pfspan")
def compile_engine():
    cc=shutil.which("g++")
    if not cc: raise RuntimeError("g++ not found. Install a C++17 compiler.")
    BIN.parent.mkdir(exist_ok=True)
    subprocess.run([cc,"-O3","-std=c++17",str(SRC),"-o",str(BIN)],check=True)
def matrix_dims(path):
    rows=[]
    with Path(path).open(newline="",encoding="utf-8-sig") as f:
        for row in csv.reader(f):
            if row and any(x.strip() for x in row):
                rows.append([int(x.strip()) for x in row])
    if not rows: raise ValueError("Matrix is empty.")
    m=len(rows[0])
    if any(len(r)!=m for r in rows): raise ValueError("Matrix must be rectangular.")
    if any(v<=0 for r in rows for v in r): raise ValueError("Processing times must be positive integers.")
    return len(rows),m
def main():
    ap=argparse.ArgumentParser(description="PFSP GA runner for included Taillard groups or a custom matrix.")
    mode=ap.add_mutually_exclusive_group(required=True)
    mode.add_argument("--group",choices=list(CFG["groups"]))
    mode.add_argument("--matrix",type=Path,help="CSV: jobs in rows, machines in columns, no header.")
    ap.add_argument("--instance",type=int,default=1)
    ap.add_argument("--all-instances",action="store_true")
    ap.add_argument("--full-surface",action="store_true")
    ap.add_argument("--pop-mult",type=float); ap.add_argument("--pc",type=float); ap.add_argument("--pm",type=float)
    ap.add_argument("--reps",type=int,default=10); ap.add_argument("--G",type=int)
    ap.add_argument("--seed-base",type=int,default=3000000201)
    ap.add_argument("--output",type=Path)
    a=ap.parse_args()
    if a.reps<1: raise SystemExit("--reps must be >=1")
    grid=CFG["grid"]
    if a.full_surface:
        configs=[(x,y,z) for x in grid["pop_mult"] for y in grid["pc"] for z in grid["pm"]]
    else:
        if a.pop_mult is None or a.pc is None or a.pm is None:
            raise SystemExit("Use --full-surface or provide --pop-mult --pc --pm.")
        configs=[(a.pop_mult,a.pc,a.pm)]
    jobs=[]
    if a.group:
        if not 1<=a.instance<=10: raise SystemExit("--instance must be 1..10")
        s=CFG["groups"][a.group]; G=a.G or s["G"]
        insts=list(range(1,11)) if a.all_instances else [a.instance]
        for inst in insts:
            mat=ROOT/"instances"/"Taillard_All"/a.group/f"{a.group}_{inst:02d}.csv"
            jobs.append((a.group,inst,mat,s["n"],s["m"],G,s["seed_base"]+inst*100000))
    else:
        if a.all_instances: raise SystemExit("--all-instances is only for --group.")
        mat=a.matrix.resolve()
        if not mat.exists(): raise SystemExit(f"Matrix not found: {mat}")
        n,m=matrix_dims(mat)
        if n>500 or m>50: raise SystemExit("Maximum supported size is 500 jobs x 50 machines.")
        if a.G is None: raise SystemExit("Custom matrix mode requires --G.")
        jobs.append((mat.stem,1,mat,n,m,a.G,a.seed_base))
    compile_engine()
    total=len(jobs)*len(configs)*a.reps
    tag=a.group if a.group else a.matrix.stem
    out=a.output or ROOT/"outputs"/f"{tag}_{time.strftime('%Y%m%d_%H%M%S')}.csv"
    out.parent.mkdir(parents=True,exist_ok=True)
    fields=["problem","instance","n","m","G","pop_mult","Ps","pc","pm","rep","seed","best_cmax","run_sec","matrix"]
    done=0
    with out.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader()
        for problem,inst,mat,n,m,G,seed_prefix in jobs:
            for mult,pc,pm in configs:
                for rep in range(1,a.reps+1):
                    seed=seed_prefix+rep*1009
                    tmp=out.parent/"._single.csv"
                    subprocess.run([str(BIN),str(mat),str(n),str(m),str(G),str(mult),str(pc),str(pm),str(seed),str(tmp)],check=True,stdout=subprocess.DEVNULL)
                    with tmp.open(newline="",encoding="utf-8") as sf:r=next(csv.DictReader(sf))
                    tmp.unlink(missing_ok=True); done+=1
                    w.writerow({"problem":problem,"instance":inst,"n":n,"m":m,"G":G,"pop_mult":mult,
                    "Ps":max(2,int(round(float(mult)*n))),"pc":pc,"pm":pm,"rep":rep,"seed":seed,
                    "best_cmax":r["best_cmax"],"run_sec":r["run_sec"],"matrix":str(mat)})
                    f.flush()
                    print(f"[{done}/{total}] {problem} i={inst} ({mult},{pc},{pm}) r={rep} Cmax={r['best_cmax']}")
    print("DONE:",out)
if __name__=="__main__": main()
