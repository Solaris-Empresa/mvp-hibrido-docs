# Especificações Técnicas - MVP Híbrido IA SOLARIS

## Visão Geral da Arquitetura

Este documento detalha as especificações técnicas completas para implementação do MVP híbrido de controle de tokens da IA SOLARIS. O sistema foi projetado para ser escalável, confiável e facilmente mantível, seguindo as melhores práticas de desenvolvimento de software e arquitetura de microsserviços.

## Arquitetura Geral do Sistema

### Componentes Principais

**1. Proxy Inteligente (Flask)**
- Responsabilidade: Interceptação e controle de requisições
- Tecnologia: Python 3.11 + Flask 2.3
- Porta: 5000
- Função: Gateway entre LibreChat e provedores de IA

**2. Dashboard Administrativo (React)**
- Responsabilidade: Interface de gestão e monitoramento
- Tecnologia: React 18 + TypeScript
- Porta: 3000
- Função: Controle administrativo e relatórios

**3. Banco de Dados Principal (PostgreSQL)**
- Responsabilidade: Armazenamento de dados transacionais
- Versão: PostgreSQL 15
- Porta: 5432
- Função: Persistência de usuários, tokens e transações

**4. Cache e Sessões (Redis)**
- Responsabilidade: Cache de alta performance
- Versão: Redis 7.0
- Porta: 6379
- Função: Cache de consultas e controle de sessões

**5. Proxy Reverso (Nginx)**
- Responsabilidade: Balanceamento e SSL
- Versão: Nginx 1.24
- Porta: 80/443
- Função: Roteamento e terminação SSL

### Fluxo de Dados

```
LibreChat → Nginx → Proxy Inteligente → LiteLLM → Provedor IA
     ↓                    ↓                         ↑
Dashboard ←→ PostgreSQL ←→ Redis ←→ Sistema de Alertas
```

## Especificações do Proxy Inteligente

### Estrutura do Projeto

```
proxy-ia-solaris/
├── src/
│   ├── main.py              # Aplicação principal Flask
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py      # Configurações do sistema
│   │   └── database.py      # Configuração do banco
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py          # Modelo de usuário
│   │   ├── token_usage.py   # Modelo de uso de tokens
│   │   └── transaction.py   # Modelo de transações
│   ├── services/
│   │   ├── __init__.py
│   │   ├── proxy_service.py # Lógica do proxy
│   │   ├── token_service.py # Controle de tokens
│   │   ├── alert_service.py # Sistema de alertas
│   │   └── email_service.py # Envio de emails
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── proxy_routes.py  # Rotas do proxy
│   │   ├── admin_routes.py  # Rotas administrativas
│   │   └── health_routes.py # Health checks
│   └── utils/
│       ├── __init__.py
│       ├── decorators.py    # Decoradores customizados
│       ├── validators.py    # Validações
│       └── helpers.py       # Funções auxiliares
├── tests/
│   ├── unit/
│   ├── integration/
│   └── fixtures/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── README.md
```

### Configurações Principais (settings.py)

```python
import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class DatabaseConfig:
    host: str = os.getenv('DB_HOST', 'localhost')
    port: int = int(os.getenv('DB_PORT', '5432'))
    name: str = os.getenv('DB_NAME', 'ia_solaris')
    user: str = os.getenv('DB_USER', 'postgres')
    password: str = os.getenv('DB_PASSWORD', '')
    
    @property
    def url(self) -> str:
        return f"postgresql://{self.user}:{self.password}@{self.host}:{self.port}/{self.name}"

@dataclass
class RedisConfig:
    host: str = os.getenv('REDIS_HOST', 'localhost')
    port: int = int(os.getenv('REDIS_PORT', '6379'))
    db: int = int(os.getenv('REDIS_DB', '0'))
    password: Optional[str] = os.getenv('REDIS_PASSWORD')
    
    @property
    def url(self) -> str:
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"

@dataclass
class TokenConfig:
    default_monthly_limit: int = int(os.getenv('DEFAULT_MONTHLY_LIMIT', '1000000'))
    alert_threshold: float = float(os.getenv('ALERT_THRESHOLD', '0.8'))
    block_threshold: float = float(os.getenv('BLOCK_THRESHOLD', '1.0'))
    max_user_limit: int = int(os.getenv('MAX_USER_LIMIT', '10000000'))
    min_user_limit: int = int(os.getenv('MIN_USER_LIMIT', '100000'))

@dataclass
class EmailConfig:
    smtp_host: str = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port: int = int(os.getenv('SMTP_PORT', '587'))
    smtp_user: str = os.getenv('SMTP_USER', '')
    smtp_password: str = os.getenv('SMTP_PASSWORD', '')
    from_email: str = os.getenv('FROM_EMAIL', 'noreply@iasolaris.com')
    use_tls: bool = os.getenv('SMTP_TLS', 'true').lower() == 'true'

@dataclass
class AppConfig:
    debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    secret_key: str = os.getenv('SECRET_KEY', 'dev-secret-key')
    host: str = os.getenv('HOST', '0.0.0.0')
    port: int = int(os.getenv('PORT', '5000'))
    log_level: str = os.getenv('LOG_LEVEL', 'INFO')
    
    # Configurações de integração
    litellm_base_url: str = os.getenv('LITELLM_BASE_URL', 'http://localhost:4000')
    openai_api_key: str = os.getenv('OPENAI_API_KEY', '')
    
    # Instâncias de configuração
    database = DatabaseConfig()
    redis = RedisConfig()
    tokens = TokenConfig()
    email = EmailConfig()
```

