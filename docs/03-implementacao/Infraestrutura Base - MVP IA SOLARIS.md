# Infraestrutura Base - MVP IA SOLARIS

## Visão Geral da Arquitetura

Este documento detalha a infraestrutura base necessária para o MVP híbrido de controle de tokens da IA SOLARIS. A arquitetura foi projetada para ser escalável, resiliente e facilmente mantível, utilizando containers Docker e orquestração via Docker Compose para simplificar o deployment e operação.

## Arquitetura de Componentes

### Diagrama de Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LibreChat     │    │  Admin Users    │    │   Monitoring    │
│   (Cliente)     │    │   (Browser)     │    │    Tools        │
└─────────┬───────┘    └─────────┬───────┘    └─────────┬───────┘
          │                      │                      │
          │ HTTP/HTTPS           │ HTTP/HTTPS           │ HTTP
          │                      │                      │
┌─────────▼──────────────────────▼──────────────────────▼───────┐
│                     Nginx Reverse Proxy                       │
│                    (Load Balancer + SSL)                      │
└─────────┬─────────────────────┬─────────────────────┬─────────┘
          │                     │                     │
          │ /v1/*              │ /admin/*            │ /metrics
          │                     │                     │
┌─────────▼───────┐    ┌────────▼────────┐    ┌──────▼──────┐
│ Proxy           │    │ Admin Dashboard │    │ Monitoring  │
│ Inteligente     │    │    (React)      │    │   Stack     │
│  (Flask)        │    │                 │    │             │
└─────────┬───────┘    └─────────────────┘    └─────────────┘
          │
          │ HTTP
          │
┌─────────▼───────┐
│    LiteLLM      │
│   (Proxy AI)    │
└─────────┬───────┘
          │
          │ HTTPS
          │
┌─────────▼───────┐
│  Provedores IA  │
│ (OpenAI, etc.)  │
└─────────────────┘

┌─────────────────┐    ┌─────────────────┐
│   PostgreSQL    │    │     Redis       │
│  (Database)     │    │    (Cache)      │
└─────────────────┘    └─────────────────┘
```

### Componentes Principais

**1. Nginx Reverse Proxy**
- **Função:** Load balancer, SSL termination, rate limiting
- **Porta:** 80 (HTTP), 443 (HTTPS)
- **Responsabilidades:**
  - Roteamento de requisições
  - Terminação SSL/TLS
  - Rate limiting e proteção DDoS
  - Compressão gzip
  - Logs de acesso

**2. Proxy Inteligente (Flask)**
- **Função:** Controle de tokens e interceptação de requisições
- **Porta:** 5000
- **Responsabilidades:**
  - Interceptação de requisições da IA
  - Controle de consumo de tokens
  - Sistema de alertas automáticos
  - Logging e auditoria
  - Integração com sistema de pagamentos

**3. Admin Dashboard (React)**
- **Função:** Interface administrativa
- **Porta:** 3000
- **Responsabilidades:**
  - Gestão de usuários
  - Monitoramento de consumo
  - Relatórios e analytics
  - Configurações do sistema

**4. LiteLLM**
- **Função:** Proxy unificado para múltiplos provedores de IA
- **Porta:** 4000
- **Responsabilidades:**
  - Abstração de APIs de IA
  - Load balancing entre provedores
  - Fallback automático
  - Normalização de respostas

**5. PostgreSQL**
- **Função:** Banco de dados principal
- **Porta:** 5432
- **Responsabilidades:**
  - Armazenamento de dados de usuários
  - Histórico de consumo de tokens
  - Logs de transações
  - Configurações do sistema

**6. Redis**
- **Função:** Cache e sessões
- **Porta:** 6379
- **Responsabilidades:**
  - Cache de consultas frequentes
  - Armazenamento de sessões
  - Rate limiting distribuído
  - Pub/Sub para notificações

## Configuração Docker Compose

### Arquivo Principal (docker-compose.yml)

```yaml
version: '3.8'

services:
  # ===== BANCO DE DADOS =====
  postgres:
    image: postgres:15-alpine
    container_name: ia-solaris-postgres
    restart: unless-stopped
    environment:
      POSTGRES_DB: ${DB_NAME:-ia_solaris}
      POSTGRES_USER: ${DB_USER:-postgres}
      POSTGRES_PASSWORD: ${DB_PASSWORD}
      POSTGRES_INITDB_ARGS: "--encoding=UTF-8 --lc-collate=C --lc-ctype=C"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init-scripts:/docker-entrypoint-initdb.d:ro
      - ./database/postgresql.conf:/etc/postgresql/postgresql.conf:ro
    ports:
      - "${DB_PORT:-5432}:5432"
    networks:
      - ia-solaris-network
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U ${DB_USER:-postgres} -d ${DB_NAME:-ia_solaris}"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # ===== CACHE REDIS =====
  redis:
    image: redis:7-alpine
    container_name: ia-solaris-redis
    restart: unless-stopped
    command: >
      redis-server 
      --requirepass ${REDIS_PASSWORD}
      --appendonly yes
      --appendfsync everysec
      --maxmemory 512mb
      --maxmemory-policy allkeys-lru
    volumes:
      - redis_data:/data
      - ./database/redis.conf:/usr/local/etc/redis/redis.conf:ro
    ports:
      - "${REDIS_PORT:-6379}:6379"
    networks:
      - ia-solaris-network
    healthcheck:
      test: ["CMD", "redis-cli", "--no-auth-warning", "-a", "${REDIS_PASSWORD}", "ping"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 10s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # ===== LITELLM PROXY =====
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    container_name: ia-solaris-litellm
    restart: unless-stopped
    environment:
      # Chaves de API
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY:-}
      GOOGLE_API_KEY: ${GOOGLE_API_KEY:-}
      
      # Configurações do banco
      DATABASE_URL: postgresql://${DB_USER:-postgres}:${DB_PASSWORD}@postgres:5432/${DB_NAME:-ia_solaris}
      
      # Configurações de performance
      LITELLM_LOG: INFO
      LITELLM_REQUEST_TIMEOUT: 600
      LITELLM_NUM_RETRIES: 3
      
      # Configurações de segurança
      LITELLM_MASTER_KEY: ${LITELLM_MASTER_KEY:-}
      LITELLM_SALT_KEY: ${LITELLM_SALT_KEY:-}
    volumes:
      - ./database/litellm-config.yaml:/app/config.yaml:ro
      - litellm_logs:/app/logs
    ports:
      - "4000:4000"
    networks:
      - ia-solaris-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:4000/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    command: [
      "--config", "/app/config.yaml",
      "--port", "4000",
      "--num_workers", "4",
      "--host", "0.0.0.0"
    ]
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # ===== PROXY INTELIGENTE =====
  proxy-inteligente:
    build:
      context: ./proxy-inteligente/proxy-ia-solaris
      dockerfile: Dockerfile
      args:
        PYTHON_VERSION: 3.11
    container_name: ia-solaris-proxy
    restart: unless-stopped
    environment:
      # Configurações da aplicação
      DEBUG: ${DEBUG:-false}
      SECRET_KEY: ${SECRET_KEY}
      HOST: 0.0.0.0
      PORT: 5000
      
      # Banco de dados
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: ${DB_NAME:-ia_solaris}
      DB_USER: ${DB_USER:-postgres}
      DB_PASSWORD: ${DB_PASSWORD}
      
      # Redis
      REDIS_HOST: redis
      REDIS_PORT: 6379
      REDIS_DB: ${REDIS_DB:-0}
      REDIS_PASSWORD: ${REDIS_PASSWORD}
      
      # Integrações
      LITELLM_BASE_URL: http://litellm:4000
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      
      # Email
      SMTP_HOST: ${SMTP_HOST}
      SMTP_PORT: ${SMTP_PORT:-587}
      SMTP_USER: ${SMTP_USER}
      SMTP_PASSWORD: ${SMTP_PASSWORD}
      FROM_EMAIL: ${FROM_EMAIL}
      SMTP_TLS: ${SMTP_TLS:-true}
      
      # Configurações de tokens
      DEFAULT_MONTHLY_LIMIT: ${DEFAULT_MONTHLY_LIMIT:-1000000}
      ALERT_THRESHOLD: ${ALERT_THRESHOLD:-0.8}
      BLOCK_THRESHOLD: ${BLOCK_THRESHOLD:-1.0}
      MAX_USER_LIMIT: ${MAX_USER_LIMIT:-10000000}
      MIN_USER_LIMIT: ${MIN_USER_LIMIT:-100000}
      
      # Logs
      LOG_LEVEL: ${LOG_LEVEL:-INFO}
    volumes:
      - proxy_logs:/app/logs
      - ./proxy-inteligente/proxy-ia-solaris/src:/app/src:ro
    ports:
      - "5000:5000"
    networks:
      - ia-solaris-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      litellm:
        condition: service_healthy
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 60s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # ===== ADMIN DASHBOARD =====
  admin-dashboard:
    build:
      context: ./admin-dashboard/admin-ia-solaris
      dockerfile: Dockerfile
      args:
        NODE_VERSION: 18
        REACT_APP_API_BASE_URL: ${REACT_APP_API_BASE_URL:-http://localhost:5000/api}
        REACT_APP_WS_URL: ${REACT_APP_WS_URL:-ws://localhost:5000}
    container_name: ia-solaris-admin
    restart: unless-stopped
    environment:
      NODE_ENV: production
    volumes:
      - ./admin-dashboard/admin-ia-solaris/nginx.conf:/etc/nginx/nginx.conf:ro
    ports:
      - "3000:80"
    networks:
      - ia-solaris-network
    depends_on:
      - proxy-inteligente
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 5
      start_period: 30s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # ===== NGINX REVERSE PROXY =====
  nginx:
    image: nginx:alpine
    container_name: ia-solaris-nginx
    restart: unless-stopped
    volumes:
      - ./database/nginx.conf:/etc/nginx/nginx.conf:ro
      - ./ssl:/etc/nginx/ssl:ro
      - nginx_logs:/var/log/nginx
    ports:
      - "80:80"
      - "443:443"
    networks:
      - ia-solaris-network
    depends_on:
      - proxy-inteligente
      - admin-dashboard
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:80/health"]
      interval: 30s
      timeout: 10s
      retries: 3
      start_period: 10s
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"

  # ===== MONITORAMENTO =====
  prometheus:
    image: prom/prometheus:latest
    container_name: ia-solaris-prometheus
    restart: unless-stopped
    volumes:
      - ./monitoring/prometheus.yml:/etc/prometheus/prometheus.yml:ro
      - prometheus_data:/prometheus
    ports:
      - "9090:9090"
    networks:
      - ia-solaris-network
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/etc/prometheus/console_libraries'
      - '--web.console.templates=/etc/prometheus/consoles'
      - '--storage.tsdb.retention.time=200h'
      - '--web.enable-lifecycle'

  grafana:
    image: grafana/grafana:latest
    container_name: ia-solaris-grafana
    restart: unless-stopped
    environment:
      GF_SECURITY_ADMIN_PASSWORD: ${GRAFANA_PASSWORD:-admin}
      GF_USERS_ALLOW_SIGN_UP: false
    volumes:
      - grafana_data:/var/lib/grafana
      - ./monitoring/grafana/dashboards:/etc/grafana/provisioning/dashboards:ro
      - ./monitoring/grafana/datasources:/etc/grafana/provisioning/datasources:ro
    ports:
      - "3001:3000"
    networks:
      - ia-solaris-network
    depends_on:
      - prometheus

# ===== VOLUMES =====
volumes:
  postgres_data:
    driver: local
  redis_data:
    driver: local
  litellm_logs:
    driver: local
  proxy_logs:
    driver: local
  nginx_logs:
    driver: local
  prometheus_data:
    driver: local
  grafana_data:
    driver: local

# ===== NETWORKS =====
networks:
  ia-solaris-network:
    driver: bridge
    ipam:
      config:
        - subnet: 172.20.0.0/16
```

## Configurações de Banco de Dados

### PostgreSQL

**Arquivo: database/postgresql.conf**
```ini
# Configurações de performance
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 64MB
checkpoint_completion_target = 0.9
wal_buffers = 16MB
default_statistics_target = 100
random_page_cost = 1.1
effective_io_concurrency = 200

# Configurações de logging
log_destination = 'stderr'
logging_collector = on
log_directory = 'pg_log'
log_filename = 'postgresql-%Y-%m-%d_%H%M%S.log'
log_rotation_age = 1d
log_rotation_size = 100MB
log_min_duration_statement = 1000
log_line_prefix = '%t [%p]: [%l-1] user=%u,db=%d,app=%a,client=%h '
log_checkpoints = on
log_connections = on
log_disconnections = on
log_lock_waits = on

# Configurações de segurança
ssl = on
ssl_cert_file = 'server.crt'
ssl_key_file = 'server.key'
password_encryption = scram-sha-256

# Configurações de conexão
max_connections = 200
listen_addresses = '*'
port = 5432
```

**Script de inicialização: database/init-scripts/01-init-database.sql**
```sql
-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_stat_statements";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Criar usuário para aplicação (se não existir)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ia_solaris_app') THEN
        CREATE ROLE ia_solaris_app WITH LOGIN PASSWORD 'app_password_here';
    END IF;
END
$$;

-- Conceder permissões
GRANT CONNECT ON DATABASE ia_solaris TO ia_solaris_app;
GRANT USAGE ON SCHEMA public TO ia_solaris_app;
GRANT CREATE ON SCHEMA public TO ia_solaris_app;

-- Configurar timezone
SET timezone = 'UTC';

-- Criar índices para performance
-- (Serão criados automaticamente pelo SQLAlchemy)

-- Configurar autovacuum
ALTER SYSTEM SET autovacuum = on;
ALTER SYSTEM SET autovacuum_max_workers = 3;
ALTER SYSTEM SET autovacuum_naptime = '1min';

-- Recarregar configuração
SELECT pg_reload_conf();
```

### Redis

**Arquivo: database/redis.conf**
```ini
# Configurações básicas
bind 0.0.0.0
port 6379
timeout 300
tcp-keepalive 300

# Configurações de memória
maxmemory 512mb
maxmemory-policy allkeys-lru
maxmemory-samples 5

# Configurações de persistência
save 900 1
save 300 10
save 60 10000
stop-writes-on-bgsave-error yes
rdbcompression yes
rdbchecksum yes
dbfilename dump.rdb
dir /data

# Configurações de AOF
appendonly yes
appendfilename "appendonly.aof"
appendfsync everysec
no-appendfsync-on-rewrite no
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Configurações de logging
loglevel notice
logfile /data/redis.log
syslog-enabled no

# Configurações de segurança
protected-mode yes
# requirepass será definido via variável de ambiente

# Configurações de performance
tcp-backlog 511
databases 16
lua-time-limit 5000
slowlog-log-slower-than 10000
slowlog-max-len 128
```

## Configuração do Nginx

### Arquivo Principal: database/nginx.conf

```nginx
user nginx;
worker_processes auto;
error_log /var/log/nginx/error.log warn;
pid /var/run/nginx.pid;

events {
    worker_connections 1024;
    use epoll;
    multi_accept on;
}

http {
    include /etc/nginx/mime.types;
    default_type application/octet-stream;

    # Configurações de logging
    log_format main '$remote_addr - $remote_user [$time_local] "$request" '
                    '$status $body_bytes_sent "$http_referer" '
                    '"$http_user_agent" "$http_x_forwarded_for" '
                    'rt=$request_time uct="$upstream_connect_time" '
                    'uht="$upstream_header_time" urt="$upstream_response_time"';

    access_log /var/log/nginx/access.log main;

    # Configurações de performance
    sendfile on;
    tcp_nopush on;
    tcp_nodelay on;
    keepalive_timeout 65;
    types_hash_max_size 2048;
    client_max_body_size 10M;

    # Configurações de compressão
    gzip on;
    gzip_vary on;
    gzip_min_length 1024;
    gzip_proxied any;
    gzip_comp_level 6;
    gzip_types
        text/plain
        text/css
        text/xml
        text/javascript
        application/json
        application/javascript
        application/xml+rss
        application/atom+xml
        image/svg+xml;

    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=admin:10m rate=5r/s;
    limit_req_zone $binary_remote_addr zone=auth:10m rate=1r/s;

    # Upstream definitions
    upstream proxy_backend {
        server proxy-inteligente:5000 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }
    
    upstream admin_backend {
        server admin-dashboard:80 max_fails=3 fail_timeout=30s;
        keepalive 32;
    }

    # Security headers
    add_header X-Frame-Options DENY always;
    add_header X-Content-Type-Options nosniff always;
    add_header X-XSS-Protection "1; mode=block" always;
    add_header Referrer-Policy "strict-origin-when-cross-origin" always;
    add_header Content-Security-Policy "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data: https:; font-src 'self' data:; connect-src 'self' ws: wss:;" always;

    # HTTP Server (redirect to HTTPS in production)
    server {
        listen 80;
        server_name _;
        
        # Health check endpoint
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }

        # API Routes (LibreChat integration)
        location /v1/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://proxy_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection 'upgrade';
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            proxy_cache_bypass $http_upgrade;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # Buffer settings
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
            proxy_busy_buffers_size 8k;
        }

        # Admin API Routes
        location /api/ {
            limit_req zone=admin burst=10 nodelay;
            
            proxy_pass http://proxy_backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # CORS headers for admin dashboard
            add_header Access-Control-Allow-Origin "http://localhost:3000" always;
            add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS" always;
            add_header Access-Control-Allow-Headers "Authorization, Content-Type, X-Requested-With" always;
            add_header Access-Control-Allow-Credentials true always;
            
            if ($request_method = 'OPTIONS') {
                return 204;
            }
        }

        # Authentication routes (stricter rate limiting)
        location /api/auth/ {
            limit_req zone=auth burst=5 nodelay;
            
            proxy_pass http://proxy_backend;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }

        # Admin Dashboard
        location /admin/ {
            limit_req zone=admin burst=10 nodelay;
            
            proxy_pass http://admin_backend/;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Handle SPA routing
            try_files $uri $uri/ /index.html;
        }

        # Metrics endpoint (for monitoring)
        location /metrics {
            allow 127.0.0.1;
            allow 172.20.0.0/16;  # Docker network
            deny all;
            
            proxy_pass http://proxy_backend/metrics;
            proxy_set_header Host $host;
        }

        # Block access to sensitive files
        location ~ /\. {
            deny all;
            access_log off;
            log_not_found off;
        }
        
        location ~ \.(env|config|ini)$ {
            deny all;
            access_log off;
            log_not_found off;
        }
    }

    # HTTPS Server (for production)
    server {
        listen 443 ssl http2;
        server_name _;
        
        # SSL Configuration
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache shared:SSL:10m;
        ssl_session_timeout 10m;
        
        # HSTS
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
        
        # Same location blocks as HTTP server
        # ... (repeat all location blocks from HTTP server)
    }
}
```

## Configuração do LiteLLM

### Arquivo: database/litellm-config.yaml

```yaml
model_list:
  # OpenAI Models
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY
      max_tokens: 4096
      temperature: 0.7
      
  - model_name: gpt-4-turbo
    litellm_params:
      model: openai/gpt-4-turbo-preview
      api_key: os.environ/OPENAI_API_KEY
      max_tokens: 4096
      temperature: 0.7
      
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: openai/gpt-3.5-turbo
      api_key: os.environ/OPENAI_API_KEY
      max_tokens: 4096
      temperature: 0.7

  # Anthropic Models (if available)
  - model_name: claude-3-opus
    litellm_params:
      model: anthropic/claude-3-opus-20240229
      api_key: os.environ/ANTHROPIC_API_KEY
      max_tokens: 4096
      temperature: 0.7
    model_info:
      mode: chat
      supports_function_calling: true

  - model_name: claude-3-sonnet
    litellm_params:
      model: anthropic/claude-3-sonnet-20240229
      api_key: os.environ/ANTHROPIC_API_KEY
      max_tokens: 4096
      temperature: 0.7

# Router settings
router_settings:
  routing_strategy: simple-shuffle
  model_group_alias:
    gpt-4-group:
      - gpt-4
      - gpt-4-turbo
    claude-group:
      - claude-3-opus
      - claude-3-sonnet
  
  # Fallback configuration
  fallbacks:
    - gpt-4: ["gpt-4-turbo", "gpt-3.5-turbo"]
    - claude-3-opus: ["claude-3-sonnet", "gpt-4"]
  
  # Rate limiting
  rpm: 500  # requests per minute
  tpm: 100000  # tokens per minute
  
  # Retry configuration
  num_retries: 3
  request_timeout: 600
  
  # Load balancing
  cooldown_time: 1  # seconds

# Logging configuration
litellm_settings:
  # Logging
  set_verbose: true
  json_logs: true
  log_level: INFO
  
  # Database logging
  database_url: os.environ/DATABASE_URL
  database_type: postgresql
  
  # Success/failure callbacks
  success_callback: ["langfuse", "prometheus"]
  failure_callback: ["langfuse", "prometheus"]
  
  # Cost tracking
  track_cost_per_model: true
  
  # Security
  master_key: os.environ/LITELLM_MASTER_KEY
  
  # Performance
  redis_host: redis
  redis_port: 6379
  redis_password: os.environ/REDIS_PASSWORD

# General settings
general_settings:
  completion_model: gpt-3.5-turbo
  disable_spend_logs: false
  disable_master_key_return: true
  enforce_user_param: false
  
  # Custom headers
  headers:
    X-LiteLLM-Version: "1.0.0"
    X-Service-Name: "IA-SOLARIS"

# Environment variables
environment_variables:
  OPENAI_API_KEY: os.environ/OPENAI_API_KEY
  ANTHROPIC_API_KEY: os.environ/ANTHROPIC_API_KEY
  DATABASE_URL: os.environ/DATABASE_URL
  REDIS_HOST: redis
  REDIS_PORT: 6379
  REDIS_PASSWORD: os.environ/REDIS_PASSWORD
```

## Monitoramento e Observabilidade

### Prometheus Configuration

**Arquivo: monitoring/prometheus.yml**
```yaml
global:
  scrape_interval: 15s
  evaluation_interval: 15s

rule_files:
  - "rules/*.yml"

scrape_configs:
  # Prometheus itself
  - job_name: 'prometheus'
    static_configs:
      - targets: ['localhost:9090']

  # IA SOLARIS Proxy
  - job_name: 'ia-solaris-proxy'
    static_configs:
      - targets: ['proxy-inteligente:5000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  # LiteLLM
  - job_name: 'litellm'
    static_configs:
      - targets: ['litellm:4000']
    metrics_path: '/metrics'
    scrape_interval: 30s

  # PostgreSQL
  - job_name: 'postgres'
    static_configs:
      - targets: ['postgres:5432']
    scrape_interval: 60s

  # Redis
  - job_name: 'redis'
    static_configs:
      - targets: ['redis:6379']
    scrape_interval: 60s

  # Nginx
  - job_name: 'nginx'
    static_configs:
      - targets: ['nginx:80']
    metrics_path: '/metrics'
    scrape_interval: 30s

alerting:
  alertmanagers:
    - static_configs:
        - targets:
          - alertmanager:9093

# Storage configuration
storage:
  tsdb:
    retention.time: 30d
    retention.size: 10GB
```

### Grafana Dashboards

**Arquivo: monitoring/grafana/dashboards/ia-solaris-overview.json**
```json
{
  "dashboard": {
    "id": null,
    "title": "IA SOLARIS - Overview",
    "tags": ["ia-solaris", "overview"],
    "timezone": "browser",
    "panels": [
      {
        "id": 1,
        "title": "Total Requests",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(rate(http_requests_total[5m]))",
            "legendFormat": "Requests/sec"
          }
        ],
        "gridPos": {"h": 8, "w": 6, "x": 0, "y": 0}
      },
      {
        "id": 2,
        "title": "Active Users",
        "type": "stat",
        "targets": [
          {
            "expr": "ia_solaris_active_users",
            "legendFormat": "Active Users"
          }
        ],
        "gridPos": {"h": 8, "w": 6, "x": 6, "y": 0}
      },
      {
        "id": 3,
        "title": "Tokens Consumed",
        "type": "stat",
        "targets": [
          {
            "expr": "sum(ia_solaris_tokens_consumed_total)",
            "legendFormat": "Total Tokens"
          }
        ],
        "gridPos": {"h": 8, "w": 6, "x": 12, "y": 0}
      },
      {
        "id": 4,
        "title": "System Health",
        "type": "stat",
        "targets": [
          {
            "expr": "up",
            "legendFormat": "{{instance}}"
          }
        ],
        "gridPos": {"h": 8, "w": 6, "x": 18, "y": 0}
      }
    ],
    "time": {
      "from": "now-1h",
      "to": "now"
    },
    "refresh": "30s"
  }
}
```

## Scripts de Gerenciamento

### Script de Backup

```bash
#!/bin/bash
# scripts/backup.sh

set -e

BACKUP_DIR="/backups/ia-solaris"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="ia-solaris-backup-${DATE}.tar.gz"

echo "🗄️  Iniciando backup do sistema IA SOLARIS..."

# Criar diretório de backup
mkdir -p $BACKUP_DIR

# Backup do banco PostgreSQL
echo "📊 Fazendo backup do PostgreSQL..."
docker-compose exec -T postgres pg_dump -U postgres ia_solaris > $BACKUP_DIR/postgres-${DATE}.sql

# Backup do Redis
echo "🔄 Fazendo backup do Redis..."
docker-compose exec -T redis redis-cli --rdb /data/dump-${DATE}.rdb
docker cp ia-solaris-redis:/data/dump-${DATE}.rdb $BACKUP_DIR/

# Backup dos volumes Docker
echo "💾 Fazendo backup dos volumes..."
docker run --rm -v ia-solaris_postgres_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/postgres-data-${DATE}.tar.gz -C /data .
docker run --rm -v ia-solaris_redis_data:/data -v $BACKUP_DIR:/backup alpine tar czf /backup/redis-data-${DATE}.tar.gz -C /data .

# Backup das configurações
echo "⚙️  Fazendo backup das configurações..."
tar czf $BACKUP_DIR/configs-${DATE}.tar.gz database/ .env docker-compose.yml

# Criar arquivo final
echo "📦 Criando arquivo de backup final..."
cd $BACKUP_DIR
tar czf $BACKUP_FILE *.sql *.rdb *.tar.gz
rm *.sql *.rdb postgres-data-*.tar.gz redis-data-*.tar.gz configs-*.tar.gz

echo "✅ Backup concluído: $BACKUP_DIR/$BACKUP_FILE"

# Limpar backups antigos (manter últimos 7 dias)
find $BACKUP_DIR -name "ia-solaris-backup-*.tar.gz" -mtime +7 -delete

echo "🧹 Backups antigos removidos"
```

### Script de Restore

```bash
#!/bin/bash
# scripts/restore.sh

set -e

if [ -z "$1" ]; then
    echo "❌ Uso: $0 <arquivo-de-backup>"
    exit 1
fi

BACKUP_FILE=$1
RESTORE_DIR="/tmp/ia-solaris-restore"

echo "🔄 Iniciando restore do sistema IA SOLARIS..."
echo "📁 Arquivo: $BACKUP_FILE"

# Verificar se arquivo existe
if [ ! -f "$BACKUP_FILE" ]; then
    echo "❌ Arquivo de backup não encontrado: $BACKUP_FILE"
    exit 1
fi

# Parar serviços
echo "🛑 Parando serviços..."
docker-compose down

# Extrair backup
echo "📦 Extraindo backup..."
mkdir -p $RESTORE_DIR
cd $RESTORE_DIR
tar xzf $BACKUP_FILE

# Restaurar banco PostgreSQL
echo "📊 Restaurando PostgreSQL..."
docker-compose up -d postgres
sleep 30
cat postgres-*.sql | docker-compose exec -T postgres psql -U postgres -d ia_solaris

# Restaurar Redis
echo "🔄 Restaurando Redis..."
docker-compose up -d redis
sleep 10
docker cp dump-*.rdb ia-solaris-redis:/data/dump.rdb
docker-compose restart redis

# Restaurar configurações
echo "⚙️  Restaurando configurações..."
tar xzf configs-*.tar.gz -C /

# Iniciar todos os serviços
echo "🚀 Iniciando todos os serviços..."
docker-compose up -d

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços..."
sleep 60

# Verificar saúde do sistema
echo "🏥 Verificando saúde do sistema..."
./scripts/health-check.sh

echo "✅ Restore concluído com sucesso!"

# Limpar arquivos temporários
rm -rf $RESTORE_DIR
```

## Segurança e Hardening

### Configurações de Segurança

**Firewall (UFW):**
```bash
# Configurar firewall básico
sudo ufw default deny incoming
sudo ufw default allow outgoing

# Permitir SSH
sudo ufw allow ssh

# Permitir HTTP/HTTPS
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp

# Permitir apenas IPs específicos para admin
sudo ufw allow from 192.168.1.0/24 to any port 3000

# Ativar firewall
sudo ufw enable
```

**Docker Security:**
```bash
# Configurar Docker daemon
sudo tee /etc/docker/daemon.json << EOF
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  },
  "live-restore": true,
  "userland-proxy": false,
  "no-new-privileges": true
}
EOF

sudo systemctl restart docker
```

### Certificados SSL

**Gerar certificados auto-assinados (desenvolvimento):**
```bash
#!/bin/bash
# scripts/generate-ssl.sh

mkdir -p ssl

# Gerar chave privada
openssl genrsa -out ssl/key.pem 2048

# Gerar certificado
openssl req -new -x509 -key ssl/key.pem -out ssl/cert.pem -days 365 \
  -subj "/C=BR/ST=SP/L=São Paulo/O=IA SOLARIS/CN=localhost"

echo "✅ Certificados SSL gerados em ./ssl/"
```

**Configurar Let's Encrypt (produção):**
```bash
#!/bin/bash
# scripts/setup-letsencrypt.sh

DOMAIN="seu-dominio.com"
EMAIL="admin@seu-dominio.com"

# Instalar certbot
sudo apt-get update
sudo apt-get install certbot python3-certbot-nginx

# Obter certificado
sudo certbot --nginx -d $DOMAIN --email $EMAIL --agree-tos --non-interactive

# Configurar renovação automática
echo "0 12 * * * /usr/bin/certbot renew --quiet" | sudo crontab -

echo "✅ Let's Encrypt configurado para $DOMAIN"
```

---

**Autor:** Manus AI  
**Data:** Janeiro 2024  
**Versão:** 1.0

