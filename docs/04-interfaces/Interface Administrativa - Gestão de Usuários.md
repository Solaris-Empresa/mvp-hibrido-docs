# Interface Administrativa - Gestão de Usuários

## Visão Geral

Este documento especifica a interface administrativa do sistema de controle de tokens da IA SOLARIS, focando na gestão completa de usuários, monitoramento de consumo e controles operacionais. A interface é projetada para administradores e gestores que precisam de visibilidade total sobre o uso da plataforma e capacidade de intervenção quando necessário.

## Dashboard Principal Administrativo

### Layout Geral

**Estrutura da Página:**
- Header com navegação principal e perfil do admin
- Sidebar com menu de funcionalidades
- Área principal com widgets e tabelas
- Footer com informações de sistema

**Widgets do Dashboard:**

1. **Resumo Geral (Cards Superiores)**
   - Total de usuários ativos
   - Consumo total de tokens no mês
   - Receita gerada
   - Alertas pendentes

2. **Gráficos de Monitoramento**
   - Consumo de tokens ao longo do tempo
   - Distribuição de uso por usuário
   - Tendências de crescimento
   - Performance do sistema

3. **Alertas e Notificações**
   - Usuários próximos ao limite
   - Problemas técnicos detectados
   - Transações pendentes
   - Relatórios de abuso

### Especificações dos Cards de Resumo

**Card 1: Usuários Ativos**
```
Título: "Usuários Ativos"
Valor Principal: 1,247
Subtítulo: "+12% vs mês anterior"
Ícone: 👥
Cor: Azul (#3B82F6)
Ação: Clique leva para lista completa de usuários
```

**Card 2: Tokens Consumidos**
```
Título: "Tokens Consumidos (Mês)"
Valor Principal: 847.2M
Subtítulo: "de 1.2B disponíveis"
Ícone: 🔥
Cor: Laranja (#F59E0B)
Ação: Clique leva para relatório detalhado
```

**Card 3: Receita Gerada**
```
Título: "Receita (Mês)"
Valor Principal: R$ 23.450
Subtítulo: "+8% vs mês anterior"
Ícone: 💰
Cor: Verde (#10B981)
Ação: Clique leva para relatório financeiro
```

**Card 4: Alertas Ativos**
```
Título: "Alertas Pendentes"
Valor Principal: 23
Subtítulo: "3 críticos, 20 avisos"
Ícone: ⚠️
Cor: Vermelho (#EF4444)
Ação: Clique leva para central de alertas
```

## Interface de Gestão de Usuários

### Lista de Usuários

**Tabela Principal:**

| Campo | Tipo | Largura | Ordenável | Filtrável |
|-------|------|---------|-----------|-----------|
| Avatar | Imagem | 60px | Não | Não |
| Nome | Texto | 200px | Sim | Sim |
| Email | Texto | 250px | Sim | Sim |
| Status | Badge | 100px | Sim | Sim |
| Plano | Badge | 120px | Sim | Sim |
| Tokens Usados | Barra + Número | 180px | Sim | Não |
| Último Acesso | Data | 150px | Sim | Sim |
| Ações | Botões | 120px | Não | Não |

**Estados de Status:**
- **Ativo:** Badge verde "Ativo"
- **Suspenso:** Badge amarelo "Suspenso"
- **Bloqueado:** Badge vermelho "Bloqueado"
- **Pendente:** Badge cinza "Pendente"

**Tipos de Plano:**
- **Básico:** Badge azul claro "Básico"
- **Pro:** Badge azul escuro "Pro"
- **Enterprise:** Badge roxo "Enterprise"
- **Trial:** Badge cinza "Trial"

### Filtros e Busca

**Barra de Busca:**
- Placeholder: "Buscar por nome, email ou ID..."
- Busca em tempo real (debounce de 300ms)
- Suporte a operadores: "nome:João", "status:ativo"