### Modelos de Dados

**Modelo de Usuário (user.py):**

```python
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from typing import Optional

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'
    
    id = Column(Integer, primary_key=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    status = Column(String(50), default='active')  # active, suspended, blocked
    plan = Column(String(50), default='basic')     # basic, pro, enterprise
    
    # Controle de tokens
    monthly_limit = Column(Integer, default=1000000)
    current_usage = Column(Integer, default=0)
    additional_tokens = Column(Integer, default=0)
    
    # Controle de alertas
    alert_80_sent = Column(Boolean, default=False)
    alert_95_sent = Column(Boolean, default=False)
    last_alert_date = Column(DateTime)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_login = Column(DateTime)
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', status='{self.status}')>"
    
    @property
    def total_available_tokens(self) -> int:
        """Retorna total de tokens disponíveis (mensais + adicionais)"""
        return self.monthly_limit + self.additional_tokens
    
    @property
    def usage_percentage(self) -> float:
        """Retorna percentual de uso dos tokens mensais"""
        if self.monthly_limit == 0:
            return 0.0
        return (self.current_usage / self.monthly_limit) * 100
    
    @property
    def remaining_tokens(self) -> int:
        """Retorna tokens restantes (considerando adicionais)"""
        return max(0, self.total_available_tokens - self.current_usage)
    
    def can_use_tokens(self, amount: int) -> bool:
        """Verifica se usuário pode usar quantidade específica de tokens"""
        return self.remaining_tokens >= amount and self.status == 'active'
    
    def consume_tokens(self, amount: int) -> bool:
        """Consome tokens do usuário"""
        if not self.can_use_tokens(amount):
            return False
        
        self.current_usage += amount
        self.updated_at = datetime.utcnow()
        return True
    
    def reset_monthly_usage(self):
        """Reseta uso mensal (mantém tokens adicionais)"""
        self.current_usage = 0
        self.alert_80_sent = False
        self.alert_95_sent = False
        self.last_alert_date = None
        self.updated_at = datetime.utcnow()
```

**Modelo de Uso de Tokens (token_usage.py):**

```python
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .user import Base

class TokenUsage(Base):
    __tablename__ = 'token_usage'
    
    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    
    # Detalhes da requisição
    request_id = Column(String(255), unique=True, nullable=False, index=True)
    model = Column(String(100), nullable=False)  # gpt-4, claude-3, etc.
    endpoint = Column(String(255), nullable=False)  # /v1/chat/completions
    method = Column(String(10), default='POST')
    
    # Tokens utilizados
    prompt_tokens = Column(Integer, default=0)
    completion_tokens = Column(Integer, default=0)
    total_tokens = Column(Integer, nullable=False)
    
    # Custos (para relatórios)
    cost_per_token = Column(Float, default=0.0)
    total_cost = Column(Float, default=0.0)
    
    # Metadados
    user_agent = Column(String(500))
    ip_address = Column(String(45))
    response_time_ms = Column(Integer)
    status_code = Column(Integer)
    error_message = Column(Text)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    
    # Relacionamentos
    user = relationship("User", backref="token_usages")
    
    def __repr__(self):
        return f"<TokenUsage(id={self.id}, user_id={self.user_id}, tokens={self.total_tokens})>"
    
    @classmethod
    def create_from_request(cls, user_id: int, request_data: dict, response_data: dict):
        """Cria registro de uso a partir de dados de requisição e resposta"""
        usage = response_data.get('usage', {})
        
        return cls(
            user_id=user_id,
            request_id=request_data.get('request_id'),
            model=request_data.get('model', 'unknown'),
            endpoint=request_data.get('endpoint', '/v1/chat/completions'),
            method=request_data.get('method', 'POST'),
            prompt_tokens=usage.get('prompt_tokens', 0),
            completion_tokens=usage.get('completion_tokens', 0),
            total_tokens=usage.get('total_tokens', 0),
            user_agent=request_data.get('user_agent'),
            ip_address=request_data.get('ip_address'),
            response_time_ms=request_data.get('response_time_ms'),
            status_code=response_data.get('status_code', 200),
            error_message=response_data.get('error')
        )
```

### Serviços Principais

**Serviço de Proxy (proxy_service.py):**

