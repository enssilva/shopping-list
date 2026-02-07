# frontend/Dockerfile

# Estágio Base (Comum para Dev e Prod)
FROM node:20-alpine AS base
WORKDIR /app

# 1. Copia dependências
COPY package*.json ./

# 2. Instala dependências
RUN npm install --legacy-peer-deps --ignore-scripts

# 3. CORREÇÃO: Adicione os binários locais ao PATH do sistema
ENV PATH="./node_modules/.bin:$PATH"

# 4. Copia o código fonte
COPY . .

# 5. Agora o comando 'quasar' será encontrado pelo PATH acima
RUN quasar prepare

# Estágio de Desenvolvimento
FROM base AS development
EXPOSE 9000
CMD ["quasar", "dev", "-m", "pwa", "--port", "9000", "--hostname", "0.0.0.0"]

# Estágio de Produção
FROM base AS build-stage
RUN quasar build -m pwa

FROM nginx:alpine AS production
COPY --from=build-stage /app/dist/pwa /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]