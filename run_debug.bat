@echo off
REM Debug wrapper: runs run.bat and saves full output to run.log
cd /d "%~dp0"
echo Running debug wrapper. Output will be saved to run.log

REM Run the main batch and capture stdout/stderr
call run.bat > run.log 2>&1

echo ======== Finished running run.bat ======== 
echo Showing last 200 lines of run.log:

powershell -Command "Get-Content -Path run.log -Tail 200 -Wait:$false"

echo.
echo If nothing obvious appears, upload `run.log` or paste its contents here.
pause
