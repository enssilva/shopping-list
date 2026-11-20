# Shopping List

Aplicação web (PWA) para gerenciamento de listas de compras, catálogo de produtos, comparação de preços entre mercados e leitura/geração de códigos de barras (EAN-13, EAN-8 e UPC).

## Arquitetura e Stack

- **Backend:** Python 3.11, FastAPI, SQLAlchemy (`psycopg`), PostgreSQL 15 (com busca sem acento via `unaccent`), autenticação JWT (`python-jose`, `passlib`/`bcrypt`).
- **Frontend:** Vue 3, Quasar v2 (PWA com Vite e Workbox), Pinia, Axios, `barcode-detector` (API nativa + fallback `zxing-wasm` empacotado localmente) e `jsbarcode`.
- **Proxy / Gateway:** Nginx (`nginx:alpine`) unificando frontend, API (`/api/v1`) e arquivos de mídia (`/media/`).
- **Infraestrutura:** Docker Compose (desenvolvimento e produção) e GitHub Actions com build multi-arquitetura (`linux/amd64` e `linux/arm64`) publicado no GHCR.

---

## Pré-requisitos

- Docker e Docker Compose (v2)
- *(Opcional, para testar no celular Android via USB)* `adb` (Android Debug Bridge)

---

## Configuração das variáveis de ambiente (`.env`)

Crie ou revise o arquivo `.env` na raiz do projeto com base no exemplo abaixo:

```env
# Segurança do Backend
SECRET_KEY=gere_com_openssl_rand_hex_32
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Banco de Dados PostgreSQL
DB_USER=admin
DB_PASSWORD=defina_uma_senha_forte
DB_NAME=grocery_db

# Opções de Produção (GHCR / Traefik)
GITHUB_USERNAME=seu_usuario_github
TAG_VERSION=v0.0.1
DOMAIN=shopping-list.exemplo.com
```

> **Dica:** para gerar uma `SECRET_KEY` segura, execute:
> ```bash
> openssl rand -hex 32
> ```

---

## Como executar em Desenvolvimento

O `docker-compose.yml` contém apenas a definição base dos serviços. Para desenvolvimento, **sempre combine-o com `docker-compose.dev.yml`**:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d
```

Se houver alteração de dependências (`requirements.txt` ou `package.json`), reconstrua as imagens com `--build`:

```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml up -d --build
```

### Endereços em Desenvolvimento
- **Aplicação (Frontend + API via Nginx):** `http://localhost:8080`
- **Documentação da API (Swagger):** `http://localhost:8080/docs`
- **ReDoc:** `http://localhost:8080/redoc`

### Credenciais iniciais
Na primeira inicialização do banco, o `backend/entrypoint.sh` cria automaticamente o usuário administrador padrão:
- **E-mail:** `admin@admin.com`
- **Senha:** `admin`

*(Recomenda-se alterar a senha após o primeiro acesso, especialmente em produção.)*

### Parar o ambiente de desenvolvimento
```bash
docker compose -f docker-compose.yml -f docker-compose.dev.yml down
```
*(Para apagar também os volumes de banco e mídia de desenvolvimento, adicione `-v`.)*

---

## Como executar em Produção

Os arquivos de produção utilizam as imagens pré-compiladas publicadas no GitHub Container Registry (`ghcr.io/${GITHUB_USERNAME}/shopping-list/...`).

### 1. Produção sem Traefik (portas `80` e `443` diretas)
```bash
docker compose -f docker-compose.prod.yml up -d
```
- **Aplicação:** `http://localhost` (API disponível em `/api/v1`; `/docs` não é exposto pelo `nginx/prod.conf`).

Para atualizar para as imagens mais recentes:
```bash
docker compose -f docker-compose.prod.yml pull
docker compose -f docker-compose.prod.yml up -d
```

Para parar:
```bash
docker compose -f docker-compose.prod.yml down
```

### 2. Produção com Traefik
Requer a rede Docker externa `traefik` já criada no servidor e as variáveis `TAG_VERSION`, `GITHUB_USERNAME` e o domínio configurados.

```bash
docker compose -f docker-compose.prod-traefik.yml up -d
```

*(Nota: em `docker-compose.prod-traefik.yml`, a label do Traefik referencia `${domain}` — certifique-se de manter a variável alinhada no ambiente de deploy.)*

