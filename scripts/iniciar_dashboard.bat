@echo off
echo ========================================
echo Iniciando Dashboard GIC
echo ========================================
echo.

REM Ativar ambiente virtual Python 3.11
call "venv_py311\Scripts\activate.bat"

REM Verificar se o ambiente foi ativado
if "%VIRTUAL_ENV%"=="" (
    echo ERRO: Ambiente virtual nao foi ativado!
    echo Verifique se o caminho esta correto: venv_py311\Scripts\activate.bat
    pause
    exit /b 1
)

echo Ambiente virtual ativado: %VIRTUAL_ENV%
echo.

REM Verificar se as dependencias estao instaladas
echo Verificando dependencias...
python -c "import flask, flask_socketio" 2>nul
if errorlevel 1 (
    echo Instalando dependencias...
    pip install -r requirements_dashboard.txt
    if errorlevel 1 (
        echo ERRO: Falha ao instalar dependencias!
        pause
        exit /b 1
    )
)

echo.
echo Dependencias verificadas!
echo.

REM Iniciar dashboard
echo Iniciando Dashboard GIC...
echo.
echo Acesse: http://localhost:5000
echo.
echo Pressione Ctrl+C para parar
echo.

python dashboard_ia_v2.py

echo.
echo Dashboard parado.
pause
