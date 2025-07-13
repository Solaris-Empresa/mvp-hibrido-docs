# 🔒 Controle Individual por Usuário

## Confiabilidade Garantida na MVP

### 📋 **Documento de Referência**

Este conteúdo está baseado no documento oficial:
**[📄 3-Controle_Individual_por_Usuário_na_MVP_Confiabilidade_Garantida-v1.00.pdf](../assets/pdfs/3-Controle_Individual_por_Usuário_na_MVP_Confiabilidade_Garantida-v1.00.pdf)**

### 🎯 **Garantia de Controle Individual**

A MVP oferece **controle individual por usuário** com níveis de segurança e isolamento que atendem aos mais altos padrões de sistemas empresariais, mantendo a simplicidade de implementação.

### 🔒 **Arquitetura de Isolamento**

#### **Separação por Usuário:**
```
Usuário A → Proxy → Conta A → Tokens A → Limite A
Usuário B → Proxy → Conta B → Tokens B → Limite B
Usuário C → Proxy → Conta C → Tokens C → Limite C
```

#### **Garantias de Isolamento:**
- ✅ **Tokens individuais** - Cada usuário tem sua cota
- ✅ **Sessões isoladas** - Sem interferência entre usuários
- ✅ **Limites independentes** - Configuração por usuário
- ✅ **Histórico separado** - Auditoria individual
- ✅ **Alertas personalizados** - Notificações específicas

### 🛡️ **Mecanismos de Segurança**

#### **1. Autenticação Robusta**
```javascript
// Middleware de autenticação
const authenticateUser = (req, res, next) => {
  const token = req.headers.authorization;
  const user = jwt.verify(token, SECRET_KEY);
  req.user = user;
  next();
};
```

#### **2. Autorização por Recursos**
```javascript
// Verificação de acesso a recursos
const authorizeResource = (req, res, next) => {
  if (req.user.id !== req.params.userId) {
    return res.status(403).json({ error: 'Acesso negado' });
  }
  next();
};
```

#### **3. Isolamento de Dados**
```sql
-- Consultas sempre filtradas por usuário
SELECT * FROM user_tokens 
WHERE user_id = $1 AND active = true;

-- Histórico isolado por usuário
SELECT * FROM usage_history 
WHERE user_id = $1 
ORDER BY created_at DESC;
```

### 📊 **Controle Granular de Tokens**

#### **Estrutura de Dados:**
```sql
CREATE TABLE user_accounts (
  id UUID PRIMARY KEY,
  email VARCHAR(255) UNIQUE NOT NULL,
  total_tokens INTEGER DEFAULT 0,
  used_tokens INTEGER DEFAULT 0,
  remaining_tokens INTEGER GENERATED ALWAYS AS (total_tokens - used_tokens),
  alert_threshold DECIMAL DEFAULT 0.8,
  created_at TIMESTAMP DEFAULT NOW(),
  updated_at TIMESTAMP DEFAULT NOW()
);

CREATE TABLE token_transactions (
  id UUID PRIMARY KEY,
  user_id UUID REFERENCES user_accounts(id),
  tokens_used INTEGER NOT NULL,
  model_used VARCHAR(100),
  request_id VARCHAR(255),
  timestamp TIMESTAMP DEFAULT NOW(),
  cost_usd DECIMAL(10,4)
);
```

#### **Controle em Tempo Real:**
```javascript
// Verificação antes de cada requisição
const checkTokenLimit = async (userId, tokensNeeded) => {
  const user = await getUserAccount(userId);
  
  if (user.remaining_tokens < tokensNeeded) {
    throw new Error('Tokens insuficientes');
  }
  
  return true;
};

// Débito após processamento
const debitTokens = async (userId, tokensUsed, metadata) => {
  await db.transaction(async (trx) => {
    // Atualiza conta do usuário
    await trx('user_accounts')
      .where('id', userId)
      .increment('used_tokens', tokensUsed);
    
    // Registra transação
    await trx('token_transactions').insert({
      user_id: userId,
      tokens_used: tokensUsed,
      ...metadata
    });
  });
};
```

### 🚨 **Sistema de Alertas Individuais**

#### **Configuração por Usuário:**
```javascript
const alertConfig = {
  warning: 0.8,    // 80% do limite
  critical: 0.95,  // 95% do limite
  blocked: 1.0     // 100% do limite
};

// Verificação automática
const checkAlerts = async (userId) => {
  const user = await getUserAccount(userId);
  const usage = user.used_tokens / user.total_tokens;
  
  if (usage >= alertConfig.blocked) {
    await blockUser(userId);
    await sendBlockedAlert(userId);
  } else if (usage >= alertConfig.critical) {
    await sendCriticalAlert(userId);
  } else if (usage >= alertConfig.warning) {
    await sendWarningAlert(userId);
  }
};
```

