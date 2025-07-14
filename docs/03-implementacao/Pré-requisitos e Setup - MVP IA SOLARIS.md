# Pré-requisitos e Setup - MVP IA SOLARIS

## Visão Geral

Este documento detalha todos os pré-requisitos necessários e o processo completo de setup para implementação do MVP híbrido de controle de tokens da IA SOLARIS. O guia é estruturado para desenvolvedores com diferentes níveis de experiência, fornecendo instruções passo a passo desde a preparação do ambiente até a validação final do sistema.

## Pré-requisitos do Sistema

### Requisitos de Hardware

**Ambiente de Desenvolvimento:**
- CPU: Mínimo 4 cores, recomendado 8 cores
- RAM: Mínimo 8GB, recomendado 16GB
- Armazenamento: Mínimo 50GB livres, recomendado 100GB SSD
- Rede: Conexão estável com internet (mínimo 10 Mbps)

**Ambiente de Produção:**
- CPU: Mínimo 8 cores, recomendado 16 cores
- RAM: Mínimo 16GB, recomendado 32GB
- Armazenamento: Mínimo 200GB SSD, recomendado 500GB NVMe
- Rede: Conexão dedicada com baixa latência
- Backup: Sistema de backup automatizado

### Requisitos de Software

**Sistema Operacional:**
- Ubuntu 20.04 LTS ou superior (recomendado)
- CentOS 8 ou superior
- macOS 12+ (apenas desenvolvimento)
- Windows 10/11 com WSL2 (apenas desenvolvimento)

**Ferramentas Essenciais:**
```bash
# Docker e Docker Compose
Docker Engine 20.10+
Docker Compose 2.0+

# Git para controle de versão
Git 2.30+

# Editor de código
VS Code, PyCharm, ou similar

# Ferramentas de linha de comando
curl, wget, jq, htop
```

**Linguagens e Runtimes:**
```bash
# Python para o backend
Python 3.11+
pip 23.0+
virtualenv ou conda

# Node.js para o frontend
Node.js 18.0+
npm 9.0+ ou yarn 1.22+

# Banco de dados (se instalação local)
PostgreSQL 15+
Redis 7.0+
```

### Contas e Chaves de API

**Obrigatórias:**
- **OpenAI API Key:** Conta ativa com créditos disponíveis
- **GitHub Account:** Para acesso ao repositório
- **Email SMTP:** Para envio de notificações (Gmail, SendGrid, etc.)

**Opcionais (Fase 2):**
- **Stripe Account:** Para processamento de pagamentos
- **Anthropic API Key:** Para modelos Claude
- **Google Cloud/AWS:** Para deploy em produção

## Preparação do Ambiente

### Instalação do Docker

**Ubuntu/Debian:**
```bash
# Remover versões antigas
sudo apt-get remove docker docker-engine docker.io containerd runc

# Atualizar repositórios
sudo apt-get update

# Instalar dependências
sudo apt-get install \
    ca-certificates \
    curl \
    gnupg \
    lsb-release

# Adicionar chave GPG oficial do Docker
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Configurar repositório
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
  $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker Engine
sudo apt-get update
sudo apt-get install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verificar instalação
sudo docker run hello-world

# Adicionar usuário ao grupo docker (evita sudo)
sudo usermod -aG docker $USER
newgrp docker
```

**CentOS/RHEL:**
```bash
# Instalar yum-utils
sudo yum install -y yum-utils

# Adicionar repositório Docker
sudo yum-config-manager \
    --add-repo \
    https://download.docker.com/linux/centos/docker-ce.repo

# Instalar Docker
sudo yum install docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Iniciar e habilitar Docker
sudo systemctl start docker
sudo systemctl enable docker

# Verificar instalação
sudo docker run hello-world
```

**macOS:**
```bash
# Instalar Docker Desktop
# Baixar de: https://www.docker.com/products/docker-desktop/

# Ou via Homebrew
brew install --cask docker

# Verificar instalação
docker --version
docker-compose --version
```

### Instalação do Git

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install git

# Configurar Git
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
```

**CentOS/RHEL:**
```bash
sudo yum install git

# Configurar Git
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
```

**macOS:**
```bash
# Git já vem instalado, ou via Homebrew
brew install git

