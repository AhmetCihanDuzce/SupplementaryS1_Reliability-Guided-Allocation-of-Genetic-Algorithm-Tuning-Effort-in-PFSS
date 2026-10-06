#!/usr/bin/env python3
"""
All C(10,3)=120 calibration triples and 7 holdouts per split.

Input must be a GA-generated full response-surface CSV for one 10-instance group.
For every calibration triple, the robust-minimax selector from 02_optimize_parameters.py
is recomputed using calibration instances only. The selected configuration is then
evaluated descriptively on the seven held-out main surfaces.

IMPORTANT: this stage reconstructs the parameter-selection/transfer logic from newly
generated response surfaces. It is not a substitute for the manuscript's independent
fresh-seed validation stage.
"""
from pathlib import Path
import argparse,csv,itertools,statistics,importlib.util

ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location("opt",ROOT/"scripts"/"02_optimize_parameters.py")
opt=importlib.util.module_from_spec(spec); spec.loader.exec_module(opt)

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("results_csv",type=Path)
    ap.add_argument("--group",required=True)
    ap.add_argument("--output",type=Path)
    args=ap.parse_args()
    rows=opt.load_runs(args.results_csv)
    rows=[r for r in rows if r["group"]==args.group]
    allinst=sorted(set(int(r["instance"]) for r in rows))
    if len(allinst)!=10:
        raise SystemExit(f"Expected 10 instances for 3->7 analysis; found {len(allinst)}.")

    # Precompute configuration means, NEH, and per-instance empirical oracle over common configurations.
    by={}; matrix={}
    for r in rows:
        i=int(r["instance"]); c=(int(float(r["pop_mult"])),float(r["pc"]),float(r["pm"]))
        by.setdefault((i,c),[]).append(float(r["best_cmax"]))
        p=Path(r["matrix"]); matrix[i]=p if p.is_absolute() else ROOT/p
        if not matrix[i].exists(): matrix[i]=ROOT/"instances"/"Taillard_50Job"/f"{args.group}_{i:02d}.csv"
    common=set.intersection(*[{c for ii,c in by if ii==i} for i in allinst])
    if len(common)<2: raise SystemExit("A full/common response surface is required.")
    means={(i,c):statistics.fmean(by[(i,c)]) for i in allinst for c in common}
    neh={i:opt.neh(opt.read_matrix(matrix[i])) for i in allinst}
    oracle={i:min(means[(i,c)] for c in common) for i in allinst}

    outrows=[]
    sid=0
    for cal in itertools.combinations(allinst,3):
        sid+=1
        _,_,_,_,_,_,sel=opt.summarize(rows,args.group,list(cal))
        c=(int(sel["pop_mult"]),float(sel["pc"]),float(sel["pm"]))
        holds=[i for i in allinst if i not in cal]
        for h in holds:
            signed=(means[(h,c)]-oracle[h])/neh[h]*100.0
            outrows.append({
                "split_id":sid,"calibration":";".join(map(str,cal)),"holdout":h,
                "pop_mult":c[0],"pc":c[1],"pm":c[2],
                "holdout_cell_mean_cmax":means[(h,c)],
                "holdout_empirical_oracle_mean_cmax":oracle[h],
                "NEH_cmax":neh[h],
                "signed_excess_pp":signed,
                "clipped_regret_pp":max(0.0,signed),
                "within_0.25pp":int(signed<=0.25)
            })
    out=args.output or ROOT/"outputs"/f"{args.group}_3to7_transfer.csv"
    out.parent.mkdir(parents=True,exist_ok=True)
    with out.open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(outrows[0]));w.writeheader();w.writerows(outrows)
    safe=sum(r["within_0.25pp"] for r in outrows)
    print(f"Completed {sid} calibration triples x 7 holdouts = {len(outrows)} comparisons.")
    print(f"Descriptive within-0.25pp count: {safe}/{len(outrows)} ({100*safe/len(outrows):.2f}%)")
    print(f"Output: {out}")

if __name__=="__main__":
    main()
