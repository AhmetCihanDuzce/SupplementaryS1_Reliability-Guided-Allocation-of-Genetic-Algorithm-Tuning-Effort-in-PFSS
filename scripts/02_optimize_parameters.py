#!/usr/bin/env python3
"""
Select a common GA parameter setting from a GA-generated response-surface CSV.

This script DOES NOT run the GA and DOES NOT read S2. It is stage 2 of the pipeline:
raw GA runs -> configuration means -> empirical oracle -> normalized regret -> common policy.

Prespecified reconstruction rule used here:
1) For each instance, the empirical oracle is the lowest mean Cmax among evaluated configurations.
2) Regret_pp(configuration, instance) = max(0, (meanCmax_configuration - meanCmax_oracle)/NEH * 100).
3) Across calibration instances, compute mean and maximum regret for every common configuration.
4) Let b be the smallest mean regret. The admissible set contains configurations with
   mean_regret <= b + 0.25 percentage points.
5) Robust-minimax selection chooses the admissible configuration with the smallest maximum regret,
   then mean regret, then mean signed excess, then parameter order.

NEH is computed directly from each processing-time matrix; it is not read from result files.
"""
from pathlib import Path
import argparse, csv, math, statistics

ROOT=Path(__file__).resolve().parents[1]

def read_matrix(path):
    with path.open(newline="",encoding="utf-8-sig") as f:
        return [[int(float(x)) for x in row] for row in csv.reader(f) if row]

def cmax(mat, perm):
    m=len(mat[0]); c=[0]*m
    for j in perm:
        c[0]+=mat[j][0]
        for k in range(1,m):
            c[k]=max(c[k],c[k-1])+mat[j][k]
    return c[-1]

def neh(mat):
    n=len(mat)
    order=sorted(range(n), key=lambda j:(-sum(mat[j]),j))
    seq=[]
    for j in order:
        best=None
        for pos in range(len(seq)+1):
            cand=seq[:pos]+[j]+seq[pos:]
            val=cmax(mat,cand)
            key=(val,tuple(cand))
            if best is None or key<best[0]:
                best=(key,cand)
        seq=best[1]
    return cmax(mat,seq)

def load_runs(path):
    with path.open(newline="",encoding="utf-8-sig") as f:
        rows=list(csv.DictReader(f))
    req={"group","instance","pop_mult","pc","pm","rep","best_cmax","matrix"}
    missing=req-set(rows[0] if rows else [])
    if missing: raise SystemExit(f"Missing columns: {sorted(missing)}")
    return rows

def summarize(rows, group=None, instances=None):
    if group: rows=[r for r in rows if r["group"]==group]
    if instances is not None:
        S=set(instances); rows=[r for r in rows if int(r["instance"]) in S]
    if not rows: raise SystemExit("No matching GA runs.")
    groups=sorted(set(r["group"] for r in rows))
    if len(groups)!=1: raise SystemExit("Optimize one group at a time; use --group.")
    group=groups[0]

    by={}
    matrix_by_inst={}
    for r in rows:
        inst=int(r["instance"]); cfg=(int(float(r["pop_mult"])),float(r["pc"]),float(r["pm"]))
        by.setdefault((inst,cfg),[]).append(float(r["best_cmax"]))
        matrix_by_inst[inst]=ROOT/r["matrix"] if not Path(r["matrix"]).is_absolute() else Path(r["matrix"])
        if not matrix_by_inst[inst].exists():
            # runner stores a path relative to S1 root
            matrix_by_inst[inst]=ROOT/"instances"/"Taillard_50Job"/f"{group}_{inst:02d}.csv"

    insts=sorted(set(i for i,c in by))
    common=set.intersection(*[{c for (ii,c) in by if ii==i} for i in insts])
    if not common: raise SystemExit("No common parameter configurations across selected instances.")

    means={(i,c):statistics.fmean(by[(i,c)]) for i in insts for c in common}
    oracle={i:min(means[(i,c)] for c in common) for i in insts}
    nehs={i:neh(read_matrix(matrix_by_inst[i])) for i in insts}

    stats=[]
    for c in sorted(common):
        signed=[(means[(i,c)]-oracle[i])/nehs[i]*100.0 for i in insts]
        clipped=[max(0.0,x) for x in signed]
        stats.append({
            "pop_mult":c[0],"pc":c[1],"pm":c[2],
            "mean_signed_excess_pp":statistics.fmean(signed),
            "mean_regret_pp":statistics.fmean(clipped),
            "max_regret_pp":max(clipped),
            "instances":len(insts)
        })
    best_mean=min(x["mean_regret_pp"] for x in stats)
    admissible=[x for x in stats if x["mean_regret_pp"] <= best_mean+0.25+1e-12]
    selected=min(admissible,key=lambda x:(x["max_regret_pp"],x["mean_regret_pp"],
                                          x["mean_signed_excess_pp"],x["pop_mult"],x["pc"],x["pm"]))
    return group,insts,nehs,oracle,stats,admissible,selected

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("results_csv",type=Path)
    ap.add_argument("--group")
    ap.add_argument("--instances",help="Comma-separated instance numbers; default=all in CSV")
    ap.add_argument("--output-dir",type=Path)
    args=ap.parse_args()
    insts=[int(x) for x in args.instances.split(",")] if args.instances else None
    rows=load_runs(args.results_csv)
    group,used,nehs,oracle,stats,adm,sel=summarize(rows,args.group,insts)
    out=args.output_dir or ROOT/"outputs"/"parameter_optimization"
    out.mkdir(parents=True,exist_ok=True)

    with (out/f"{group}_cell_statistics.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(stats[0])); w.writeheader(); w.writerows(stats)
    with (out/f"{group}_selected_policy.csv").open("w",newline="",encoding="utf-8") as f:
        w=csv.DictWriter(f,fieldnames=list(sel)); w.writeheader(); w.writerow(sel)

    print(f"Group: {group}")
    print(f"Calibration instances: {used}")
    print(f"Common evaluated configurations: {len(stats)}")
    print(f"Admissible configurations (+0.25 pp from best mean regret): {len(adm)}")
    print("SELECTED PARAMETER POLICY")
    print(f"  Ps/n = {sel['pop_mult']}")
    print(f"  pc   = {sel['pc']}")
    print(f"  pm   = {sel['pm']}")
    print(f"  mean clipped regret = {sel['mean_regret_pp']:.6f} pp")
    print(f"  maximum regret      = {sel['max_regret_pp']:.6f} pp")
    print(f"Outputs: {out}")

if __name__=="__main__":
    main()
