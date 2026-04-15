@echo off
REM install_essential.bat - Install essential dependencies

echo ====================================
echo  INSTALLING ESSENTIAL DEPENDENCIES
echo ====================================
echo.

REM Check Python
python --version > nul 2>&1
if errorlevel 1 (
    echo ERROR: Python not found. Please install Python 3.8+.
    pause
    exit /b 1
)

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
)

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo Upgrading pip...
python -m pip install --upgrade pip

echo Installing essential packages...
pip install fastapi uvicorn pydantic numpy requests

echo Testing installation...
python -c "import fastapi; import numpy; print('SUCCESS: FastAPI v' + fastapi.__version__ + ', NumPy v' + numpy.__version__)"

if errorlevel 1 (
    echo ERROR: Installation failed.
    pause
    exit /b 1
)

echo.
echo ESSENTIAL DEPENDENCIES INSTALLED SUCCESSFULLY!
echo You can now run the system with start_all.bat
echo.
pause
exit /b 0