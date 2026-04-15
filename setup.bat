@echo off
REM setup.bat - Script de instalação para Windows do Sistema Biomimético

echo 🧬 INSTALANDO SISTEMA BIOMIMÉTICO
echo ==================================
echo.

REM Verificar Python
echo 🔍 Verificando Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ❌ Python não encontrado. Instale Python 3.11+ em: https://python.org
    pause
    exit /b 1
)

for /f "tokens=2" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo ✅ Python %PYTHON_VERSION% encontrado

REM Verificar se está na pasta correta
if not exist "requirements.txt" (
    if not exist "src\" (
        echo ❌ Não parece estar na pasta do projeto Biomimetic
        echo    Execute: cd Biomimetic
        pause
        exit /b 1
    )
)

REM Criar ambiente virtual
echo.
echo 🐍 Criando ambiente virtual...
if not exist "venv\" (
    python -m venv venv
    echo ✅ Ambiente virtual criado: venv\
) else (
    echo ⚠️  Ambiente virtual já existe: venv\
)

REM Ativar ambiente
echo.
echo 🔧 Ativando ambiente virtual...
if exist "venv\Scripts\activate.bat" (
    call venv\Scripts\activate.bat
    echo ✅ Ambiente ativado
) else (
    echo ❌ Não foi possível ativar ambiente virtual
    pause
    exit /b 1
)

REM Instalar dependências
echo.
echo 📦 Instalando dependências...
python -m pip install --upgrade pip
echo.

REM Menu de instalação
echo Escolha o tipo de instalação:
echo 1^) Completa ^(recomendado^) - todas as dependências
echo 2^) Leve - apenas essenciais
echo 3^) Personalizada - escolher módulos
set /p install_choice="Digite 1, 2 ou 3: "

if "%install_choice%"=="1" (
    echo Instalando todas as dependências...
    if exist "requirements.txt" (
        pip install -r requirements.txt
    ) else (
        echo ❌ Arquivo requirements.txt não encontrado
        pause
        exit /b 1
    )
) else if "%install_choice%"=="2" (
    echo Instalando dependências essenciais...
    pip install fastapi==0.104.1 "uvicorn[standard]"==0.24.0 pydantic==2.5.0 numpy==1.24.3 requests==2.31.0
    echo ✅ Dependências essenciais instaladas
    echo    Outras dependências podem ser instaladas depois com:
    echo    pip install plotly shap lime boto3 torch transformers
) else if "%install_choice%"=="3" (
    echo Instalação personalizada...
    echo Módulos disponíveis:
    echo   fastapi, uvicorn, pydantic, numpy, requests
    echo   plotly, shap, lime, boto3, torch, transformers
    set /p modules="Digite os módulos separados por espaço: "
    pip install %modules%
) else (
    echo ❌ Opção inválida
    pause
    exit /b 1
)

REM Testar instalação
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

REM Criar teste rápido
echo.
echo 📄 Criando script de teste rápido...
(
echo #!/usr/bin/env python3
echo """
echo Teste rápido da instalação do Sistema Biomimético
echo """
echo import sys
echo.
echo print("🧬 TESTE DE INSTALAÇÃO DO SISTEMA BIOMIMÉTICO")
echo print("=" * 50)
echo.
echo # Verificar módulos essenciais
echo modules = ['fastapi', 'uvicorn', 'pydantic', 'numpy', 'requests']
echo for module in modules:
echo     try:
echo         __import__(module^)
echo         print(f"✅ {module}")
echo     except ImportError:
echo         print(f"❌ {module} não instalado")
echo.
echo print()
echo print("🎯 PRÓXIMOS PASSOS:")
echo print("1. Execute: python teste_rapido.py")
echo print("2. Ou inicie a API: python src/core/evolution/evolution_api.py")
echo print("3. Acesse: http://localhost:8000/health")
) > teste_instalacao.py

echo ✅ Script criado: teste_instalacao.py

echo.
echo 🎉 INSTALAÇÃO COMPLETA!
echo ========================
echo.
echo 📋 COMANDOS DISPONÍVEIS:
echo    python teste_instalacao.py    - Verificar instalação
echo    python teste_rapido.py        - Testar sistema biomimético
echo    python iniciar_sistema.py main - Sistema principal
echo    python src/core/evolution/evolution_api.py - API evolutiva
echo.
echo 📚 DOCUMENTAÇÃO:
echo    Consulte INICIACAO_RAPIDA.md para guia rápido
echo    Consulte README.md para documentação completa
echo.
echo 🔧 SE HOUVER ERROS:
echo    - Execute: pip install -r requirements.txt --force-reinstall
echo    - Ou me envie a mensagem de erro
echo.
echo Boa sorte com o sistema biomimético! 🚀
pause