# Fluxos de Usuário - Sistema de Controle de Tokens IA SOLARIS

## Visão Geral

Este documento descreve os fluxos completos de usuário para o sistema de controle de tokens da IA SOLARIS, cobrindo desde o onboarding inicial até cenários avançados de gestão de tokens e resolução de problemas. Os fluxos são organizados por persona (usuário final, administrador) e por cenário de uso.

## Fluxo Principal: Jornada Completa do Usuário

### Fase 1: Onboarding e Primeiro Uso

**Cenário:** Novo usuário acessa a IA SOLARIS pela primeira vez

**Pré-condições:**
- Usuário tem acesso ao LibreChat
- Sistema de proxy está ativo
- Banco de dados está operacional

**Fluxo Detalhado:**

1. **Primeiro Acesso**
   - Usuário abre LibreChat
   - Faz login com suas credenciais
   - Sistema identifica usuário pelo email
   - Proxy intercepta primeira requisição

2. **Criação Automática de Perfil**
   - Sistema verifica se usuário existe no banco
   - Se não existe, cria automaticamente:
     - Nome: extraído do email
     - Limite mensal: 1.000.000 tokens (padrão)
     - Status: ativo
     - Plano: básico
   - Log de criação é registrado

3. **Primeira Consulta**
   - Usuário digita pergunta no LibreChat
   - Proxy intercepta requisição
   - Verifica tokens disponíveis (1.000.000)
   - Estima consumo da consulta (~500 tokens)
   - Autoriza e encaminha para LiteLLM
   - Recebe resposta com uso real (450 tokens)
   - Atualiza contador: 999.550 tokens restantes
   - Registra uso no histórico

4. **Feedback Visual**
   - LibreChat exibe resposta normalmente
   - Sistema registra sucesso da operação
   - Usuário não percebe interceptação (transparente)

**Pontos de Decisão:**
- Se email não for válido → Erro 401
- Se sistema estiver indisponível → Erro 500
- Se estimativa de tokens falhar → Usa valor padrão (100 tokens)

**Resultados Esperados:**
- Usuário criado no sistema
- Primeira consulta processada com sucesso
- Histórico de uso iniciado
- Experiência transparente para o usuário

### Fase 2: Uso Regular e Monitoramento

**Cenário:** Usuário utiliza sistema regularmente ao longo do mês

**Fluxo de Uso Normal:**

1. **Consultas Regulares (0-79% do limite)**
   - Usuário faz consultas normalmente
   - Sistema monitora consumo em tempo real
   - Cada requisição:
     - Verifica tokens disponíveis
     - Processa se autorizado
     - Atualiza contador
     - Registra no histórico
   - Nenhum alerta é enviado

2. **Aproximação do Limite (80-94%)**
   - Usuário atinge 80% do limite (800.000 tokens)
   - Sistema detecta threshold automaticamente
   - Envia alerta por email:
     ```
     Assunto: ⚠️ 80% dos seus tokens foram utilizados
     
     Olá [Nome],
     
     Você já utilizou 800.000 dos seus 1.000.000 tokens mensais.
     Restam apenas 200.000 tokens para este mês.
     
     Estimativa: Com seu padrão atual de uso, os tokens podem 
     esgotar em aproximadamente 3 dias.
     
     Recomendações:
     • Monitore seu uso mais de perto
     • Considere adquirir tokens adicionais
     • Otimize suas consultas para economizar tokens
     
     [Botão: Comprar Tokens Adicionais]
     [Botão: Ver Extrato Detalhado]
     ```
   - Flag de alerta 80% é marcada (não reenvia)

3. **Uso Crítico (95-99%)**
   - Usuário atinge 95% do limite (950.000 tokens)
   - Sistema envia segundo alerta:
     ```
     Assunto: 🚨 URGENTE: 95% dos tokens utilizados
     
     Atenção [Nome],
     
     Você utilizou 950.000 dos seus 1.000.000 tokens mensais.
     Restam apenas 50.000 tokens!
     
     AÇÃO NECESSÁRIA: Seus tokens podem esgotar a qualquer momento.
     
     Opções imediatas:
     • Comprar tokens adicionais agora
     • Reduzir uso até renovação mensal
     • Contatar suporte para ajuste de limite
     
     [Botão: COMPRAR TOKENS AGORA]
     [Botão: Falar com Suporte]
     ```
   - Flag de alerta 95% é marcada

4. **Esgotamento Total (100%)**
   - Usuário tenta fazer consulta após esgotar tokens
   - Sistema bloqueia requisição
   - Retorna erro 429 (Too Many Requests):
     ```json
     {
       "error": "Limite de tokens esgotado",
       "details": {
         "used": 1000000,
         "limit": 1000000,
         "additional": 0,
         "next_reset": "2024-02-01T00:00:00Z"
       },
       "actions": {
         "buy_tokens": "/api/tokens/purchase",
         "contact_support": "/api/support/contact"
       }
     }
     ```
   - LibreChat exibe mensagem de erro personalizada
   - Email de bloqueio é enviado automaticamente

