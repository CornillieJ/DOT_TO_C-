@echo off
setlocal enabledelayedexpansion

echo Checking if Python is installed...
where python >nul 2>nul
if %errorlevel%==0 (
    echo Python is already installed.
    python --version
    goto :EOF
)
echo Python is not installed. Downloading Python...

set "python_url=https://www.python.org/ftp/python/3.11.5/python-3.11.5-amd64.exe"
set "installer=python-installer.exe"

if exist %installer% del %installer%
curl -o %installer% %python_url%
if not exist %installer% (
    echo Failed to download Python installer. Exiting.
    exit /b 1
)

:: Install Python silently
echo Installing Python...
start /wait %installer% /quiet InstallAllUsers=1 PrependPath=1
if %errorlevel% neq 0 (
    echo Python installation failed. Exiting.
    del %installer%
    exit /b 1
)

:: Cleanup
del %installer%
echo Python installation completed successfully.
python --version
