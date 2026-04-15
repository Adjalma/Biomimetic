@echo off
REM test_backend_fixed.bat - Teste o backend corrigido para Windows

echo ====================================
echo  BACKEND TEST - DIAGNOSTIC
echo ====================================
echo.

REM Verificar ambiente virtual
if not exist "venv\Scripts\activate.bat" (
    echo ERROR: Virtual environment not found.
    echo Please run: .\install_essential.bat
    pause
    exit /b 1
)

echo 1. Activating virtual environment...
call venv\Scripts\activate.bat

echo 2. Checking Python dependencies...

REM Criar arquivo temporário com código Python
echo import sys > check_deps.py
echo print('Python version:', sys.version) >> check_deps.py
echo. >> check_deps.py
echo try: >> check_deps.py
echo     import fastapi >> check_deps.py
echo     print('✓ FastAPI:', fastapi.__version__) >> check_deps.py
echo except ImportError as e: >> check_deps.py
echo     print('✗ FastAPI missing:', e) >> check_deps.py
echo     sys.exit(1) >> check_deps.py
echo. >> check_deps.py
echo try: >> check_deps.py
echo     import uvicorn >> check_deps.py
echo     print('✓ Uvicorn:', uvicorn.__version__) >> check_deps.py
echo except ImportError as e: >> check_deps.py
echo     print('✗ Uvicorn missing:', e) >> check_deps.py
echo     sys.exit(1) >> check_deps.py
echo. >> check_deps.py
echo try: >> check_deps.py
echo     import numpy >> check_deps.py
echo     print('✓ NumPy:', numpy.__version__) >> check_deps.py
echo except ImportError: >> check_deps.py
echo     print('⚠ NumPy missing (optional)') >> check_deps.py
echo. >> check_deps.py
echo print('All essential dependencies OK') >> check_deps.py

REM Executar verificação
python check_deps.py

REM Verificar se houve erro
if errorlevel 1 (
    echo.
    echo DEPENDENCY ERROR: Essential packages missing.
    echo Run: .\install_essential.bat
    del check_deps.py
    pause
    exit /b 1
)

REM Limpar arquivo temporário
del check_deps.py

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