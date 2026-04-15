#!/bin/bash

# Setup script para Evolution Dashboard
echo "🔧 Configurando Evolution Dashboard..."

# Verificar Node.js
if ! command -v node &> /dev/null; then
    echo "❌ Node.js não encontrado. Instale Node.js 18+ e tente novamente."
    exit 1
fi

NODE_VERSION=$(node -v | cut -d'v' -f2 | cut -d'.' -f1)
if [ "$NODE_VERSION" -lt 18 ]; then
    echo "❌ Node.js versão $NODE_VERSION encontrada. Necessário Node.js 18+."
    exit 1
fi

echo "✅ Node.js $(node -v) detectado"

# Verificar npm/yarn
if command -v yarn &> /dev/null; then
    PACKAGE_MANAGER="yarn"
elif command -v npm &> /dev/null; then
    PACKAGE_MANAGER="npm"
else
    echo "❌ Nenhum gerenciador de pacotes encontrado (npm ou yarn)."
    exit 1
fi

echo "✅ Gerenciador de pacotes: $PACKAGE_MANAGER"

# Instalar dependências
echo "📦 Instalando dependências..."
if [ "$PACKAGE_MANAGER" = "yarn" ]; then
    yarn install
else
    npm install
fi

if [ $? -ne 0 ]; then
    echo "❌ Falha ao instalar dependências."
    exit 1
fi

# Configurar arquivo .env
if [ ! -f .env.local ]; then
    echo "📄 Criando arquivo .env.local..."
    cp .env.local.example .env.local
    echo "✅ Arquivo .env.local criado. Verifique as configurações."
fi

# Verificar se a API está rodando
echo "🔗 Verificando conexão com a API..."
if command -v curl &> /dev/null; then
    if curl -s http://localhost:8000/health > /dev/null; then
        echo "✅ API Evolution detectada em http://localhost:8000"
    else
        echo "⚠️  API Evolution não respondendo em http://localhost:8000"
        echo "   Certifique-se de que o servidor da API está rodando."
    fi
else
    echo "⚠️  curl não disponível, pulando verificação da API."
fi

echo ""
echo "🎉 Setup completo!"
echo ""
echo "Para iniciar o dashboard:"
echo "  $PACKAGE_MANAGER run dev"
echo ""
echo "Acesse: http://localhost:3000"
echo ""
echo "Para build de produção:"
echo "  $PACKAGE_MANAGER run build"
echo "  $PACKAGE_MANAGER run start"
echo ""