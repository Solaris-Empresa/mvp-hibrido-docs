# 🔧 Referência Técnica
## MVP Híbrido - Controle de Tokens IA SOLARIS

### 📋 **Índice desta Seção**

1. [APIs e Endpoints](apis-endpoints.md)
2. [Schema do Banco de Dados](schema-banco.md)
3. [Configurações e Variáveis](configuracoes.md)
4. [Troubleshooting](troubleshooting.md)
5. [Monitoramento e Logs](monitoramento.md)

---

### 🎯 **Objetivo desta Seção**

Esta é sua **referência rápida** durante o desenvolvimento:

- **APIs documentadas** com exemplos
- **Schema completo** do banco de dados
- **Configurações** necessárias
- **Troubleshooting** para problemas comuns
- **Monitoramento** e observabilidade

### 📊 **Visão Geral da Arquitetura de Dados**

```mermaid
erDiagram
    USERS ||--o{ TOKEN_USAGE : has
    USERS ||--o{ SUBSCRIPTIONS : has
    USERS ||--o{ CREDIT_TRANSACTIONS : has
    
    USERS {
        uuid id PK
        string email
        string name
        timestamp created_at
        timestamp updated_at
        boolean active
    }
    
    SUBSCRIPTIONS {
        uuid id PK
        uuid user_id FK
        string plan_type
        integer monthly_tokens
        timestamp start_date
        timestamp end_date
        boolean active
    }
    
    TOKEN_USAGE {
        uuid id PK
        uuid user_id FK
        integer tokens_used
        integer tokens_remaining
        date usage_date
        timestamp created_at
    }
    
    CREDIT_TRANSACTIONS {
        uuid id PK
        uuid user_id FK
        integer tokens_added
        decimal amount_paid
        string transaction_type
        timestamp created_at
    }
```

### 🔌 **APIs Principais**

#### **Proxy IA SOLARIS (Port 3001)**
```
GET    /api/health              # Health check
POST   /api/auth/login          # Autenticação
GET    /api/tokens/current      # Saldo atual
POST   /api/tokens/consume      # Consumir tokens
GET    /api/tokens/history      # Histórico de uso
POST   /api/credits/purchase    # Comprar créditos
```

#### **LiteLLM (Port 4000)**
```
POST   /chat/completions        # Proxy para OpenAI
GET    /health                  # Health check
GET    /metrics                 # Métricas Prometheus
```

#### **Admin Dashboard (Port 3002)**
```
GET    /admin/dashboard         # Métricas gerais
GET    /admin/users             # Lista usuários
POST   /admin/users/:id/credits # Adicionar créditos
GET    /admin/usage/stats       # Estatísticas de uso
```

### 📊 **Métricas e Monitoramento**

#### **Métricas Principais**
```javascript
// Métricas coletadas
const metrics = {
  // Usuários
  total_users: 1247,
  active_users_today: 892,
  new_users_today: 23,
  
  // Tokens
  tokens_consumed_today: 2300000,
  tokens_remaining_total: 15600000,
  average_tokens_per_user: 2580,
  
  // Financeiro
  revenue_today: 1250.00,
  revenue_month: 45230.00,
  credits_purchased_today: 15,
  
  // Sistema
  proxy_response_time: 45, // ms
  litellm_response_time: 120, // ms
  error_rate: 0.02 // 2%
};
```

#### **Alertas Configurados**
```yaml
# Alertas críticos
alerts:
  - name: "High Error Rate"
    condition: error_rate > 0.05
    severity: critical
    
  - name: "Slow Response Time"
    condition: response_time > 1000
    severity: warning
    
  - name: "Database Connection"
    condition: db_connections < 1
    severity: critical
    
  - name: "Token Consumption Spike"
    condition: tokens_per_minute > 10000
    severity: warning
```

### 🔧 **Configurações Principais**

#### **Variáveis de Ambiente**
```bash
# Database
DATABASE_URL=postgresql://solaris:password@localhost:5432/ia_solaris
REDIS_URL=redis://localhost:6379

# LiteLLM
LITELLM_URL=http://localhost:4000
LITELLM_API_KEY=sk-litellm-key

# OpenAI
OPENAI_API_KEY=sk-openai-key
ANTHROPIC_API_KEY=sk-anthropic-key

# JWT
JWT_SECRET=your-super-secret-key
JWT_EXPIRES_IN=24h

# Email (Fase 2)
SMTP_HOST=smtp.gmail.com
SMTP_PORT=587
SMTP_USER=noreply@iasolaris.com.br
SMTP_PASS=app-password

# Stripe (Fase 2)
STRIPE_SECRET_KEY=sk_test_stripe_key
STRIPE_WEBHOOK_SECRET=whsec_webhook_secret
```

