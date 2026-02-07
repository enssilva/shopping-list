#!/bin/sh

# Encerra o script se qualquer comando falhar
set -e

echo "Verificando conexão com o banco de dados..."

# 1. Script Python para Aguardar Conexão e Preparar o Banco (Extensions/Functions)
python << END
import sys
import time
from sqlalchemy import text
from app.db.session import engine

# Tenta conectar por 30 vezes (60 segundos)
max_retries = 30
for i in range(max_retries):
    try:
        with engine.connect() as conn:
            # A. Testa a conexão
            conn.execute(text("SELECT 1"))
            
            # B. Habilita a extensão unaccent (Necessária para busca sem acento)
            conn.execute(text("CREATE EXTENSION IF NOT EXISTS unaccent;"))
            
            # C. Cria a função imutável necessária para o índice do SQLAlchemy
            # O PostgreSQL exige que funções em índices sejam IMMUTABLE via código
            conn.execute(text("""
                CREATE OR REPLACE FUNCTION unaccent_immutable(text)
                RETURNS text AS \$\$
                    SELECT public.unaccent('public.unaccent', \$1);
                \$\$ LANGUAGE sql IMMUTABLE PARALLEL SAFE STRICT;
            """))
            
            conn.commit()
            
        print("Banco de dados conectado e funções configuradas com sucesso!")
        sys.exit(0)
    except Exception as e:
        print(f"Tentativa {i+1}/{max_retries} falhou: {e}")
        print("Banco indisponível. Tentando novamente em 2s...")
        time.sleep(2)

print("ERRO: Não foi possível conectar ou configurar o banco de dados.")
sys.exit(1)
END

echo "Banco pronto. Criando tabelas do sistema..."
# 2. Cria as tabelas (Agora vai funcionar pois a função unaccent_immutable já existe)
python -c "from app.db.base import Base; from app.db.session import engine; Base.metadata.create_all(bind=engine)"

echo "Gerenciando usuário administrador..."
# 3. Cria o usuário administrador padrão
python -c "from app.main import create_admin_user; create_admin_user()"

echo "Iniciando aplicação..."
# 4. Inicia o servidor
exec "$@"