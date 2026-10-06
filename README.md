# Supplementary S1 — Code and Reproducibility

This package contains the executable genetic-algorithm implementation, experiment runners, the original prespecified prospective validation protocol, the recommended risk-guided staged operational policy, exact prospective processing-time matrices, and verification utilities used to support the manuscript.

## GA implementation

The supplied C++17 reference engine implements:
- permutation representation;
- random Fisher–Yates initialization;
- binary tournament selection;
- fixed-cardinality position-preserving OBX, k=floor(n/2);
- insertion/shift mutation;
- one-elite generational replacement;
- no embedded local search;
- `std::mt19937_64` random-number generation;
- PFSP makespan (`Cmax`) evaluation;
- parameter grid Ps/n={1,2,3,4,5}, pc={0.85,0.8875,0.925,0.9625,1.00},
  pm={0.025,0.05,0.075,0.10,0.125}, with R=10 for the retained historical response surfaces.

## Immediate executable self-test

Run one of:
- Windows: `RUN_REAL_GA_SELFTEST.bat`
- macOS/Linux: `./run_real_ga_selftest.sh`
- any platform with Python and a C++17 compiler: `python scripts/SELFTEST_REAL_GA.py`

The self-test starts from `Ta50x5_01.csv`, executes ten fresh GA runs for the first
prespecified parameter configuration, and must reproduce exactly:

`2740, 2752, 2741, 2735, 2735, 2735, 2752, 2735, 2746, 2735`

No historical result CSV is read to generate these values.

## Generate response-surface experiments from scratch

One 10-rep parameter configuration:
`python scripts/run_ga_experiments.py --group Ta50x5 --instance 1 --pop-mult 1 --pc 0.85 --pm 0.025`

One complete 125-configuration response surface (1,250 GA runs):
`python scripts/run_ga_experiments.py --group Ta50x5 --instance 1 --full-surface`

All ten instances of one group (12,500 GA runs):
`python scripts/run_ga_experiments.py --group Ta50x5 --all-instances --full-surface`

Complete retained 50-job main experiment (37,500 GA runs):
`python scripts/run_ga_experiments.py --all-50job --full-surface`

Newly generated outputs are written under `outputs/`.

## Prospective 24-target panel and original confirmatory implementation

The exact processing-time matrices are in `instances/Prospective_24/` and are named by
target index and size, for example `Target01_30x5.csv`.

The prespecified target design is:
`data/prospective/Prospective_24_Target_Design_Prespecified.csv`

The submission-facing transcription of the protocol fixed before target outcomes were observed is:
`protocol/Prospective_Protocol_Prespecified_v1.1_2026-08-27.json`

That original conservative implementation is retained unchanged because it underpins the confirmatory prospective analysis: GREEN used direct center reuse, AMBER used at most 116 tuning runs, and RED used 1,250 runs. Across the 24 targets it used 6,185 tuning runs and is the basis of the original 21/24 policy-versus-center result. See `protocol/ORIGINAL_PROSPECTIVE_VALIDATION_NOTE.md`.

Run:
`python scripts/verify_prospective_matrices_exact.py`

This independently checks all 24 archived SHA-256 identities and all 24 deterministic NEH values.

## Recommended risk-guided staged operational policy

The manuscript's final practitioner recommendation is the lower-cost staged implementation:

- **GREEN:** center + available +/-1 axial neighbors; Stage-1 R=5; confirm raw top 3 with reps 6-10; maximum 50 tuning runs.
- **AMBER:** +/-1 Cartesian neighborhood (at most 27 configurations); Stage-1 R=3; confirm raw top 8 with reps 4-10; maximum 137 tuning runs.
- **RED:** full 125-configuration grid; Stage-1 R=2; confirm raw top 30 with reps 3-10; 490 tuning runs.

Search breadth increases with historical transfer risk, while replication is concentrated on finalists. Historical evidence determines the risk ordering and search breadth; the staged replication schedule is the lower-cost operational refinement evaluated on the exact 24-target panel.

The complete specification is in:
- `protocol/Recommended_Risk_Guided_Operational_Policy_v1.0.json`
- `recommended_operational_policy/RECOMMENDED_OPERATIONAL_POLICY_AND_VALIDATION_PROTOCOL_v1.0.md`
- `recommended_operational_policy/Recommended_Operational_Policy_Summary.csv`
- `recommended_operational_policy/Recommended_Operational_Policy_Budget_By_Target.csv`

Across the 24 targets, the recommended policy uses **3,767 tuning runs**, which is **87.44% fewer** than universal 125x10 retuning (30,000 runs) and **39.09% fewer** than the original conservative prospective schedule (6,185 runs).

Re-run the staged policy together with its reliability-blind matched-budget validation comparator for one target:
`python scripts/run_recommended_operational_policy_validation.py --target 12`

Re-run all 24 targets:
`python scripts/run_recommended_operational_policy_validation.py --all`

The all-target run is computationally expensive.

After Supplementary S2 has been extracted or its ZIP retained, reconstruct the reported 24-target matched-budget evidence with:
`python scripts/verify_recommended_operational_policy_validation.py --s2 <path-to-S2>`

The comparator uses 3,768 tuning runs across 24 targets and does not use historical reliability to allocate effort. The reported matched-budget evidence is descriptive rather than a new prespecified confirmatory endpoint.

## Canonical Ta100x20 595/840 verification

The canonical Ta100x20 comparison-level artifact is distributed in Supplementary S2.
Run:
`python scripts/verify_ta100x20_595_s2.py --s2 <path-to-S2-zip-or-extracted-folder>`

The verifier requires the canonical historical result to reconstruct as 595/840.

## Reproducibility scope

S1 includes the retained 50-job processing-time matrices and executable GA response-surface workflow, the exact 24-target prospective matrices, the original prespecified prospective validation protocol, and the final recommended staged operational policy with its matched-budget validation workflow. Supplementary S2 contains the complete manuscript-facing result tables and raw validation evidence, including the canonical Ta100x20 reconstruction, the original 24-target prospective validation results, and the 24-target staged-policy-versus-blind comparison.

The supplied reference implementation provides seed-controlled replay and verification; however, identical nominal seeds do not necessarily guarantee bitwise-identical GA trajectories or final outcomes across different compiler, standard-library, or numerical-library environments. Small implementation-dependent differences in random-number mapping, operation ordering, or tie handling may alter individual stochastic runs. Reproduced results should therefore be expected to show consistency at the aggregate experimental level rather than exact run-by-run identity across software environments.

The portable C++ sources are reference implementations of the documented GA logic and are not claimed to be byte-identical copies of every historical production source. See `SOURCE_LINEAGE.md`.

## Main files

- `src/ga_single_exact_reference.cpp` — C++17 GA reference engine.
- `scripts/run_ga_experiments.py` — historical response-surface generator.
- `scripts/SELFTEST_REAL_GA.py` — exact ten-run self-test.
- `scripts/run_recommended_operational_policy_validation.py` — recommended staged policy plus matched-budget blind validation.
- `scripts/verify_recommended_operational_policy_validation.py` — cross-package reconstruction of the reported matched-budget results from S2.
- `scripts/verify_all.py` — manuscript-critical standalone summary checks.
- `scripts/verify_prospective_matrices_exact.py` — exact prospective-matrix verification.
- `config/prespecified_50job_main.json` — retained 50-job design and seed families.
- `instances/Taillard_50Job/` — 30 retained 50-job matrices.
- `instances/Prospective_24/` — exact 24 prospective matrices.
