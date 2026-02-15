@echo off
setlocal enabledelayedexpansion
cd /d "%~dp0"
echo.
echo ============================================
echo   WAN2GP Server Launcher (RTX 3070)
echo ============================================
echo.
echo Killing any stuck Python processes...
taskkill /IM python.exe /F 2>nul
timeout /t 3 /nobreak
echo.
echo Checking GPU status...
.\.venv\Scripts\python.exe -c "import torch; print(f'GPU Ready: {torch.cuda.get_device_name()}')" 2>nul
echo.
echo Starting Wan2GP server on http://localhost:7861
echo Press Ctrl+C to stop the server
echo.
.\.venv\Scripts\python.exe wgp.py --listen --server-port 7861
pause