#### **Configuração LiteLLM**
```yaml
# litellm_config.yaml
model_list:
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: ${OPENAI_API_KEY}
      
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: openai/gpt-3.5-turbo
      api_key: ${OPENAI_API_KEY}
      
  - model_name: claude-3
    litellm_params:
      model: anthropic/claude-3-sonnet-20240229
      api_key: ${ANTHROPIC_API_KEY}

general_settings:
  database_url: ${DATABASE_URL}
  store_model_in_db: true
  
router_settings:
  routing_strategy: simple-shuffle
  model_group_alias:
    gpt-4: ["gpt-4"]
    gpt-3.5: ["gpt-3.5-turbo"]
    claude: ["claude-3"]
```

### 🚨 **Troubleshooting Comum**

#### **Problema 1: Tokens não atualizados**
![Troubleshooting Tokens](../assets/diagramas/1.ProblemaTokensnãosãoatualizadoscorretamente.png)

**Sintomas:**
- Contador não atualiza após uso
- Saldo incorreto na interface

**Soluções:**
1. Verificar logs do proxy
2. Validar conexão com PostgreSQL
3. Checar middleware de tokens

#### **Problema 2: Alertas não enviados**
![Troubleshooting Alertas](../assets/diagramas/2.ProblemaAlertasnãosãoenviados.png)

**Sintomas:**
- Modal de 80% não aparece
- Usuário não recebe avisos

**Soluções:**
1. Verificar cálculo de percentual
2. Validar headers HTTP
3. Checar JavaScript frontend

#### **Problema 3: Performance degradada**
![Troubleshooting Performance](../assets/diagramas/3.ProblemaPerformancedegradada.png)

**Sintomas:**
- Respostas lentas
- Timeouts frequentes

**Soluções:**
1. Verificar índices do banco
2. Otimizar queries SQL
3. Implementar cache Redis

### 📊 **Logs Estruturados**

#### **Formato de Log**
```json
{
  "timestamp": "2024-01-15T10:30:00Z",
  "level": "info",
  "service": "proxy-solaris",
  "user_id": "uuid-user-123",
  "action": "token_consumption",
  "details": {
    "tokens_consumed": 1250,
    "tokens_remaining": 248750,
    "model": "gpt-4",
    "response_time": 1200
  },
  "trace_id": "trace-abc-123"
}
```

#### **Níveis de Log**
- **ERROR** - Falhas críticas que impedem funcionamento
- **WARN** - Problemas que não impedem funcionamento
- **INFO** - Eventos importantes do sistema
- **DEBUG** - Informações detalhadas para desenvolvimento

### 📚 **Documentos de Referência**

- 📄 [PDF: Diagramas Técnicos Completos](../assets/pdfs/6-DiagramasMermaid-MVPHíbridoControledeTokensIASOLARIS-v1.00.pdf)

### 🔍 **Ferramentas de Debug**

#### **Comandos Úteis**
```bash
# Verificar logs do proxy
docker logs proxy-solaris -f

# Conectar no PostgreSQL
psql -h localhost -U solaris -d ia_solaris

# Verificar Redis
redis-cli ping

# Testar LiteLLM
curl -X POST http://localhost:4000/health

# Verificar métricas
curl http://localhost:4000/metrics
```

#### **Queries de Debug**
```sql
-- Verificar usuários com mais consumo
SELECT u.email, SUM(tu.tokens_used) as total_tokens
FROM users u
JOIN token_usage tu ON u.id = tu.user_id
WHERE tu.usage_date >= CURRENT_DATE - INTERVAL '7 days'
GROUP BY u.id, u.email
ORDER BY total_tokens DESC
LIMIT 10;

-- Verificar alertas não enviados
SELECT u.email, tu.tokens_used, tu.tokens_remaining
FROM users u
JOIN token_usage tu ON u.id = tu.user_id
WHERE (tu.tokens_used::float / (tu.tokens_used + tu.tokens_remaining)) >= 0.8
AND tu.usage_date = CURRENT_DATE;
```

---

### 🎯 **Conclusão**

Parabéns! Você agora tem **toda a documentação** necessária para implementar o MVP Híbrido:

✅ **Entendeu o negócio** e por que escolhemos esta abordagem  
✅ **Visualizou a arquitetura** e como os componentes se conectam  
✅ **Tem o guia passo a passo** para implementação  
✅ **Conhece todas as interfaces** necessárias  
✅ **Possui a referência técnica** completa  

### 🚀 **Próximos Passos**

1. **Clone este repositório** para seu ambiente
2. **Siga o guia de implementação** passo a passo
3. **Use os mockups** para criar as interfaces
4. **Consulte a referência** durante desenvolvimento
5. **Teste cada componente** conforme implementa

### 📞 **Suporte**

- **GitHub Issues** - Para dúvidas técnicas específicas
- **Email**: dev@iasolaris.com.br
- **Projeto**: [IA SOLARIS GitHub Project](https://github.com/orgs/Solaris-Empresa/projects/1/views/4)

---

### 📖 **Navegação**

- ⬅️ [Interfaces](../04-interfaces/)
- 🎯 [Visão do Negócio](../01-negocio/)
- 🏗️ [Arquitetura](../02-arquitetura/)
- 🚀 [Implementação](../03-implementacao/)
- 🏠 [Início](../../README.md)

