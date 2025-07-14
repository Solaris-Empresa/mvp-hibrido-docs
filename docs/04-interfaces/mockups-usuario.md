# 📱 Mockups de Interface de Usuário
## MVP Híbrido - Controle de Tokens IA SOLARIS

### 🎯 **Visão Geral das Interfaces**

As interfaces de usuário foram projetadas para se integrar **naturalmente** ao LibreChat existente, mantendo a experiência familiar enquanto adiciona controle de tokens.

### 📊 **1. Tela Principal do Chat**

![Chat Principal](https://github.com/Solaris-Empresa/mvp-hibrido-docs/blob/main/docs/assets/mockups/mockup_chat_principal.png)

#### **Elementos Principais:**
- **Contador de Tokens** (canto superior direito)
- **Indicador Visual** do saldo restante
- **Chat Interface** inalterada do LibreChat
- **Sidebar** com assistentes disponíveis

#### **Especificações Técnicas:**
```javascript
// Componente: TokenCounter
const TokenCounter = {
  position: 'top-right',
  display: 'tokens restantes: {saldo}',
  updateInterval: 'real-time',
  colorScheme: {
    normal: '#10B981',    // Verde
    warning: '#F59E0B',   // Amarelo (80%)
    critical: '#EF4444'   // Vermelho (90%+)
  }
}
```

#### **Estados do Contador:**
| Saldo | Cor | Comportamento |
|-------|-----|---------------|
| > 20% | Verde | Normal |
| 10-20% | Amarelo | Aviso discreto |
| < 10% | Vermelho | Alerta visível |
| 0% | Vermelho | Bloqueio total |

### 📋 **2. Extrato de Consumo**

![Extrato de Consumo](https://github.com/Solaris-Empresa/mvp-hibrido-docs/blob/main/docs/assets/mockups/mockup_extrato_consumo.png)

#### **Localização:**
- **Menu**: Configurações → Extrato de Consumo
- **Acesso**: Botão no contador de tokens

#### **Informações Exibidas:**
- **Saldo Atual**: Tokens restantes no mês
- **Consumo Mensal**: Progresso visual (barra)
- **Histórico Diário**: Gráfico de linha
- **Breakdown por Modelo**: GPT-4, Claude, etc.
- **Botão de Compra**: Créditos adicionais

#### **Especificações de Layout:**
```css
.extrato-container {
  max-width: 800px;
  margin: 0 auto;
  padding: 24px;
}

.progress-bar {
  height: 12px;
  border-radius: 6px;
  background: linear-gradient(90deg, #10B981 0%, #F59E0B 80%, #EF4444 100%);
}

.chart-container {
  height: 300px;
  margin: 24px 0;
}
```

### 🛒 **3. Tela de Compra de Créditos**

![Compra de Créditos](https://github.com/Solaris-Empresa/mvp-hibrido-docs/blob/main/docs/assets/mockups/mockup_compra_creditos.png)

#### **Estrutura da Página:**
- **Header**: Logo IA SOLARIS + navegação
- **Título**: "Comprar Créditos Adicionais"
- **Cards de Preços**: 3 opções de pacotes
- **Saldo Atual**: Widget informativo
- **Métodos de Pagamento**: Ícones de cartão

#### **Pacotes de Tokens:**
| Pacote | Tokens | Preço | Badge |
|--------|--------|-------|-------|
| Básico | 200.000 | R$ 50,00 | - |
| Popular | 500.000 | R$ 120,00 | "Mais Popular" |
| Premium | 1.000.000 | R$ 230,00 | - |

#### **Especificações dos Cards:**
```css
.pricing-card {
  border: 2px solid #E5E7EB;
  border-radius: 12px;
  padding: 24px;
  text-align: center;
  transition: all 0.3s ease;
}

.pricing-card.popular {
  border-color: #3B82F6;
  transform: scale(1.05);
  box-shadow: 0 10px 25px rgba(59, 130, 246, 0.15);
}

.buy-button {
  background: linear-gradient(135deg, #3B82F6 0%, #1D4ED8 100%);
  color: white;
  border: none;
  border-radius: 8px;
  padding: 12px 24px;
  font-weight: 600;
  cursor: pointer;
}
```

### 🎨 **Design System**

#### **Paleta de Cores:**
```css
:root {
  --primary-blue: #3B82F6;
  --success-green: #10B981;
  --warning-yellow: #F59E0B;
  --danger-red: #EF4444;
  --gray-50: #F9FAFB;
  --gray-100: #F3F4F6;
  --gray-900: #111827;
}
```

#### **Tipografia:**
```css
.heading-1 { font-size: 2.25rem; font-weight: 700; }
.heading-2 { font-size: 1.875rem; font-weight: 600; }
.body-large { font-size: 1.125rem; font-weight: 400; }
.body-regular { font-size: 1rem; font-weight: 400; }
.caption { font-size: 0.875rem; font-weight: 500; }
```

#### **Espaçamento:**
```css
.spacing-xs { margin: 4px; }
.spacing-sm { margin: 8px; }
.spacing-md { margin: 16px; }
.spacing-lg { margin: 24px; }
.spacing-xl { margin: 32px; }
```

### 📱 **Responsividade**

#### **Breakpoints:**
```css
/* Mobile First */
.container {
  padding: 16px;
}

/* Tablet */
@media (min-width: 768px) {
  .container {
    padding: 24px;
    max-width: 768px;
    margin: 0 auto;
  }
}

/* Desktop */
@media (min-width: 1024px) {
  .container {
    padding: 32px;
    max-width: 1024px;
  }
}
```

#### **Adaptações Mobile:**
- **Contador de tokens**: Menor, posição ajustada
- **Extrato**: Gráfico simplificado, scroll horizontal
- **Compra**: Cards empilhados verticalmente

### 🔧 **Integração com LibreChat**

#### **Método de Integração:**
1. **CSS Injection**: Estilos adicionais via arquivo CSS
2. **JavaScript Overlay**: Componentes React injetados
3. **API Hooks**: Interceptação de chamadas existentes

#### **Arquivos a Modificar:**
```
librechat/
├── client/src/components/
│   ├── Chat/ChatHeader.jsx     # Adicionar contador
│   └── Nav/SettingsMenu.jsx    # Adicionar link extrato
├── client/src/styles/
│   └── solaris-tokens.css      # Estilos novos
└── client/src/hooks/
    └── useTokens.js            # Hook para tokens
```

### 🧪 **Estados de Teste**

#### **Cenários para Testar:**
1. **Usuário Novo**: 1.000.000 tokens disponíveis
2. **Usuário 50%**: 500.000 tokens restantes
3. **Usuário 80%**: 200.000 tokens (alerta amarelo)
4. **Usuário 95%**: 50.000 tokens (alerta vermelho)
5. **Usuário 100%**: 0 tokens (bloqueado)

#### **Dados de Teste:**
```javascript
const testUsers = [
  {
    id: 1,
    name: "João Silva",
    tokensTotal: 1000000,
    tokensUsed: 0,
    status: "active"
  },
  {
    id: 2,
    name: "Maria Santos",
    tokensTotal: 1000000,
    tokensUsed: 800000,
    status: "warning"
  },
  {
    id: 3,
    name: "Pedro Costa",
    tokensTotal: 1000000,
    tokensUsed: 1000000,
    status: "blocked"
  }
];
```

### 🎯 **Próximos Passos**

1. **[Mockups de Modais](mockups-modais.md)** - Alertas e bloqueios
2. **[Interface Administrativa](mockups-admin.md)** - Gestão de usuários
3. **[Especificações Técnicas](especificacoes-tecnicas.md)** - Detalhes de implementação
4. **[Fluxos de Usuário](fluxos-usuario.md)** - Jornadas completas

---

**💡 Estas interfaces mantêm a familiaridade do LibreChat enquanto adicionam controle preciso de tokens de forma não-intrusiva.**