```python
import asyncio
import aiohttp
import time
from typing import Dict, Any, Optional, Tuple
from flask import current_app
from .token_service import TokenService
from .alert_service import AlertService
from ..models.token_usage import TokenUsage
from ..utils.helpers import generate_request_id, extract_user_from_request

class ProxyService:
    def __init__(self):
        self.token_service = TokenService()
        self.alert_service = AlertService()
        self.litellm_base_url = current_app.config['LITELLM_BASE_URL']
    
    async def process_request(self, request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Processa requisição completa com controle de tokens"""
        
        # 1. Extrair informações do usuário
        user_email = extract_user_from_request(request_data)
        if not user_email:
            return {"error": "Usuário não identificado"}, 401
        
        # 2. Verificar e obter usuário
        user = self.token_service.get_or_create_user(user_email)
        if not user:
            return {"error": "Erro ao processar usuário"}, 500
        
        # 3. Verificar status do usuário
        if user.status != 'active':
            return {"error": f"Conta {user.status}. Contate o suporte."}, 403
        
        # 4. Estimar tokens da requisição
        estimated_tokens = self._estimate_tokens(request_data)
        
        # 5. Verificar disponibilidade de tokens
        if not user.can_use_tokens(estimated_tokens):
            # Enviar alerta de bloqueio se necessário
            await self.alert_service.send_block_alert(user)
            return {
                "error": "Limite de tokens esgotado",
                "details": {
                    "used": user.current_usage,
                    "limit": user.monthly_limit,
                    "additional": user.additional_tokens
                }
            }, 429
        
        # 6. Fazer requisição para LiteLLM
        start_time = time.time()
        response_data, status_code = await self._forward_request(request_data)
        response_time_ms = int((time.time() - start_time) * 1000)
        
        # 7. Processar resposta e atualizar tokens
        if status_code == 200 and 'usage' in response_data:
            actual_tokens = response_data['usage']['total_tokens']
            
            # Consumir tokens reais
            success = self.token_service.consume_tokens(user.id, actual_tokens)
            if not success:
                current_app.logger.error(f"Falha ao consumir tokens para usuário {user.id}")
            
            # Registrar uso
            usage_record = TokenUsage.create_from_request(
                user_id=user.id,
                request_data={
                    **request_data,
                    'request_id': generate_request_id(),
                    'response_time_ms': response_time_ms
                },
                response_data=response_data
            )
            self.token_service.save_usage_record(usage_record)
            
            # Verificar alertas
            await self._check_and_send_alerts(user)
        
        return response_data, status_code
    
    async def _forward_request(self, request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """Encaminha requisição para LiteLLM"""
        try:
            url = f"{self.litellm_base_url}/v1/chat/completions"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': request_data.get('authorization', '')
            }
            
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=request_data, headers=headers) as response:
                    response_data = await response.json()
                    return response_data, response.status
                    
        except aiohttp.ClientError as e:
            current_app.logger.error(f"Erro ao encaminhar requisição: {e}")
            return {"error": "Erro interno do servidor"}, 500
        except Exception as e:
            current_app.logger.error(f"Erro inesperado: {e}")
            return {"error": "Erro interno do servidor"}, 500
    
    def _estimate_tokens(self, request_data: Dict[str, Any]) -> int:
        """Estima tokens baseado no conteúdo da requisição"""
        messages = request_data.get('messages', [])
        total_chars = 0
        
        for message in messages:
            content = message.get('content', '')
            total_chars += len(str(content))
        
        # Estimativa: ~4 caracteres por token (aproximação)
        estimated_tokens = max(total_chars // 4, 100)  # Mínimo de 100 tokens
        
        # Adicionar margem de segurança de 20%
        return int(estimated_tokens * 1.2)
    
    async def _check_and_send_alerts(self, user):
        """Verifica e envia alertas baseados no uso atual"""
        usage_percentage = user.usage_percentage
        
        # Alerta de 80%
        if usage_percentage >= 80 and not user.alert_80_sent:
            await self.alert_service.send_usage_alert(user, 80)
            self.token_service.mark_alert_sent(user.id, '80')
        
        # Alerta de 95%
        elif usage_percentage >= 95 and not user.alert_95_sent:
            await self.alert_service.send_usage_alert(user, 95)
            self.token_service.mark_alert_sent(user.id, '95')
```

**Serviço de Tokens (token_service.py):**

