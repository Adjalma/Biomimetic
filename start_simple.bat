@echo off
REM start_simple.bat - Script simplificado sem emojis para iniciar sistema

echo ============================================
echo  SISTEMA BIOMIMETICO - INICIADOR SIMPLES
echo ============================================
echo.

REM Verificar ambiente
if not exist "venv\Scripts\activate.bat" (
    echo ERRO: Ambiente virtual nao encontrado.
    echo Execute primeiro: setup.bat (opcao 1)
    pause
    exit /b 1
)

echo Opcoes:
echo 1) Iniciar Backend (API)
echo 2) Iniciar Frontend (Dashboard)
echo 3) Iniciar Ambos
echo 4) Sair
echo.
set /p choice="Escolha (1-4): "

if "%choice%"=="1" goto backend
if "%choice%"=="2" goto frontend
if "%choice%"=="3" goto both
if "%choice%"=="4" exit /b 0

echo Opcao invalida.
pause
exit /b 1

:backend
echo.
echo Iniciando Backend...
call venv\Scripts\activate.bat
start "API Evolution" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python src/core/evolution/evolution_api.py"
echo Backend iniciado em nova janela.
echo Acesse: http://localhost:8000
echo Documentacao: http://localhost:8000/docs
echo.
pause
exit /b 0

:frontend
echo.
echo Iniciando Frontend...
if not exist "frontend\" (
    echo ERRO: Pasta frontend nao encontrada.
    pause
    exit /b 1
)

cd frontend
if exist "setup_frontend.bat" (
    call setup_frontend.bat
    if errorlevel 1 (
        echo ERRO: Falha no setup do frontend.
        cd ..
        pause
        exit /b 1
    )
)

echo Iniciando servidor de desenvolvimento...
start "Evolution Dashboard" cmd /k "cd /d %~dp0\frontend && npm run dev"
echo Frontend iniciado em nova janela.
echo Acesse: http://localhost:3000
echo.
cd ..
pause
exit /b 0

:both
echo.
echo Iniciando Backend e Frontend...
echo.
echo [1/2] Iniciando Backend...
call venv\Scripts\activate.bat
start "API Evolution" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python src/core/evolution/evolution_api.py"
echo Backend iniciado.

echo Aguardando 3 segundos...
ping -n 3 127.0.0.1 > nul

echo.
echo [2/2] Iniciando Frontend...
if not exist "frontend\" (
    echo AVISO: Pasta frontend nao encontrada. Ignorando.
) else (
    cd frontend
    if exist "setup_frontend.bat" (
        call setup_frontend.bat > nul 2>&1
    )
    if not errorlevel 1 (
        start "Evolution Dashboard" cmd /k "cd /d %~dp0\frontend && npm run dev"
        echo Frontend iniciado.
    ) else (
        echo AVISO: Falha no setup do frontend. Iniciando apenas backend.
    )
    cd ..
)

echo.
echo Sistema iniciado com sucesso!
echo.
echo URLs:
echo   Backend:  http://localhost:8000
echo   Frontend: http://localhost:3000 (se instalado)
echo   Docs API: http://localhost:8000/docs
echo.
echo Mantenha as janelas abertas para o sistema funcionar.
echo.
pause
exit /b 0