# Configurar Git
git config --global user.name "Seu Nome"
git config --global user.email "seu-email@exemplo.com"
```

### Instalação do Python (Desenvolvimento Local)

**Ubuntu/Debian:**
```bash
# Instalar Python 3.11
sudo apt-get update
sudo apt-get install software-properties-common
sudo add-apt-repository ppa:deadsnakes/ppa
sudo apt-get update
sudo apt-get install python3.11 python3.11-venv python3.11-pip

# Criar alias para python
echo 'alias python=python3.11' >> ~/.bashrc
echo 'alias pip=pip3' >> ~/.bashrc
source ~/.bashrc

# Verificar instalação
python --version
pip --version
```

**CentOS/RHEL:**
```bash
# Instalar Python 3.11
sudo yum install python3.11 python3.11-pip

# Verificar instalação
python3.11 --version
pip3.11 --version
```

**macOS:**
```bash
# Via Homebrew
brew install python@3.11

# Verificar instalação
python3.11 --version
pip3.11 --version
```

### Instalação do Node.js (Desenvolvimento Local)

**Ubuntu/Debian:**
```bash
# Via NodeSource repository
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt-get install -y nodejs

# Verificar instalação
node --version
npm --version
```

**CentOS/RHEL:**
```bash
# Via NodeSource repository
curl -fsSL https://rpm.nodesource.com/setup_18.x | sudo bash -
sudo yum install -y nodejs

# Verificar instalação
node --version
npm --version
```

**macOS:**
```bash
# Via Homebrew
brew install node@18

# Verificar instalação
node --version
npm --version
```

## Configuração do Projeto

### Clonagem do Repositório

```bash
# Clonar repositório
git clone https://github.com/Solaris-Empresa/mvp-hibrido-docs.git
cd mvp-hibrido-docs

# Verificar estrutura
ls -la

# Deve mostrar:
# ├── proxy-inteligente/
# ├── admin-dashboard/
# ├── database/
# ├── scripts/
# ├── .env.example
# ├── docker-compose.yml
# └── README.md
```

### Configuração de Variáveis de Ambiente

**Criar arquivo .env:**
```bash
# Copiar template
cp .env.example .env

# Editar arquivo .env
nano .env
```

**Configurações obrigatórias no .env:**
```bash
# === CONFIGURAÇÕES BÁSICAS ===
DEBUG=false
SECRET_KEY=sua-chave-secreta-super-forte-aqui
HOST=0.0.0.0
PORT=5000

# === BANCO DE DADOS ===
DB_HOST=postgres
DB_PORT=5432
DB_NAME=ia_solaris
DB_USER=postgres
DB_PASSWORD=senha-super-forte-postgres

# === REDIS ===
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=senha-super-forte-redis

# === OPENAI ===
OPENAI_API_KEY=sk-sua-chave-openai-aqui
OPENAI_API_BASE=https://api.openai.com/v1

# === LITELLM ===
LITELLM_BASE_URL=http://litellm:4000

# === EMAIL (SMTP) ===
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=seu-email@gmail.com
SMTP_PASSWORD=sua-senha-app-gmail
FROM_EMAIL=noreply@iasolaris.com
SMTP_TLS=true

# === TOKENS ===
DEFAULT_MONTHLY_LIMIT=1000000
ALERT_THRESHOLD=0.8
BLOCK_THRESHOLD=1.0
MAX_USER_LIMIT=10000000
MIN_USER_LIMIT=100000

# === LOGS ===
LOG_LEVEL=INFO
```

**Gerar chaves seguras:**
```bash
# Gerar SECRET_KEY
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Gerar senhas de banco
openssl rand -base64 32
```

### Configuração de Email SMTP

**Gmail (Recomendado para desenvolvimento):**
1. Ativar autenticação de 2 fatores na conta Google
2. Gerar senha de app específica:
   - Ir em: Conta Google → Segurança → Senhas de app
   - Selecionar "Email" e "Outro"
   - Copiar senha gerada para SMTP_PASSWORD

**SendGrid (Recomendado para produção):**
```bash
SMTP_HOST=smtp.sendgrid.net
SMTP_PORT=587
SMTP_USER=apikey
SMTP_PASSWORD=sua-api-key-sendgrid
```

**Mailgun:**
```bash
SMTP_HOST=smtp.mailgun.org
SMTP_PORT=587
SMTP_USER=postmaster@seu-dominio.mailgun.org
SMTP_PASSWORD=sua-senha-mailgun
```

### Configuração da OpenAI API

**Obter chave da API:**
1. Acessar: https://platform.openai.com/api-keys
2. Fazer login na conta OpenAI
3. Clicar em "Create new secret key"
4. Copiar chave (sk-...)
5. Adicionar créditos na conta se necessário

**Testar chave:**
```bash
# Testar via curl
curl https://api.openai.com/v1/models \
  -H "Authorization: Bearer sk-sua-chave-aqui"

