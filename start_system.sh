#!/bin/bash
# start_system.sh - Iniciar Sistema Evolutivo Biomimético (Backend + Frontend) para Linux/Mac

set -e

echo "🚀 INICIANDO SISTEMA EVOLUTIVO BIOMIMÉTICO"
echo "============================================"
echo

# Função para verificar se o ambiente virtual está ativado
check_venv() {
    if [ -z "$VIRTUAL_ENV" ]; then
        echo "❌ Ambiente virtual não ativado."
        echo "   Execute: source venv/bin/activate"
        return 1
    fi
    return 0
}

# Função para iniciar backend
start_backend() {
    echo
    echo "🧬 Iniciando Backend (API Evolution)..."
    
    if ! check_venv; then
        return 1
    fi
    
    # Verificar se a API já está rodando
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "⚠️  Backend já está rodando em http://localhost:8000"
    else
        # Iniciar em background
        python src/core/evolution/evolution_api.py > backend.log 2>&1 &
        BACKEND_PID=$!
        echo $BACKEND_PID > backend.pid
        
        # Aguardar inicialização
        echo "⏳ Aguardando inicialização da API..."
        sleep 5
        
        if curl -s http://localhost:8000/health > /dev/null 2>&1; then
            echo "✅ Backend iniciado (PID: $BACKEND_PID)"
            echo "🌐 Acesse: http://localhost:8000"
            echo "📚 Documentação: http://localhost:8000/docs"
        else
            echo "❌ Falha ao iniciar backend. Verifique backend.log"
            return 1
        fi
    fi
}

# Função para iniciar frontend
start_frontend() {
    echo
    echo "🎨 Iniciando Frontend (Evolution Dashboard)..."
    
    if [ ! -d "frontend" ]; then
        echo "❌ Pasta frontend não encontrada."
        return 1
    fi
    
    cd frontend
    
    # Verificar se Node.js está instalado
    if ! command -v node > /dev/null 2>&1; then
        echo "❌ Node.js não encontrado. Instale Node.js 18+."
        cd ..
        return 1
    fi
    
    # Verificar se dependências estão instaladas
    if [ ! -d "node_modules" ]; then
        echo "📦 Instalando dependências do frontend..."
        if command -v yarn > /dev/null 2>&1; then
            yarn install
        else
            npm install
        fi
        
        if [ $? -ne 0 ]; then
            echo "❌ Falha ao instalar dependências do frontend."
            cd ..
            return 1
        fi
    fi
    
    # Verificar se já está rodando
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "⚠️  Frontend já está rodando em http://localhost:3000"
    else
        # Iniciar em background
        if command -v yarn > /dev/null 2>&1; then
            yarn dev > ../frontend.log 2>&1 &
        else
            npm run dev > ../frontend.log 2>&1 &
        fi
        FRONTEND_PID=$!
        echo $FRONTEND_PID > ../frontend.pid
        
        # Aguardar inicialização
        echo "⏳ Aguardando inicialização do dashboard..."
        sleep 8
        
        if curl -s http://localhost:3000 > /dev/null 2>&1; then
            echo "✅ Frontend iniciado (PID: $FRONTEND_PID)"
            echo "🌐 Acesse: http://localhost:3000"
        else
            echo "❌ Falha ao iniciar frontend. Verifique frontend.log"
            cd ..
            return 1
        fi
    fi
    
    cd ..
}

# Função para verificar status
check_status() {
    echo
    echo "🔍 Verificando status do sistema..."
    echo
    
    # Verificar backend
    echo "🧬 Backend (API Evolution):"
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "   ✅ Rodando em http://localhost:8000"
        curl -s http://localhost:8000/health | python3 -c "import json, sys; data=json.load(sys.stdin); print(f'   Status: {data[\"status\"]}'); print(f'   Uptime: {data[\"uptime_seconds\"]}s')" 2>/dev/null || echo "   Status: OK"
    else
        echo "   ❌ Não está respondendo"
    fi
    
    echo
    
    # Verificar frontend
    echo "🎨 Frontend (Dashboard):"
    if curl -s http://localhost:3000 > /dev/null 2>&1; then
        echo "   ✅ Rodando em http://localhost:3000"
    else
        echo "   ❌ Não está respondendo"
    fi
    
    echo
    
    # Verificar processos
    echo "📊 Processos:"
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid 2>/dev/null)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            echo "   ✅ Backend PID: $BACKEND_PID"
        else
            echo "   ❌ Backend PID $BACKEND_PID não encontrado"
        fi
    fi
    
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid 2>/dev/null)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            echo "   ✅ Frontend PID: $FRONTEND_PID"
        else
            echo "   ❌ Frontend PID $FRONTEND_PID não encontrado"
        fi
    fi
}

# Função para parar sistema
stop_system() {
    echo
    echo "🛑 Parando sistema..."
    
    if [ -f "backend.pid" ]; then
        BACKEND_PID=$(cat backend.pid 2>/dev/null)
        if ps -p $BACKEND_PID > /dev/null 2>&1; then
            kill $BACKEND_PID 2>/dev/null
            echo "✅ Backend parado (PID: $BACKEND_PID)"
        fi
        rm -f backend.pid
    fi
    
    if [ -f "frontend.pid" ]; then
        FRONTEND_PID=$(cat frontend.pid 2>/dev/null)
        if ps -p $FRONTEND_PID > /dev/null 2>&1; then
            kill $FRONTEND_PID 2>/dev/null
            echo "✅ Frontend parado (PID: $FRONTEND_PID)"
        fi
        rm -f frontend.pid
    fi
    
    echo "✅ Sistema parado."
}

# Menu principal
show_menu() {
    echo "Escolha o que iniciar:"
    echo "1) Apenas Backend (API Evolution)"
    echo "2) Apenas Frontend (Evolution Dashboard)"
    echo "3) Ambos (Recomendado)"
    echo "4) Verificar status do sistema"
    echo "5) Parar sistema"
    echo "6) Sair"
    echo
    read -p "Digite sua escolha (1-6): " choice
    
    case $choice in
        1)
            start_backend
            ;;
        2)
            start_frontend
            ;;
        3)
            start_backend
            if [ $? -eq 0 ]; then
                sleep 2
                start_frontend
            fi
            ;;
        4)
            check_status
            ;;
        5)
            stop_system
            ;;
        6)
            echo "👋 Saindo..."
            exit 0
            ;;
        *)
            echo "❌ Opção inválida"
            ;;
    esac
    
    echo
    read -p "Pressione Enter para continuar..."
    echo
    show_menu
}

# Verificar se estamos no diretório correto
if [ ! -d "src" ] && [ ! -f "requirements.txt" ]; then
    echo "❌ Não parece estar na pasta do projeto Biomimetic"
    echo "   Execute: cd Biomimetic"
    exit 1
fi

# Executar menu
show_menu