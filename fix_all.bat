@echo off
REM fix_all.bat - Corrige todos os problemas e inicia o sistema

echo ====================================
echo  FIX ALL PROBLEMS - BIOMIMETIC SYSTEM
echo ====================================
echo.

echo Este script vai:
echo 1. Verificar Python
echo 2. Criar/verificar ambiente virtual
echo 3. Instalar dependencias essenciais
echo 4. Testar o backend
echo 5. Iniciar o sistema
echo.

set /p confirm="Continuar? (s/n): "
if /i not "%confirm%"=="s" (
    echo Cancelado.
    pause
    exit /b 0
)

echo.
echo ===== ETAPA 1: VERIFICAR PYTHON =====
python --version > nul 2>&1
if errorlevel 1 (
    echo ERRO: Python nao encontrado no PATH.
    echo Instale Python 3.8+ e adicione ao PATH.
    echo Baixe em: https://www.python.org/downloads/
    pause
    exit /b 1
)

python -c "import sys; print('Python ' + sys.version.split()[0])"
echo OK: Python instalado.

echo.
echo ===== ETAPA 2: VERIFICAR AMBIENTE VIRTUAL =====
if not exist "venv\Scripts\activate.bat" (
    echo Criando ambiente virtual...
    python -m venv venv
    if errorlevel 1 (
        echo ERRO: Falha ao criar ambiente virtual.
        pause
        exit /b 1
    )
    echo OK: Ambiente virtual criado.
) else (
    echo OK: Ambiente virtual ja existe.
)

echo.
echo ===== ETAPA 3: INSTALAR DEPENDENCIAS =====
echo Ativando ambiente virtual...
call venv\Scripts\activate.bat

echo Atualizando pip...
python -m pip install --upgrade pip

echo Instalando dependencias essenciais...
echo (Isso pode levar alguns minutos...)
pip install fastapi uvicorn pydantic numpy requests

echo Verificando instalacao...
python -c "
try:
    import fastapi
    import uvicorn
    import pydantic
    import numpy
    import requests
    print('✅ Todas dependencias instaladas:')
    print('   FastAPI   v' + fastapi.__version__)
    print('   Uvicorn   v' + uvicorn.__version__)
    print('   Pydantic  v' + pydantic.__version__)
    print('   NumPy     v' + numpy.__version__)
    print('   Requests  v' + requests.__version__)
except ImportError as e:
    print('❌ Erro:', e)
    exit(1)
"

if errorlevel 1 (
    echo ERRO: Instalacao falhou.
    pause
    exit /b 1
)

echo OK: Dependencias instaladas.

echo.
echo ===== ETAPA 4: TESTAR BACKEND =====
echo Testando inicializacao da API...
python -c "
import sys
sys.path.insert(0, '.')
try:
    from src.core.evolution.evolution_api import app
    print('✅ API FastAPI carregada')
    print(f'   Rotas: {len(app.routes)}')
    
    # Testar se consegue criar instancia do sistema
    from src.core.evolution.evolution_api import EvolutionSystem
    system = EvolutionSystem()
    print('✅ EvolutionSystem inicializado')
    print(f'   Mutacoes: {system.mutation_count}')
    print(f'   Evolucoes: {system.evolution_count}')
    
except Exception as e:
    print('❌ Erro:', e)
    import traceback
    traceback.print_exc()
    exit(1)
"

if errorlevel 1 (
    echo AVISO: Houve erro no teste, mas continuando...
)

echo.
echo ===== ETAPA 5: INICIAR SISTEMA =====
echo Iniciando Backend (API)...
echo.
echo MANUAL: Por favor, mantenha esta janela ABERTA.
echo         O backend vai rodar aqui e mostrar logs.
echo         Em outra janela, acesse http://localhost:8000/docs
echo.
echo Pressione Ctrl+C para parar o backend.
echo.

REM Iniciar backend
python src/core/evolution/evolution_api.py

echo.
echo Backend parado.
pause
exit /b 0