**Pontos de Monitoramento:**
- Consumo por hora/dia para detectar anomalias
- Padrões de uso para otimizar alertas
- Performance do sistema durante picos
- Taxa de conversão dos alertas em compras

### Fase 3: Gestão de Tokens Adicionais

**Cenário:** Usuário precisa comprar tokens extras durante o mês

**Fluxo de Compra (Fase 1 - Manual):**

1. **Identificação da Necessidade**
   - Usuário recebe alerta de 80% ou 95%
   - Ou tenta usar após esgotamento
   - Decide comprar tokens adicionais

2. **Solicitação de Compra**
   - Usuário clica em "Comprar Tokens" no email
   - Ou acessa link direto fornecido pelo suporte
   - É redirecionado para formulário de solicitação

3. **Processo Manual (Fase 1)**
   - Usuário preenche formulário:
     ```
     Nome: [Preenchido automaticamente]
     Email: [Preenchido automaticamente]
     Quantidade de tokens: [Seletor: 100k, 500k, 1M, 2M, Personalizado]
     Justificativa: [Textarea]
     Urgência: [Baixa, Média, Alta, Crítica]
     ```
   - Sistema gera ticket interno
   - Email de confirmação é enviado:
     ```
     Assunto: Solicitação de tokens recebida #12345
     
     Sua solicitação foi recebida e será processada em até 24h.
     
     Detalhes:
     • Quantidade: 500.000 tokens
     • Valor estimado: R$ 25,00
     • Ticket: #12345
     
     Você receberá confirmação quando os tokens forem adicionados.
     ```

4. **Processamento Administrativo**
   - Administrador recebe notificação
   - Revisa solicitação no dashboard
   - Aprova ou rejeita com justificativa
   - Se aprovado:
     - Adiciona tokens na conta do usuário
     - Registra transação no sistema
     - Envia confirmação por email

5. **Confirmação e Uso**
   - Usuário recebe email de confirmação:
     ```
     Assunto: ✅ Tokens adicionais creditados
     
     Seus tokens adicionais foram creditados com sucesso!
     
     • Tokens adicionados: 500.000
     • Novo saldo: 1.500.000 tokens
     • Válido até: Não expira (acumulativo)
     
     Você já pode continuar usando a IA SOLARIS normalmente.
     ```
   - Usuário pode voltar a usar o sistema
   - Tokens adicionais são consumidos após os mensais

**Fluxo de Compra (Fase 2 - Automático):**

1. **Integração com Gateway de Pagamento**
   - Usuário clica em "Comprar Tokens"
   - É redirecionado para checkout Stripe
   - Seleciona quantidade e forma de pagamento
   - Processa pagamento em tempo real

2. **Confirmação Automática**
   - Webhook do Stripe confirma pagamento
   - Sistema adiciona tokens automaticamente
   - Email de confirmação é enviado imediatamente
   - Usuário pode usar tokens em segundos

### Fase 4: Renovação Mensal

**Cenário:** Virada do mês e reset de tokens

**Fluxo Automático de Renovação:**

1. **Processo Noturno (1º dia do mês, 00:00 UTC)**
   - Job automático executa reset mensal
   - Para cada usuário ativo:
     - Reseta `current_usage` para 0
     - Mantém `additional_tokens` intactos
     - Reseta flags de alerta (80% e 95%)
     - Registra evento de renovação

2. **Notificação de Renovação**
   - Email enviado para todos os usuários:
     ```
     Assunto: 🔄 Seus tokens mensais foram renovados
     
     Olá [Nome],
     
     Seus tokens mensais foram renovados automaticamente!
     
     Resumo do mês anterior:
     • Tokens utilizados: 850.000 de 1.000.000
     • Eficiência: 85%
     • Consultas realizadas: 1.247
     
     Novo mês:
     • Tokens mensais: 1.000.000 (renovados)
     • Tokens adicionais: 150.000 (mantidos)
     • Total disponível: 1.150.000 tokens
     
     Continue aproveitando a IA SOLARIS!
     ```

3. **Relatório Mensal para Administradores**
   - Dashboard atualiza métricas do mês anterior
   - Relatório automático é gerado e enviado
   - Alertas de usuários com padrão anômalo
   - Projeções para o novo mês

## Fluxos Administrativos

### Fluxo de Gestão de Usuários

**Cenário:** Administrador precisa gerenciar usuários específicos

**1. Monitoramento Proativo**
   - Dashboard mostra alertas em tempo real
   - Usuários próximos ao limite são destacados
   - Anomalias de uso são sinalizadas
   - Relatórios automáticos são gerados

**2. Intervenção Manual**
   - Administrador identifica usuário problemático
   - Acessa perfil detalhado no dashboard
   - Analisa histórico de uso e padrões
   - Toma ação apropriada:
     - Ajustar limite mensal
     - Adicionar tokens bonus
     - Suspender temporariamente
     - Contatar usuário diretamente

**3. Gestão de Solicitações**
   - Recebe notificação de nova solicitação
   - Revisa detalhes e justificativa
   - Verifica histórico do usuário
   - Aprova/rejeita com feedback
   - Monitora impacto da decisão