```python
from typing import Optional, List
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, func
from datetime import datetime, timedelta
from ..models.user import User
from ..models.token_usage import TokenUsage
from ..config.settings import AppConfig

class TokenService:
    def __init__(self):
        self.config = AppConfig()
        self.engine = create_engine(self.config.database.url)
        self.Session = sessionmaker(bind=self.engine)
    
    def get_or_create_user(self, email: str) -> Optional[User]:
        """Obtém usuário existente ou cria novo"""
        with self.Session() as session:
            user = session.query(User).filter(User.email == email).first()
            
            if not user:
                user = User(
                    email=email,
                    name=email.split('@')[0],  # Nome temporário
                    monthly_limit=self.config.tokens.default_monthly_limit
                )
                session.add(user)
                session.commit()
                session.refresh(user)
            
            return user
    
    def consume_tokens(self, user_id: int, amount: int) -> bool:
        """Consome tokens do usuário"""
        with self.Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            if user.consume_tokens(amount):
                session.commit()
                return True
            
            return False
    
    def add_additional_tokens(self, user_id: int, amount: int, reason: str = "") -> bool:
        """Adiciona tokens adicionais ao usuário"""
        with self.Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return False
            
            user.additional_tokens += amount
            user.updated_at = datetime.utcnow()
            session.commit()
            
            # Log da transação
            self._log_token_transaction(user_id, amount, 'addition', reason)
            return True
    
    def reset_monthly_usage(self, user_id: Optional[int] = None):
        """Reseta uso mensal (todos os usuários ou específico)"""
        with self.Session() as session:
            query = session.query(User)
            if user_id:
                query = query.filter(User.id == user_id)
            
            users = query.all()
            for user in users:
                user.reset_monthly_usage()
            
            session.commit()
    
    def get_user_stats(self, user_id: int) -> dict:
        """Retorna estatísticas detalhadas do usuário"""
        with self.Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if not user:
                return {}
            
            # Uso nos últimos 30 dias
            thirty_days_ago = datetime.utcnow() - timedelta(days=30)
            recent_usage = session.query(func.sum(TokenUsage.total_tokens)).filter(
                TokenUsage.user_id == user_id,
                TokenUsage.created_at >= thirty_days_ago
            ).scalar() or 0
            
            # Uso por modelo
            model_usage = session.query(
                TokenUsage.model,
                func.sum(TokenUsage.total_tokens)
            ).filter(
                TokenUsage.user_id == user_id,
                TokenUsage.created_at >= thirty_days_ago
            ).group_by(TokenUsage.model).all()
            
            return {
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.name,
                    'status': user.status,
                    'plan': user.plan
                },
                'tokens': {
                    'monthly_limit': user.monthly_limit,
                    'current_usage': user.current_usage,
                    'additional_tokens': user.additional_tokens,
                    'remaining': user.remaining_tokens,
                    'usage_percentage': user.usage_percentage
                },
                'usage_30_days': recent_usage,
                'usage_by_model': dict(model_usage),
                'alerts': {
                    'alert_80_sent': user.alert_80_sent,
                    'alert_95_sent': user.alert_95_sent,
                    'last_alert_date': user.last_alert_date
                }
            }
    
    def get_system_stats(self) -> dict:
        """Retorna estatísticas gerais do sistema"""
        with self.Session() as session:
            # Contadores básicos
            total_users = session.query(User).count()
            active_users = session.query(User).filter(User.status == 'active').count()
            
            # Uso total no mês atual
            current_month_start = datetime.utcnow().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            monthly_usage = session.query(func.sum(TokenUsage.total_tokens)).filter(
                TokenUsage.created_at >= current_month_start
            ).scalar() or 0
            
            # Top usuários por consumo
            top_users = session.query(
                User.email,
                User.current_usage
            ).order_by(User.current_usage.desc()).limit(10).all()
            
            return {
                'users': {
                    'total': total_users,
                    'active': active_users,
                    'suspended': session.query(User).filter(User.status == 'suspended').count(),
                    'blocked': session.query(User).filter(User.status == 'blocked').count()
                },
                'usage': {
                    'monthly_total': monthly_usage,
                    'average_per_user': monthly_usage / active_users if active_users > 0 else 0
                },
                'top_users': [{'email': email, 'usage': usage} for email, usage in top_users]
            }
    
    def save_usage_record(self, usage_record: TokenUsage):
        """Salva registro de uso no banco"""
        with self.Session() as session:
            session.add(usage_record)
            session.commit()
    
    def mark_alert_sent(self, user_id: int, alert_type: str):
        """Marca alerta como enviado"""
        with self.Session() as session:
            user = session.query(User).filter(User.id == user_id).first()
            if user:
                if alert_type == '80':
                    user.alert_80_sent = True
                elif alert_type == '95':
                    user.alert_95_sent = True
                
                user.last_alert_date = datetime.utcnow()
                session.commit()
    
    def _log_token_transaction(self, user_id: int, amount: int, transaction_type: str, reason: str):
        """Log interno de transações de tokens"""
        # Implementar logging estruturado para auditoria
        pass
```

## Especificações do Dashboard Administrativo

### Estrutura do Projeto React

```
admin-ia-solaris/
├── public/
│   ├── index.html
│   └── favicon.ico
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Layout.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── LoadingSpinner.tsx
│   │   ├── dashboard/
│   │   │   ├── StatsCards.tsx
│   │   │   ├── UsageChart.tsx
│   │   │   └── AlertsPanel.tsx
│   │   ├── users/
│   │   │   ├── UsersList.tsx
│   │   │   ├── UserDetails.tsx
│   │   │   └── UserForm.tsx
│   │   └── reports/
│   │       ├── ConsumptionReport.tsx
│   │       └── ExportOptions.tsx
│   ├── hooks/
│   │   ├── useApi.ts
│   │   ├── useAuth.ts
│   │   └── useRealTime.ts
│   ├── services/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   └── websocket.ts
│   ├── types/
│   │   ├── user.ts
│   │   ├── token.ts
│   │   └── api.ts
│   ├── utils/
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   └── constants.ts
│   ├── App.tsx
│   ├── index.tsx
│   └── index.css
├── package.json
├── tsconfig.json
├── tailwind.config.js
└── Dockerfile
```

### Configuração Principal (package.json)

```json
{
  "name": "admin-ia-solaris",
  "version": "1.0.0",
  "private": true,
  "dependencies": {
    "@headlessui/react": "^1.7.17",
    "@heroicons/react": "^2.0.18",
    "@reduxjs/toolkit": "^1.9.7",
    "@tanstack/react-query": "^5.8.4",
    "axios": "^1.6.2",
    "chart.js": "^4.4.0",
    "date-fns": "^2.30.0",
    "react": "^18.2.0",
    "react-chartjs-2": "^5.2.0",
    "react-dom": "^18.2.0",
    "react-hook-form": "^7.47.0",
    "react-redux": "^8.1.3",
    "react-router-dom": "^6.18.0",
    "react-table": "^7.8.0",
    "socket.io-client": "^4.7.4",
    "tailwindcss": "^3.3.5",
    "typescript": "^5.2.2"
  },
  "devDependencies": {
    "@types/react": "^18.2.37",
    "@types/react-dom": "^18.2.15",
    "@types/react-table": "^7.7.18",
    "autoprefixer": "^10.4.16",
    "postcss": "^8.4.31",
    "vite": "^4.5.0",
    "@vitejs/plugin-react": "^4.1.1"
  },
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "preview": "vite preview",
    "test": "vitest",
    "lint": "eslint src --ext ts,tsx"
  }
}
```

