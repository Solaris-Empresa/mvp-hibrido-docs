# 🏗️ Arquitetura e Conceitos
## MVP Híbrido - Controle de Tokens IA SOLARIS

### 📋 **Índice desta Seção**

1. [Diagrama Geral da Arquitetura](diagrama-geral.md)
2. [Componentes Principais](https://github.com/Solaris-Empresa/mvp-hibrido-docs/blob/main/docs/assets/diagramas/Diagrama%20de%20Componentes%20T%C3%A9cnicos.png)

---

### 🎯 **Objetivo desta Seção**

Agora que você entende o **contexto de negócio**, vamos mergulhar na **arquitetura técnica**:

- **Como os componentes** se conectam
- **Qual o fluxo** de dados e requisições
- **Quais são os estados** do sistema
- **Como implementar** cada parte

### 🏗️ **Visão Geral da Arquitetura**

![Arquitetura MVP Híbrido](https://github.com/Solaris-Empresa/mvp-hibrido-docs/blob/main/docs/assets/diagramas/Diagrama%20de%20Arquitetura%20MVP%20H%C3%ADbrido.png)

### 🎯 **Princípios Fundamentais**

#### **1. Separação de Responsabilidades**
- **LibreChat** → Interface e experiência do usuário
- **Proxy IA SOLARIS** → Controle de tokens e regras de negócio
- **LiteLLM** → Contabilização precisa e roteamento
- **PostgreSQL** → Persistência de dados

#### **2. Baixo Acoplamento**
- Cada componente pode ser **desenvolvido independentemente**
- **Falhas isoladas** não afetam todo o sistema
- **Updates** podem ser feitos sem parar outros serviços

#### **3. Alta Observabilidade**
- **Logs detalhados** em cada componente
- **Métricas** de consumo em tempo real
- **Alertas** automáticos para problemas

### 📊 **Componentes Principais**

| Componente | Responsabilidade | Tecnologia |
|------------|------------------|------------|
| **LibreChat** | Interface do usuário | React/Node.js |
| **Proxy IA SOLARIS** | Controle de tokens | Express.js |
| **LiteLLM** | Roteamento e contabilização | Python |
| **PostgreSQL** | Banco de dados | SQL |
| **Redis** | Cache e sessões | NoSQL |

### 🔄 **Fluxos Principais**

#### **Fluxo Normal (Tokens Disponíveis)**
```mermaid
graph TD
    A[Usuário envia mensagem] --> B[LibreChat recebe]
    B --> C[Proxy verifica tokens]
    C --> D{Tokens disponíveis?}
    D -->|Sim| E[LiteLLM processa]
    E --> F[API externa]
    F --> G[Resposta + contagem]
    G --> H[Atualiza saldo]
    H --> I[Retorna para usuário]
```

#### **Fluxo de Alerta (80% consumido)**
```mermaid
graph TD
    A[Verificação de saldo] --> B{Saldo < 20%?}
    B -->|Sim| C[Gera alerta]
    C --> D[Envia para interface]
    D --> E[Modal de aviso]
    E --> F[Usuário continua]
```

#### **Fluxo de Bloqueio (100% consumido)**
```mermaid
graph TD
    A[Requisição recebida] --> B[Verifica saldo]
    B --> C{Saldo = 0?}
    C -->|Sim| D[Bloqueia requisição]
    D --> E[Retorna erro 429]
    E --> F[Modal de bloqueio]
    F --> G[Instrução para compra]
```

### 🎨 **Diagramas Técnicos Disponíveis**

Esta seção inclui **10+ diagramas técnicos** organizados por complexidade:

#### **📊 Conceituais (Fácil)**
- [Arquitetura Geral](https://github.com/Solaris-Empresa/mvp-hibrido-docs/blob/main/docs/assets/diagramas/Diagrama%20de%20Arquitetura%20MVP%20H%C3%ADbrido.png)
- [Jornada do Usuário](../assets/diagramas/JornadaCompletadoUsuário-Fase1----Manual---+Fase2---Automática.png)
- [Processo de Negócio](../assets/diagramas/ProcessodeNegócioGestãoCompletadeTokens.png)
- [Diagrama de Estados](https://github.com/Solaris-Empresa/mvp-hibrido-docs/blob/main/docs/assets/diagramas/Estados%20do%20Usu%C3%A1rio%20no%20Sistema.png)
- [Fase 1- ] [(https://github.com/Solaris-Empresa/mvp-hibrido-docs/blob/main/docs/assets/diagramas/Processo%20de%20Neg%C3%B3cio%20Ciclo%20Mensal%20de%20Tokens.png)](https://github.com/Solaris-Empresa/mvp-hibrido-docs/blob/main/docs/assets/diagramas/Processo%20Administra%C3%A7%C3%A3o%20de%20Cr%C3%A9ditos%20(Fase%201%20-%20Manual).png)
- [Fase 2]- (https://github.com/Solaris-Empresa/mvp-hibrido-docs/blob/main/docs/assets/diagramas/Processo%20Integra%C3%A7%C3%A3o%20com%20Stripe%20(Fase%202).png
- 

#### **🔧 Técnicos (Médio)**
- [Componentes Técnicos](https://github.com/Solaris-Empresa/mvp-hibrido-docs/blob/main/docs/assets/diagramas/Diagrama%20de%20Componentes%20T%C3%A9cnicos.png)


#### **⚙️ Implementação (Avançado)**
- [Deployment](https://github.com/Solaris-Empresa/mvp-hibrido-docs/blob/main/docs/assets/diagramas/Diagrama%20de%20Deployment%20(Arquitetura%20de%20Produ%C3%A7%C3%A3o).png)
- [Segurança](https://github.com/Solaris-Empresa/mvp-hibrido-docs/blob/main/docs/assets/diagramas/Diagrama%20de%20Seguran%C3%A7a%20e%20Autentica%C3%A7%C3%A3o.png)
- [Monitoramento](https://github.com/Solaris-Empresa/mvp-hibrido-docs/blob/main/docs/assets/diagramas/Estados%20do%20Sistema%20de%20Monitoramento.png)

### 🎯 **Estados do Sistema**

O sistema opera em diferentes estados baseados no consumo:

#### **🟢 Estado Normal (0-79% consumido)**
- Requisições processadas normalmente
- Interface mostra saldo disponível
- Sem alertas ou bloqueios

#### **🟡 Estado de Alerta (80-99% consumido)**
- Requisições ainda processadas
- Modal de alerta exibido
- Opção de compra de créditos

#### **🔴 Estado de Bloqueio (100% consumido)**
- Requisições bloqueadas
- Modal de bloqueio exibido
- Instrução para compra via email

---

### 🚀 **Próximo Passo**

Agora que você entende a **arquitetura geral**, vamos para a **implementação prática**:

**➡️ [Guia de Implementação](../03-implementacao/)**

---

### 📖 **Navegação**

- ⬅️ [Visão do Negócio](../01-negocio/)
- ➡️ [Implementação](../03-implementacao/)
- 🎨 [Interfaces](../04-interfaces/)
- 🔧 [Referência](../05-referencia/)
- 🏠 [Início](../../README.md)

