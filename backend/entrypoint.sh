#!/bin/sh

echo "Aguardando banco de dados..."

# 1. Cria as tabelas (processo único)
python -c "from app.db.base import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)"

# 2. Cria o usuário administrador padrão (processo único)
python -c "from app.main import create_admin_user; create_admin_user()"

echo "Banco de dados preparado. Iniciando Gunicorn com 4 workers..."

# 3. Inicia o Gunicorn
exec "$@"