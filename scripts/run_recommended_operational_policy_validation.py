#!/usr/bin/env python3
"""Run the recommended staged risk-guided operational policy and its matched-budget blind validation."""
from pathlib import Path
import argparse, csv, itertools, shutil, subprocess, sys, tempfile, statistics

ROOT=Path(__file__).resolve().parents[1]
SRC=ROOT/'src'/'ga_single_exact_reference.cpp'
BIN=ROOT/'bin'/('ga_pfspan.exe' if sys.platform.startswith('win') else 'ga_pfspan')
TARGETS=ROOT/'data'/'prospective'/'Prospective_24_Target_Design_Prespecified.csv'
MATS=ROOT/'instances'/'Prospective_24'
GRID_POP=[1,2,3,4,5]
GRID_PC=[0.85,0.8875,0.925,0.9625,1.0]
GRID_PM=[0.025,0.05,0.075,0.10,0.125]
FULL_GRID=list(itertools.product(GRID_POP,GRID_PC,GRID_PM))
GUIDED_SPEC={
    'GREEN': {'stage_R':5,'K':3,'final_R':10},
    'AMBER': {'stage_R':3,'K':8,'final_R':10},
    'RED':   {'stage_R':2,'K':30,'final_R':10},
}

def compile_engine():
    cc=shutil.which('g++')
    if not cc:
        raise SystemExit('g++ not found; install a C++17 compiler.')
    BIN.parent.mkdir(exist_ok=True)
    subprocess.run([cc,'-O3','-std=c++17',str(SRC),'-o',str(BIN)],check=True)

def read_targets():
    with TARGETS.open('r',encoding='utf-8-sig',newline='') as f:
        rows=list(csv.DictReader(f))
    return {int(r['target_index']):r for r in rows}

def idx(levels, value):
    for i,x in enumerate(levels):
        if abs(float(x)-float(value))<1e-12:
            return i
    raise ValueError((levels,value))

def neighborhood(center, risk):
    if risk=='RED':
        return list(FULL_GRID)
    p,pc,pm=center
    ip,ic,im=idx(GRID_POP,p),idx(GRID_PC,pc),idx(GRID_PM,pm)
    if risk=='GREEN':
        out={(p,pc,pm)}
        for axis,(levels,i) in enumerate([(GRID_POP,ip),(GRID_PC,ic),(GRID_PM,im)]):
            for di in (-1,1):
                j=i+di
                if 0<=j<len(levels):
                    c=[p,pc,pm]
                    c[axis]=levels[j]
                    out.add(tuple(c))
        return sorted(out)
    Ps=GRID_POP[max(0,ip-1):min(len(GRID_POP),ip+2)]
    PCs=GRID_PC[max(0,ic-1):min(len(GRID_PC),ic+2)]
    PMs=GRID_PM[max(0,im-1):min(len(GRID_PM),im+2)]
    return sorted(itertools.product(Ps,PCs,PMs))

def run_ga(matrix,n,m,G,cfg,seed,tmpdir):
    pop,pc,pm=cfg
    out=tmpdir/f'one_{seed}_{pop}_{pc}_{pm}.csv'
    subprocess.run([str(BIN),str(matrix),str(n),str(m),str(G),str(pop),str(pc),str(pm),str(seed),str(out)],
                   check=True,stdout=subprocess.DEVNULL)
    with out.open('r',encoding='utf-8',newline='') as f:
        r=next(csv.DictReader(f))
    out.unlink(missing_ok=True)
    return int(r['best_cmax']),float(r['run_sec'])

def write_rows(path, rows):
    if not rows:
        return
    with path.open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)

def mean_by_cfg(rows):
    d={}
    for r in rows:
        cfg=(int(r['pop_mult']),float(r['pc']),float(r['pm']))
        d.setdefault(cfg,[]).append(float(r['best_cmax']))
    return {k:statistics.fmean(v) for k,v in d.items()}

