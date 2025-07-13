# 🚀 IA SOLARIS - MVP Híbrido de Controle de Tokens

## 📋 Visão Geral

O **IA SOLARIS MVP Híbrido** é uma solução completa e pronta para produção que implementa controle preciso de tokens por usuário para sistemas de IA, especificamente projetada para integração com o LibreChat. Esta implementação oferece uma abordagem híbrida que mantém o LibreChat intacto enquanto adiciona funcionalidades avançadas de controle, monitoramento e monetização.

### 🎯 Características Principais

- **🔒 Controle Individual de Tokens**: Cada usuário possui sua própria cota de tokens
- **⚡ Proxy Inteligente**: Intercepta e controla requisições sem modificar o LibreChat
- **📊 Dashboard Administrativo**: Interface completa para gerenciamento
- **🚨 Sistema de Alertas**: Notificações automáticas por email
- **💰 Monetização**: Sistema de créditos e controle de custos
- **🔄 Integração LiteLLM**: Suporte a múltiplos provedores de IA
- **📈 Monitoramento**: Métricas e relatórios detalhados
- **🛡️ Segurança**: Rate limiting e autenticação robusta

## 🏗️ Arquitetura

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LibreChat     │───▶│ Proxy Inteligente│───▶│    LiteLLM      │
│                 │    │   IA SOLARIS    │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │                        │
                                ▼                        ▼
                       ┌─────────────────┐    ┌─────────────────┐
                       │   PostgreSQL    │    │   OpenAI API    │
                       │   (Controle)    │    │   (Modelos)     │
                       └─────────────────┘    └─────────────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ Dashboard Admin │
                       │   (React)       │
                       └─────────────────┘
```

## 🚀 Instalação Rápida

### Pré-requisitos

- **Docker** e **Docker Compose** instalados
- **Git** para clonar o repositório
- **Chave da OpenAI** (obrigatória)
- **Configuração SMTP** para emails (recomendada)

### Instalação em 3 Passos

```bash
# 1. Clonar o repositório
git clone <url-do-repositorio>
cd mvp-ia-solaris-turnkey

# 2. Configurar ambiente
cp .env.example .env
# Edite o .env e configure sua OPENAI_API_KEY

# 3. Executar instalação automática
chmod +x scripts/install.sh
./scripts/install.sh
```

### Acesso Imediato

Após a instalação:

- **Dashboard Admin**: http://localhost/admin
- **API Proxy**: http://localhost/v1
- **LiteLLM Debug**: http://localhost/litellm

## ⚙️ Configuração Detalhada

### 1. Arquivo de Ambiente (.env)

```bash
# Configurações obrigatórias
OPENAI_API_KEY=sk-your-openai-api-key-here

# Configurações de email (recomendadas)
SMTP_USERNAME=your-email@gmail.com
SMTP_PASSWORD=your-app-password

# Configurações opcionais (já têm valores padrão)
DEFAULT_TOKENS_PER_USER=1000
CONVERSION_FACTOR=0.376
CREDITS_EMAIL=creditos@iasolaris.com.br
```

### 2. Integração com LibreChat

Configure o LibreChat para usar o proxy:

```yaml
# No docker-compose.yml do LibreChat
environment:
  - OPENAI_API_KEY=sk-qualquer-valor
  - OPENAI_REVERSE_PROXY=http://localhost:5000/v1
```

### 3. Configuração de Usuários

Acesse o dashboard administrativo e:

1. Adicione usuários manualmente
2. Configure tokens iniciais
3. Monitore consumo em tempo real
4. Configure alertas personalizados

## 📊 Funcionalidades

### Dashboard Administrativo

- **👥 Gerenciamento de Usuários**: Adicionar, editar e monitorar usuários
- **⚡ Controle de Tokens**: Distribuir e monitorar consumo
- **📈 Estatísticas**: Gráficos e relatórios detalhados
- **⚙️ Configurações**: Personalizar limites e alertas
- **🚨 Alertas**: Sistema de notificações automáticas

### Sistema de Tokens

- **Distribuição Automática**: Tokens padrão para novos usuários
- **Alertas Inteligentes**: Notificações em 80% e 95% de uso
- **Bloqueio Automático**: Proteção contra uso excessivo
- **Histórico Completo**: Rastreamento de todas as transações
- **Relatórios**: Análise de consumo e custos

### Proxy Inteligente

- **Interceptação Transparente**: Funciona sem modificar LibreChat
- **Controle por Usuário**: Isolamento completo de quotas
- **Rate Limiting**: Proteção contra abuso
- **Logging Detalhado**: Auditoria completa de uso
- **Fallback Inteligente**: Continuidade de serviço

## 🔧 Administração

### Comandos Úteis

```bash
# Ver status dos serviços
docker-compose -f database/docker-compose.yml ps

# Ver logs em tempo real
docker-compose -f database/docker-compose.yml logs -f

# Reiniciar serviços
docker-compose -f database/docker-compose.yml restart

# Parar tudo
docker-compose -f database/docker-compose.yml down

# Backup do banco
docker-compose -f database/docker-compose.yml exec postgres pg_dump -U ia_solaris_user ia_solaris > backup.sql
```

### Troubleshooting

```bash
# Script de diagnóstico automático
./scripts/troubleshoot.sh

# Verificação rápida
./scripts/troubleshoot.sh check