**Filtros Laterais:**
```
Status da Conta:
☐ Ativo (1,247)
☐ Suspenso (23)
☐ Bloqueado (8)
☐ Pendente (45)

Tipo de Plano:
☐ Básico (856)
☐ Pro (324)
☐ Enterprise (67)
☐ Trial (123)

Consumo de Tokens:
☐ Baixo (0-30%)
☐ Médio (31-70%)
☐ Alto (71-90%)
☐ Crítico (91-100%)

Data de Cadastro:
☐ Última semana
☐ Último mês
☐ Últimos 3 meses
☐ Mais de 6 meses
```

### Detalhes do Usuário

**Modal de Informações Completas:**

**Aba 1: Informações Gerais**
```
Dados Pessoais:
- Nome completo
- Email
- Telefone
- Data de nascimento
- Endereço completo

Dados da Conta:
- ID do usuário
- Data de cadastro
- Último login
- IP do último acesso
- Dispositivo utilizado
```

**Aba 2: Consumo e Tokens**
```
Resumo Mensal:
- Limite mensal: 1.000.000 tokens
- Consumidos: 750.000 tokens (75%)
- Restantes: 250.000 tokens
- Tokens adicionais: 50.000 tokens

Histórico de Consumo:
- Gráfico dos últimos 30 dias
- Picos de uso identificados
- Padrões de comportamento

Histórico de Compras:
- Data | Quantidade | Valor | Status
- Tabela com todas as transações
```

**Aba 3: Atividade e Logs**
```
Atividade Recente:
- Timestamp | Ação | Detalhes
- Login/logout
- Consultas realizadas
- Compras efetuadas
- Alterações de perfil

Logs de Sistema:
- Alertas gerados
- Bloqueios aplicados
- Intervenções administrativas
```

### Ações Administrativas

**Ações Rápidas (Botões na Tabela):**
- **Visualizar:** Ícone de olho - Abre modal de detalhes
- **Editar:** Ícone de lápis - Permite edição de dados
- **Suspender/Ativar:** Ícone de play/pause - Alterna status
- **Menu:** Ícone de três pontos - Ações adicionais

**Ações do Menu Expandido:**
```
👤 Ver Perfil Completo
✏️ Editar Informações
🔄 Resetar Tokens do Mês
➕ Adicionar Tokens Bonus
📧 Enviar Notificação
📊 Relatório Detalhado
🚫 Suspender Conta
❌ Bloquear Conta
🗑️ Excluir Usuário
```

### Formulários de Edição

**Formulário de Edição de Usuário:**

**Seção 1: Dados Básicos**
```html
<form class="user-edit-form">
  <div class="form-section">
    <h3>Informações Pessoais</h3>
    <div class="form-row">
      <input type="text" name="firstName" label="Nome" required>
      <input type="text" name="lastName" label="Sobrenome" required>
    </div>
    <div class="form-row">
      <input type="email" name="email" label="Email" required>
      <input type="tel" name="phone" label="Telefone">
    </div>
  </div>
</form>
```

**Seção 2: Configurações da Conta**
```html
<div class="form-section">
  <h3>Configurações da Conta</h3>
  <div class="form-row">
    <select name="status" label="Status da Conta">
      <option value="active">Ativo</option>
      <option value="suspended">Suspenso</option>
      <option value="blocked">Bloqueado</option>
    </select>
    <select name="plan" label="Plano">
      <option value="basic">Básico</option>
      <option value="pro">Pro</option>
      <option value="enterprise">Enterprise</option>
    </select>
  </div>
</div>
```

**Seção 3: Controle de Tokens**
```html
<div class="form-section">
  <h3>Gestão de Tokens</h3>
  <div class="form-row">
    <input type="number" name="monthlyLimit" label="Limite Mensal" min="100000" max="10000000">
    <input type="number" name="bonusTokens" label="Tokens Bonus" min="0">
  </div>
  <div class="form-row">
    <textarea name="adjustmentReason" label="Motivo do Ajuste" rows="3" placeholder="Descreva o motivo da alteração..."></textarea>
  </div>
</div>
```

