# 🔧 Pré-requisitos e Setup
## MVP Híbrido - Controle de Tokens IA SOLARIS

### 📋 **Checklist de Pré-requisitos**

#### **🖥️ Ambiente de Desenvolvimento**
- [ ] **Node.js 18+** instalado
- [ ] **PostgreSQL 14+** instalado e configurado
- [ ] **Redis 6+** instalado e rodando
- [ ] **Git** para controle de versão
- [ ] **Docker** (opcional, mas recomendado)

#### **🔑 Credenciais Necessárias**
- [ ] **OpenAI API Key** com créditos suficientes
- [ ] **Acesso ao LibreChat** já funcionando
- [ ] **Banco PostgreSQL** com permissões de criação
- [ ] **Redis** acessível (local ou remoto)

#### **📚 Conhecimentos Técnicos**
- [ ] **JavaScript/Node.js** básico
- [ ] **Express.js** para APIs
- [ ] **PostgreSQL** queries básicas
- [ ] **Docker** (se usar containerização)

### 🛠️ **Instalação do Ambiente**

#### **1. Node.js e NPM**
```bash
# Verificar se já está instalado
node --version  # Deve ser 18+
npm --version

# Se não estiver instalado, baixar de: https://nodejs.org/
```

#### **2. PostgreSQL**
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# Iniciar serviço
sudo systemctl start postgresql
sudo systemctl enable postgresql

# Criar usuário e banco
sudo -u postgres psql
CREATE USER solaris_user WITH PASSWORD 'sua_senha_segura';
CREATE DATABASE solaris_mvp OWNER solaris_user;
GRANT ALL PRIVILEGES ON DATABASE solaris_mvp TO solaris_user;
\q
```

#### **3. Redis**
```bash
# Ubuntu/Debian
sudo apt install redis-server

# Iniciar serviço
sudo systemctl start redis-server
sudo systemctl enable redis-server

# Testar conexão
redis-cli ping  # Deve retornar PONG
```

### 🔧 **Configuração do LibreChat**

#### **Localizar Configuração Atual**
```bash
# Encontrar onde está instalado o LibreChat
cd /caminho/para/librechat

# Verificar se está funcionando
npm run dev  # ou como você inicia normalmente
```

#### **Identificar URL da API**
- **Padrão**: `http://localhost:3080/api/ask`
- **Verificar** no arquivo de configuração do LibreChat
- **Anotar** para configurar o proxy depois

### 📁 **Estrutura de Diretórios**

#### **Organização Recomendada**
```
projeto-solaris/
├── librechat/              # LibreChat original (não mexer)
├── proxy-solaris/          # Nosso proxy (novo)
│   ├── src/
│   ├── config/
│   ├── tests/
│   └── package.json
├── database/               # Scripts SQL
│   ├── migrations/
│   └── seeds/
└── docs/                   # Esta documentação
```

### 🔐 **Variáveis de Ambiente**

#### **Arquivo .env Template**
```env
# Banco de Dados
DATABASE_URL=postgresql://solaris_user:sua_senha@localhost:5432/solaris_mvp
DB_HOST=localhost
DB_PORT=5432
DB_NAME=solaris_mvp
DB_USER=solaris_user
DB_PASSWORD=sua_senha_segura

# Redis
REDIS_URL=redis://localhost:6379
REDIS_HOST=localhost
REDIS_PORT=6379

# APIs
OPENAI_API_KEY=sk-sua-chave-openai-aqui
LITELLM_BASE_URL=http://localhost:4000

# Proxy
PROXY_PORT=3081
LIBRECHAT_URL=http://localhost:3080
JWT_SECRET=sua-chave-jwt-super-secreta

# Ambiente
NODE_ENV=development
LOG_LEVEL=debug
```

### 🧪 **Verificação do Setup**

#### **1. Testar Banco PostgreSQL**
```bash
# Conectar ao banco
psql -h localhost -U solaris_user -d solaris_mvp

# Testar criação de tabela
CREATE TABLE test_table (id SERIAL PRIMARY KEY, name VARCHAR(50));
INSERT INTO test_table (name) VALUES ('teste');
SELECT * FROM test_table;
DROP TABLE test_table;
\q
```

#### **2. Testar Redis**
```bash
# Conectar ao Redis
redis-cli

# Testar operações básicas
SET test_key "teste"
GET test_key
DEL test_key
EXIT
```

#### **3. Testar OpenAI API**
```bash
# Testar com curl
curl -X POST "https://api.openai.com/v1/chat/completions" \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-3.5-turbo",
    "messages": [{"role": "user", "content": "Hello!"}],
    "max_tokens": 10
  }'
```

### 📦 **Dependências do Projeto**

#### **package.json Base**
```json
{
  "name": "proxy-solaris-mvp",
  "version": "1.0.0",
  "description": "Proxy inteligente para controle de tokens IA SOLARIS",
  "main": "src/index.js",
  "scripts": {
    "start": "node src/index.js",
    "dev": "nodemon src/index.js",
    "test": "jest",
    "migrate": "node database/migrate.js"
  },
  "dependencies": {
    "express": "^4.18.2",
    "pg": "^8.11.0",
    "redis": "^4.6.7",
    "jsonwebtoken": "^9.0.0",
    "bcrypt": "^5.1.0",
    "cors": "^2.8.5",
    "helmet": "^7.0.0",
    "dotenv": "^16.1.4",
    "axios": "^1.4.0",
    "winston": "^3.9.0"
  },
  "devDependencies": {
    "nodemon": "^2.0.22",
    "jest": "^29.5.0",
    "supertest": "^6.3.3"
  }
}
```

### 🐳 **Setup com Docker (Opcional)**

#### **docker-compose.yml**
```yaml
version: '3.8'
services:
  postgres:
    image: postgres:14
    environment:
      POSTGRES_DB: solaris_mvp
      POSTGRES_USER: solaris_user
      POSTGRES_PASSWORD: sua_senha_segura
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data

  redis:
    image: redis:6-alpine
    ports:
      - "6379:6379"

  proxy-solaris:
    build: ./proxy-solaris
    ports:
      - "3081:3081"
    depends_on:
      - postgres
      - redis
    environment:
      - DATABASE_URL=postgresql://solaris_user:sua_senha_segura@postgres:5432/solaris_mvp
      - REDIS_URL=redis://redis:6379

volumes:
  postgres_data:
```

### ✅ **Checklist Final**

#### **Antes de Começar a Implementação**
- [ ] Todos os serviços rodando (PostgreSQL, Redis)
- [ ] Variáveis de ambiente configuradas
- [ ] OpenAI API testada e funcionando
- [ ] LibreChat funcionando normalmente
- [ ] Estrutura de diretórios criada
- [ ] Git inicializado no projeto

#### **Validação do Setup**
```bash
# Testar conexões
npm run test-connections

# Verificar logs
tail -f logs/setup.log

# Status dos serviços
systemctl status postgresql redis-server
```

### 🚀 **Próximo Passo**

Após completar todos os pré-requisitos:
1. **[Infraestrutura Base](infraestrutura-base.md)** - Criar banco e tabelas
2. **[Proxy Básico](proxy-basico.md)** - Implementar proxy inicial
3. **[Integração LiteLLM](integracao-litellm.md)** - Conectar contador de tokens

---

**💡 Um setup bem feito garante implementação sem problemas. Não pule etapas!**

