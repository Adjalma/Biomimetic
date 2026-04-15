@echo off
REM setup.bat - Script principal do Sistema Biomimético (Instalação + Inicialização)

:main_menu
cls
echo 🧬 SISTEMA BIOMIMÉTICO - MENU PRINCIPAL
echo =========================================
echo.
echo Escolha uma opção:
echo 1^) Instalar/Configurar sistema
echo 2^) Iniciar sistema ^(Backend + Frontend^)
echo 3^) Apenas Backend ^(API Evolution^)
echo 4^) Apenas Frontend ^(Evolution Dashboard^)
echo 5^) Verificar status do sistema
echo 6^) Sair
echo.
set /p choice="Digite sua escolha (1-6): "

if "%choice%"=="1" goto install_menu
if "%choice%"=="2" goto start_both
if "%choice%"=="3" goto start_backend
if "%choice%"=="4" goto start_frontend
if "%choice%"=="5" goto check_status
if "%choice%"=="6" exit /b 0

echo ❌ Opção inválida. Pressione qualquer tecla para continuar...
pause >nul
goto main_menu

:install_menu
cls
echo 📦 MENU DE INSTALAÇÃO
echo ======================
echo.
echo Escolha o tipo de instalação:
echo 1^) Completa ^(recomendado^) - todas as dependências
echo 2^) Leve - apenas essenciais
echo 3^) Personalizada - escolher módulos
echo 4^) Voltar ao menu principal
echo.
set /p install_choice="Digite 1, 2, 3 ou 4: "

if "%install_choice%"=="1" goto install_full
if "%install_choice%"=="2" goto install_light
if "%install_choice%"=="3" goto install_custom
if "%install_choice%"=="4" goto main_menu

echo ❌ Opção inválida
pause
goto install_menu

:install_full
echo.
echo 🔍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale Python 3.11+ em: https://python.org
    pause
    goto install_menu
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% encontrado

if not exist "requirements.txt" (
    if not exist "src\" (
        echo ❌ Não parece estar na pasta do projeto Biomimetic
        echo    Execute: cd Biomimetic
        pause
        goto install_menu
    )
)

echo.
echo 🐍 Criando ambiente virtual...
if not exist "venv\" (
    python -m venv venv
    echo ✅ Ambiente virtual criado: venv\
) else (
    echo ⚠️  Ambiente virtual já existe: venv\
)

echo.
echo 🔧 Ativando ambiente virtual...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Ambiente ativado
) else (
    echo ❌ Não foi possível ativar ambiente virtual
    pause
    goto install_menu
)

echo.
echo 📦 Instalando todas as dependências...
python -m pip install --upgrade pip
if exist "requirements.txt" (
    pip install -r requirements.txt
) else (
    echo ❌ Arquivo requirements.txt não encontrado
    pause
    goto install_menu
)

call :test_installation
if errorlevel 1 (
    echo ❌ Instalação falhou.
    pause
    goto install_menu
)

echo.
echo 🎉 INSTALAÇÃO COMPLETA!
echo.
set /p start_now="Deseja iniciar o sistema agora? (s/n): "
if /i "%start_now%"=="s" goto start_both
echo ℹ️  Para iniciar o sistema depois, use as opções 2, 3 ou 4 do menu principal.
pause
goto main_menu

:install_light
echo.
echo 🔍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale Python 3.11+ em: https://python.org
    pause
    goto install_menu
)

echo.
echo 🐍 Criando ambiente virtual...
if not exist "venv\" (
    python -m venv venv
    echo ✅ Ambiente virtual criado: venv\
) else (
    echo ⚠️  Ambiente virtual já existe: venv\
)

echo.
echo 🔧 Ativando ambiente virtual...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Ambiente ativado
) else (
    echo ❌ Não foi possível ativar ambiente virtual
    pause
    goto install_menu
)

echo.
echo 📦 Instalando dependências essenciais...
python -m pip install --upgrade pip
pip install fastapi==0.104.1 "uvicorn[standard]"==0.24.0 pydantic==2.5.0 numpy==1.24.3 requests==2.31.0
echo ✅ Dependências essenciais instaladas
echo ℹ️  Outras dependências podem ser instaladas depois com:
echo    pip install plotly shap lime boto3 torch transformers

call :test_installation
if errorlevel 1 (
    echo ❌ Instalação falhou.
    pause
    goto install_menu
)

echo.
echo 🎉 INSTALAÇÃO LEVE COMPLETA!
echo.
set /p start_now="Deseja iniciar o sistema agora? (s/n): "
if /i "%start_now%"=="s" goto start_both
echo ℹ️  Para iniciar o sistema depois, use as opções 2, 3 ou 4 do menu principal.
pause
goto main_menu

:install_custom
echo.
echo Módulos disponíveis:
echo   fastapi, uvicorn, pydantic, numpy, requests
echo   plotly, shap, lime, boto3, torch, transformers
set /p modules="Digite os módulos separados por espaço: "

