@echo off
call install_python.bat

pushd %~dp0
python3 .\Convert.py %1
popd
pause
