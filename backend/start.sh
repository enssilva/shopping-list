#!/bin/bash

echo "Executando Migrações/Seeds..."
# Move para a raiz do container e executa o módulo app.seed
cd /app && python -m app.seed

echo "Iniciando Servidor FastAPI..."
# Retorna para /app se necessário ou chama o módulo completo
exec uvicorn app.main:app --host 0.0.0.0 --port 8000