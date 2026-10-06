QUICK START - WINDOWS

Double-click:
  RUN_COMPLETE_PARAMETER_OPTIMIZATION.bat

Then select one of the included Taillard problem groups (1-11).
The script runs the complete parameter surface for all 10 instances:
  10 instances x 125 parameter configurations x 10 replications = 12,500 GA runs.

Option 12 accepts a user's own headerless CSV processing-time matrix.
For a custom problem, enter the CSV path and generation count G; the script
then evaluates the complete 125-configuration parameter surface with 10 replications.

Results are written to the outputs folder.
Requirements: Python 3 and g++ with C++17 support.
