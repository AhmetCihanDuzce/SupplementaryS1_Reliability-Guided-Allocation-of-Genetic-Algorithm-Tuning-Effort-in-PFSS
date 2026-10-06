@echo off
python scripts\run_complete_parameter_optimization.py --group Ta50x5 --quick-demo
if errorlevel 1 exit /b 1
pause
