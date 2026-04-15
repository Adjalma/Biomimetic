# Script para corrigir Docker do AI-Biomimetica
# Execute como administrador no PowerShell

Write-Host "=== CORRIGINDO DOCKER DO AI-BIOMIMETICA ===" -ForegroundColor Cyan

# 1. Verificar diretório
if (-not (Test-Path "requirements_docker.txt")) {
    Write-Host "ERRO: Execute este script dentro de C:\AI-Server\AI-Biomimetica" -ForegroundColor Red
    exit 1
}

# 2. Criar requirements_docker.txt simplificado
Write-Host "Criando requirements_docker.txt simplificado..." -ForegroundColor Yellow
@"
fastapi>=0.104.0
uvicorn[standard]>=0.24.0
httpx>=0.25.0
python-dotenv>=1.0.0
pydantic>=2.5.0
sqlalchemy>=2.0.0
psycopg2-binary>=2.9.9
aiofiles>=23.2.1
python-multipart>=0.0.6
"@ | Set-Content -Path "requirements_docker.txt" -Encoding UTF8

# 3. Criar Dockerfile robusto
Write-Host "Criando Dockerfile robusto..." -ForegroundColor Yellow
@"
FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (cache de camadas)
COPY requirements_docker.txt .

# Instalar pip mais recente primeiro
RUN pip install --upgrade pip

# Instalar pacotes individualmente para melhor debug
RUN pip install --no-cache-dir \
    fastapi \
    uvicorn \
    httpx \
    python-dotenv \
    pydantic \
    sqlalchemy \
    psycopg2-binary \
    aiofiles \
    python-multipart

# Copiar o restante do código
COPY . .

# Expor porta da API
EXPOSE 8000

# Comando para rodar a API
CMD ["uvicorn", "src.app.bio_console_api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
"@ | Set-Content -Path "Dockerfile" -Encoding UTF8

# 4. Verificar arquivos
Write-Host "`nVerificando arquivos criados:" -ForegroundColor Green
Get-Content requirements_docker.txt
Write-Host "`n---`n" -ForegroundColor Gray
Get-Content Dockerfile | Select-Object -First 10
Write-Host "`n... (continua)" -ForegroundColor Gray

# 5. Voltar para diretório raiz e rebuild
Write-Host "`nVoltando para C:\AI-Server e rebuild..." -ForegroundColor Cyan
cd ..

# 6. Parar containers
Write-Host "Parando containers..." -ForegroundColor Yellow
docker-compose down 2>$null

# 7. Remover imagem antiga
Write-Host "Removendo imagem antiga..." -ForegroundColor Yellow
docker rmi ai-server-chokmah_api -f 2>$null

# 8. Rebuild com no-cache
Write-Host "Iniciando rebuild (isso pode levar alguns minutos)..." -ForegroundColor Cyan
docker-compose build --no-cache

# 9. Verificar resultado
if ($LASTEXITCODE -eq 0) {
    Write-Host "`n=== BUILD CONCLUÍDO COM SUCESSO! ===" -ForegroundColor Green
    Write-Host "Para iniciar os containers, execute:" -ForegroundColor Yellow
    Write-Host "docker-compose up -d" -ForegroundColor White
    Write-Host "`nPara verificar os containers:" -ForegroundColor Yellow
    Write-Host "docker ps" -ForegroundColor White
} else {
    Write-Host "`n=== BUILD FALHOU ===" -ForegroundColor Red
    Write-Host "Consulte os logs acima para identificar o erro." -ForegroundColor Yellow
}

Write-Host "`nScript concluído." -ForegroundColor Cyan