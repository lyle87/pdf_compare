@echo off
REM Debug wrapper: runs run.bat and saves full output to run.log
cd /d "%~dp0"
echo Running debug wrapper. Output will be saved to run.log









pauseecho If nothing obvious appears, upload `run.log` or paste its contents here.echo.powershell -Command "Get-Content -Path 'run.log' -Tail 200 -Wait:$false"echo Showing last 200 lines of run.log:
necho ======== Finished running run.bat ========call run.bat > run.log 2>&1n:: Run the main batch and capture stdout/stderr