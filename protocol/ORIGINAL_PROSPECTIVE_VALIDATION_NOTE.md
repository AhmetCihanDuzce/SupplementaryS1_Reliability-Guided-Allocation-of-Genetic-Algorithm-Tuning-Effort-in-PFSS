# Original Prospective Validation Implementation — Preservation Note

The file `Prospective_Protocol_Prespecified_v1.1_2026-08-27.json` records the implementation fixed before any of the 24 prospective target outcomes were observed. It is retained unchanged because it is the basis of the original confirmatory prospective analysis.

That conservative validation implementation used:

- **GREEN:** transferred center with no target-specific tuning;
- **AMBER:** local neighborhood, Stage-1 R=3, raw top 5 extended to R=10, at most 116 tuning runs;
- **RED:** all 125 configurations at R=10, 1,250 tuning runs.

Across the 24-target panel this schedule used 6,185 tuning runs and produced the original 21/24 policy-versus-center within-tolerance result.

The manuscript's **recommended operational policy is different**. It preserves the same historical reliability thresholds and increasing-risk search breadth, but uses staged screening and finalist confirmation with maximum per-target tuning budgets of 50 (GREEN), 137 (AMBER), and 490 (RED). The recommended policy is documented in `Recommended_Risk_Guided_Operational_Policy_v1.0.json` and in `../recommended_operational_policy/`.

Keeping these two implementations separate prevents retrospective alteration of the original prospective endpoint while allowing the lower-cost operational recommendation to reflect the full body of evidence.