### Tipos TypeScript

**types/user.ts:**

```typescript
export interface User {
  id: number;
  email: string;
  name: string;
  status: 'active' | 'suspended' | 'blocked' | 'pending';
  plan: 'basic' | 'pro' | 'enterprise' | 'trial';
  monthlyLimit: number;
  currentUsage: number;
  additionalTokens: number;
  usagePercentage: number;
  remainingTokens: number;
  alert80Sent: boolean;
  alert95Sent: boolean;
  lastAlertDate?: string;
  createdAt: string;
  updatedAt: string;
  lastLogin?: string;
}

export interface UserStats {
  user: User;
  tokens: {
    monthlyLimit: number;
    currentUsage: number;
    additionalTokens: number;
    remaining: number;
    usagePercentage: number;
  };
  usage30Days: number;
  usageByModel: Record<string, number>;
  alerts: {
    alert80Sent: boolean;
    alert95Sent: boolean;
    lastAlertDate?: string;
  };
}

export interface UserFilters {
  status?: string[];
  plan?: string[];
  usageLevel?: string[];
  dateRange?: {
    start: string;
    end: string;
  };
  search?: string;
}

export interface UserUpdateData {
  name?: string;
  status?: string;
  plan?: string;
  monthlyLimit?: number;
  additionalTokens?: number;
  reason?: string;
}
```

**types/token.ts:**

```typescript
export interface TokenUsage {
  id: number;
  userId: number;
  requestId: string;
  model: string;
  endpoint: string;
  method: string;
  promptTokens: number;
  completionTokens: number;
  totalTokens: number;
  costPerToken: number;
  totalCost: number;
  userAgent?: string;
  ipAddress?: string;
  responseTimeMs?: number;
  statusCode: number;
  errorMessage?: string;
  createdAt: string;
}

export interface SystemStats {
  users: {
    total: number;
    active: number;
    suspended: number;
    blocked: number;
  };
  usage: {
    monthlyTotal: number;
    averagePerUser: number;
  };
  topUsers: Array<{
    email: string;
    usage: number;
  }>;
}

export interface Alert {
  id: number;
  type: 'critical' | 'warning' | 'info';
  title: string;
  message: string;
  userId?: number;
  createdAt: string;
  resolvedAt?: string;
  actions?: string[];
}
```

### Serviços de API

**services/api.ts:**

```typescript
import axios, { AxiosInstance, AxiosResponse } from 'axios';
import { User, UserStats, UserFilters, UserUpdateData, SystemStats, TokenUsage, Alert } from '../types';

class ApiService {
  private api: AxiosInstance;

  constructor() {
    this.api = axios.create({
      baseURL: process.env.REACT_APP_API_BASE_URL || 'http://localhost:5000/api',
      timeout: 10000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Interceptor para adicionar token de autenticação
    this.api.interceptors.request.use((config) => {
      const token = localStorage.getItem('admin_token');
      if (token) {
        config.headers.Authorization = `Bearer ${token}`;
      }
      return config;
    });

    // Interceptor para tratar erros
    this.api.interceptors.response.use(
      (response) => response,
      (error) => {
        if (error.response?.status === 401) {
          localStorage.removeItem('admin_token');
          window.location.href = '/login';
        }
        return Promise.reject(error);
      }
    );
  }

  // Métodos de usuários
  async getUsers(filters?: UserFilters): Promise<User[]> {
    const response: AxiosResponse<User[]> = await this.api.get('/admin/users', {
      params: filters,
    });
    return response.data;
  }

  async getUserById(id: number): Promise<User> {
    const response: AxiosResponse<User> = await this.api.get(`/admin/users/${id}`);
    return response.data;
  }

  async getUserStats(id: number): Promise<UserStats> {
    const response: AxiosResponse<UserStats> = await this.api.get(`/admin/users/${id}/stats`);
    return response.data;
  }

  async updateUser(id: number, data: UserUpdateData): Promise<User> {
    const response: AxiosResponse<User> = await this.api.put(`/admin/users/${id}`, data);
    return response.data;
  }

  async suspendUser(id: number, reason: string): Promise<void> {
    await this.api.post(`/admin/users/${id}/suspend`, { reason });
  }

  async activateUser(id: number): Promise<void> {
    await this.api.post(`/admin/users/${id}/activate`);
  }

  async deleteUser(id: number): Promise<void> {
    await this.api.delete(`/admin/users/${id}`);
  }

  async addTokens(id: number, amount: number, reason: string): Promise<void> {
    await this.api.post(`/admin/users/${id}/tokens`, { amount, reason });
  }

  async resetMonthlyUsage(id: number): Promise<void> {
    await this.api.post(`/admin/users/${id}/reset-usage`);
  }

  // Métodos de sistema
  async getSystemStats(): Promise<SystemStats> {
    const response: AxiosResponse<SystemStats> = await this.api.get('/admin/stats');
    return response.data;
  }

  async getAlerts(): Promise<Alert[]> {
    const response: AxiosResponse<Alert[]> = await this.api.get('/admin/alerts');
    return response.data;
  }

  async resolveAlert(id: number): Promise<void> {
    await this.api.post(`/admin/alerts/${id}/resolve`);
  }

  // Métodos de relatórios
  async getUsageReport(filters: any): Promise<TokenUsage[]> {
    const response: AxiosResponse<TokenUsage[]> = await this.api.get('/admin/reports/usage', {
      params: filters,
    });
    return response.data;
  }

  async exportReport(type: string, format: string, filters: any): Promise<Blob> {
    const response = await this.api.post(
      '/admin/reports/export',
      { type, format, filters },
      { responseType: 'blob' }
    );
    return response.data;
  }

  // Métodos de autenticação
  async login(email: string, password: string): Promise<{ token: string; user: any }> {
    const response = await this.api.post('/auth/login', { email, password });
    return response.data;
  }

  async logout(): Promise<void> {
    await this.api.post('/auth/logout');
    localStorage.removeItem('admin_token');
  }

  async refreshToken(): Promise<{ token: string }> {
    const response = await this.api.post('/auth/refresh');
    return response.data;
  }
}

export const apiService = new ApiService();
export default apiService;
```

