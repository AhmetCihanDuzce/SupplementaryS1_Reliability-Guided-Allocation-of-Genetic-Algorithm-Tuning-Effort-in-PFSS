#!/usr/bin/env python3
"""Recompute the 24-target recommended-policy matched-budget validation from Supplementary S2."""
from pathlib import Path
import argparse,csv,io,zipfile,statistics

RELS=['05_Recommended_Operational_Policy_Validation','05_Budget_Matched_Direct_Comparison']
FILES={
    'raw':['Recommended_Operational_Policy_Final_Validation_Raw.csv','Budget_Matched_Final_Validation_Raw.csv'],
    'final':['Recommended_Operational_Policy_Validation.csv','Budget_Matched_Direct_Comparison.csv'],
    'aggregate':['Recommended_Operational_Policy_Aggregate.csv','Budget_Matched_Aggregate.csv'],
    'selected':['Recommended_Operational_Policy_Selected_Configurations.csv','Budget_Matched_Selected_Configurations.csv'],
}

def csv_rows_bytes(b):
    return list(csv.DictReader(io.StringIO(b.decode('utf-8-sig'))))

def resolve_root(path):
    p=Path(path)
    if p.is_dir():
        for rel in RELS:
            if (p/rel).is_dir():
                return p, rel
        q=p/'Supplementary_S2_Data_Results_and_Quality_Assurance'
        for rel in RELS:
            if (q/rel).is_dir():
                return q, rel
        raise FileNotFoundError(f'Cannot find any of {RELS} under {p}')
    return None

def read_from(path, subs):
    p=Path(path)
    if isinstance(subs,str): subs=[subs]
    resolved=resolve_root(p) if p.is_dir() else None
    if resolved is not None:
        root, rel = resolved
        for sub in subs:
            candidate=root/rel/sub
            if candidate.exists():
                return candidate.read_bytes()
        raise FileNotFoundError((rel,subs))
    with zipfile.ZipFile(p) as z:
        for rel in RELS:
            for sub in subs:
                suffix=f'{rel}/{sub}'
                names=[n for n in z.namelist() if n.endswith(suffix)]
                if len(names)==1:
                    return z.read(names[0])
        raise FileNotFoundError((RELS,subs))

def close(a,b,tol=1e-9):
    return abs(float(a)-float(b))<=tol

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--s2',required=True,help='S2 ZIP or extracted package/folder')
    a=ap.parse_args()

    raw=csv_rows_bytes(read_from(a.s2,FILES['raw']))
    final=csv_rows_bytes(read_from(a.s2,FILES['final']))
    agg=csv_rows_bytes(read_from(a.s2,FILES['aggregate']))
    selected=csv_rows_bytes(read_from(a.s2,FILES['selected']))

    assert len(raw)==960
    assert len(final)==24 and len(selected)==24

    by={}
    for r in raw:
        t=int(float(r['target_index']))
        role=r['role']
        rep=int(r['rep'])
        seed=int(r['seed'])
        val=float(r['best_cmax'])
        assert role in {'GUIDED_BEST','BLIND_BEST'}
        assert seed==3800000000+t*10000+rep
        by.setdefault(t,{}).setdefault(role,{})[rep]=val

    assert set(by)==set(range(1,25))
    fby={int(r['target_index']):r for r in final}
    sby={int(r['target_index']):r for r in selected}
    calc=[]

    for t in range(1,25):
        g=by[t]['GUIDED_BEST']
        b=by[t]['BLIND_BEST']
        assert set(g)==set(range(1,21)) and set(b)==set(range(1,21))
        gv=[g[i] for i in range(1,21)]
        bv=[b[i] for i in range(1,21)]
        gm,bm=statistics.fmean(gv),statistics.fmean(bv)
        diff=bm-gm
        adv=100*diff/bm
        gw=sum(x<y for x,y in zip(gv,bv))
        bw=sum(x>y for x,y in zip(gv,bv))
        ties=sum(x==y for x,y in zip(gv,bv))
        winner='GUIDED' if gm<bm else ('BLIND' if gm>bm else 'EXACT_TIE')
        practical='GUIDED' if adv>0.05 else ('BLIND' if adv<-0.05 else 'PRACTICAL_TIE')

        r=fby[t]
        assert close(gm,r['guided_mean']) and close(bm,r['blind_mean'])
        assert close(diff,r['blind_minus_guided']) and close(adv,r['guided_advantage_pct'])
        assert gw==int(r['guided_wins']) and bw==int(r['blind_wins']) and ties==int(r['ties'])
        assert practical==r['practical_class']

        sr=sby[t]
        assert int(sr['guided_tuning_budget'])==int(r['guided_tuning_budget'])
        assert int(sr['blind_tuning_budget'])==int(r['blind_tuning_budget'])
        calc.append((t,r['risk'],adv,winner,practical,
                     int(r['guided_tuning_budget']),int(r['blind_tuning_budget'])))

    def counts(rows):
        return dict(
            n_targets=len(rows),
            guided_better_raw=sum(x[3]=='GUIDED' for x in rows),
            blind_better_raw=sum(x[3]=='BLIND' for x in rows),
            exact_tie_raw=sum(x[3]=='EXACT_TIE' for x in rows),
            guided_practical=sum(x[4]=='GUIDED' for x in rows),
            blind_practical=sum(x[4]=='BLIND' for x in rows),
            practical_tie=sum(x[4]=='PRACTICAL_TIE' for x in rows),
            mean_guided_adv_pct=statistics.fmean(x[2] for x in rows),
            median_guided_adv_pct=statistics.median(x[2] for x in rows),
            guided_budget=sum(x[5] for x in rows),
            blind_budget=sum(x[6] for x in rows),
        )

    amap={r['scope']:r for r in agg}
    for scope in ['ALL','GREEN','AMBER','RED']:
        rows=calc if scope=='ALL' else [x for x in calc if x[1]==scope]
        cc=counts(rows)
        ar=amap[scope]
        for k in ['guided_better_raw','blind_better_raw','exact_tie_raw',
                  'guided_practical','blind_practical','practical_tie',
                  'guided_budget','blind_budget']:
            assert int(ar[k])==int(cc[k]), (scope,k,ar[k],cc[k])
        nkey='n_targets' if 'n_targets' in ar else 'n_cells'
        assert int(ar[nkey])==cc['n_targets']
        for k in ['mean_guided_adv_pct','median_guided_adv_pct']:
            assert close(ar[k],cc[k]), (scope,k,ar[k],cc[k])

    c=counts(calc)
    assert c['guided_budget']==3767 and c['blind_budget']==3768
    print('PASS — recommended staged policy matched-budget validation')
    print('Validation rows:',len(raw),'= 24 targets x 2 methods x 20 fresh CRN reps')
    print(f"Raw mean-Cmax results: guided {c['guided_better_raw']}/24, "
          f"blind {c['blind_better_raw']}/24, exact ties {c['exact_tie_raw']}/24")
    print(f"+/-0.05% practical classes: guided {c['guided_practical']}/24, "
          f"blind {c['blind_practical']}/24, ties {c['practical_tie']}/24")
    print(f"Mean guided advantage: {c['mean_guided_adv_pct']:.12f}%")
    print(f"Median guided advantage: {c['median_guided_adv_pct']:.12f}%")
    print(f"Tuning budgets: guided {c['guided_budget']}, blind {c['blind_budget']}")

if __name__=='__main__':
    main()
