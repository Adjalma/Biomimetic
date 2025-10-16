# ========================================
# Script para Iniciar Dashboard GIC
# ========================================

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Iniciando Dashboard GIC" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Ativar ambiente virtual Python 3.11
Write-Host "Ativando ambiente virtual..." -ForegroundColor Yellow
& ".\venv_py311\Scripts\Activate.ps1"

# Verificar se o ambiente foi ativado
if (-not $env:VIRTUAL_ENV) {
    Write-Host "ERRO: Ambiente virtual não foi ativado!" -ForegroundColor Red
    Write-Host "Verifique se o caminho está correto: .\venv_py311\Scripts\Activate.ps1" -ForegroundColor Red
    Read-Host "Pressione Enter para sair"
    exit 1
}

Write-Host "Ambiente virtual ativado: $env:VIRTUAL_ENV" -ForegroundColor Green
Write-Host ""

# Verificar se as dependências estão instaladas
Write-Host "Verificando dependências..." -ForegroundColor Yellow
try {
    python -c "import flask, flask_socketio" 2>$null
    Write-Host "Dependências já estão instaladas!" -ForegroundColor Green
} catch {
    Write-Host "Instalando dependências..." -ForegroundColor Yellow
    pip install -r requirements_dashboard.txt
    if ($LASTEXITCODE -ne 0) {
        Write-Host "ERRO: Falha ao instalar dependências!" -ForegroundColor Red
        Read-Host "Pressione Enter para sair"
        exit 1
    }
}

Write-Host ""
Write-Host "Dependências verificadas!" -ForegroundColor Green
Write-Host ""

# Iniciar dashboard
Write-Host "Iniciando Dashboard GIC..." -ForegroundColor Cyan
Write-Host ""
Write-Host "Acesse: http://localhost:5000" -ForegroundColor Green
Write-Host ""
Write-Host "Pressione Ctrl+C para parar" -ForegroundColor Yellow
Write-Host ""

python dashboard_ia_v2.py

Write-Host ""
Write-Host "Dashboard parado." -ForegroundColor Yellow
Read-Host "Pressione Enter para sair"
