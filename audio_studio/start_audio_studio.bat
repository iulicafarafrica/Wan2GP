@echo off
REM Wan2GP Audio Studio - Quick Start Script (Windows)

echo ==================================
echo Wan2GP Audio Studio Quick Start
echo ==================================
echo.

REM Get script directory
set SCRIPT_DIR=%~dp0
set PROJECT_DIR=%SCRIPT_DIR%..

REM Check if virtual environment exists
if not exist "%PROJECT_DIR%\.venv" (
    echo Error: Virtual environment not found at %PROJECT_DIR%\.venv
    echo Please create a virtual environment first.
    pause
    exit /b 1
)

REM Activate virtual environment
echo Activating virtual environment...
call "%PROJECT_DIR%\.venv\Scripts\activate.bat"

REM Check if Node.js is installed
where node >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: Node.js is not installed.
    echo Please install Node.js 18.x or 20.x from https://nodejs.org/
    pause
    exit /b 1
)

REM Check if npm is installed
where npm >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo Error: npm is not installed.
    echo Please install npm (comes with Node.js).
    pause
    exit /b 1
)

REM Install backend dependencies if needed
if not exist "%PROJECT_DIR%\audio_backend\.deps_installed" (
    echo.
    echo Installing backend dependencies...
    pip install -r "%PROJECT_DIR%\audio_backend\requirements.txt"
    type nul > "%PROJECT_DIR%\audio_backend\.deps_installed"
)

REM Install frontend dependencies if needed
if not exist "%PROJECT_DIR%\audio_frontend\node_modules" (
    echo.
    echo Installing frontend dependencies...
    cd /d "%PROJECT_DIR%\audio_frontend"
    call npm install
    cd /d "%PROJECT_DIR%"
)

REM Parse arguments
set START_BACKEND=1
set START_FRONTEND=1
set DEV_MODE=1

:parse_args
if "%~1"=="--backend-only" (
    set START_FRONTEND=0
    shift
    goto parse_args
)
if "%~1"=="--frontend-only" (
    set START_BACKEND=0
    shift
    goto parse_args
)
if "%~1"=="--production" (
    set DEV_MODE=0
    shift
    goto parse_args
)
if "%~1"=="--help" goto show_help
if "%~1"=="-h" goto show_help
if not "%~1"=="" shift & goto parse_args

if "%DEV_MODE%"=="1" (
    echo.
    echo Starting in DEVELOPMENT mode...
    echo.
    
    if "%START_BACKEND%"=="1" (
        echo Starting FastAPI backend on http://127.0.0.1:8001...
        cd /d "%PROJECT_DIR%"
        start "Audio Studio Backend" python audio_backend\main.py
        echo Backend started.
        echo.
    )
    
    if "%START_FRONTEND%"=="1" (
        echo Starting Vite frontend on http://localhost:3000...
        cd /d "%PROJECT_DIR%\audio_frontend"
        start "Audio Studio Frontend" npm run dev
        echo Frontend started.
        echo.
    )
    
    echo ==================================
    echo Servers started successfully!
    echo ==================================
    echo.
    echo Frontend: http://localhost:3000
    echo Backend:  http://127.0.0.1:8001
    echo API Docs: http://127.0.0.1:8001/docs
    echo.
    echo Close the terminal windows to stop the servers.
    echo.
    pause
) else (
    echo.
    echo Starting in PRODUCTION mode...
    echo.
    
    REM Build frontend
    echo Building frontend...
    cd /d "%PROJECT_DIR%\audio_frontend"
    call npm run build
    cd /d "%PROJECT_DIR%"
    
    if "%START_BACKEND%"=="1" (
        echo.
        echo Starting FastAPI backend serving built frontend...
        echo Access at: http://127.0.0.1:8001
        echo.
        cd /d "%PROJECT_DIR%"
        python audio_backend\main.py
    )
)

goto :eof

:show_help
echo Usage: %~nx0 [OPTIONS]
echo.
echo Options:
echo   --backend-only    Start only the backend server
echo   --frontend-only   Start only the frontend server
echo   --production      Start in production mode (build frontend)
echo   --help, -h        Show this help message
echo.
echo Examples:
echo   %~nx0              Start both backend and frontend in development mode
echo   %~nx0 --backend-only  Start only the backend
echo   %~nx0 --production     Build frontend and start backend serving it
pause
exit /b 0