# Ver logs de erro
./scripts/troubleshoot.sh logs
```

## 📈 Monitoramento

### Métricas Disponíveis

- **Usuários Ativos**: Número de usuários utilizando o sistema
- **Tokens Consumidos**: Total de tokens utilizados por período
- **Custos**: Estimativa de custos por usuário e total
- **Performance**: Tempo de resposta e disponibilidade
- **Alertas**: Histórico de notificações enviadas

### Logs e Auditoria

- **Logs Estruturados**: JSON para fácil análise
- **Rastreamento de Usuário**: Cada requisição é associada a um usuário
- **Histórico de Tokens**: Registro completo de consumo
- **Eventos de Sistema**: Alertas, bloqueios e configurações

## 🔒 Segurança

### Medidas Implementadas

- **Rate Limiting**: Proteção contra abuso de API
- **Autenticação**: Controle de acesso por usuário
- **Isolamento**: Quotas individuais por usuário
- **Logs de Auditoria**: Rastreamento completo de atividades
- **Configurações Seguras**: Senhas e chaves protegidas

### Boas Práticas

- Altere todas as senhas padrão em produção
- Configure SSL/TLS para acesso externo
- Monitore logs regularmente
- Faça backups periódicos do banco de dados
- Mantenha as chaves de API seguras

## 🚀 Deploy em Produção

### Preparação

1. **Configure SSL/TLS**:
   ```bash
   # Adicione certificados em database/ssl/
   cp seu-certificado.pem database/ssl/cert.pem
   cp sua-chave.key database/ssl/key.pem
   ```

2. **Altere Senhas**:
   ```bash
   # No arquivo .env, altere:
   POSTGRES_PASSWORD=senha-forte-producao
   REDIS_PASSWORD=senha-redis-producao
   SECRET_KEY=chave-secreta-unica
   ```

3. **Configure Domínio**:
   ```bash
   # No .env
   DOMAIN=seudominio.com
   ADMIN_DOMAIN=admin.seudominio.com
   ```

### Deploy

```bash
# 1. Configurar ambiente de produção
export NODE_ENV=production
export FLASK_ENV=production

# 2. Build para produção
docker-compose -f database/docker-compose.yml build

# 3. Iniciar em produção
docker-compose -f database/docker-compose.yml up -d

# 4. Verificar saúde dos serviços
./scripts/troubleshoot.sh check
```

## 📚 Documentação Técnica

### Estrutura do Projeto

```
mvp-ia-solaris-turnkey/
├── proxy-inteligente/          # Proxy Flask
│   └── proxy-ia-solaris/
│       ├── src/
│       │   ├── models/         # Modelos de dados
│       │   ├── services/       # Lógica de negócio
│       │   ├── routes/         # Endpoints da API
│       │   └── main.py         # Aplicação principal
│       ├── Dockerfile
│       └── requirements.txt
├── admin-dashboard/            # Dashboard React
│   └── admin-ia-solaris/
│       ├── src/
│       │   ├── components/     # Componentes React
│       │   └── App.jsx         # Aplicação principal
│       ├── Dockerfile
│       └── package.json
├── database/                   # Configurações de infraestrutura
│   ├── docker-compose.yml     # Orquestração de serviços
│   ├── litellm-config.yaml    # Configuração LiteLLM
│   ├── nginx.conf             # Configuração Nginx
│   └── init-scripts/          # Scripts de inicialização
├── scripts/                    # Scripts de automação
│   ├── install.sh             # Instalação automática
│   └── troubleshoot.sh        # Diagnóstico e solução
├── config/                     # Configurações adicionais
├── docs/                       # Documentação detalhada
└── .env.example               # Exemplo de configuração
```

### APIs Disponíveis

#### Proxy IA SOLARIS (http://localhost:5000/v1)

- `GET /health` - Status do sistema
- `POST /chat/completions` - Endpoint principal (compatível com OpenAI)
- `GET /models` - Lista de modelos disponíveis
- `GET /admin/users` - Gerenciamento de usuários
- `POST /admin/users/{id}/add-tokens` - Adicionar tokens

#### Dashboard Admin (http://localhost:3000)

- Interface web completa para administração
- Gerenciamento de usuários e tokens
- Relatórios e estatísticas
- Configurações do sistema

## 🤝 Suporte e Contribuição

### Problemas Comuns

1. **Containers não iniciam**: Verifique se as portas estão livres
2. **API não responde**: Confirme se OPENAI_API_KEY está configurada
3. **Emails não enviam**: Verifique configurações SMTP
4. **Dashboard não carrega**: Limpe cache do navegador

### Obtendo Ajuda

1. Execute o script de diagnóstico: `./scripts/troubleshoot.sh`
2. Verifique os logs: `docker-compose logs -f`
3. Consulte a documentação técnica em `/docs`

### Contribuindo

Este é um projeto turn-key completo. Para customizações:

1. Faça fork do projeto
2. Implemente suas modificações
3. Teste thoroughly
4. Documente as mudanças

## 📄 Licença

Este projeto é fornecido como uma solução completa para implementação do MVP híbrido de controle de tokens da IA SOLARIS.

## 🎉 Conclusão

O **IA SOLARIS MVP Híbrido** oferece uma solução completa e pronta para produção que permite implementar controle preciso de tokens com o mínimo de esforço. Com instalação automatizada, documentação completa e scripts de troubleshooting, desenvolvedores de qualquer nível podem implementar esta solução rapidamente.

**Principais benefícios:**

- ✅ **Instalação em minutos** com script automatizado
- ✅ **Zero modificações** no LibreChat existente
- ✅ **Interface administrativa** completa e intuitiva
- ✅ **Monitoramento em tempo real** de uso e custos
- ✅ **Sistema de alertas** automático por email
- ✅ **Escalabilidade** para crescimento futuro
- ✅ **Documentação completa** e suporte a troubleshooting

---

**🚀 Comece agora mesmo executando `./scripts/install.sh` e tenha seu sistema de controle de tokens funcionando em poucos minutos!**

