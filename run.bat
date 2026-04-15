@echo off
REM run.bat - Main launcher for Biomimetic System

:menu
cls
echo ================================
echo  BIOMIMETIC SYSTEM LAUNCHER
echo ================================
echo.
echo 1) Install Dependencies
echo 2) Start Backend (API)
echo 3) Start Frontend (Dashboard)
echo 4) Start Both
echo 5) Check System Status
echo 6) Exit
echo.
set /p choice="Enter choice (1-6): "

if "%choice%"=="1" goto install
if "%choice%"=="2" goto backend
if "%choice%"=="3" goto frontend
if "%choice%"=="4" goto both
if "%choice%"=="5" goto status
if "%choice%"=="6" exit /b 0

echo Invalid choice. Press any key to try again...
pause > nul
goto menu

:install
cls
echo ================================
echo  INSTALL DEPENDENCIES
echo ================================
echo.
echo This will install FastAPI, NumPy, and other required packages.
echo.
set /p confirm="Continue? (y/n): "
if /i not "%confirm%"=="y" goto menu

call install_essential.bat
if errorlevel 1 (
    echo Installation failed. Press any key to return to menu...
    pause > nul
)
goto menu

:backend
cls
echo ================================
echo  STARTING BACKEND (API)
echo ================================
echo.
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found.
    echo Please run option 1 (Install Dependencies) first.
    pause
    goto menu
)

call venv\Scripts\activate.bat
echo Starting backend on http://localhost:8000
echo.
start "API Evolution" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python src/core/evolution/evolution_api.py"
echo Backend started in new window.
echo Press any key to return to menu...
pause > nul
goto menu

:frontend
cls
echo ================================
echo  STARTING FRONTEND (DASHBOARD)
echo ================================
echo.
if not exist "frontend\" (
    echo ERROR: Frontend folder not found.
    pause
    goto menu
)

cd frontend
if exist "setup_frontend.bat" (
    call setup_frontend.bat > nul 2>&1
    if errorlevel 1 (
        echo WARNING: Frontend setup may have failed.
    )
)

echo Starting frontend on http://localhost:3000
echo.
start "Evolution Dashboard" cmd /k "cd /d %~dp0\frontend && npm run dev"
echo Frontend started in new window.
cd ..
echo Press any key to return to menu...
pause > nul
goto menu

:both
cls
echo ================================
echo  STARTING FULL SYSTEM
echo ================================
echo.
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found.
    echo Please run option 1 (Install Dependencies) first.
    pause
    goto menu
)

echo Starting Backend...
call venv\Scripts\activate.bat
start "API Evolution" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python src/core/evolution/evolution_api.py"
echo Backend started.

echo Waiting 3 seconds...
ping -n 3 127.0.0.1 > nul

echo.
echo Starting Frontend...
if not exist "frontend\" (
    echo WARNING: Frontend folder not found. Backend only.
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
echo System started successfully!
echo.
echo URLs:
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000 (if installed)
echo   API Docs: http://localhost:8000/docs
echo.
echo Keep windows open for system to work.
echo Press any key to return to menu...
pause > nul
goto menu

:status
cls
echo ================================
echo  SYSTEM STATUS
echo ================================
echo.
echo Checking backend...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -TimeoutSec 2; echo 'BACKEND: RUNNING (http://localhost:8000)'; echo '  Response: ' + $response.Content } catch { echo 'BACKEND: NOT RUNNING' }"
echo.
echo Checking frontend...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3000' -TimeoutSec 2; echo 'FRONTEND: RUNNING (http://localhost:3000)' } catch { echo 'FRONTEND: NOT RUNNING' }"
echo.
echo Press any key to return to menu...
pause > nul
goto menu