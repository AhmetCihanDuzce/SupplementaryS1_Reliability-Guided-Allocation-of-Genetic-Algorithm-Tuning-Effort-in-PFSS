# Recommended Risk-Guided Staged Operational Policy and Budget-Matched Validation — Protocol v1.0

## Scientific role

This document specifies the manuscript's final operational recommendation. Historical transfer experiments provide the risk ordering and motivate increasing search breadth from GREEN to AMBER to RED. The lower-replication screening-and-confirmation schedule is the computational refinement evaluated on the exact 24-target panel.

This recommended policy is distinct from the original conservative prospective validation implementation, which remains preserved unchanged for confirmatory inference.

## Common GA design

The GA architecture, parameter grid, target matrices, generation counts, and historical risk labels are inherited from the documented study. The parameter grid is:

- pop_mult = {1,2,3,4,5}
- pc = {0.85, 0.8875, 0.925, 0.9625, 1.0}
- pm = {0.025, 0.05, 0.075, 0.10, 0.125}

Target-specific generation counts and exact matrix files are given in `data/prospective/Prospective_24_Target_Design_Prespecified.csv`.

## Recommended risk-guided staged policy

The historical reliability thresholds remain 0.90 and 0.75. The actions are:

- **GREEN:** transferred center plus all available +/-1 axial grid neighbors; Stage-1 R=5; raw top K=3; confirmation-only reps 6..10; maximum 50 tuning runs.
- **AMBER:** +/-1 Cartesian neighborhood around the transferred center, at most 27 configurations; Stage-1 R=3; raw top K=8; confirmation-only reps 4..10; maximum 137 tuning runs.
- **RED:** full 125-configuration grid; Stage-1 R=2; raw top K=30; confirmation-only reps 3..10; 490 tuning runs.

Boundary values are clipped to the available parameter grid.

Within each stage, configurations are ranked by mean Cmax ascending with deterministic tie-break `(pop_mult, pc, pm)` ascending. The raw top-K set is confirmed. Final policy selection uses the finalist with the lowest **confirmation-only** mean Cmax, with the same deterministic parameter tie-break. Screening observations are therefore not allowed to dominate the final finalist comparison. The transferred center is not forced into the finalist set and is not used as an acceptance gate.

## Observed 24-target tuning budget

Because GREEN and AMBER neighborhood sizes shrink at parameter-grid boundaries, the realized target-level budgets vary below their maximum values. Across the 24-target panel:

- GREEN: 370 tuning runs across 8 targets;
- AMBER: 1,437 tuning runs across 12 targets;
- RED: 1,960 tuning runs across 4 targets;
- **TOTAL: 3,767 tuning runs**.

For reference:

- universal 125x10 retuning across 24 targets = 30,000 runs;
- original conservative prospective schedule = 6,185 runs.

Thus the staged policy uses 87.44% fewer configuration runs than universal retuning and 39.09% fewer than the original conservative prospective schedule. These are run-count comparisons, not wall-clock savings.

## Reliability-blind matched-budget validation comparator

To test whether historical risk information improves allocation of tuning effort rather than merely whether tuning helps, a reliability-blind comparator uses essentially the same total budget. For every target:

- Stage-1: all 125 parameter configurations at R=1;
- raw top K=8 by Stage-1 Cmax with deterministic parameter tie-break;
- confirmation-only reps 2..5;
- select the finalist with the lowest confirmation-only mean Cmax.

This uses 157 tuning runs per target, **3,768 across 24 targets**.

## Seed families

Common random numbers are used within each target and stage:

- recommended risk-guided search: `3600000000 + target_index*10000 + rep`
- reliability-blind search: `3700000000 + target_index*10000 + rep`
- fresh final validation: `3800000000 + target_index*10000 + rep`

The final validation uses 20 fresh reps per selected configuration. These validation data are never used for search or selection.

## Reported 24-target validation result

Under fresh validation:

- lower mean Cmax: guided 16/24, blind 5/24, exact ties 3/24;
- interpretive +/-0.05% practical band: guided 9/24, blind 1/24, practical ties 14/24;
- mean target-level guided advantage = 0.050265517350%;
- median target-level guided advantage = 0.037247210556%.

These matched-budget results support the recommended lower-cost operational implementation within the tested panel. They are reported as descriptive validation rather than as a new prespecified confirmatory endpoint.

## Original prospective validation implementation

The original confirmatory prospective analysis remains tied to its prespecified conservative implementation:

- GREEN: direct center reuse, 0 target-specific tuning;
- AMBER: local neighborhood, Stage-1 R=3, raw top 5 extended to R=10, at most 116 tuning runs;
- RED: full 125 configurations at R=10, 1,250 runs;
- 24-target total = 6,185 tuning runs.

Those outcomes are retained unchanged and must not be recomputed as though they had arisen from the final staged operational policy.
