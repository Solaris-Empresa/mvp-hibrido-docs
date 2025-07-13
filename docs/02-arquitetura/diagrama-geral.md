# 🏗️ Diagrama Geral da Arquitetura
## MVP Híbrido - Controle de Tokens IA SOLARIS

### 📊 **Visão Macro do Sistema**

![Arquitetura MVP Híbrido](../assets/diagramas/01-arquitetura-geral.png)

### 🎯 **Conceito Principal**

A arquitetura híbrida foi projetada para **NÃO modificar o LibreChat**, mantendo-o como está e adicionando uma camada inteligente de controle.

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   LibreChat     │    │  Proxy Inteli-  │    │    LiteLLM      │    │     OpenAI      │
│   (Original)    │───▶│  gente SOLARIS  │───▶│   (Contador)    │───▶│   (Provedor)    │
│                 │    │                 │    │                 │    │                 │
└─────────────────┘    └─────────────────┘    └─────────────────┘    └─────────────────┘
        ▲                        │                        │                        │
        │                        ▼                        ▼                        ▼
        │               ┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
        │               │   PostgreSQL    │    │     Redis       │    │   Resposta AI   │
        └───────────────│   (Usuários)    │    │    (Cache)      │    │                 │
                        │                 │    │                 │    │                 │
                        └─────────────────┘    └─────────────────┘    └─────────────────┘
```

### 🔄 **Fluxo de Funcionamento**

#### **1. Requisição do Usuário**
- Usuário faz pergunta no LibreChat
- LibreChat envia para Proxy SOLARIS (ao invés de OpenAI direto)

#### **2. Verificação de Tokens**
- Proxy consulta PostgreSQL: usuário tem tokens?
- Se SIM: continua fluxo
- Se NÃO: bloqueia e retorna modal de compra

#### **3. Processamento Inteligente**
- Proxy envia requisição para LiteLLM
- LiteLLM conta tokens precisamente (99% vs 60%)
- LiteLLM envia para OpenAI

#### **4. Resposta e Contabilização**
- OpenAI responde para LiteLLM
- LiteLLM conta tokens da resposta
- Proxy atualiza saldo no PostgreSQL
- Resposta chega ao LibreChat

### 🎯 **Vantagens da Arquitetura**

| Aspecto | Benefício |
|---------|-----------|
| **LibreChat Inalterado** | Zero modificações no código original |
| **Precisão de Tokens** | 99% vs 60% do LibreChat nativo |
| **Manutenibilidade** | Updates do LibreChat não afetam sistema |
| **Escalabilidade** | Proxy pode servir múltiplas instâncias |
| **Flexibilidade** | Fácil adicionar novos provedores |

### 🔧 **Componentes Técnicos**

#### **Proxy Inteligente SOLARIS**
- **Linguagem**: Node.js/Express
- **Função**: Interceptar e controlar requisições
- **Responsabilidades**:
  - Autenticação de usuários
  - Verificação de saldo de tokens
  - Aplicação de regras de negócio
  - Logging e monitoramento

#### **LiteLLM (Contador Preciso)**
- **Função**: Contabilização precisa de tokens
- **Vantagens**:
  - Suporte a múltiplos provedores
  - Contagem precisa de tokens
  - Rate limiting nativo
  - Métricas detalhadas

#### **PostgreSQL (Banco Principal)**
- **Tabelas principais**:
  - `users` - Dados dos usuários
  - `token_usage` - Histórico de consumo
  - `subscriptions` - Planos e renovações
  - `transactions` - Compras de créditos

#### **Redis (Cache e Sessões)**
- **Uso**:
  - Cache de saldos de tokens
  - Sessões de usuário
  - Rate limiting
  - Dados temporários

### 📈 **Escalabilidade**

```
                    ┌─────────────────┐
                    │   Load Balancer │
                    └─────────┬───────┘
                              │
              ┌───────────────┼───────────────┐
              ▼               ▼               ▼
    ┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
    │ Proxy SOLARIS 1 │ │ Proxy SOLARIS 2 │ │ Proxy SOLARIS N │
    └─────────────────┘ └─────────────────┘ └─────────────────┘
              │               │               │
              └───────────────┼───────────────┘
                              ▼
                    ┌─────────────────┐
                    │   PostgreSQL    │
                    │   (Cluster)     │
                    └─────────────────┘
```

### 🔒 **Segurança**

#### **Autenticação**
- JWT tokens para sessões
- Integração com sistema de auth do LibreChat
- Rate limiting por usuário

#### **Autorização**
- Verificação de saldo antes de cada requisição
- Logs detalhados de todas as operações
- Isolamento de dados por usuário

### 📊 **Monitoramento**

#### **Métricas Coletadas**
- Tokens consumidos por usuário/hora/dia
- Latência das requisições
- Taxa de erro por provedor
- Uso de cache Redis

#### **Alertas Automáticos**
- Usuário atingindo 80% do limite
- Usuário sem tokens (100%)
- Falhas de sistema
- Performance degradada

### 🎯 **Por que esta Arquitetura é Simples**

#### **Para Desenvolvedores**
- ✅ **Não mexe no LibreChat** - zero risco de quebrar
- ✅ **Componentes independentes** - fácil de testar
- ✅ **Tecnologias conhecidas** - Node.js, PostgreSQL, Redis
- ✅ **Documentação completa** - tudo explicado aqui

#### **Para Manutenção**
- ✅ **Updates independentes** - LibreChat atualiza sem afetar proxy
- ✅ **Logs centralizados** - fácil debug
- ✅ **Rollback simples** - proxy pode ser desligado
- ✅ **Testes isolados** - cada componente testável

### 🚀 **Próximos Passos**

1. **[Componentes Principais](componentes-principais.md)** - Detalhes de cada componente
2. **[Fluxo de Dados](fluxo-dados.md)** - Como os dados fluem no sistema
3. **[Estados do Sistema](estados-sistema.md)** - Estados possíveis e transições

---

**💡 Esta arquitetura garante controle preciso de tokens mantendo a simplicidade e confiabilidade do LibreChat original.**