def one_target(target_index,t,outroot,tmpdir):
    n,m,G=int(t['n']),int(t['m']),int(t['G'])
    risk=t['action'].strip().upper()
    center=(int(float(t['pop_mult'])),float(t['pc']),float(t['pm']))
    matrix=MATS/t['matrix_file']
    if not matrix.exists():
        raise FileNotFoundError(matrix)
    target_id=t.get('target_id',f'T{target_index:02d}_{n}x{m}')
    tdir=outroot/f'Target{target_index:02d}_{n}x{m}'
    tdir.mkdir(parents=True,exist_ok=True)
    spec=GUIDED_SPEC[risk]

    guided_candidates=neighborhood(center,risk)
    gs=[]
    for cfg in guided_candidates:
        for rep in range(1,spec['stage_R']+1):
            seed=3600000000+target_index*10000+rep
            best,sec=run_ga(matrix,n,m,G,cfg,seed,tmpdir)
            gs.append({'method':'GUIDED','phase':'STAGE1','target_index':target_index,'target_id':target_id,
                       'pop_mult':cfg[0],'pc':cfg[1],'pm':cfg[2],'rep':rep,'seed':seed,
                       'best_cmax':best,'run_sec':sec})
    write_rows(tdir/'guided_stage1.csv',gs)
    gmeans=mean_by_cfg(gs)
    gfinalists=[k for k,_ in sorted(gmeans.items(),key=lambda kv:(kv[1],kv[0]))[:min(spec['K'],len(gmeans))]]

    gc=[]
    for cfg in gfinalists:
        for rep in range(spec['stage_R']+1,spec['final_R']+1):
            seed=3600000000+target_index*10000+rep
            best,sec=run_ga(matrix,n,m,G,cfg,seed,tmpdir)
            gc.append({'method':'GUIDED','phase':'CONFIRM_ONLY','target_index':target_index,'target_id':target_id,
                       'pop_mult':cfg[0],'pc':cfg[1],'pm':cfg[2],'rep':rep,'seed':seed,
                       'best_cmax':best,'run_sec':sec})
    write_rows(tdir/'guided_confirmation.csv',gc)
    gcm=mean_by_cfg(gc)
    gbest=min(gcm,key=lambda k:(gcm[k],k))

    bs=[]
    for cfg in FULL_GRID:
        rep=1
        seed=3700000000+target_index*10000+rep
        best,sec=run_ga(matrix,n,m,G,cfg,seed,tmpdir)
        bs.append({'method':'BLIND','phase':'STAGE1','target_index':target_index,'target_id':target_id,
                   'pop_mult':cfg[0],'pc':cfg[1],'pm':cfg[2],'rep':rep,'seed':seed,
                   'best_cmax':best,'run_sec':sec})
    write_rows(tdir/'blind_stage1.csv',bs)
    bmeans=mean_by_cfg(bs)
    bfinalists=[k for k,_ in sorted(bmeans.items(),key=lambda kv:(kv[1],kv[0]))[:8]]

    bc=[]
    for cfg in bfinalists:
        for rep in range(2,6):
            seed=3700000000+target_index*10000+rep
            best,sec=run_ga(matrix,n,m,G,cfg,seed,tmpdir)
            bc.append({'method':'BLIND','phase':'CONFIRM_ONLY','target_index':target_index,'target_id':target_id,
                       'pop_mult':cfg[0],'pc':cfg[1],'pm':cfg[2],'rep':rep,'seed':seed,
                       'best_cmax':best,'run_sec':sec})
    write_rows(tdir/'blind_confirmation.csv',bc)
    bcm=mean_by_cfg(bc)
    bbest=min(bcm,key=lambda k:(bcm[k],k))

    vr=[]
    for role,cfg in [('GUIDED_BEST',gbest),('BLIND_BEST',bbest)]:
        for rep in range(1,21):
            seed=3800000000+target_index*10000+rep
            best,sec=run_ga(matrix,n,m,G,cfg,seed,tmpdir)
            vr.append({'method':'DIRECT_COMPARE','phase':'FINAL_VALIDATION','target_index':target_index,
                       'target_id':target_id,'pop_mult':cfg[0],'pc':cfg[1],'pm':cfg[2],
                       'rep':rep,'seed':seed,'best_cmax':best,'run_sec':sec,'role':role})
    write_rows(tdir/'validation_raw.csv',vr)

    gv=[r['best_cmax'] for r in vr if r['role']=='GUIDED_BEST']
    bv=[r['best_cmax'] for r in vr if r['role']=='BLIND_BEST']
    gm,bm=statistics.fmean(gv),statistics.fmean(bv)
    wins=sum(a<b for a,b in zip(gv,bv))
    losses=sum(a>b for a,b in zip(gv,bv))
    ties=sum(a==b for a,b in zip(gv,bv))
    adv=100*(bm-gm)/bm
    practical='GUIDED' if adv>0.05 else ('BLIND' if adv<-0.05 else 'PRACTICAL_TIE')
    grow=len(guided_candidates)*spec['stage_R']+len(gfinalists)*(spec['final_R']-spec['stage_R'])
    brow=125+8*4
    summary={'target_index':target_index,'target_id':target_id,'n':n,'m':m,'risk':risk,
             'guided_best':str(gbest),'guided_confirm_mean':gcm[gbest],
             'blind_best':str(bbest),'blind_confirm_mean':bcm[bbest],
             'guided_mean':gm,'blind_mean':bm,'blind_minus_guided':bm-gm,
             'guided_advantage_pct':adv,'guided_wins':wins,'blind_wins':losses,'ties':ties,
             'practical_class':practical,'guided_tuning_budget':grow,'blind_tuning_budget':brow}
    write_rows(tdir/'summary.csv',[summary])
    print(f"Target {target_index:02d}: {risk} guided={gm:.4f} blind={bm:.4f} "
          f"adv={adv:.6f}% {practical}")
    return summary

def main():
    ap=argparse.ArgumentParser()
    g=ap.add_mutually_exclusive_group(required=True)
    g.add_argument('--target',type=int)
    g.add_argument('--all',action='store_true')
    ap.add_argument('--output-dir',type=Path,default=ROOT/'outputs'/'recommended_operational_policy_validation')
    a=ap.parse_args()

    targets=read_targets()
    target_indices=range(1,25) if a.all else [a.target]
    for t in target_indices:
        if t not in targets:
            raise SystemExit(f'Unknown target {t}')

    compile_engine()
    a.output_dir.mkdir(parents=True,exist_ok=True)
    summaries=[]
    with tempfile.TemporaryDirectory(prefix='recommended_policy_validation_') as td:
        tmpdir=Path(td)
        for t in target_indices:
            summaries.append(one_target(t,targets[t],a.output_dir,tmpdir))
    write_rows(a.output_dir/'summary_selected_targets.csv',summaries)
    print('DONE:',a.output_dir)

if __name__=='__main__':
    main()