---

## Como testar no celular via cabo USB (Android)

Os navegadores móveis exigem **HTTPS** ou **`localhost`** (*Secure Context*) para liberar a câmera ao vivo (`getUserMedia`). Usando o túnel reverso do `adb`, o celular acessa `http://localhost:8080` diretamente, liberando a câmera em desenvolvimento sem precisar configurar certificado SSL.

### 1. Preparar o celular (Android)
1. Acesse **Configurações → Sobre o telefone** e toque **7 vezes** em **Número da versão** (ou *Número da compilação*) para ativar o modo desenvolvedor.
2. Abra **Configurações → Sistema → Opções do desenvolvedor**.
3. Ative **Depuração USB** (*USB debugging*).
4. Conecte o celular ao computador via cabo USB e aceite o alerta **"Permitir depuração USB?"** na tela do aparelho.

### 2. Configurar o túnel no computador
Verifique se o aparelho foi reconhecido:
```bash
adb devices
```
*(O status deve aparecer como `device`. Se aparecer `unauthorized`, confirme a permissão na tela do celular.)*

Crie o encaminhamento reverso da porta `8080`:
```bash
adb reverse tcp:8080 tcp:8080
```

*(Alternativa visual pelo Chrome/Chromium no PC: acesse `chrome://inspect/#devices`, clique em **Port forwarding...**, adicione a porta `8080` apontando para `localhost:8080` e marque **Enable port forwarding**.)*

### 3. Acessar no celular
- Abra o navegador no celular e acesse: `http://localhost:8080`
- Para remover o túnel quando terminar:
  ```bash
  adb reverse --remove tcp:8080
  ```

### E no iPhone (iOS) ou acesso sem cabo?
- No iOS não há `adb`. Para testar a câmera ao vivo em desenvolvimento, exponha `http://localhost:8080` com um túnel HTTPS (por exemplo, `cloudflared tunnel --url http://localhost:8080`, `ngrok` ou Tailscale).
- Caso acesse em HTTP simples pelo IP da rede local (`http://<IP-DO-PC>:8080`), o login e a navegação funcionam normalmente (a API usa caminho relativo `/api/v1`), e o botão **Scan from Photo** continua disponível como alternativa à câmera ao vivo.

---

## Recursos do leitor e gerador de código de barras

- **Leitura ao vivo (`BarcodeScanner.vue`):** utiliza `window.BarcodeDetector` nativo quando suportado (ex.: Chrome no Android) com fallback automático para `zxing-wasm` (WebAssembly local, funcionando offline na PWA). Inclui troca de lente traseira, controle de lanterna (`torch`), atalhos de zoom (`1x`–`3x`), validação de dígito verificador (EAN-8, UPC-A, EAN-13) e confirmação de duas leituras consecutivas.
- **Leitura por foto (*Scan from Photo*):** utiliza a câmera nativa do celular (foco macro/HDR) para códigos pequenos ou embalagens com reflexo, tentando leitura normal e rotacionada em 90°.
- **Geração de código de barras (`BarcodeGenerator.vue`):** seleciona automaticamente `EAN13`, `EAN8` ou `UPC` (com fallback para `CODE128` caso o dígito verificador seja inválido), com fundo branco puro e *quiet zone* ampliada para facilitar a leitura por outros aplicativos.

---

## Dicas e comandos úteis

- **Cache de Service Worker (PWA) ao alternar dev/prod em `localhost`:** se o navegador carregar uma versão antiga do frontend após trocar de ambiente ou atualizar o build, abra o DevTools (`F12`) → **Application / Armazenamento** → **Service Workers** → **Unregister** (ou limpe os dados do site) e recarregue com `Ctrl + Shift + R`.
- **Ver logs dos containers (dev):**
  ```bash
  docker compose -f docker-compose.yml -f docker-compose.dev.yml logs -f
  ```
- **Rodar o ESLint do frontend (dev):**
  ```bash
  docker compose -f docker-compose.yml -f docker-compose.dev.yml exec frontend npm run lint
  ```
- **CI/CD (`.github/workflows/deploy.yml`):** pushes na branch `main` ou tags `v*` disparam automaticamente o build e push multi-arquitetura (`amd64` e `arm64`) das imagens `grocery-backend`, `grocery-frontend` e `grocery-gateway` no GHCR.