# Deve retornar lista de modelos disponíveis
```

**Configurar limites de uso:**
1. Acessar: https://platform.openai.com/account/billing/limits
2. Definir limite mensal apropriado
3. Configurar alertas de uso

## Validação do Setup

### Verificação de Dependências

**Script de verificação:**
```bash
#!/bin/bash
# Salvar como: scripts/check-dependencies.sh

echo "🔍 Verificando dependências do sistema..."

# Verificar Docker
if command -v docker &> /dev/null; then
    echo "✅ Docker: $(docker --version)"
else
    echo "❌ Docker não encontrado"
    exit 1
fi

# Verificar Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "✅ Docker Compose: $(docker-compose --version)"
else
    echo "❌ Docker Compose não encontrado"
    exit 1
fi

# Verificar Git
if command -v git &> /dev/null; then
    echo "✅ Git: $(git --version)"
else
    echo "❌ Git não encontrado"
    exit 1
fi

# Verificar Python (se desenvolvimento local)
if command -v python3.11 &> /dev/null; then
    echo "✅ Python: $(python3.11 --version)"
else
    echo "⚠️  Python 3.11 não encontrado (OK se usando apenas Docker)"
fi

# Verificar Node.js (se desenvolvimento local)
if command -v node &> /dev/null; then
    echo "✅ Node.js: $(node --version)"
else
    echo "⚠️  Node.js não encontrado (OK se usando apenas Docker)"
fi

# Verificar arquivo .env
if [ -f .env ]; then
    echo "✅ Arquivo .env encontrado"
    
    # Verificar variáveis críticas
    if grep -q "OPENAI_API_KEY=sk-" .env; then
        echo "✅ OPENAI_API_KEY configurada"
    else
        echo "❌ OPENAI_API_KEY não configurada ou inválida"
        exit 1
    fi
    
    if grep -q "DB_PASSWORD=" .env && ! grep -q "DB_PASSWORD=$" .env; then
        echo "✅ DB_PASSWORD configurada"
    else
        echo "❌ DB_PASSWORD não configurada"
        exit 1
    fi
else
    echo "❌ Arquivo .env não encontrado"
    exit 1
fi

echo "🎉 Todas as dependências verificadas com sucesso!"
```

**Executar verificação:**
```bash
chmod +x scripts/check-dependencies.sh
./scripts/check-dependencies.sh
```

### Teste de Conectividade

**Testar conexão com OpenAI:**
```bash
# Script de teste
cat > test-openai.sh << 'EOF'
#!/bin/bash
source .env

echo "🔍 Testando conexão com OpenAI..."

