@echo off
setlocal EnableExtensions
cd /d "%~dp0"

echo ============================================================
echo PFSP GA - COMPLETE PARAMETER OPTIMIZATION
echo 10 instances x 125 parameter configurations x 10 replications
echo ============================================================
echo.
echo  1  - Ta20x5
echo  2  - Ta20x10
echo  3  - Ta20x20
echo  4  - Ta50x5
echo  5  - Ta50x10
echo  6  - Ta50x20
echo  7  - Ta100x5
echo  8  - Ta100x10
echo  9  - Ta100x20
echo 10  - Ta200x10
echo 11  - Ta200x20
echo 12  - Custom PFSP matrix (CSV)
echo  0  - Exit
echo.
set /p choice=Enter selection: 

if "%choice%"=="0" exit /b 0
if "%choice%"=="1" set GROUP=Ta20x5
if "%choice%"=="2" set GROUP=Ta20x10
if "%choice%"=="3" set GROUP=Ta20x20
if "%choice%"=="4" set GROUP=Ta50x5
if "%choice%"=="5" set GROUP=Ta50x10
if "%choice%"=="6" set GROUP=Ta50x20
if "%choice%"=="7" set GROUP=Ta100x5
if "%choice%"=="8" set GROUP=Ta100x10
if "%choice%"=="9" set GROUP=Ta100x20
if "%choice%"=="10" set GROUP=Ta200x10
if "%choice%"=="11" set GROUP=Ta200x20
if "%choice%"=="12" goto CUSTOM

if not defined GROUP goto INVALID

echo.
echo Selected: %GROUP%
echo Starting complete parameter optimization...
python scripts\run_ga_multisize.py --group %GROUP% --all-instances --full-surface
if errorlevel 1 goto ERROR
echo.
echo COMPLETE. Results are in the outputs folder.
pause
exit /b 0

:CUSTOM
echo.
echo Enter the full path to a headerless CSV processing-time matrix.
echo One job per row; one machine per column.
set /p MATRIX=CSV path: 
if not exist "%MATRIX%" (
  echo File not found: %MATRIX%
  pause
  exit /b 1
)
set /p GEN=Generation count G: 
if "%GEN%"=="" (
  echo Generation count is required.
  pause
  exit /b 1
)
echo.
echo Starting full 125-configuration parameter optimization for:
echo %MATRIX%
python scripts\run_ga_multisize.py --matrix "%MATRIX%" --G %GEN% --full-surface
if errorlevel 1 goto ERROR
echo.
echo COMPLETE. Results are in the outputs folder.
pause
exit /b 0

:INVALID
echo Invalid selection.
pause
exit /b 1

:ERROR
echo.
echo The run stopped with an error. Check that Python 3 and g++ are installed.
pause
exit /b 1
