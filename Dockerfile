FROM python:3.11-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    curl \
    git \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements primeiro (cache de camadas)
COPY requirements_docker.txt .
RUN pip install --no-cache-dir -r requirements_docker.txt

# Copiar o restante do código
COPY . .

# Expor porta da API
EXPOSE 8000

# Comando para rodar a API
CMD ["uvicorn", "src.app.bio_console_api:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]