response=$(curl -s -w "%{http_code}" -o /tmp/openai-test.json \
  -H "Authorization: Bearer $OPENAI_API_KEY" \
  -H "Content-Type: application/json" \
  https://api.openai.com/v1/models)

if [ "$response" = "200" ]; then
    echo "✅ Conexão com OpenAI OK"
    echo "📋 Modelos disponíveis:"
    jq -r '.data[].id' /tmp/openai-test.json | head -5
else
    echo "❌ Erro na conexão com OpenAI (HTTP $response)"
    cat /tmp/openai-test.json
    exit 1
fi
EOF

chmod +x test-openai.sh
./test-openai.sh
```

**Testar SMTP:**
```bash
# Script de teste de email
cat > test-smtp.sh << 'EOF'
#!/bin/bash
source .env

echo "📧 Testando configuração SMTP..."

python3 << PYTHON
import smtplib
import os
from email.mime.text import MIMEText

try:
    # Configurações do .env
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = int(os.getenv('SMTP_PORT'))
    smtp_user = os.getenv('SMTP_USER')
    smtp_password = os.getenv('SMTP_PASSWORD')
    from_email = os.getenv('FROM_EMAIL')
    
    # Criar conexão
    server = smtplib.SMTP(smtp_host, smtp_port)
    server.starttls()
    server.login(smtp_user, smtp_password)
    
    # Criar mensagem de teste
    msg = MIMEText('Teste de configuração SMTP do MVP IA SOLARIS')
    msg['Subject'] = 'Teste SMTP - MVP IA SOLARIS'
    msg['From'] = from_email
    msg['To'] = smtp_user
    
    # Enviar email
    server.send_message(msg)
    server.quit()
    
    print("✅ SMTP configurado corretamente")
    print(f"📧 Email de teste enviado para {smtp_user}")
    
except Exception as e:
    print(f"❌ Erro na configuração SMTP: {e}")
    exit(1)
PYTHON
EOF

chmod +x test-smtp.sh
./test-smtp.sh
```

## Setup de Desenvolvimento Local

### Ambiente Python Virtual

**Criar ambiente virtual:**
```bash
# Navegar para o proxy
cd proxy-inteligente/proxy-ia-solaris

# Criar ambiente virtual
python3.11 -m venv venv

# Ativar ambiente virtual
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate     # Windows

# Atualizar pip
pip install --upgrade pip

# Instalar dependências
pip install -r requirements.txt

# Verificar instalação
pip list
```

**Configurar IDE (VS Code):**
```json
// .vscode/settings.json
{
    "python.defaultInterpreterPath": "./proxy-inteligente/proxy-ia-solaris/venv/bin/python",
    "python.linting.enabled": true,
    "python.linting.pylintEnabled": true,
    "python.formatting.provider": "black",
    "python.testing.pytestEnabled": true,
    "python.testing.pytestArgs": [
        "tests"
    ]
}
```

### Ambiente Node.js

**Configurar frontend:**
```bash
# Navegar para o dashboard
cd admin-dashboard/admin-ia-solaris

# Instalar dependências
npm install

# Verificar instalação
npm list

# Configurar variáveis de ambiente
echo "REACT_APP_API_BASE_URL=http://localhost:5000/api" > .env.local
```

### Banco de Dados Local (Opcional)

**Instalar PostgreSQL:**
```bash
# Ubuntu/Debian
sudo apt-get install postgresql postgresql-contrib

# Configurar usuário
sudo -u postgres createuser --interactive
# Nome: postgres
# Superuser: y

# Criar banco
sudo -u postgres createdb ia_solaris

# Configurar senha
sudo -u postgres psql
\password postgres
# Digite a senha configurada no .env
\q
```

**Instalar Redis:**
```bash
# Ubuntu/Debian
sudo apt-get install redis-server

# Configurar senha
sudo nano /etc/redis/redis.conf
# Descomentar e configurar: requirepass sua-senha-redis

# Reiniciar Redis
sudo systemctl restart redis-server
```

## Troubleshooting Comum

### Problemas com Docker

**Erro: "permission denied"**
```bash
# Adicionar usuário ao grupo docker
sudo usermod -aG docker $USER
newgrp docker

# Ou usar sudo temporariamente
sudo docker run hello-world
```

**Erro: "port already in use"**
```bash
# Verificar portas em uso
sudo netstat -tulpn | grep :5000

# Parar processo usando a porta
sudo kill -9 PID_DO_PROCESSO

# Ou alterar porta no docker-compose.yml
```

**Erro: "no space left on device"**
```bash
# Limpar containers e imagens não utilizados
docker system prune -a

# Verificar espaço em disco
df -h
```

### Problemas com Python

**Erro: "module not found"**
```bash
# Verificar se ambiente virtual está ativo
which python
# Deve mostrar caminho do venv

# Reinstalar dependências
pip install -r requirements.txt --force-reinstall
```

**Erro: "permission denied" ao instalar pacotes**
```bash
# Usar ambiente virtual (recomendado)
python -m venv venv
source venv/bin/activate

# Ou instalar para usuário
pip install --user package_name
```

### Problemas com Node.js

**Erro: "EACCES permission denied"**
```bash
# Configurar npm para usuário
mkdir ~/.npm-global
npm config set prefix '~/.npm-global'
echo 'export PATH=~/.npm-global/bin:$PATH' >> ~/.bashrc
source ~/.bashrc
```

**Erro: "node-sass" ou dependências nativas**
```bash
# Limpar cache e reinstalar
npm cache clean --force
rm -rf node_modules package-lock.json
npm install
```

### Problemas com OpenAI API

**Erro: "invalid API key"**
- Verificar se chave começa com "sk-"
- Verificar se não há espaços extras
- Testar chave diretamente no site da OpenAI

**Erro: "rate limit exceeded"**
- Verificar limites na conta OpenAI
- Implementar retry com backoff
- Considerar upgrade do plano

**Erro: "insufficient quota"**
- Adicionar créditos na conta OpenAI
- Verificar billing settings
- Configurar alertas de uso

## Scripts de Automação

### Script de Setup Completo

```bash
#!/bin/bash
# scripts/setup-complete.sh

set -e

echo "🚀 Iniciando setup completo do MVP IA SOLARIS..."

# Verificar se está na raiz do projeto
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ Execute este script na raiz do projeto"
    exit 1
fi

# Verificar dependências
echo "🔍 Verificando dependências..."
./scripts/check-dependencies.sh

# Configurar .env se não existir
if [ ! -f .env ]; then
    echo "📝 Configurando arquivo .env..."
    cp .env.example .env
    echo "⚠️  Configure as variáveis no arquivo .env e execute novamente"
    exit 1
fi

# Testar conectividade
echo "🌐 Testando conectividade..."
./test-openai.sh
./test-smtp.sh

# Construir imagens Docker
echo "🔧 Construindo imagens Docker..."
docker-compose build --no-cache

# Iniciar banco de dados
echo "🗄️  Iniciando banco de dados..."
docker-compose up -d postgres redis

# Aguardar banco ficar pronto
echo "⏳ Aguardando banco de dados..."
sleep 30

# Executar migrações
echo "🔄 Executando migrações..."
docker-compose run --rm proxy-inteligente python -c "
from src.models.user import Base
from src.config.settings import AppConfig
from sqlalchemy import create_engine

config = AppConfig()
engine = create_engine(config.database.url)
Base.metadata.create_all(engine)
print('✅ Tabelas criadas com sucesso!')
"

# Iniciar todos os serviços
echo "🚀 Iniciando todos os serviços..."
docker-compose up -d

# Aguardar serviços ficarem prontos
echo "⏳ Aguardando serviços..."
sleep 60

# Executar testes de saúde
echo "🏥 Executando health checks..."
./scripts/health-check.sh

echo "🎉 Setup completo finalizado!"
echo ""
echo "📋 Serviços disponíveis:"
echo "   • Proxy API: http://localhost:5000"
echo "   • Dashboard Admin: http://localhost:3000"
echo "   • LiteLLM: http://localhost:4000"
echo ""
echo "📊 Para monitorar:"
echo "   docker-compose logs -f"
```

### Script de Health Check

```bash
#!/bin/bash
# scripts/health-check.sh

echo "🏥 Executando health checks..."

# Verificar proxy
if curl -f http://localhost:5000/health >/dev/null 2>&1; then
    echo "✅ Proxy Inteligente: OK"
else
    echo "❌ Proxy Inteligente: FALHA"
    docker-compose logs proxy-inteligente | tail -20
fi

# Verificar admin dashboard
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ Dashboard Admin: OK"
else
    echo "❌ Dashboard Admin: FALHA"
    docker-compose logs admin-dashboard | tail -20
fi

# Verificar LiteLLM
if curl -f http://localhost:4000/health >/dev/null 2>&1; then
    echo "✅ LiteLLM: OK"
else
    echo "❌ LiteLLM: FALHA"
    docker-compose logs litellm | tail -20
fi

# Verificar banco de dados
if docker-compose exec -T postgres pg_isready -U postgres >/dev/null 2>&1; then
    echo "✅ PostgreSQL: OK"
else
    echo "❌ PostgreSQL: FALHA"
    docker-compose logs postgres | tail -20
fi

# Verificar Redis
if docker-compose exec -T redis redis-cli ping >/dev/null 2>&1; then
    echo "✅ Redis: OK"
else
    echo "❌ Redis: FALHA"
    docker-compose logs redis | tail -20
fi

echo "🏥 Health check concluído!"
```

## Próximos Passos

Após completar este setup:

1. **Validar Funcionamento:** Execute todos os health checks
2. **Configurar Monitoramento:** Implementar logs e métricas
3. **Executar Testes:** Rodar suite completa de testes
4. **Documentar Customizações:** Registrar alterações específicas
5. **Treinar Equipe:** Capacitar desenvolvedores no sistema

---

**Autor:** Manus AI  
**Data:** Janeiro 2024  
**Versão:** 1.0

