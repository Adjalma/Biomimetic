@echo off
REM setup_frontend.bat - Script de instalação do Evolution Dashboard para Windows
echo 🔧 Configurando Evolution Dashboard...
echo.

REM Verificar Node.js
echo 🔍 Verificando Node.js...
where node >nul 2>&1
if errorlevel 1 (
    echo ❌ Node.js não encontrado. Instale Node.js 18+ em: https://nodejs.org/
    pause
    exit /b 1
)

for /f "tokens=1" %%i in ('node --version') do set NODE_VERSION=%%i
echo ✅ Node.js %NODE_VERSION% detectado

REM Verificar npm/yarn
echo 🔍 Verificando gerenciador de pacotes...
where yarn >nul 2>&1
if not errorlevel 1 (
    set PACKAGE_MANAGER=yarn
) else (
    where npm >nul 2>&1
    if not errorlevel 1 (
        set PACKAGE_MANAGER=npm
    ) else (
        echo ❌ Nenhum gerenciador de pacotes encontrado (npm ou yarn).
        pause
        exit /b 1
    )
)
echo ✅ Gerenciador de pacotes: %PACKAGE_MANAGER%

REM Instalar dependências
echo.
echo 📦 Instalando dependências...
if "%PACKAGE_MANAGER%"=="yarn" (
    yarn install
) else (
    npm install
)

if errorlevel 1 (
    echo ❌ Falha ao instalar dependências.
    pause
    exit /b 1
)

REM Configurar arquivo .env.local
echo.
echo 📄 Configurando variáveis de ambiente...
if not exist .env.local (
    copy .env.local.example .env.local
    echo ✅ Arquivo .env.local criado a partir do exemplo.
) else (
    echo ⚠️  Arquivo .env.local já existe. Mantendo configurações atuais.
)

REM Verificar se a API está rodando (opcional)
echo.
echo 🔗 Verificando conexão com a API Evolution...
powershell -Command "try { $response = Invoke-WebRequest -Uri 'http://localhost:8000/health' -TimeoutSec 2; echo '✅ API Evolution detectada em http://localhost:8000' } catch { echo '⚠️  API Evolution não respondendo em http://localhost:8000'; echo '   Certifique-se de que o servidor da API está rodando.' }"

echo.
echo 🎉 Setup do frontend completo!
echo.
echo 📋 COMANDOS DISPONÍVEIS:
echo    %PACKAGE_MANAGER% run dev    - Iniciar servidor de desenvolvimento
echo    %PACKAGE_MANAGER% run build  - Build de produção
echo    %PACKAGE_MANAGER% run start  - Executar build de produção
echo    %PACKAGE_MANAGER% run lint   - Verificar código
echo.
echo 🚀 Para iniciar o dashboard:
echo    %PACKAGE_MANAGER% run dev
echo.
echo 🌐 Acesse: http://localhost:3000
echo.
pause