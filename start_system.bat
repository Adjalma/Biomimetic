@echo off
REM start_system.bat - Iniciar Sistema Evolutivo Biomimético (Backend + Frontend)
echo 🚀 INICIANDO SISTEMA EVOLUTIVO BIOMIMÉTICO
echo ============================================
echo.

REM Verificar ambiente virtual
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Ambiente virtual não encontrado.
    echo    Execute setup.bat primeiro para configurar o ambiente.
    pause
    exit /b 1
)

echo Escolha o que iniciar:
echo 1^) Apenas Backend ^(API Evolution^)
echo 2^) Apenas Frontend ^(Evolution Dashboard^)
echo 3^) Ambos ^(Recomendado^)
echo 4^) Verificar status do sistema
echo 5^) Sair
echo.
set /p choice="Digite sua escolha (1-5): "

if "%choice%"=="1" goto start_backend
if "%choice%"=="2" goto start_frontend
if "%choice%"=="3" goto start_both
if "%choice%"=="4" goto check_status
if "%choice%"=="5" exit /b 0

echo ❌ Opção inválida
pause
exit /b 1

:start_backend
echo.
echo 🧬 Iniciando Backend (API Evolution)...
call venv\Scripts\activate.bat
start "API Evolution" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python src/core/evolution/evolution_api.py"
echo ✅ Backend iniciado em nova janela.
echo 🌐 Acesse: http://localhost:8000
echo 📚 Documentação: http://localhost:8000/docs
echo.
pause
exit /b 0

:start_frontend
echo.
echo 🎨 Iniciando Frontend (Evolution Dashboard)...
if not exist "frontend\" (
    echo ❌ Pasta frontend não encontrada.
    pause
    exit /b 1
)

cd frontend
call setup_frontend.bat
if errorlevel 1 (
    echo ❌ Falha no setup do frontend.
    pause
    exit /b 1
)

echo.
echo 🚀 Iniciando servidor de desenvolvimento...
start "Evolution Dashboard" cmd /k "cd /d %~dp0\frontend && npm run dev"
echo ✅ Frontend iniciado em nova janela.
echo 🌐 Acesse: http://localhost:3000
echo.
pause
exit /b 0

:start_both
echo.
echo 🔄 Iniciando Backend e Frontend...
echo.
echo 🧬 Iniciando Backend...
call venv\Scripts\activate.bat
start "API Evolution" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python src/core/evolution/evolution_api.py"
echo ✅ Backend iniciado.

echo Aguardando 3 segundos...
ping -n 3 127.0.0.1 > nul

echo.
echo 🎨 Iniciando Frontend...
if not exist "frontend\" (
    echo ❌ Pasta frontend não encontrada.
    echo    O frontend será ignorado.
) else (
    cd frontend
    call setup_frontend.bat >nul 2>&1
    if not errorlevel 1 (
        start "Evolution Dashboard" cmd /k "cd /d %~dp0\frontend && npm run dev"
        echo ✅ Frontend iniciado.
    ) else (
        echo ⚠️  Falha no setup do frontend. Iniciando apenas o backend.
    )
)

echo.
echo ✅ Sistema iniciado com sucesso!
echo.
echo 📍 URLs:
echo    Backend:  http://localhost:8000
echo    Frontend: http://localhost:3000 ^(se instalado^)
echo    Docs API: http://localhost:8000/docs
echo.
echo ⚠️  Mantenha as janelas abertas para o sistema funcionar.
echo.
pause
exit /b 0

:check_status
echo.
echo 🔍 Verificando status do sistema...
echo.

REM Verificar backend
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -TimeoutSec 2; echo '✅ Backend (API) está rodando em http://localhost:8000'; echo '   Resposta: ' + $response.Content } catch { echo '❌ Backend não está respondendo.' }"

echo.

REM Verificar frontend
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3000' -TimeoutSec 2; echo '✅ Frontend está rodando em http://localhost:3000' } catch { echo '❌ Frontend não está respondendo.' }"

echo.
pause
exit /b 0