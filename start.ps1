# start.ps1 - PowerShell script para iniciar o sistema Biomimetic

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "  BIOMIMETIC SYSTEM - POWER SHELL LAUNCHER" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan
Write-Host ""

# Verificar ambiente virtual
if (-not (Test-Path "venv\Scripts\activate.bat")) {
    Write-Host "ERRO: Ambiente virtual nao encontrado." -ForegroundColor Red
    Write-Host "Execute primeiro: .\install_essential.bat" -ForegroundColor Yellow
    pause
    exit 1
}

# Menu
Write-Host "Opcoes:" -ForegroundColor White
Write-Host "1) Iniciar Backend (API)" -ForegroundColor Gray
Write-Host "2) Iniciar Frontend (Dashboard)" -ForegroundColor Gray
Write-Host "3) Iniciar Ambos" -ForegroundColor Gray
Write-Host "4) Verificar status" -ForegroundColor Gray
Write-Host "5) Sair" -ForegroundColor Gray
Write-Host ""
$choice = Read-Host "Escolha (1-5)"

# Opcao 1: Backend
if ($choice -eq "1") {
    Write-Host ""
    Write-Host "Iniciando Backend..." -ForegroundColor Green
    
    # Ativar ambiente virtual
    & "venv\Scripts\activate.bat"
    
    # Iniciar backend em nova janela
    Start-Process cmd -ArgumentList "/k", "cd /d `"$PWD`" && call venv\Scripts\activate.bat && python src/core/evolution/evolution_api.py" -WindowStyle Normal -Title "API Evolution"
    
    Write-Host "Backend iniciado em nova janela." -ForegroundColor Green
    Write-Host "Acesse: http://localhost:8000" -ForegroundColor Cyan
    Write-Host "Documentacao: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    pause
    exit 0
}

# Opcao 2: Frontend
if ($choice -eq "2") {
    Write-Host ""
    Write-Host "Iniciando Frontend..." -ForegroundColor Green
    
    if (-not (Test-Path "frontend\")) {
        Write-Host "ERRO: Pasta frontend nao encontrada." -ForegroundColor Red
        pause
        exit 1
    }
    
    Set-Location "frontend"
    
    if (Test-Path "setup_frontend.bat") {
        & ".\setup_frontend.bat"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "AVISO: Setup do frontend pode ter falhado." -ForegroundColor Yellow
        }
    }
    
    Write-Host "Iniciando servidor de desenvolvimento..." -ForegroundColor Green
    Start-Process cmd -ArgumentList "/k", "cd /d `"$PWD`" && npm run dev" -WindowStyle Normal -Title "Evolution Dashboard"
    
    Write-Host "Frontend iniciado em nova janela." -ForegroundColor Green
    Write-Host "Acesse: http://localhost:3000" -ForegroundColor Cyan
    Write-Host ""
    Set-Location ".."
    pause
    exit 0
}

# Opcao 3: Ambos
if ($choice -eq "3") {
    Write-Host ""
    Write-Host "Iniciando Backend e Frontend..." -ForegroundColor Green
    
    # Backend
    Write-Host "[1/2] Iniciando Backend..." -ForegroundColor Gray
    & "venv\Scripts\activate.bat"
    Start-Process cmd -ArgumentList "/k", "cd /d `"$PWD`" && call venv\Scripts\activate.bat && python src/core/evolution/evolution_api.py" -WindowStyle Normal -Title "API Evolution"
    Write-Host "Backend iniciado." -ForegroundColor Green
    
    # Esperar
    Write-Host "Aguardando 5 segundos..." -ForegroundColor Gray
    Start-Sleep -Seconds 5
    
    # Frontend
    Write-Host "[2/2] Iniciando Frontend..." -ForegroundColor Gray
    if (Test-Path "frontend\") {
        Set-Location "frontend"
        if (Test-Path "setup_frontend.bat") {
            & ".\setup_frontend.bat" | Out-Null
        }
        if ($LASTEXITCODE -eq 0) {
            Start-Process cmd -ArgumentList "/k", "cd /d `"$PWD`" && npm run dev" -WindowStyle Normal -Title "Evolution Dashboard"
            Write-Host "Frontend iniciado." -ForegroundColor Green
        } else {
            Write-Host "AVISO: Frontend nao iniciado." -ForegroundColor Yellow
        }
        Set-Location ".."
    } else {
        Write-Host "AVISO: Pasta frontend nao encontrada." -ForegroundColor Yellow
    }
    
    Write-Host ""
    Write-Host "Sistema iniciado com sucesso!" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "URLs:" -ForegroundColor White
    Write-Host "  Backend:  http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  Frontend: http://localhost:3000" -ForegroundColor Cyan
    Write-Host "  Docs API: http://localhost:8000/docs" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Mantenha as janelas abertas." -ForegroundColor Yellow
    Write-Host ""
    pause
    exit 0
}

# Opcao 4: Status
if ($choice -eq "4") {
    Write-Host ""
    Write-Host "Verificando status do sistema..." -ForegroundColor Green
    Write-Host ""
    
    # Verificar backend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:8000/health" -TimeoutSec 2 -ErrorAction Stop
        Write-Host "✅ BACKEND: RODANDO (http://localhost:8000)" -ForegroundColor Green
        Write-Host "   Resposta: $($response.Content)" -ForegroundColor Gray
    } catch {
        Write-Host "❌ BACKEND: NAO RESPONDE" -ForegroundColor Red
    }
    
    Write-Host ""
    
    # Verificar frontend
    try {
        $response = Invoke-WebRequest -Uri "http://localhost:3000" -TimeoutSec 2 -ErrorAction Stop
        Write-Host "✅ FRONTEND: RODANDO (http://localhost:3000)" -ForegroundColor Green
    } catch {
        Write-Host "❌ FRONTEND: NAO RESPONDE" -ForegroundColor Red
    }
    
    Write-Host ""
    pause
    exit 0
}

# Opcao 5: Sair
if ($choice -eq "5") {
    exit 0
}

Write-Host "Opcao invalida." -ForegroundColor Red
pause
exit 1