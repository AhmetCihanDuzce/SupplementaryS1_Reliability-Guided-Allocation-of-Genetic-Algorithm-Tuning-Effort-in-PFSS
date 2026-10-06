# Ready-to-Run PFSP Genetic Algorithm

Use `scripts/run_ga_multisize.py` to solve the included Taillard benchmarks or your own PFSP matrix.

Included groups:
Ta20x5, Ta20x10, Ta20x20,
Ta50x5, Ta50x10, Ta50x20,
Ta100x5, Ta100x10, Ta100x20,
Ta200x10, Ta200x20.

All ten processing-time matrices for each group are included in `instances/Taillard_All/`.

Complete 125-configuration surface for all 10 instances:
    python scripts/run_ga_multisize.py --group Ta100x20 --all-instances --full-surface

One parameter setting:
    python scripts/run_ga_multisize.py --group Ta100x10 --instance 3 --pop-mult 3 --pc 0.925 --pm 0.075 --reps 10

Own problem:
Prepare a headerless CSV with one job per row, one machine per column, and positive integer processing times.
    python scripts/run_ga_multisize.py --matrix my_problem.csv --G 10000 --pop-mult 3 --pc 0.925 --pm 0.075 --reps 10

Own problem, full surface:
    python scripts/run_ga_multisize.py --matrix my_problem.csv --G 10000 --full-surface

The runner detects n and m automatically for custom matrices. This build supports up to 500 jobs and 50 machines.

GA: random permutation initialization; binary tournament; fixed-cardinality position-preserving OBX;
insertion/shift mutation; elitism=1; generational replacement; Cmax objective; std::mt19937_64.

Full grid:
Ps/n={1,2,3,4,5}; pc={0.85,0.8875,0.925,0.9625,1.00};
pm={0.025,0.05,0.075,0.10,0.125}; default R=10.

Requirements: Python 3 and g++ with C++17 support.