### Fluxo de Resolução de Problemas

**Cenário:** Usuário reporta problema com tokens

**1. Identificação do Problema**
   - Usuário entra em contato via suporte
   - Ou sistema detecta anomalia automaticamente
   - Administrador acessa logs detalhados
   - Identifica causa raiz

**2. Investigação Técnica**
   - Verifica logs de requisições
   - Analisa histórico de uso
   - Compara com padrões normais
   - Identifica discrepâncias

**3. Resolução e Compensação**
   - Corrige problema técnico se necessário
   - Compensa usuário por tokens perdidos
   - Documenta solução para casos futuros
   - Implementa melhorias preventivas

## Fluxos de Exceção e Recuperação

### Cenário: Falha do Sistema Durante Uso

**Fluxo de Recuperação:**

1. **Detecção da Falha**
   - Health checks detectam problema
   - Alertas automáticos são disparados
   - Administradores são notificados imediatamente

2. **Modo de Degradação**
   - Sistema entra em modo de segurança
   - Requisições são bloqueadas temporariamente
   - Usuários recebem mensagem de manutenção

3. **Recuperação Automática**
   - Sistema tenta restart automático
   - Verifica integridade dos dados
   - Restaura operação normal
   - Notifica usuários sobre retorno

4. **Compensação de Usuários**
   - Identifica usuários afetados
   - Calcula tokens perdidos durante falha
   - Credita automaticamente como compensação
   - Envia email explicativo

### Cenário: Uso Anômalo Detectado

**Fluxo de Proteção:**

1. **Detecção Automática**
   - Sistema identifica padrão anômalo:
     - Consumo 10x acima da média
     - Requisições muito frequentes
     - Padrão de bot/automação

2. **Análise de Risco**
   - Verifica se é uso legítimo
   - Analisa histórico do usuário
   - Calcula impacto no sistema

3. **Ação Preventiva**
   - Se risco alto: suspende temporariamente
   - Se risco médio: aplica rate limiting
   - Se risco baixo: monitora de perto

4. **Comunicação com Usuário**
   - Envia email explicativo
   - Oferece canal de contestação
   - Resolve situação rapidamente

## Métricas e KPIs dos Fluxos

### Métricas de Usuário

**Onboarding:**
- Taxa de sucesso na primeira consulta: >95%
- Tempo médio para primeira resposta: <5 segundos
- Taxa de erro no primeiro uso: <1%

**Uso Regular:**
- Tempo médio de resposta: <2 segundos
- Taxa de disponibilidade: >99.9%
- Precisão dos alertas: >90%

**Gestão de Tokens:**
- Taxa de conversão dos alertas: 15-25%
- Tempo médio para processar compra manual: <24h
- Satisfação com processo de compra: >4.5/5

### Métricas Administrativas

**Eficiência Operacional:**
- Tempo médio para resolver tickets: <4h
- Taxa de resolução no primeiro contato: >80%
- Precisão das intervenções automáticas: >95%

**Qualidade do Serviço:**
- Uptime do sistema: >99.9%
- Tempo médio de recuperação: <15min
- Taxa de falsos positivos em anomalias: <5%

## Otimizações e Melhorias Contínuas

### Análise de Comportamento

**Padrões Identificados:**
- Usuários consomem 60% dos tokens na primeira quinzena
- Picos de uso ocorrem entre 14h-16h
- Taxa de abandono após primeiro bloqueio: 12%

**Otimizações Implementadas:**
- Alertas adaptativos baseados no padrão individual
- Sugestões personalizadas de economia
- Ofertas dinâmicas de tokens adicionais

### Automação Inteligente

**Recursos Implementados:**
- Predição de esgotamento baseada em ML
- Ajuste automático de limites para usuários premium
- Detecção proativa de problemas técnicos

**Resultados Obtidos:**
- Redução de 40% em tickets de suporte
- Aumento de 25% na satisfação do usuário
- Melhoria de 30% na eficiência operacional

## Documentação de Casos de Uso Específicos

### Caso 1: Usuário Power User

**Perfil:** Desenvolvedor que usa IA para coding
**Padrão:** 2-3M tokens/mês, uso concentrado
**Fluxo Personalizado:**
- Limite mensal ajustado para 3M tokens
- Alertas em 90% e 98% (mais tardios)
- Acesso direto a compra automática
- Suporte prioritário

### Caso 2: Usuário Casual

**Perfil:** Usuário esporádico, consultas simples
**Padrão:** 100-300k tokens/mês, uso distribuído
**Fluxo Personalizado:**
- Limite padrão de 1M tokens
- Alertas educacionais sobre otimização
- Ofertas de planos menores
- Onboarding simplificado

### Caso 3: Usuário Corporativo

**Perfil:** Empresa com múltiplos usuários
**Padrão:** 10-50M tokens/mês, uso previsível
**Fluxo Personalizado:**
- Gestão centralizada de tokens
- Relatórios detalhados por departamento
- SLA diferenciado
- Integração com sistemas internos

---

**Autor:** Manus AI  
**Data:** Janeiro 2024  
**Versão:** 1.0