## Interface de Monitoramento em Tempo Real

### Dashboard de Monitoramento

**Métricas em Tempo Real:**

1. **Requisições por Segundo**
   - Gráfico de linha em tempo real
   - Valores atuais e médias
   - Alertas de picos anômalos

2. **Distribuição de Carga**
   - Gráfico de pizza por modelo de IA
   - Percentual de uso por endpoint
   - Identificação de gargalos

3. **Status dos Serviços**
   - Indicadores verde/vermelho
   - Tempo de resposta médio
   - Disponibilidade (uptime)

4. **Alertas Ativos**
   - Lista em tempo real
   - Classificação por criticidade
   - Ações de resolução

### Central de Alertas

**Tipos de Alerta:**

**Críticos (Vermelho):**
- Sistema fora do ar
- Falha na cobrança
- Usuário com consumo anômalo
- Tentativa de fraude detectada

**Avisos (Amarelo):**
- Performance degradada
- Usuário próximo ao limite
- Falha em email de notificação
- Backup não realizado

**Informativos (Azul):**
- Novo usuário cadastrado
- Compra de tokens realizada
- Atualização de sistema
- Relatório mensal gerado

**Interface de Alerta:**
```
[🔴] CRÍTICO - Sistema de Pagamento Indisponível
Detectado em: 14:32:15
Duração: 00:05:23
Usuários afetados: 23
Ações: [Investigar] [Escalar] [Resolver]
Descrição: Gateway de pagamento retornando erro 500...

[🟡] AVISO - Usuário com Consumo Alto
Usuário: João Silva (ID: 12345)
Consumo: 950.000 tokens (95%)
Ações: [Contatar] [Ajustar Limite] [Monitorar]
Descrição: Usuário está próximo do limite mensal...
```

## Relatórios e Analytics

### Relatório de Consumo

**Filtros Disponíveis:**
- Período: Dia, semana, mês, trimestre, ano
- Usuários: Específicos ou grupos
- Modelos de IA: GPT-4, Claude, etc.
- Tipo de uso: Chat, API, integração

**Visualizações:**
1. **Gráfico de Linha:** Consumo ao longo do tempo
2. **Gráfico de Barras:** Top usuários consumidores
3. **Heatmap:** Horários de maior uso
4. **Tabela Detalhada:** Dados granulares

### Relatório Financeiro

**Métricas Principais:**
- Receita total por período
- Receita por tipo de plano
- Receita por tokens adicionais
- Previsão de receita

**Análises:**
- Taxa de conversão (trial → pago)
- Churn rate por plano
- Lifetime value (LTV) por usuário
- Custo de aquisição (CAC)

### Exportação de Dados

**Formatos Disponíveis:**
- CSV para análise em planilhas
- PDF para relatórios executivos
- JSON para integração com outros sistemas
- Excel com formatação avançada

**Agendamento de Relatórios:**
- Frequência: Diário, semanal, mensal
- Destinatários: Lista de emails
- Filtros pré-configurados
- Entrega automática

## Configurações do Sistema

### Configurações Gerais

**Limites Globais:**
```
Limite padrão mensal: 1.000.000 tokens
Limite máximo por usuário: 10.000.000 tokens
Limite mínimo por usuário: 100.000 tokens
Percentual de alerta: 80%
Percentual de bloqueio: 100%
```

**Configurações de Email:**
```
Servidor SMTP: smtp.gmail.com
Porta: 587
Autenticação: TLS
Remetente: noreply@iasolaris.com
Template de alerta: [Selecionar]
Template de bloqueio: [Selecionar]
```

**Configurações de Pagamento:**
```
Gateway principal: Stripe
Gateway secundário: PayPal
Moeda: BRL (Real Brasileiro)
Taxa de processamento: 3.5%
Webhook URL: https://api.iasolaris.com/webhooks/payment
```

### Gestão de Permissões

**Níveis de Acesso:**

