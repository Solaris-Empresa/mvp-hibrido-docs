# Dockerfile para o Dashboard Administrativo IA SOLARIS
FROM node:20-alpine AS builder

# Definir diretório de trabalho
WORKDIR /app

# Copiar package files
COPY package*.json ./
COPY pnpm-lock.yaml ./

# Instalar pnpm
RUN npm install -g pnpm

# Instalar dependências
RUN pnpm install --frozen-lockfile

# Copiar código fonte
COPY . .

# Build da aplicação
RUN pnpm run build

# Estágio de produção
FROM nginx:alpine

# Instalar curl para health check
RUN apk add --no-cache curl

# Copiar arquivos buildados
COPY --from=builder /app/dist /usr/share/nginx/html

# Copiar configuração customizada do nginx
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Criar usuário não-root
RUN addgroup -g 1001 -S iasolaris && \
    adduser -S iasolaris -u 1001

# Ajustar permissões
RUN chown -R iasolaris:iasolaris /usr/share/nginx/html && \
    chown -R iasolaris:iasolaris /var/cache/nginx && \
    chown -R iasolaris:iasolaris /var/log/nginx && \
    chown -R iasolaris:iasolaris /etc/nginx/conf.d && \
    touch /var/run/nginx.pid && \
    chown -R iasolaris:iasolaris /var/run/nginx.pid

# Mudar para usuário não-root
USER iasolaris

# Expor porta
EXPOSE 3000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:3000/ || exit 1

# Comando padrão
CMD ["nginx", "-g", "daemon off;"]

