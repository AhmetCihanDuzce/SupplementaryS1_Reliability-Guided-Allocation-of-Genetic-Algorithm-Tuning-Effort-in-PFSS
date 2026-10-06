# Submission Scope and Audit Note

This archive is intended as the submission-facing Supplementary S1 reproducibility package aligned with the manuscript's final recommended staged policy.

Verified content includes:
- executable C++17 GA reference implementation;
- retained 50-job processing-time matrices and parameter-grid runners;
- exact ten-run Ta50x5 self-test;
- original prespecified prospective validation protocol and deterministic seed specifications;
- all 24 exact prospective processing-time matrices;
- 24/24 SHA-256 identity checks and 24/24 deterministic NEH checks;
- explicit specification and executable workflow for the recommended 50/137/490 staged operational policy;
- budget accounting showing 3,767 tuning runs across the 24 targets;
- code and protocol for the 3,768-run reliability-blind matched-budget validation comparator;
- cross-package verification utilities for manuscript-facing S2 results.

The package does not claim that every intermediate file from every historical computing session has been retained. Where the manuscript relies on reconstructed historical evidence, the corresponding comparison-level data and independent verifiers are distributed in Supplementary S2.

## Original validation versus final operational recommendation

Two implementations are intentionally retained and must not be conflated.

1. **Original conservative prospective validation implementation.** This was fixed before the 24 target outcomes were observed and used GREEN=0 target-specific tuning, AMBER<=116 runs, and RED=1,250 runs. It used 6,185 tuning runs across 24 targets and remains the basis of the original confirmatory 21/24 policy-versus-center analysis.

2. **Recommended staged operational implementation.** This preserves the same historical risk thresholds and increasing-risk search breadth but uses staged screening and finalist confirmation: GREEN<=50, AMBER<=137, RED=490. It used 3,767 tuning runs across the same 24 targets and is the policy recommended for future operational use in the manuscript. Its matched-budget comparison with a 3,768-run reliability-blind tuner is descriptive validation rather than a retrospective replacement of the original confirmatory endpoint.

## Prospective matrix provenance

All 24 prospective matrices are byte-identical to the archived pre-outcome fingerprints. A provenance audit established that the prespecified PCG64DXSM seed rule used a 16-bit integer draw stream. This implementation detail is documented in `PROSPECTIVE_MATRIX_REPLAY_CLARIFICATION.md`.

## Naming convention

Submission-facing target labels use `Target01`...`Target24` and `target_index`. Parameter combinations are referred to as configurations. Internal work-package, internal workflow and development labels are not used in this package.
