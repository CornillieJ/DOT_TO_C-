@echo off
pushd %~dp0
call .\install_python.bat
python3 .\import_interfaces.py %1
popd
ECHO The interfaces have been written to imported_interfaces.txt
ECHO You can now run the Convert script
pause
