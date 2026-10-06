# Ta100x20 Canonical 595/840 Reproducibility Note

The manuscript's Ta100x20 historical anchor is 595/840 (70.833333%) under the 0.25-pp near-optimal criterion and G=17,000. The complete canonical data chain is supplied in Supplementary S2.

Recovered evidence:
- 12,500 main GA runs (10 instances × 125 configurations × R=10);
- canonical standard-NEH vector for all ten targets;
- all 120 C(10,3) calibration triples and prespecified robust-minimax selections;
- 790 independent fresh-validation GA runs (79 distinct conditions × R=10);
- all 840 comparison-level outcomes;
- 595/840 aggregate near-optimal count.

The S2 standalone verifier independently recomputes standard NEH, checks all archived best permutations against the supplied matrices, reproduces 120/120 split policies, rebuilds 840/840 holdout comparisons, and returns 595/840.

Use `scripts/verify_ta100x20_595_s2.py` to invoke that verifier from S1.
