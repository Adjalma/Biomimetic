#!/bin/bash
# Script de auto-push simplificado para GitHub
# Uso: ./scripts/git_push.sh [mensagem]

set -e

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$REPO_DIR"

echo "🔍 Verificando repositório git..."
if [ ! -d ".git" ]; then
    echo "❌ Não é um repositório git"
    exit 1
fi

echo "📊 Obtendo status..."
git status --short

echo "🚀 Executando auto-push..."
python3 scripts/git_auto_push.py "$@"

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ Push realizado com sucesso!"
    
    # Mostrar último commit
    echo ""
    echo "📋 Último commit:"
    git log --oneline -1
else
    echo "❌ Falha no auto-push"
    exit 1
fi