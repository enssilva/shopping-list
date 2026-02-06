FROM node:20-alpine

# Instala o CLI globalmente
RUN npm install -g @quasar/cli

WORKDIR /app

# 1. Copia arquivos de dependências
COPY package*.json ./

# 2. Instala as dependências pulando scripts automáticos (como o postinstall)
# Isso evita que o 'quasar prepare' rode antes de termos os arquivos do projeto.
RUN npm install --legacy-peer-deps --ignore-scripts

# 3. Agora copiamos o restante dos arquivos (quasar.config.js, etc)
COPY . .

# Garante que binários nativos funcionem no Linux Alpine [cite: 2, 3]
RUN npm rebuild

# 4. Agora que os arquivos existem, rodamos o prepare manualmente
RUN quasar prepare

ENV PATH /app/node_modules/.bin:$PATH

EXPOSE 9000

CMD ["quasar", "dev", "-m", "pwa", "--port", "9000", "--hostname", "0.0.0.0"]
# CMD ["quasar", "build", "-m", "pwa", "--port", "9000", "--hostname", "0.0.0.0"]