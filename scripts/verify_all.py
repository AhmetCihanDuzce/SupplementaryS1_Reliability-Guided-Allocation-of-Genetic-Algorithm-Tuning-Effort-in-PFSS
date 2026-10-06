#!/usr/bin/env python3
"""Standalone verification of manuscript-critical historical and prospective totals."""
from pathlib import Path
import csv, json

ROOT = Path(__file__).resolve().parents[1]

def read_csv(path):
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def as_bool(x):
    return str(x).strip().lower() in {"true","1","yes"}

def close(a,b,tol=1e-10):
    return abs(float(a)-float(b)) <= tol

HIST = ROOT/"data"/"historical"/"Current_Manuscript_Historical_Anchor_Summary.csv"
PROS = ROOT/"data"/"prospective"/"Prospective_24_Target_Summary.csv"
PROTOCOL = ROOT/"protocol"/"Prospective_Protocol_Prespecified_v1.1_2026-08-27.json"
RECOMMENDED_BUDGET = ROOT/"recommended_operational_policy"/"Recommended_Operational_Policy_Budget_By_Target.csv"

for p in (HIST, PROS, PROTOCOL, RECOMMENDED_BUDGET):
    if not p.exists():
        raise FileNotFoundError(f"Required local file missing: {p}")

h = read_csv(HIST)
anchors = [r for r in h if r["anchor"].strip().upper() != "OVERALL"]
expected = {
    "20x5": (749,840,89.17,9000),
    "20x10":(775,840,92.26,8000),
    "20x20":(720,840,85.71,8000),
    "50x5": (824,840,98.10,2000),
    "50x10":(656,840,78.10,9000),
    "50x20":(613,840,72.98,9000),
    "100x5":(837,840,99.64,9000),
    "100x10":(814,840,96.90,9000),
    "100x20":(595,840,70.83,17000),
}
assert len(anchors) == 9
for r in anchors:
    key = r["anchor"]
    ec, en, er, eg = expected[key]
    assert int(r["safe_count"]) == ec
    assert int(r["comparisons"]) == en
    assert close(r["safe_rate_pct"], er, 0.0051)
    assert int(r["G"]) == eg

hist_safe = sum(int(r["safe_count"]) for r in anchors)
hist_n = sum(int(r["comparisons"]) for r in anchors)
assert (hist_safe, hist_n) == (6583,7560)

protocol = json.loads(PROTOCOL.read_text(encoding="utf-8"))
assert protocol.get("status") == "PRESPECIFIED_BEFORE_ANY_PROSPECTIVE_GA_OUTCOME"
protocol_text = json.dumps(protocol, ensure_ascii=False)
for x in [749,775,720,824,656,613,837,814,595]:
    assert str(x) in protocol_text

p = read_csv(PROS)
assert len(p) == 24
assert [int(r["target_index"]) for r in p] == list(range(1,25))
actions = {a: sum(r["action"] == a for r in p) for a in ("GREEN","AMBER","RED")}
assert actions == {"GREEN":8,"AMBER":12,"RED":4}

policy_safe = sum(as_bool(r["policy_safe"]) for r in p)
center_safe = sum(as_bool(r["center_safe"]) for r in p)
assert policy_safe == 21 and center_safe == 21

policy_se = [float(r["policy_signed_excess_pp"]) for r in p]
center_se = [float(r["center_signed_excess_pp"]) for r in p]
policy_clip = [max(0.0,x) for x in policy_se]
center_clip = [max(0.0,x) for x in center_se]
runs = sum(int(float(r["policy_tuning_runs"])) for r in p)

mean_policy_se = sum(policy_se)/24
mean_policy_clip = sum(policy_clip)/24
mean_center_clip = sum(center_clip)/24
reduction = 1-runs/30000

assert close(mean_policy_se, -0.009092122733021249, 1e-12)
assert close(mean_policy_clip, 0.06823129364422649, 1e-12)
assert close(mean_center_clip, 0.11463739911827482, 1e-12)
assert runs == 6185
assert close(reduction, 0.7938333333333334, 1e-12)

def within(margin, field):
    return sum(float(r[field]) <= margin for r in p)

assert [within(x,"policy_signed_excess_pp") for x in (0.10,0.25,0.50)] == [19,21,23]
assert [within(x,"center_signed_excess_pp") for x in (0.10,0.25,0.50)] == [13,21,23]

above = [(int(r["n"]),int(r["m"])) for r in p if not as_bool(r["policy_safe"])]
assert above == [(60,15),(70,15),(90,20)]

discordant = [(int(r["n"]),int(r["m"]),as_bool(r["policy_safe"]),as_bool(r["center_safe"]))
              for r in p if as_bool(r["policy_safe"]) != as_bool(r["center_safe"])]
assert discordant == [(70,20,True,False),(90,20,False,True)]

# Recommended staged operational policy budget accounting
rb = read_csv(RECOMMENDED_BUDGET)
assert len(rb) == 24
assert [int(r["target_index"]) for r in rb] == list(range(1,25))
recommended_runs = sum(int(r["total_tuning_runs"]) for r in rb)
by_risk = {risk: sum(int(r["total_tuning_runs"]) for r in rb if r["risk"] == risk) for risk in ("GREEN","AMBER","RED")}
assert recommended_runs == 3767
assert by_risk == {"GREEN":370,"AMBER":1437,"RED":1960}
assert max(int(r["total_tuning_runs"]) for r in rb if r["risk"] == "GREEN") <= 50
assert max(int(r["total_tuning_runs"]) for r in rb if r["risk"] == "AMBER") <= 137
assert min(int(r["total_tuning_runs"]) for r in rb if r["risk"] == "RED") == 490
assert max(int(r["total_tuning_runs"]) for r in rb if r["risk"] == "RED") == 490
reduction_vs_universal = 1 - recommended_runs/30000
reduction_vs_conservative = 1 - recommended_runs/runs
assert close(reduction_vs_universal, 0.8744333333333333, 1e-12)
assert close(reduction_vs_conservative, 0.39094583670169764, 1e-12)

print("PASS — standalone manuscript-critical verification")
print(f"Historical: {hist_safe}/{hist_n} = {100*hist_safe/hist_n:.2f}%")
print("Actions:", actions)
print(f"Policy within 0.25 pp: {policy_safe}/24 = {100*policy_safe/24:.1f}%")
print(f"Direct center within 0.25 pp: {center_safe}/24 = {100*center_safe/24:.1f}%")
print(f"Mean policy signed excess: {mean_policy_se:.10f} pp")
print(f"Mean policy clipped loss: {mean_policy_clip:.10f} pp")
print(f"Mean direct-center clipped loss: {mean_center_clip:.10f} pp")
print(f"Original conservative prospective tuning: {runs}/30000; reduction = {100*reduction:.2f}%")
print(f"Recommended staged operational tuning: {recommended_runs}/30000; reduction = {100*reduction_vs_universal:.2f}%")
print(f"Recommended vs conservative reduction: {100*reduction_vs_conservative:.2f}%")
print("Recommended budget by risk:", by_risk)
print("Policy above-tolerance targets:", above)
print("Policy/center discordance:", discordant)
