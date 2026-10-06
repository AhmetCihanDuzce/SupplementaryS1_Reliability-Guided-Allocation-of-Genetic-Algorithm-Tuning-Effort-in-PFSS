# Executable GA Grid and Parameter-Selection Utilities

This archive contains an executable chain from processing-time matrices to fresh GA
runs and parameter-grid results. It also contains transparent parameter-selection
utilities for newly generated response surfaces.

## What is reproduced exactly from scratch
For the retained 50-job inputs, `scripts/run_ga_experiments.py` calls the actual C++ GA
engine over the prespecified parameter grid. The self-test verifies the implementation against
ten known Ta50x5 run outcomes.

## Parameter-selection utilities
`02_optimize_parameters.py` implements the documented admissible-region / robust-minimax
selection logic on a user-supplied set of newly generated response surfaces.

`03_historical_3to7_transfer.py` enumerates all C(10,3)=120 calibration triples and
applies that selection utility to the seven holdouts for each split.

These utilities make the computational selection logic inspectable and executable. The manuscript's historical SAFE rates depend on independent fresh-validation records; the corresponding retained records and provenance are supplied in Supplementary S2. For Ta100x20, the canonical 595/840 comparison-level artifact has been recovered in full and is supplied in S2, together with a standalone verifier that rebuilds all 120 split policies and all 840 holdout comparisons from the archived main and fresh runs.

## Fast technical demonstration
Windows:
    RUN_PARAMETER_OPTIMIZATION_DEMO.bat

or:
    python scripts/run_complete_parameter_optimization.py --group Ta50x5 --quick-demo

This performs real C++ GA runs at multiple parameter settings and then invokes the
selection utility on the newly generated output. It is a technical execution test, not
a reproduction of a manuscript anchor.

## Full retained 50-job response-surface workflow
    python scripts/run_complete_parameter_optimization.py --group Ta50x5

The command regenerates all 10 x 125 x 10 = 12,500 GA runs for the selected retained
50-job group and then performs the descriptive 3-to-7 selection/holdout reconstruction
on those newly generated surfaces.

No S2 result CSV is used to generate the GA runs.
