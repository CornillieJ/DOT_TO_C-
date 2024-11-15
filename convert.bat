@echo off
pushd %~dp0
call install_python.bat
REM for %%A in (%*) do (
REM    python3 .\import_interfaces.py %%A
REM )
for %%A in (%*) do (
    python3 .\Convert.py %%A
)
REM del .\interfaces_import.txt
popd
ECHO Your files are in the output folder
pause
