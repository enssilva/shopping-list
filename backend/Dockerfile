# Usa uma imagem leve do Python 3.11
FROM python:3.11-slim

# Define o diretório de trabalho dentro do container
WORKDIR /app

# Variáveis de ambiente para o Python (não gerar arquivos .pyc e logs imediatos)
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Instala dependências do sistema (necessário para compilar certas libs)
RUN apt-get update && apt-get install -y \
    gcc \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copia o arquivo de requisitos primeiro (para aproveitar o cache do Docker)
COPY requirements.txt .

# Instala as dependências do Python
RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código para dentro do container
COPY . .

# Dá permissão ao script de entrada
RUN chmod +x /app/entrypoint.sh

# Define o entrypoint
ENTRYPOINT ["/app/entrypoint.sh"]

EXPOSE 8000