## Especificações de Infraestrutura

### Docker Compose Completo

```yaml
version: '3.8'

services:
  # Banco de dados principal
  postgres:
    image: postgres:15-alpine
    container_name: ia-solaris-db
    environment:
      POSTGRES_DB: ia_solaris
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./database/init-scripts:/docker-entrypoint-initdb.d
    ports:
      - "5432:5432"
    networks:
      - ia-solaris-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U postgres"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Cache Redis
  redis:
    image: redis:7-alpine
    container_name: ia-solaris-redis
    command: redis-server --requirepass ${REDIS_PASSWORD}
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    networks:
      - ia-solaris-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 30s
      timeout: 10s
      retries: 3

  # LiteLLM Proxy
  litellm:
    image: ghcr.io/berriai/litellm:main-latest
    container_name: ia-solaris-litellm
    environment:
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      ANTHROPIC_API_KEY: ${ANTHROPIC_API_KEY}
      DATABASE_URL: postgresql://postgres:${DB_PASSWORD}@postgres:5432/ia_solaris
    volumes:
      - ./database/litellm-config.yaml:/app/config.yaml
    ports:
      - "4000:4000"
    networks:
      - ia-solaris-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
    restart: unless-stopped
    command: ["--config", "/app/config.yaml", "--port", "4000", "--num_workers", "8"]

  # Proxy Inteligente
  proxy-inteligente:
    build:
      context: ./proxy-inteligente/proxy-ia-solaris
      dockerfile: Dockerfile
    container_name: ia-solaris-proxy
    environment:
      DB_HOST: postgres
      DB_PORT: 5432
      DB_NAME: ia_solaris
      DB_USER: postgres
      DB_PASSWORD: ${DB_PASSWORD}
      REDIS_HOST: redis
      REDIS_PORT: 6379
      REDIS_PASSWORD: ${REDIS_PASSWORD}
      LITELLM_BASE_URL: http://litellm:4000
      OPENAI_API_KEY: ${OPENAI_API_KEY}
      SMTP_HOST: ${SMTP_HOST}
      SMTP_PORT: ${SMTP_PORT}
      SMTP_USER: ${SMTP_USER}
      SMTP_PASSWORD: ${SMTP_PASSWORD}
      FROM_EMAIL: ${FROM_EMAIL}
      SECRET_KEY: ${SECRET_KEY}
      DEBUG: "false"
    ports:
      - "5000:5000"
    networks:
      - ia-solaris-network
    depends_on:
      postgres:
        condition: service_healthy
      redis:
        condition: service_healthy
      litellm:
        condition: service_started
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  # Dashboard Administrativo
  admin-dashboard:
    build:
      context: ./admin-dashboard/admin-ia-solaris
      dockerfile: Dockerfile
    container_name: ia-solaris-admin
    environment:
      REACT_APP_API_BASE_URL: http://proxy-inteligente:5000/api
    ports:
      - "3000:80"
    networks:
      - ia-solaris-network
    depends_on:
      - proxy-inteligente
    restart: unless-stopped

  # Nginx Reverse Proxy
  nginx:
    image: nginx:alpine
    container_name: ia-solaris-nginx
    volumes:
      - ./database/nginx.conf:/etc/nginx/nginx.conf
      - ./ssl:/etc/nginx/ssl
    ports:
      - "80:80"
      - "443:443"
    networks:
      - ia-solaris-network
    depends_on:
      - proxy-inteligente
      - admin-dashboard
    restart: unless-stopped

volumes:
  postgres_data:
  redis_data:

networks:
  ia-solaris-network:
    driver: bridge
```

### Configuração do Nginx

