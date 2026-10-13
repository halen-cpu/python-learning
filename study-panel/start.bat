@echo off
title Python Study Panel
cd /d "%~dp0"
set PY=C:\Users\13377\AppData\Local\Programs\Python\Python313\python.exe
if not exist "%PY%" set PY=python
"%PY%" app.py
if errorlevel 3 exit
echo.
echo Server stopped. Press any key to close this window.
pause >nul
