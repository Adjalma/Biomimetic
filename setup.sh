#!/bin/bash
# setup.sh - Script de instalação rápida do Sistema Biomimético

set -e

echo "🧬 INSTALANDO SISTEMA BIOMIMÉTICO"
echo "=================================="
echo

# Verificar Python
echo "🔍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado. Instale Python 3.11+ em: https://python.org"
    exit 1
fi

PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
echo "✅ Python $PYTHON_VERSION encontrado"

# Verificar se está na pasta correta
if [ ! -f "requirements.txt" ] && [ ! -d "src" ]; then
    echo "❌ Não parece estar na pasta do projeto Biomimetic"
    echo "   Execute: cd Biomimetic"
    exit 1
fi

# Criar ambiente virtual
echo
echo "🐍 Criando ambiente virtual..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    echo "✅ Ambiente virtual criado: venv/"
else
    echo "⚠️  Ambiente virtual já existe: venv/"
fi

# Ativar ambiente
echo
echo "🔧 Ativando ambiente virtual..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
    echo "✅ Ambiente ativado"
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
    echo "✅ Ambiente ativado (Windows)"
else
    echo "❌ Não foi possível ativar ambiente virtual"
    exit 1
fi

# Instalar dependências
echo
echo "📦 Instalando dependências..."
pip install --upgrade pip
echo

# Instalar com opções
echo "Escolha o tipo de instalação:"
echo "1) Completa (recomendado) - todas as dependências"
echo "2) Leve - apenas essenciais"
echo "3) Personalizada - escolher módulos"
read -p "Digite 1, 2 ou 3: " install_choice

case $install_choice in
    1)
        echo "Instalando todas as dependências..."
        if [ -f "requirements.txt" ]; then
            pip install -r requirements.txt
        else
            echo "❌ Arquivo requirements.txt não encontrado"
            exit 1
        fi
        ;;
    2)
        echo "Instalando dependências essenciais..."
        pip install fastapi==0.104.1 uvicorn[standard]==0.24.0 pydantic==2.5.0 numpy==1.24.3 requests==2.31.0
        echo "✅ Dependências essenciais instaladas"
        echo "   Outras dependências podem ser instaladas depois com:"
        echo "   pip install plotly shap lime boto3 torch transformers"
        ;;
    3)
        echo "Instalação personalizada..."
        echo "Módulos disponíveis:"
        echo "  fastapi, uvicorn, pydantic, numpy, requests"
        echo "  plotly, shap, lime, boto3, torch, transformers"
        read -p "Digite os módulos separados por espaço: " modules
        pip install $modules
        ;;
    *)
        echo "❌ Opção inválida"
        exit 1
        ;;
esac

# Testar instalação
echo
echo "🧪 Testando instalação..."
python3 -c "
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

# Criar teste rápido
echo
echo "📄 Criando script de teste rápido..."
cat > teste_instalacao.py << 'EOF'
#!/usr/bin/env python3
"""
Teste rápido da instalação do Sistema Biomimético
"""
import sys

print("🧬 TESTE DE INSTALAÇÃO DO SISTEMA BIOMIMÉTICO")
print("=" * 50)

# Verificar módulos essenciais
modules = ['fastapi', 'uvicorn', 'pydantic', 'numpy', 'requests']
for module in modules:
    try:
        __import__(module)
        print(f"✅ {module}")
    except ImportError:
        print(f"❌ {module} não instalado")

print()
print("🎯 PRÓXIMOS PASSOS:")
print("1. Execute: python teste_rapido.py")
print("2. Ou inicie a API: python src/core/evolution/evolution_api.py")
print("3. Acesse: http://localhost:8000/health")
EOF

chmod +x teste_instalacao.py
echo "✅ Script criado: teste_instalacao.py"

echo
echo "🎉 INSTALAÇÃO COMPLETA!"
echo "========================"
echo
echo "📋 COMANDOS DISPONÍVEIS:"
echo "   python teste_instalacao.py    - Verificar instalação"
echo "   python teste_rapido.py        - Testar sistema biomimético"
echo "   python iniciar_sistema.py main - Sistema principal"
echo "   python src/core/evolution/evolution_api.py - API evolutiva"
echo
echo "📚 DOCUMENTAÇÃO:"
echo "   Consulte INICIACAO_RAPIDA.md para guia rápido"
echo "   Consulte README.md para documentação completa"
echo
echo "🔧 SE HOUVER ERROS:"
echo "   - Execute: pip install -r requirements.txt --force-reinstall"
echo "   - Ou me envie a mensagem de erro"
echo
echo "Boa sorte com o sistema biomimético! 🚀"