```nginx
events {
    worker_connections 1024;
}

http {
    upstream proxy_backend {
        server proxy-inteligente:5000;
    }
    
    upstream admin_backend {
        server admin-dashboard:80;
    }
    
    # Rate limiting
    limit_req_zone $binary_remote_addr zone=api:10m rate=10r/s;
    limit_req_zone $binary_remote_addr zone=admin:10m rate=5r/s;
    
    server {
        listen 80;
        server_name localhost;
        
        # Redirect HTTP to HTTPS in production
        # return 301 https://$server_name$request_uri;
        
        # API Proxy Routes
        location /v1/ {
            limit_req zone=api burst=20 nodelay;
            
            proxy_pass http://proxy_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
            
            # Timeouts
            proxy_connect_timeout 60s;
            proxy_send_timeout 60s;
            proxy_read_timeout 60s;
            
            # Buffer settings
            proxy_buffering on;
            proxy_buffer_size 4k;
            proxy_buffers 8 4k;
        }
        
        # Admin API Routes
        location /api/ {
            limit_req zone=admin burst=10 nodelay;
            
            proxy_pass http://proxy_backend;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Admin Dashboard
        location /admin/ {
            limit_req zone=admin burst=10 nodelay;
            
            proxy_pass http://admin_backend/;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
            proxy_set_header X-Forwarded-Proto $scheme;
        }
        
        # Health checks
        location /health {
            access_log off;
            return 200 "healthy\n";
            add_header Content-Type text/plain;
        }
        
        # Security headers
        add_header X-Frame-Options DENY;
        add_header X-Content-Type-Options nosniff;
        add_header X-XSS-Protection "1; mode=block";
        add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    }
    
    # HTTPS configuration (for production)
    server {
        listen 443 ssl http2;
        server_name localhost;
        
        ssl_certificate /etc/nginx/ssl/cert.pem;
        ssl_certificate_key /etc/nginx/ssl/key.pem;
        ssl_protocols TLSv1.2 TLSv1.3;
        ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        
        # Same location blocks as HTTP server
        # ... (repeat location blocks from above)
    }
}
```

### Scripts de Instalação

**scripts/install.sh:**

```bash
#!/bin/bash

set -e

echo "🚀 Iniciando instalação do MVP IA SOLARIS..."

# Verificar dependências
command -v docker >/dev/null 2>&1 || { echo "❌ Docker não encontrado. Instale o Docker primeiro."; exit 1; }
command -v docker-compose >/dev/null 2>&1 || { echo "❌ Docker Compose não encontrado. Instale o Docker Compose primeiro."; exit 1; }

# Verificar arquivo .env
if [ ! -f .env ]; then
    echo "📝 Criando arquivo .env a partir do template..."
    cp .env.example .env
    echo "⚠️  IMPORTANTE: Configure as variáveis no arquivo .env antes de continuar!"
    echo "   Especialmente: OPENAI_API_KEY, DB_PASSWORD, REDIS_PASSWORD"
    read -p "Pressione Enter após configurar o arquivo .env..."
fi

# Carregar variáveis de ambiente
source .env

# Verificar variáveis obrigatórias
if [ -z "$OPENAI_API_KEY" ]; then
    echo "❌ OPENAI_API_KEY não configurada no arquivo .env"
    exit 1
fi

if [ -z "$DB_PASSWORD" ]; then
    echo "❌ DB_PASSWORD não configurada no arquivo .env"
    exit 1
fi

echo "🔧 Construindo imagens Docker..."
docker-compose build --no-cache

echo "🗄️  Iniciando banco de dados..."
docker-compose up -d postgres redis

echo "⏳ Aguardando banco de dados ficar pronto..."
sleep 30

echo "🔄 Executando migrações do banco..."
docker-compose run --rm proxy-inteligente python -c "
from src.models.user import Base
from src.config.settings import AppConfig
from sqlalchemy import create_engine

config = AppConfig()
engine = create_engine(config.database.url)
Base.metadata.create_all(engine)
print('✅ Tabelas criadas com sucesso!')
"

echo "🚀 Iniciando todos os serviços..."
docker-compose up -d

echo "⏳ Aguardando serviços ficarem prontos..."
sleep 60

# Verificar se os serviços estão funcionando
echo "🔍 Verificando status dos serviços..."

# Verificar proxy
if curl -f http://localhost:5000/health >/dev/null 2>&1; then
    echo "✅ Proxy Inteligente: OK"
else
    echo "❌ Proxy Inteligente: FALHA"
fi

# Verificar admin dashboard
if curl -f http://localhost:3000 >/dev/null 2>&1; then
    echo "✅ Dashboard Admin: OK"
else
    echo "❌ Dashboard Admin: FALHA"
fi

# Verificar LiteLLM
if curl -f http://localhost:4000/health >/dev/null 2>&1; then
    echo "✅ LiteLLM: OK"
else
    echo "❌ LiteLLM: FALHA"
fi

echo ""
echo "🎉 Instalação concluída!"
echo ""
echo "📋 Acessos disponíveis:"
echo "   • Proxy API: http://localhost:5000"
echo "   • Dashboard Admin: http://localhost:3000"
echo "   • LiteLLM: http://localhost:4000"
echo ""
echo "🔧 Para integrar com LibreChat, configure:"
echo "   OPENAI_REVERSE_PROXY=http://localhost:5000/v1"
echo ""
echo "📊 Para monitorar os logs:"
echo "   docker-compose logs -f"
echo ""
echo "🛑 Para parar os serviços:"
echo "   docker-compose down"
echo ""
echo "✅ Sistema pronto para uso!"
```

### Monitoramento e Observabilidade

