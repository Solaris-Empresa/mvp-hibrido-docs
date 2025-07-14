# Mockups de Modais - Sistema de Alertas e Bloqueios

## Visão Geral

Este documento especifica os modais de alerta e bloqueio do sistema de controle de tokens da IA SOLARIS. Os modais são elementos críticos da experiência do usuário, responsáveis por comunicar o status de consumo de tokens e implementar as medidas de controle necessárias para evitar gastos excessivos.

## Modal de Alerta - 80% de Consumo

### Especificações Visuais

**Título:** "⚠️ Atenção: 80% dos tokens consumidos"

**Corpo da Mensagem:**
```
Você já utilizou 80% dos seus tokens mensais disponíveis.

Tokens restantes: 200.000 de 1.000.000
Estimativa para fim do mês: Esgotamento em 3 dias

Recomendações:
• Monitore seu uso mais de perto
• Considere adquirir tokens adicionais
• Revise suas consultas para otimizar o consumo
```

**Botões de Ação:**
- **Primário:** "Comprar Tokens Adicionais" (azul)
- **Secundário:** "Ver Extrato Detalhado" (cinza)
- **Terciário:** "Continuar Usando" (texto simples)

### Comportamento Técnico

**Trigger:** Quando o usuário atinge exatamente 80% do limite mensal
**Frequência:** Exibido apenas uma vez por mês por usuário
**Persistência:** Modal não pode ser fechado com ESC ou clique fora
**Timeout:** Não possui timeout automático
**Analytics:** Registra evento "alert_80_percent_shown" com user_id e timestamp

### Estados do Modal

**Estado Normal:**
- Fundo semi-transparente (rgba(0,0,0,0.7))
- Modal centralizado com bordas arredondadas
- Ícone de alerta amarelo proeminente
- Texto em hierarquia clara (título, corpo, ações)

**Estado de Loading (ao clicar em ações):**
- Botões ficam desabilitados
- Spinner de carregamento aparece
- Texto muda para "Processando..."

**Estado de Erro:**
- Mensagem de erro aparece em vermelho
- Botão "Tentar Novamente" substitui ações originais
- Opção "Continuar Mesmo Assim" permanece disponível

## Modal de Bloqueio - 100% de Consumo

### Especificações Visuais

**Título:** "🚫 Limite de tokens esgotado"

**Corpo da Mensagem:**
```
Você utilizou todos os seus tokens mensais disponíveis.

Tokens utilizados: 1.000.000 de 1.000.000
Próxima renovação: 15 de Janeiro de 2024

Para continuar usando a IA SOLARIS:
• Adquira tokens adicionais imediatamente
• Aguarde a renovação mensal automática
• Entre em contato com suporte para planos especiais
```

**Botões de Ação:**
- **Primário:** "Comprar Tokens Agora" (verde)
- **Secundário:** "Falar com Suporte" (azul)
- **Informativo:** "Ver Histórico de Uso" (cinza)

### Comportamento Técnico

**Trigger:** Quando o usuário atinge 100% do limite mensal
**Frequência:** Exibido a cada tentativa de uso após esgotamento
**Persistência:** Modal bloqueia completamente a interface
**Fechamento:** Apenas através das ações disponíveis
**Redirecionamento:** Usuário é redirecionado para página de compra ou suporte

### Estados do Modal

**Estado de Bloqueio Ativo:**
- Fundo completamente opaco (rgba(0,0,0,0.9))
- Modal não pode ser fechado
- Ícone de bloqueio vermelho
- Botões com call-to-action mais agressivo

**Estado de Processamento de Compra:**
- Integração com gateway de pagamento
- Indicador de progresso da transação
- Mensagens de status em tempo real

**Estado Pós-Compra:**
- Confirmação de tokens adicionados
- Novo saldo disponível
- Botão "Continuar Usando" habilitado

## Modais de Contexto Administrativo

### Modal de Gestão de Usuário (Admin)

**Título:** "Gerenciar Usuário: [Nome do Usuário]"

**Seções:**
1. **Informações Básicas**
   - Nome, email, data de cadastro
   - Status da conta (ativo/suspenso/banido)
   - Plano atual e data de renovação

2. **Controle de Tokens**
   - Limite mensal atual
   - Tokens consumidos no mês
   - Histórico de compras adicionais
   - Botão "Ajustar Limite"

3. **Ações Administrativas**
   - Resetar tokens do mês
   - Adicionar tokens bonus
   - Suspender/reativar conta
   - Enviar notificação personalizada

### Modal de Ajuste de Limite

**Título:** "Ajustar Limite Mensal"

**Campos:**
- Limite atual (somente leitura)
- Novo limite (input numérico)
- Motivo do ajuste (textarea obrigatório)
- Data de vigência (seletor de data)

**Validações:**
- Limite mínimo: 100.000 tokens
- Limite máximo: 10.000.000 tokens
- Motivo obrigatório com mínimo de 20 caracteres

## Especificações Técnicas de Implementação

### Estrutura HTML Base

```html
<div class="modal-overlay" id="tokenModal">
  <div class="modal-container">
    <div class="modal-header">
      <span class="modal-icon"></span>
      <h2 class="modal-title"></h2>
    </div>
    <div class="modal-body">
      <div class="modal-content"></div>
      <div class="modal-stats"></div>
    </div>
    <div class="modal-footer">
      <div class="modal-actions"></div>
    </div>
  </div>
</div>
```