**Super Admin:**
- Acesso total ao sistema
- Configurações globais
- Gestão de outros admins
- Relatórios financeiros completos

**Admin:**
- Gestão de usuários
- Monitoramento de consumo
- Relatórios operacionais
- Configurações básicas

**Operador:**
- Visualização de dashboards
- Suporte a usuários
- Relatórios básicos
- Sem acesso a configurações

**Suporte:**
- Acesso apenas a tickets
- Histórico de usuários
- Logs de sistema
- Sem acesso a dados financeiros

## Especificações Técnicas

### Arquitetura da Interface

**Frontend:**
- Framework: React 18
- Estado: Redux Toolkit
- Roteamento: React Router v6
- UI Library: Tailwind CSS + Headless UI
- Gráficos: Chart.js / D3.js
- Tabelas: React Table v8

**Comunicação com Backend:**
- API REST com autenticação JWT
- WebSocket para dados em tempo real
- Polling para atualizações periódicas
- Cache com React Query

### Estrutura de Componentes

```
AdminDashboard/
├── Layout/
│   ├── Header.jsx
│   ├── Sidebar.jsx
│   └── Footer.jsx
├── Dashboard/
│   ├── StatsCards.jsx
│   ├── Charts.jsx
│   └── AlertsPanel.jsx
├── Users/
│   ├── UsersList.jsx
│   ├── UserDetails.jsx
│   ├── UserForm.jsx
│   └── UserActions.jsx
├── Monitoring/
│   ├── RealTimeMetrics.jsx
│   ├── AlertsCenter.jsx
│   └── SystemStatus.jsx
├── Reports/
│   ├── ConsumptionReport.jsx
│   ├── FinancialReport.jsx
│   └── ExportOptions.jsx
└── Settings/
    ├── GeneralSettings.jsx
    ├── PermissionsManager.jsx
    └── SystemConfig.jsx
```

### APIs Necessárias

**Endpoints de Usuários:**
```
GET /api/admin/users - Lista usuários com filtros
GET /api/admin/users/:id - Detalhes de usuário específico
PUT /api/admin/users/:id - Atualiza dados do usuário
POST /api/admin/users/:id/tokens - Adiciona tokens bonus
POST /api/admin/users/:id/suspend - Suspende usuário
POST /api/admin/users/:id/activate - Ativa usuário
DELETE /api/admin/users/:id - Remove usuário
```

**Endpoints de Monitoramento:**
```
GET /api/admin/metrics/realtime - Métricas em tempo real
GET /api/admin/alerts - Lista de alertas ativos
POST /api/admin/alerts/:id/resolve - Resolve alerta
GET /api/admin/system/status - Status dos serviços
GET /api/admin/system/health - Health check completo
```

**Endpoints de Relatórios:**
```
GET /api/admin/reports/consumption - Relatório de consumo
GET /api/admin/reports/financial - Relatório financeiro
POST /api/admin/reports/export - Exporta relatório
GET /api/admin/reports/scheduled - Lista relatórios agendados
POST /api/admin/reports/schedule - Agenda novo relatório
```

## Testes e Validação

### Cenários de Teste

**Teste 1: Gestão de Usuários**
- Criar, editar e excluir usuários
- Aplicar diferentes filtros na lista
- Testar ações em lote
- Verificar permissões por nível de acesso

**Teste 2: Monitoramento em Tempo Real**
- Simular picos de tráfego
- Testar alertas automáticos
- Verificar atualização de métricas
- Validar performance da interface

**Teste 3: Relatórios**
- Gerar relatórios com diferentes filtros
- Testar exportação em todos os formatos
- Verificar agendamento de relatórios
- Validar precisão dos dados

### Métricas de Performance

- **Tempo de carregamento:** < 2 segundos
- **Atualização em tempo real:** < 1 segundo
- **Responsividade:** Suporte a tablets e desktops
- **Disponibilidade:** 99.9% uptime

---

**Autor:** Manus AI  
**Data:** Janeiro 2024  
**Versão:** 1.0

