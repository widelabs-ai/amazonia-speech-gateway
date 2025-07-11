# Use uma imagem oficial do Python como base
FROM python:3.12-slim

# Definir variáveis de ambiente
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Instalar Poetry
RUN pip install poetry

# Configurar Poetry para não criar ambiente virtual (já estamos no container)
ENV POETRY_NO_INTERACTION=1 \
    POETRY_VENV_IN_PROJECT=1 \
    POETRY_VIRTUALENVS_CREATE=false

# Definir diretório de trabalho
WORKDIR /app

# Copiar arquivos de configuração do Poetry
COPY pyproject.toml poetry.lock ./

# Instalar dependências do Python
RUN poetry install --only=main --no-root

# Copiar o código fonte
COPY . .

# Gerar os arquivos protobuf
RUN chmod +x grpc_server/generate_protos.sh && \
    ./grpc_server/generate_protos.sh

# Expor a porta do gRPC
EXPOSE 50051

# Definir usuário não-root para segurança
RUN useradd --create-home --shell /bin/bash app && \
    chown -R app:app /app
USER app

# Comando para executar a aplicação
CMD ["python", "-m", "grpc_server"]