### Classes CSS Principais

```css
.modal-overlay {
  position: fixed;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: rgba(0, 0, 0, 0.7);
  display: flex;
  justify-content: center;
  align-items: center;
  z-index: 9999;
}

.modal-container {
  background: white;
  border-radius: 12px;
  max-width: 500px;
  width: 90%;
  box-shadow: 0 20px 40px rgba(0, 0, 0, 0.3);
  animation: modalSlideIn 0.3s ease-out;
}

.modal-header {
  padding: 24px 24px 16px;
  border-bottom: 1px solid #e5e7eb;
  text-align: center;
}

.modal-icon {
  font-size: 48px;
  display: block;
  margin-bottom: 16px;
}

.modal-title {
  font-size: 24px;
  font-weight: 600;
  color: #1f2937;
  margin: 0;
}
```

### JavaScript de Controle

```javascript
class TokenModal {
  constructor(type, data) {
    this.type = type; // 'alert' | 'block' | 'admin'
    this.data = data;
    this.element = null;
  }

  show() {
    this.createElement();
    this.bindEvents();
    document.body.appendChild(this.element);
    this.trackEvent('modal_shown');
  }

  hide() {
    if (this.element) {
      this.element.remove();
      this.trackEvent('modal_closed');
    }
  }

  createElement() {
    const template = this.getTemplate();
    this.element = document.createElement('div');
    this.element.innerHTML = template;
    this.element = this.element.firstElementChild;
  }

  bindEvents() {
    const actions = this.element.querySelectorAll('[data-action]');
    actions.forEach(button => {
      button.addEventListener('click', (e) => {
        this.handleAction(e.target.dataset.action);
      });
    });
  }

  handleAction(action) {
    switch(action) {
      case 'buy_tokens':
        this.redirectToPurchase();
        break;
      case 'view_usage':
        this.redirectToUsage();
        break;
      case 'contact_support':
        this.openSupport();
        break;
      case 'continue':
        this.hide();
        break;
    }
  }

  trackEvent(event) {
    // Integração com sistema de analytics
    analytics.track(event, {
      modal_type: this.type,
      user_id: this.data.userId,
      timestamp: new Date().toISOString()
    });
  }
}
```

### Integração com Sistema de Tokens

```javascript
// Verificação automática de limites
function checkTokenLimits(userId, currentUsage, monthlyLimit) {
  const percentage = (currentUsage / monthlyLimit) * 100;
  
  if (percentage >= 100) {
    showBlockModal(userId, currentUsage, monthlyLimit);
    return false; // Bloqueia uso
  } else if (percentage >= 80 && !hasShownAlert80(userId)) {
    showAlertModal(userId, currentUsage, monthlyLimit);
    markAlert80Shown(userId);
  }
  
  return true; // Permite uso
}

// Integração com API de compras
async function handleTokenPurchase(userId, amount) {
  try {
    const response = await fetch('/api/tokens/purchase', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ userId, amount })
    });
    
    if (response.ok) {
      const result = await response.json();
      updateUserTokens(userId, result.newBalance);
      showSuccessMessage('Tokens adicionados com sucesso!');
      hideModal();
    } else {
      showErrorMessage('Erro ao processar compra. Tente novamente.');
    }
  } catch (error) {
    showErrorMessage('Erro de conexão. Verifique sua internet.');
  }
}
```

## Testes e Validação

### Cenários de Teste

**Teste 1: Exibição do Modal de 80%**
- Simular usuário com 800.000 tokens consumidos
- Verificar se modal aparece na próxima requisição
- Confirmar que não aparece novamente no mesmo mês

**Teste 2: Bloqueio por Esgotamento**
- Simular usuário com 1.000.000 tokens consumidos
- Verificar bloqueio total da interface
- Testar fluxo de compra de tokens adicionais

**Teste 3: Responsividade**
- Testar modais em diferentes tamanhos de tela
- Verificar acessibilidade (navegação por teclado)
- Validar contraste e legibilidade

### Métricas de Sucesso

- **Taxa de Conversão:** % de usuários que compram tokens após ver modal
- **Taxa de Abandono:** % de usuários que param de usar após bloqueio
- **Tempo de Resposta:** Tempo médio para carregar modal
- **Satisfação:** Score de feedback dos usuários sobre clareza das mensagens

## Considerações de UX

### Princípios de Design

1. **Clareza:** Mensagens diretas e sem ambiguidade
2. **Urgência Apropriada:** Alertas proporcionais ao nível de criticidade
3. **Ações Claras:** Botões com labels que indicam exatamente o que fazem
4. **Feedback Visual:** Estados de loading e confirmação bem definidos

### Acessibilidade

- Suporte a leitores de tela (aria-labels)
- Navegação por teclado funcional
- Contraste adequado (WCAG 2.1 AA)
- Textos alternativos para ícones

### Personalização

- Mensagens adaptadas ao perfil do usuário
- Recomendações baseadas no histórico de uso
- Opções de contato direto para usuários premium

---

**Autor:** Manus AI  
**Data:** Janeiro 2024  
**Versão:** 1.0

