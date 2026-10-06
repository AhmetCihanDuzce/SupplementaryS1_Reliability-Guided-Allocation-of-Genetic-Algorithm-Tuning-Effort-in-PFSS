# Recommended Risk-Guided Staged Operational Policy

This directory documents the manuscript's final practitioner recommendation and its 24-target matched-budget validation.

## Recommended action map

- GREEN: center + available +/-1 axial neighbors, Stage-1 R=5, raw top 3 confirmed through R=10, maximum 50 tuning runs.
- AMBER: +/-1 Cartesian neighborhood, Stage-1 R=3, raw top 8 confirmed through R=10, maximum 137 tuning runs.
- RED: full 125-configuration grid, Stage-1 R=2, raw top 30 confirmed through R=10, 490 tuning runs.

Across the exact 24-target panel the realized risk-guided budget is 3,767 tuning runs. This is 87.44% below universal 125x10 retuning (30,000 runs) and 39.09% below the 6,185-run conservative prospective validation schedule.

The same target panel was also evaluated against a reliability-blind tuner using 3,768 runs. The final validation uses 20 fresh common-random-number replications per selected configuration. This matched-budget evidence supports the lower-cost operational recommendation but is descriptive rather than a new prespecified confirmatory endpoint.

Main files:
- `RECOMMENDED_OPERATIONAL_POLICY_AND_VALIDATION_PROTOCOL_v1.0.md`
- `Recommended_Operational_Policy_Summary.csv`
- `Recommended_Operational_Policy_Budget_Summary.csv`
- `Recommended_Operational_Policy_Budget_By_Target.csv`

Executable reproduction:
- one target: `python scripts/run_recommended_operational_policy_validation.py --target 12`
- all targets: `python scripts/run_recommended_operational_policy_validation.py --all`

Cross-package reconstruction from S2:
`python scripts/verify_recommended_operational_policy_validation.py --s2 <path-to-S2>`