echo.
echo 🔍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale Python 3.11+ em: https://python.org
    pause
    goto install_menu
)

echo.
echo 🐍 Criando ambiente virtual...
if not exist "venv\" (
    python -m venv venv
    echo ✅ Ambiente virtual criado: venv\
) else (
    echo ⚠️  Ambiente virtual já existe: venv\
)

echo.
echo 🔧 Ativando ambiente virtual...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Ambiente ativado
) else (
    echo ❌ Não foi possível ativar ambiente virtual
    pause
    goto install_menu
)

echo.
echo 📦 Instalando módulos personalizados...
python -m pip install --upgrade pip
pip install %modules%

call :test_installation
if errorlevel 1 (
    echo ❌ Instalação falhou.
    pause
    goto install_menu
)

echo.
echo 🎉 INSTALAÇÃO PERSONALIZADA COMPLETA!
echo.
set /p start_now="Deseja iniciar o sistema agora? (s/n): "
if /i "%start_now%"=="s" goto start_both
echo ℹ️  Para iniciar o sistema depois, use as opções 2, 3 ou 4 do menu principal.
pause
goto main_menu

:test_installation
echo.
echo 🧪 Testando instalação...
python -c "
import sys
try:
    import fastapi
    import numpy
    print('✅ FastAPI v' + fastapi.__version__)
    print('✅ NumPy v' + numpy.__version__)
    print('✅ Instalação bem-sucedida!')
except ImportError as e:
    print('❌ Erro:', e)
    sys.exit(1)
"
if errorlevel 1 exit /b 1
exit /b 0

:start_both
cls
echo 🚀 INICIANDO SISTEMA COMPLETO (BACKEND + FRONTEND)
echo ===================================================
echo.
echo 🧬 Iniciando Backend...
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Ambiente virtual não encontrado.
    echo    Execute a opção 1 (Instalar) primeiro.
    pause
    goto main_menu
)

call venv\Scripts\activate.bat
start "API Evolution" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python src/core/evolution/evolution_api.py"
echo ✅ Backend iniciado em nova janela.

timeout /t 3 /nobreak >nul

echo.
echo 🎨 Iniciando Frontend...
if not exist "frontend\" (
    echo ❌ Pasta frontend não encontrada.
    echo    O frontend será ignorado.
) else (
    cd frontend
    if exist "setup_frontend.bat" (
        call setup_frontend.bat >nul 2>&1
    )
    if not errorlevel 1 (
        start "Evolution Dashboard" cmd /k "cd /d %~dp0\frontend && npm run dev"
        echo ✅ Frontend iniciado.
    ) else (
        echo ⚠️  Falha no setup do frontend. Iniciando apenas o backend.
    )
    cd ..
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
goto main_menu

:start_backend
cls
echo 🧬 INICIANDO BACKEND (API EVOLUTION)
echo =====================================
echo.
if not exist "venv\Scripts\activate.bat" (
    echo ❌ Ambiente virtual não encontrado.
    echo    Execute a opção 1 (Instalar) primeiro.
    pause
    goto main_menu
)

call venv\Scripts\activate.bat
start "API Evolution" cmd /k "cd /d %~dp0 && call venv\Scripts\activate.bat && python src/core/evolution/evolution_api.py"
echo ✅ Backend iniciado em nova janela.
echo 🌐 Acesse: http://localhost:8000
echo 📚 Documentação: http://localhost:8000/docs
echo.
pause
goto main_menu

:start_frontend
cls
echo 🎨 INICIANDO FRONTEND (EVOLUTION DASHBOARD)
echo ============================================
echo.
if not exist "frontend\" (
    echo ❌ Pasta frontend não encontrada.
    echo    Execute a opção 1 (Instalar) primeiro para baixar o frontend.
    pause
    goto main_menu
)

cd frontend
if exist "setup_frontend.bat" (
    call setup_frontend.bat
    if errorlevel 1 (
        echo ❌ Falha no setup do frontend.
        cd ..
        pause
        goto main_menu
    )
)

echo.
echo 🚀 Iniciando servidor de desenvolvimento...
start "Evolution Dashboard" cmd /k "cd /d %~dp0\frontend && npm run dev"
echo ✅ Frontend iniciado em nova janela.
echo 🌐 Acesse: http://localhost:3000
echo.
cd ..
pause
goto main_menu

:check_status
cls
echo 🔍 VERIFICANDO STATUS DO SISTEMA
echo =================================
echo.
echo 🧬 Backend (API Evolution):
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -TimeoutSec 2; echo '   ✅ Rodando em http://localhost:8000'; echo '   Status: ' + ($response.Content | ConvertFrom-Json).status } catch { echo '   ❌ Não está respondendo' }"
echo.
echo 🎨 Frontend (Dashboard):
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:3000' -TimeoutSec 2; echo '   ✅ Rodando em http://localhost:3000' } catch { echo '   ❌ Não está respondendo' }"
echo.
pause
goto main_menu