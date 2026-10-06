# Source Lineage and Reproducibility Scope

The historical experiments used one prespecified GA architecture. Exact makespan evaluation
was accelerated during the experimental campaign, but fitness evaluation consumes no random
numbers; evaluator substitutions that return identical Cmax values do not alter the intended
GA stochastic trajectory.

The portable C++ sources distributed in Supplementary S1 are reference implementations of
the documented GA logic and are not claimed to be byte-identical copies of every historical
production source. The historical production archive records `gastructure_v2_fast.cpp` with
SHA-256 `a6bf581208ac4ff7919730dbefffdf0c850f21904ed2738631cee5baa3377cda`.
The reference implementation is intended for inspection and deterministic replay checks, not
for reproducing historical wall-clock times.

For Ta100x20, the manuscript and prespecified prospective protocol use the canonical historical
SAFE count 595/840. The complete comparison-level reconstruction is distributed in
Supplementary S2 and includes 12,500 main runs, 120 calibration-split policies, 790 independent
fresh-validation runs, and 840 holdout comparisons. An alternate 597/840 normalization artifact
was examined during audit, is not used in the manuscript, and is not distributed as submission
evidence.

The exact 24-target prospective matrices are distributed in this package and independently
verified against their archived SHA-256 fingerprints and NEH values. The recommended staged operational policy and its matched-budget validation use these exact matrices, the same GA architecture and parameter grid, separate search seed families, and a fresh common-seed validation stream. The original conservative prospective implementation is retained separately because it underpins the prespecified confirmatory analysis.
