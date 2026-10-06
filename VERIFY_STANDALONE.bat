@echo off
python scripts\verify_all.py
if errorlevel 1 exit /b 1
python scripts\verify_prospective_matrices_exact.py
if errorlevel 1 exit /b 1
pause
