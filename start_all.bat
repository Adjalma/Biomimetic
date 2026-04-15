@echo off
REM start_all.bat - Inicia Backend e Frontend automaticamente

echo ====================================
echo  BIOMIMETIC SYSTEM - AUTO START
echo ====================================
echo.

REM Check virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found.
    echo Please run setup.bat first.
    pause
    exit /b 1
)

echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/3] Starting Backend (API)...
start "API Evolution" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python src/core/evolution/evolution_api.py"
echo Backend started.

echo Waiting for backend to initialize...
ping -n 5 127.0.0.1 > nul

echo [3/3] Starting Frontend (Dashboard)...
if not exist "frontend\" (
    echo WARNING: Frontend folder not found. Skipping.
) else (
    cd frontend
    if exist "setup_frontend.bat" (
        call setup_frontend.bat > nul 2>&1
    )
    if not errorlevel 1 (
        start "Evolution Dashboard" cmd /k "cd /d %~dp0\frontend && npm run dev"
        echo Frontend started.
    ) else (
        echo WARNING: Frontend setup failed. Backend only.
    )
    cd ..
)

echo.
echo SYSTEM STARTED SUCCESSFULLY!
echo.
echo URLs:
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000 (if installed)
echo   API Docs: http://localhost:8000/docs
echo.
echo Keep windows open for system to work.
echo.
pause
exit /b 0