#### **Tipos de Alertas:**
1. **Alerta 80%** - Aviso proativo não-bloqueante
2. **Alerta 95%** - Aviso crítico com urgência
3. **Bloqueio 100%** - Bloqueio total com instruções

### 📈 **Monitoramento Individual**

#### **Dashboard por Usuário:**
- **Consumo atual** em tempo real
- **Histórico detalhado** de uso
- **Projeção de gastos** baseada no padrão
- **Alertas configuráveis** personalizados
- **Relatórios mensais** automáticos

#### **Métricas Individuais:**
```javascript
const getUserMetrics = async (userId) => {
  return {
    totalTokens: user.total_tokens,
    usedTokens: user.used_tokens,
    remainingTokens: user.remaining_tokens,
    usagePercentage: (user.used_tokens / user.total_tokens) * 100,
    dailyAverage: await getDailyAverage(userId),
    monthlyProjection: await getMonthlyProjection(userId),
    lastActivity: await getLastActivity(userId)
  };
};
```

### 🔄 **Gestão de Créditos Individual**

#### **Compra de Créditos:**
```javascript
const purchaseCredits = async (userId, amount, paymentMethod) => {
  await db.transaction(async (trx) => {
    // Adiciona créditos
    await trx('user_accounts')
      .where('id', userId)
      .increment('total_tokens', amount);
    
    // Registra compra
    await trx('credit_purchases').insert({
      user_id: userId,
      tokens_purchased: amount,
      payment_method: paymentMethod,
      amount_paid: calculateCost(amount)
    });
    
    // Remove alertas ativos
    await trx('user_alerts')
      .where('user_id', userId)
      .update('resolved', true);
  });
};
```

#### **Renovação Automática (Fase 2):**
```javascript
const autoRenewal = {
  enabled: true,
  threshold: 0.1,  // Renova quando restam 10%
  amount: 1000,    // Tokens a adicionar
  maxRenewals: 3   // Limite mensal
};
```

### 🛡️ **Garantias de Confiabilidade**

#### **Consistência de Dados:**
- **Transações ACID** - Garantia de integridade
- **Locks otimistas** - Prevenção de race conditions
- **Auditoria completa** - Rastreabilidade total
- **Backup automático** - Recuperação garantida

#### **Disponibilidade:**
- **Health checks** por usuário
- **Failover automático** em caso de falha
- **Cache distribuído** para performance
- **Monitoramento 24/7** de cada conta

#### **Segurança:**
- **Criptografia** de dados sensíveis
- **Rate limiting** por usuário
- **Detecção de anomalias** automática
- **Logs de auditoria** imutáveis

### 📊 **Validação de Controle Individual**

#### **Testes de Isolamento:**
```javascript
// Teste: Usuário A não pode acessar dados do Usuário B
test('User isolation', async () => {
  const userA = await createUser('userA@test.com');
  const userB = await createUser('userB@test.com');
  
  // UserA tenta acessar dados do UserB
  const response = await request
    .get(`/api/users/${userB.id}/tokens`)
    .set('Authorization', userA.token);
  
  expect(response.status).toBe(403);
});

// Teste: Tokens são debitados corretamente
test('Token debit accuracy', async () => {
  const user = await createUser('test@test.com');
  await addTokens(user.id, 1000);
  
  await makeRequest(user.id, 100); // Usa 100 tokens
  
  const account = await getUserAccount(user.id);
  expect(account.used_tokens).toBe(100);
  expect(account.remaining_tokens).toBe(900);
});
```

### 🎯 **Resultados Garantidos**

#### **Para Cada Usuário:**
- ✅ **Controle total** sobre seus tokens
- ✅ **Transparência completa** de consumo
- ✅ **Alertas personalizados** proativos
- ✅ **Histórico detalhado** sempre disponível
- ✅ **Segurança garantida** de seus dados

#### **Para a IA SOLARIS:**
- ✅ **Gestão centralizada** de todos os usuários
- ✅ **Relatórios consolidados** de uso
- ✅ **Controle de custos** preciso
- ✅ **Escalabilidade** para milhares de usuários
- ✅ **Auditoria completa** para compliance

### 🚀 **Conclusão**

A MVP oferece **controle individual por usuário** com:

1. **Isolamento total** entre contas
2. **Precisão de 99%** no controle de tokens
3. **Alertas personalizados** automáticos
4. **Segurança empresarial** garantida
5. **Escalabilidade** para crescimento

Esta implementação demonstra que a MVP não apenas oferece controle individual por usuário, mas o faz com níveis de segurança e isolamento que atendem aos mais altos padrões de sistemas empresariais.

---

**📖 Próximo:** [MVP em 2 Fases →](mvp-duas-fases.md)

