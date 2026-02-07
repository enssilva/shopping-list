# Estágio Base (Comum)
FROM node:20-alpine as base
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .

# Estágio de Desenvolvimento (alvo: development)
FROM base as development
EXPOSE 9000
CMD ["quasar", "dev", "-m", "pwa", "--port", "9000", "--hostname", "0.0.0.0"]

# Estágio de Produção (alvo: production)
FROM base as build-stage
RUN npx quasar build -m pwa

FROM nginx:alpine as production
COPY --from=build-stage /app/dist/pwa /usr/share/nginx/html
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]