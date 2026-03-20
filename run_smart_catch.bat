@echo off
setlocal

set "SCRIPT_DIR=%~dp0"
cd /d "%SCRIPT_DIR%"

set "CONFIG_PATH=config\config.json"
if not "%~1"=="" set "CONFIG_PATH=%~1"

if not exist ".venv\Scripts\python.exe" (
    echo Error: .venv\Scripts\python.exe not found. 1>&2
    exit /b 1
)

".venv\Scripts\python.exe" app.py "%CONFIG_PATH%"
exit /b %ERRORLEVEL%
