@echo off
REM Save the current directory and change to the batch file's directory
pushd %~dp0

REM Run the Python script with the dragged file as an argument
python3 .\Convert.py %1

REM Return to the original directory (optional)
popd

ECHO Your files are in the output folder
pause
