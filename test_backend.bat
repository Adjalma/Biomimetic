@echo off
REM test_backend.bat - Teste o backend e mostre erros

echo ====================================
echo  BACKEND TEST - DIAGNOSTIC
echo ====================================
echo.

REM Verificar ambiente virtual
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found.
    exit /b 1
)

echo 1. Activating virtual environment...
call venv\Scripts\activate.bat

echo 2. Checking Python dependencies...
python -c "
import sys
print('Python version:', sys.version)

try:
    import fastapi
    print('✓ FastAPI:', fastapi.__version__)
except ImportError as e:
    print('✗ FastAPI missing:', e)
    sys.exit(1)

try:
    import uvicorn
    print('✓ Uvicorn:', uvicorn.__version__)
except ImportError as e:
    print('✗ Uvicorn missing:', e)
    sys.exit(1)

try:
    import numpy
    print('✓ NumPy:', numpy.__version__)
except ImportError:
    print('⚠ NumPy missing (optional)')

print('All essential dependencies OK')
"

if errorlevel 1 (
    echo.
    echo DEPENDENCY ERROR: Essential packages missing.
    echo Run: .\install_essential.bat
    pause
    exit /b 1
)

echo.
echo 3. Starting backend in TEST mode...
echo    This window will stay open. Press Ctrl+C to stop.
echo.

REM Executar backend sem start (fica visível)
python src/core/evolution/evolution_api.py

echo.
echo Backend stopped.
pause
exit /b 0