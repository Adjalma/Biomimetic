@echo off
REM install_essential_fixed.bat - Install essential dependencies (fixed version)

echo ====================================
echo  INSTALLING ESSENTIAL DEPENDENCIES
echo ====================================
echo.

REM Check Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+.
    echo Download from: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python found.
python --version

REM Check/create virtual environment
if not exist "venv\Scripts\activate.bat" (
    echo Creating virtual environment...
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment.
        pause
        exit /b 1
    )
    echo Virtual environment created.
) else (
    echo Virtual environment already exists.
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing essential packages...
echo This may take a few minutes...
pip install fastapi uvicorn pydantic numpy requests

echo Testing installation...
REM Create test file to avoid multi-line issues
echo import sys > test_install.py
echo try: >> test_install.py
echo     import fastapi >> test_install.py
echo     import uvicorn >> test_install.py  
echo     import pydantic >> test_install.py
echo     import numpy >> test_install.py
echo     import requests >> test_install.py
echo     print('SUCCESS: All packages installed') >> test_install.py
echo     print('FastAPI:', fastapi.__version__) >> test_install.py
echo     print('Uvicorn:', uvicorn.__version__) >> test_install.py
echo     print('Pydantic:', pydantic.__version__) >> test_install.py
echo     print('NumPy:', numpy.__version__) >> test_install.py
echo     print('Requests:', requests.__version__) >> test_install.py
echo except ImportError as e: >> test_install.py
echo     print('FAILED:', e) >> test_install.py
echo     sys.exit(1) >> test_install.py

python test_install.py
del test_install.py

if errorlevel 1 (
    echo ERROR: Installation failed.
    pause
    exit /b 1
)

echo.
echo ====================================
echo  ESSENTIAL DEPENDENCIES INSTALLED!
echo ====================================
echo.
echo You can now run the system with:
echo   .\run.bat           (menu)
echo   .\start_all.bat     (auto start)
echo   .\fix_all.bat       (fix and start)
echo.
echo URLs when running:
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000
echo   API Docs: http://localhost:8000/docs
echo.
pause
exit /b 0