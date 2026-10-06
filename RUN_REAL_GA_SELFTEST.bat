@echo off
python scripts\SELFTEST_REAL_GA.py
if errorlevel 1 exit /b 1
pause