**Configuração de Logs Estruturados:**

```python
import logging
import json
from datetime import datetime
from typing import Dict, Any

class StructuredLogger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)
        
        # Handler para stdout
        handler = logging.StreamHandler()
        handler.setFormatter(self.JsonFormatter())
        self.logger.addHandler(handler)
    
    class JsonFormatter(logging.Formatter):
        def format(self, record):
            log_entry = {
                'timestamp': datetime.utcnow().isoformat(),
                'level': record.levelname,
                'logger': record.name,
                'message': record.getMessage(),
                'module': record.module,
                'function': record.funcName,
                'line': record.lineno
            }
            
            # Adicionar campos extras se existirem
            if hasattr(record, 'user_id'):
                log_entry['user_id'] = record.user_id
            if hasattr(record, 'request_id'):
                log_entry['request_id'] = record.request_id
            if hasattr(record, 'tokens_used'):
                log_entry['tokens_used'] = record.tokens_used
            
            return json.dumps(log_entry)
    
    def info(self, message: str, **kwargs):
        self._log(logging.INFO, message, **kwargs)
    
    def warning(self, message: str, **kwargs):
        self._log(logging.WARNING, message, **kwargs)
    
    def error(self, message: str, **kwargs):
        self._log(logging.ERROR, message, **kwargs)
    
    def _log(self, level: int, message: str, **kwargs):
        extra = {k: v for k, v in kwargs.items() if k not in ['exc_info', 'stack_info']}
        self.logger.log(level, message, extra=extra)

# Uso do logger
logger = StructuredLogger('ia-solaris')

# Exemplo de uso
logger.info("Token consumption", 
           user_id=123, 
           request_id="req_abc123", 
           tokens_used=1500,
           model="gpt-4")
```

**Health Checks Avançados:**

```python
from flask import Blueprint, jsonify
import psutil
import redis
from sqlalchemy import text
from ..config.settings import AppConfig
from ..services.token_service import TokenService

health_bp = Blueprint('health', __name__)

@health_bp.route('/health')
def health_check():
    """Health check básico"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.utcnow().isoformat(),
        'version': '1.0.0'
    })

@health_bp.route('/health/detailed')
def detailed_health_check():
    """Health check detalhado com dependências"""
    config = AppConfig()
    checks = {}
    overall_status = 'healthy'
    
    # Verificar banco de dados
    try:
        token_service = TokenService()
        with token_service.Session() as session:
            session.execute(text('SELECT 1'))
        checks['database'] = {'status': 'healthy', 'response_time_ms': 0}
    except Exception as e:
        checks['database'] = {'status': 'unhealthy', 'error': str(e)}
        overall_status = 'unhealthy'
    
    # Verificar Redis
    try:
        r = redis.Redis.from_url(config.redis.url)
        start_time = time.time()
        r.ping()
        response_time = (time.time() - start_time) * 1000
        checks['redis'] = {'status': 'healthy', 'response_time_ms': round(response_time, 2)}
    except Exception as e:
        checks['redis'] = {'status': 'unhealthy', 'error': str(e)}
        overall_status = 'unhealthy'
    
    # Verificar LiteLLM
    try:
        response = requests.get(f"{config.litellm_base_url}/health", timeout=5)
        if response.status_code == 200:
            checks['litellm'] = {'status': 'healthy', 'response_time_ms': response.elapsed.total_seconds() * 1000}
        else:
            checks['litellm'] = {'status': 'unhealthy', 'status_code': response.status_code}
            overall_status = 'degraded'
    except Exception as e:
        checks['litellm'] = {'status': 'unhealthy', 'error': str(e)}
        overall_status = 'unhealthy'
    
    # Verificar recursos do sistema
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    
    checks['system'] = {
        'status': 'healthy' if cpu_percent < 80 and memory.percent < 80 else 'degraded',
        'cpu_percent': cpu_percent,
        'memory_percent': memory.percent,
        'disk_percent': (disk.used / disk.total) * 100
    }
    
    if checks['system']['status'] == 'degraded':
        overall_status = 'degraded'
    
    return jsonify({
        'status': overall_status,
        'timestamp': datetime.utcnow().isoformat(),
        'checks': checks
    })

@health_bp.route('/metrics')
def metrics():
    """Métricas para Prometheus"""
    token_service = TokenService()
    stats = token_service.get_system_stats()
    
    metrics_text = f"""
# HELP ia_solaris_users_total Total number of users
# TYPE ia_solaris_users_total gauge
ia_solaris_users_total{{status="active"}} {stats['users']['active']}
ia_solaris_users_total{{status="suspended"}} {stats['users']['suspended']}
ia_solaris_users_total{{status="blocked"}} {stats['users']['blocked']}

# HELP ia_solaris_tokens_used_total Total tokens used this month
# TYPE ia_solaris_tokens_used_total counter
ia_solaris_tokens_used_total {stats['usage']['monthly_total']}

# HELP ia_solaris_tokens_average_per_user Average tokens per active user
# TYPE ia_solaris_tokens_average_per_user gauge
ia_solaris_tokens_average_per_user {stats['usage']['average_per_user']}
"""
    
    return metrics_text, 200, {'Content-Type': 'text/plain; charset=utf-8'}
```

---

**Autor:** Manus AI  
**Data:** Janeiro 2024  
**Versão:** 1.0

