# Desenvolvimento do Proxy Inteligente - MVP IA SOLARIS

## Visão Geral

Este documento detalha o desenvolvimento completo do Proxy Inteligente, o componente central do MVP híbrido de controle de tokens da IA SOLARIS. O proxy atua como um middleware transparente entre o LibreChat e os provedores de IA, implementando controle de tokens, sistema de alertas e auditoria completa de uso.

## Arquitetura do Proxy

### Fluxo de Requisições

```
LibreChat → Nginx → Proxy Inteligente → LiteLLM → Provedor IA
     ↑                    ↓                         ↑
     └── Resposta ←── Processamento ←── Resposta ←──┘
                          ↓
                    [Controle de Tokens]
                    [Sistema de Alertas]
                    [Logging/Auditoria]
                    [Cache/Performance]
```

### Componentes Principais

1. **Interceptador de Requisições:** Captura todas as chamadas para IA
2. **Controlador de Tokens:** Gerencia limites e consumo
3. **Sistema de Alertas:** Notificações automáticas por email
4. **Auditoria:** Logging completo de todas as operações
5. **Cache Inteligente:** Otimização de performance
6. **API Administrativa:** Interface para gestão

## Estrutura do Projeto

### Organização de Diretórios

```
proxy-ia-solaris/
├── src/
│   ├── __init__.py
│   ├── main.py                 # Aplicação Flask principal
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py         # Configurações centralizadas
│   │   ├── database.py         # Setup do banco de dados
│   │   └── logging.py          # Configuração de logs
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py             # Modelo base SQLAlchemy
│   │   ├── user.py             # Modelo de usuário
│   │   ├── token_usage.py      # Histórico de uso de tokens
│   │   ├── transaction.py      # Transações financeiras
│   │   ├── alert.py            # Sistema de alertas
│   │   └── audit_log.py        # Logs de auditoria
│   ├── services/
│   │   ├── __init__.py
│   │   ├── proxy_service.py    # Lógica principal do proxy
│   │   ├── token_service.py    # Gestão de tokens
│   │   ├── alert_service.py    # Sistema de alertas
│   │   ├── email_service.py    # Envio de emails
│   │   ├── cache_service.py    # Gerenciamento de cache
│   │   ├── audit_service.py    # Auditoria e compliance
│   │   └── litellm_service.py  # Integração com LiteLLM
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── proxy_routes.py     # Rotas do proxy (/v1/*)
│   │   ├── admin_routes.py     # Rotas administrativas (/api/admin/*)
│   │   ├── auth_routes.py      # Autenticação (/api/auth/*)
│   │   ├── user_routes.py      # Rotas de usuário (/api/user/*)
│   │   └── health_routes.py    # Health checks (/health, /metrics)
│   ├── middleware/
│   │   ├── __init__.py
│   │   ├── auth_middleware.py  # Autenticação e autorização
│   │   ├── rate_limit.py       # Rate limiting
│   │   ├── cors_middleware.py  # CORS handling
│   │   └── error_handler.py    # Tratamento de erros
│   ├── utils/
│   │   ├── __init__.py
│   │   ├── decorators.py       # Decoradores customizados
│   │   ├── validators.py       # Validações de entrada
│   │   ├── helpers.py          # Funções auxiliares
│   │   ├── constants.py        # Constantes do sistema
│   │   └── exceptions.py       # Exceções customizadas
│   └── templates/
│       ├── emails/
│       │   ├── alert_80.html   # Template alerta 80%
│       │   ├── alert_95.html   # Template alerta 95%
│       │   ├── blocked.html    # Template bloqueio
│       │   └── monthly_reset.html # Template renovação mensal
│       └── admin/
│           └── dashboard.html  # Dashboard básico
├── tests/
│   ├── __init__.py
│   ├── conftest.py            # Configurações pytest
│   ├── unit/
│   │   ├── test_models.py
│   │   ├── test_services.py
│   │   └── test_utils.py
│   ├── integration/
│   │   ├── test_proxy_flow.py
│   │   ├── test_admin_api.py
│   │   └── test_alerts.py
│   └── fixtures/
│       ├── sample_requests.json
│       └── test_data.sql
├── migrations/
│   ├── versions/
│   └── alembic.ini
├── requirements.txt
├── requirements-dev.txt
├── Dockerfile
├── docker-compose.dev.yml
├── .env.example
├── .gitignore
├── pytest.ini
├── setup.py
└── README.md
```

## Configuração e Setup

### Arquivo de Configurações (config/settings.py)

```python
import os
from dataclasses import dataclass, field
from typing import Optional, List, Dict, Any
from urllib.parse import quote_plus

@dataclass
class DatabaseConfig:
    """Configurações do banco de dados PostgreSQL"""
    host: str = os.getenv('DB_HOST', 'localhost')
    port: int = int(os.getenv('DB_PORT', '5432'))
    name: str = os.getenv('DB_NAME', 'ia_solaris')
    user: str = os.getenv('DB_USER', 'postgres')
    password: str = os.getenv('DB_PASSWORD', '')
    
    # Configurações de pool de conexões
    pool_size: int = int(os.getenv('DB_POOL_SIZE', '10'))
    max_overflow: int = int(os.getenv('DB_MAX_OVERFLOW', '20'))
    pool_timeout: int = int(os.getenv('DB_POOL_TIMEOUT', '30'))
    pool_recycle: int = int(os.getenv('DB_POOL_RECYCLE', '3600'))
    
    # SSL
    ssl_mode: str = os.getenv('DB_SSL_MODE', 'prefer')
    
    @property
    def url(self) -> str:
        """URL de conexão com o banco"""
        password_encoded = quote_plus(self.password) if self.password else ''
        auth = f"{self.user}:{password_encoded}@" if self.user else ""
        return f"postgresql://{auth}{self.host}:{self.port}/{self.name}"
    
    @property
    def async_url(self) -> str:
        """URL de conexão assíncrona"""
        return self.url.replace('postgresql://', 'postgresql+asyncpg://')

@dataclass
class RedisConfig:
    """Configurações do Redis para cache e sessões"""
    host: str = os.getenv('REDIS_HOST', 'localhost')
    port: int = int(os.getenv('REDIS_PORT', '6379'))
    db: int = int(os.getenv('REDIS_DB', '0'))
    password: Optional[str] = os.getenv('REDIS_PASSWORD')
    
    # Configurações de pool
    max_connections: int = int(os.getenv('REDIS_MAX_CONNECTIONS', '50'))
    retry_on_timeout: bool = os.getenv('REDIS_RETRY_ON_TIMEOUT', 'true').lower() == 'true'
    socket_timeout: int = int(os.getenv('REDIS_SOCKET_TIMEOUT', '5'))
    
    @property
    def url(self) -> str:
        """URL de conexão com Redis"""
        auth = f":{self.password}@" if self.password else ""
        return f"redis://{auth}{self.host}:{self.port}/{self.db}"

@dataclass
class TokenConfig:
    """Configurações de controle de tokens"""
    default_monthly_limit: int = int(os.getenv('DEFAULT_MONTHLY_LIMIT', '1000000'))
    alert_threshold_80: float = float(os.getenv('ALERT_THRESHOLD_80', '0.8'))
    alert_threshold_95: float = float(os.getenv('ALERT_THRESHOLD_95', '0.95'))
    block_threshold: float = float(os.getenv('BLOCK_THRESHOLD', '1.0'))
    
    # Limites do sistema
    max_user_limit: int = int(os.getenv('MAX_USER_LIMIT', '10000000'))
    min_user_limit: int = int(os.getenv('MIN_USER_LIMIT', '100000'))
    
    # Estimativa de tokens
    chars_per_token: float = float(os.getenv('CHARS_PER_TOKEN', '4.0'))
    estimation_margin: float = float(os.getenv('ESTIMATION_MARGIN', '1.2'))
    
    # Cache de verificações
    cache_ttl_seconds: int = int(os.getenv('TOKEN_CACHE_TTL', '300'))

@dataclass
class EmailConfig:
    """Configurações de email SMTP"""
    smtp_host: str = os.getenv('SMTP_HOST', 'smtp.gmail.com')
    smtp_port: int = int(os.getenv('SMTP_PORT', '587'))
    smtp_user: str = os.getenv('SMTP_USER', '')
    smtp_password: str = os.getenv('SMTP_PASSWORD', '')
    from_email: str = os.getenv('FROM_EMAIL', 'noreply@iasolaris.com')
    from_name: str = os.getenv('FROM_NAME', 'IA SOLARIS')
    use_tls: bool = os.getenv('SMTP_TLS', 'true').lower() == 'true'
    use_ssl: bool = os.getenv('SMTP_SSL', 'false').lower() == 'true'
    
    # Configurações de retry
    max_retries: int = int(os.getenv('EMAIL_MAX_RETRIES', '3'))
    retry_delay: int = int(os.getenv('EMAIL_RETRY_DELAY', '5'))
    
    # Templates
    template_dir: str = os.getenv('EMAIL_TEMPLATE_DIR', 'src/templates/emails')

@dataclass
class LiteLLMConfig:
    """Configurações de integração com LiteLLM"""
    base_url: str = os.getenv('LITELLM_BASE_URL', 'http://localhost:4000')
    timeout: int = int(os.getenv('LITELLM_TIMEOUT', '600'))
    max_retries: int = int(os.getenv('LITELLM_MAX_RETRIES', '3'))
    retry_delay: int = int(os.getenv('LITELLM_RETRY_DELAY', '1'))
    
    # Health check
    health_check_interval: int = int(os.getenv('LITELLM_HEALTH_CHECK_INTERVAL', '60'))
    health_check_timeout: int = int(os.getenv('LITELLM_HEALTH_CHECK_TIMEOUT', '10'))

@dataclass
class SecurityConfig:
    """Configurações de segurança"""
    secret_key: str = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')
    jwt_secret: str = os.getenv('JWT_SECRET', secret_key)
    jwt_expiration_hours: int = int(os.getenv('JWT_EXPIRATION_HOURS', '24'))
    
    # Rate limiting
    rate_limit_per_minute: int = int(os.getenv('RATE_LIMIT_PER_MINUTE', '60'))
    rate_limit_burst: int = int(os.getenv('RATE_LIMIT_BURST', '10'))
    
    # CORS
    cors_origins: List[str] = field(default_factory=lambda: 
        os.getenv('CORS_ORIGINS', 'http://localhost:3000').split(','))
    
    # API Keys
    admin_api_key: Optional[str] = os.getenv('ADMIN_API_KEY')

@dataclass
class LoggingConfig:
    """Configurações de logging"""
    level: str = os.getenv('LOG_LEVEL', 'INFO')
    format: str = os.getenv('LOG_FORMAT', 'json')  # json ou text
    file_path: Optional[str] = os.getenv('LOG_FILE_PATH')
    max_file_size: str = os.getenv('LOG_MAX_FILE_SIZE', '10MB')
    backup_count: int = int(os.getenv('LOG_BACKUP_COUNT', '5'))
    
    # Structured logging
    include_request_id: bool = os.getenv('LOG_INCLUDE_REQUEST_ID', 'true').lower() == 'true'
    include_user_id: bool = os.getenv('LOG_INCLUDE_USER_ID', 'true').lower() == 'true'

@dataclass
class AppConfig:
    """Configuração principal da aplicação"""
    # Configurações básicas
    debug: bool = os.getenv('DEBUG', 'false').lower() == 'true'
    testing: bool = os.getenv('TESTING', 'false').lower() == 'true'
    host: str = os.getenv('HOST', '0.0.0.0')
    port: int = int(os.getenv('PORT', '5000'))
    workers: int = int(os.getenv('WORKERS', '4'))
    
    # Configurações de integração
    openai_api_key: str = os.getenv('OPENAI_API_KEY', '')
    anthropic_api_key: str = os.getenv('ANTHROPIC_API_KEY', '')
    
    # Instâncias de configuração
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    redis: RedisConfig = field(default_factory=RedisConfig)
    tokens: TokenConfig = field(default_factory=TokenConfig)
    email: EmailConfig = field(default_factory=EmailConfig)
    litellm: LiteLLMConfig = field(default_factory=LiteLLMConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    logging: LoggingConfig = field(default_factory=LoggingConfig)
    
    def __post_init__(self):
        """Validações pós-inicialização"""
        if not self.openai_api_key and not self.testing:
            raise ValueError("OPENAI_API_KEY é obrigatória")
        
        if not self.security.secret_key or self.security.secret_key == 'dev-secret-key-change-in-production':
            if not self.debug and not self.testing:
                raise ValueError("SECRET_KEY deve ser configurada para produção")
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Cria configuração a partir de variáveis de ambiente"""
        return cls()

# Instância global de configuração
config = AppConfig.from_env()
```

### Configuração do Banco de Dados (config/database.py)

```python
from sqlalchemy import create_engine, event
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import QueuePool
import logging
from contextlib import contextmanager
from typing import Generator

from .settings import config

logger = logging.getLogger(__name__)

# Base para todos os modelos
Base = declarative_base()

class DatabaseManager:
    """Gerenciador de conexões com banco de dados"""
    
    def __init__(self):
        self.engine = None
        self.SessionLocal = None
        self._setup_engine()
        self._setup_session()
    
    def _setup_engine(self):
        """Configura engine do SQLAlchemy"""
        self.engine = create_engine(
            config.database.url,
            poolclass=QueuePool,
            pool_size=config.database.pool_size,
            max_overflow=config.database.max_overflow,
            pool_timeout=config.database.pool_timeout,
            pool_recycle=config.database.pool_recycle,
            pool_pre_ping=True,  # Verifica conexões antes de usar
            echo=config.debug,   # Log SQL queries em debug
            future=True          # SQLAlchemy 2.0 style
        )
        
        # Event listeners para logging
        if config.logging.level == 'DEBUG':
            event.listen(self.engine, "before_cursor_execute", self._log_sql_start)
            event.listen(self.engine, "after_cursor_execute", self._log_sql_end)
    
    def _setup_session(self):
        """Configura factory de sessões"""
        self.SessionLocal = sessionmaker(
            bind=self.engine,
            autocommit=False,
            autoflush=False,
            expire_on_commit=False
        )
    
    def _log_sql_start(self, conn, cursor, statement, parameters, context, executemany):
        """Log início de query SQL"""
        context._query_start_time = time.time()
        logger.debug(f"SQL Query Start: {statement[:100]}...")
    
    def _log_sql_end(self, conn, cursor, statement, parameters, context, executemany):
        """Log fim de query SQL"""
        total = time.time() - context._query_start_time
        logger.debug(f"SQL Query End: {total:.4f}s")
    
    @contextmanager
    def get_session(self) -> Generator[Session, None, None]:
        """Context manager para sessões de banco"""
        session = self.SessionLocal()
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            session.close()
    
    def create_tables(self):
        """Cria todas as tabelas"""
        Base.metadata.create_all(bind=self.engine)
        logger.info("Database tables created successfully")
    
    def drop_tables(self):
        """Remove todas as tabelas (cuidado!)"""
        Base.metadata.drop_all(bind=self.engine)
        logger.warning("All database tables dropped")
    
    def health_check(self) -> bool:
        """Verifica saúde da conexão com banco"""
        try:
            with self.get_session() as session:
                session.execute("SELECT 1")
            return True
        except Exception as e:
            logger.error(f"Database health check failed: {e}")
            return False

# Instância global do gerenciador
db_manager = DatabaseManager()

# Função helper para obter sessão
def get_db_session():
    """Função helper para obter sessão de banco"""
    return db_manager.get_session()

# Dependency para FastAPI/Flask
def get_db():
    """Dependency injection para sessão de banco"""
    with db_manager.get_session() as session:
        yield session
```

## Modelos de Dados

### Modelo Base (models/base.py)

```python
from sqlalchemy import Column, Integer, DateTime, String
from sqlalchemy.ext.declarative import declared_attr
from datetime import datetime
import uuid

from ..config.database import Base

class TimestampMixin:
    """Mixin para campos de timestamp"""
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

class UUIDMixin:
    """Mixin para UUID como chave primária"""
    @declared_attr
    def uuid(cls):
        return Column(String(36), default=lambda: str(uuid.uuid4()), unique=True, nullable=False)

class BaseModel(Base, TimestampMixin):
    """Modelo base para todas as entidades"""
    __abstract__ = True
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    def to_dict(self) -> dict:
        """Converte modelo para dicionário"""
        return {
            column.name: getattr(self, column.name)
            for column in self.__table__.columns
        }
    
    def update_from_dict(self, data: dict):
        """Atualiza modelo a partir de dicionário"""
        for key, value in data.items():
            if hasattr(self, key):
                setattr(self, key, value)
        self.updated_at = datetime.utcnow()
    
    def __repr__(self):
        return f"<{self.__class__.__name__}(id={self.id})>"
```

### Modelo de Usuário (models/user.py)

```python
from sqlalchemy import Column, Integer, String, Boolean, Float, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional
import enum

from .base import BaseModel

class UserStatus(enum.Enum):
    """Status possíveis do usuário"""
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BLOCKED = "blocked"
    PENDING = "pending"

class UserPlan(enum.Enum):
    """Planos disponíveis"""
    BASIC = "basic"
    PRO = "pro"
    ENTERPRISE = "enterprise"
    TRIAL = "trial"

class User(BaseModel):
    """Modelo de usuário do sistema"""
    __tablename__ = 'users'
    
    # Informações básicas
    email = Column(String(255), unique=True, nullable=False, index=True)
    name = Column(String(255), nullable=False)
    phone = Column(String(20), nullable=True)
    
    # Status e plano
    status = Column(Enum(UserStatus), default=UserStatus.ACTIVE, nullable=False, index=True)
    plan = Column(Enum(UserPlan), default=UserPlan.BASIC, nullable=False)
    
    # Controle de tokens
    monthly_limit = Column(Integer, default=1000000, nullable=False)
    current_usage = Column(Integer, default=0, nullable=False)
    additional_tokens = Column(Integer, default=0, nullable=False)
    
    # Controle de alertas
    alert_80_sent = Column(Boolean, default=False, nullable=False)
    alert_95_sent = Column(Boolean, default=False, nullable=False)
    last_alert_date = Column(DateTime, nullable=True)
    
    # Metadados
    last_login = Column(DateTime, nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    notes = Column(Text, nullable=True)  # Notas administrativas
    
    # Configurações personalizadas
    custom_alert_threshold_80 = Column(Float, nullable=True)
    custom_alert_threshold_95 = Column(Float, nullable=True)
    email_notifications_enabled = Column(Boolean, default=True, nullable=False)
    
    # Relacionamentos
    token_usages = relationship("TokenUsage", back_populates="user", cascade="all, delete-orphan")
    transactions = relationship("Transaction", back_populates="user", cascade="all, delete-orphan")
    alerts = relationship("Alert", back_populates="user", cascade="all, delete-orphan")
    audit_logs = relationship("AuditLog", back_populates="user", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', status='{self.status.value}')>"
    
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
    
    @property
    def is_active(self) -> bool:
        """Verifica se usuário está ativo"""
        return self.status == UserStatus.ACTIVE
    
    @property
    def alert_threshold_80(self) -> float:
        """Retorna threshold personalizado ou padrão para alerta 80%"""
        return self.custom_alert_threshold_80 or 0.8
    
    @property
    def alert_threshold_95(self) -> float:
        """Retorna threshold personalizado ou padrão para alerta 95%"""
        return self.custom_alert_threshold_95 or 0.95
    
    def can_use_tokens(self, amount: int) -> bool:
        """Verifica se usuário pode usar quantidade específica de tokens"""
        return (
            self.is_active and 
            self.remaining_tokens >= amount
        )
    
    def consume_tokens(self, amount: int) -> bool:
        """Consome tokens do usuário"""
        if not self.can_use_tokens(amount):
            return False
        
        self.current_usage += amount
        self.updated_at = datetime.utcnow()
        return True
    
    def add_additional_tokens(self, amount: int) -> None:
        """Adiciona tokens adicionais"""
        self.additional_tokens += amount
        self.updated_at = datetime.utcnow()
    
    def reset_monthly_usage(self) -> None:
        """Reseta uso mensal (mantém tokens adicionais)"""
        self.current_usage = 0
        self.alert_80_sent = False
        self.alert_95_sent = False
        self.last_alert_date = None
        self.updated_at = datetime.utcnow()
    
    def should_send_alert_80(self) -> bool:
        """Verifica se deve enviar alerta de 80%"""
        return (
            self.usage_percentage >= (self.alert_threshold_80 * 100) and
            not self.alert_80_sent and
            self.email_notifications_enabled
        )
    
    def should_send_alert_95(self) -> bool:
        """Verifica se deve enviar alerta de 95%"""
        return (
            self.usage_percentage >= (self.alert_threshold_95 * 100) and
            not self.alert_95_sent and
            self.email_notifications_enabled
        )
    
    def mark_alert_sent(self, alert_type: str) -> None:
        """Marca alerta como enviado"""
        if alert_type == '80':
            self.alert_80_sent = True
        elif alert_type == '95':
            self.alert_95_sent = True
        
        self.last_alert_date = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_login(self) -> None:
        """Atualiza informações de login"""
        self.last_login = datetime.utcnow()
        self.login_count += 1
        self.updated_at = datetime.utcnow()
    
    def suspend(self, reason: Optional[str] = None) -> None:
        """Suspende usuário"""
        self.status = UserStatus.SUSPENDED
        if reason:
            self.notes = f"{self.notes or ''}\n[{datetime.utcnow()}] Suspenso: {reason}".strip()
        self.updated_at = datetime.utcnow()
    
    def activate(self) -> None:
        """Ativa usuário"""
        self.status = UserStatus.ACTIVE
        self.updated_at = datetime.utcnow()
    
    def block(self, reason: Optional[str] = None) -> None:
        """Bloqueia usuário"""
        self.status = UserStatus.BLOCKED
        if reason:
            self.notes = f"{self.notes or ''}\n[{datetime.utcnow()}] Bloqueado: {reason}".strip()
        self.updated_at = datetime.utcnow()
```

### Modelo de Uso de Tokens (models/token_usage.py)

```python
from sqlalchemy import Column, Integer, String, DateTime, Float, Text, ForeignKey, Boolean, Index
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Optional, Dict, Any

from .base import BaseModel

class TokenUsage(BaseModel):
    """Modelo para histórico de uso de tokens"""
    __tablename__ = 'token_usage'
    
    # Relacionamento com usuário
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False, index=True)
    user = relationship("User", back_populates="token_usages")
    
    # Identificação da requisição
    request_id = Column(String(255), unique=True, nullable=False, index=True)
    session_id = Column(String(255), nullable=True, index=True)
    
    # Detalhes da requisição
    model = Column(String(100), nullable=False, index=True)  # gpt-4, claude-3, etc.
    endpoint = Column(String(255), nullable=False)  # /v1/chat/completions
    method = Column(String(10), default='POST', nullable=False)
    
    # Tokens utilizados
    prompt_tokens = Column(Integer, default=0, nullable=False)
    completion_tokens = Column(Integer, default=0, nullable=False)
    total_tokens = Column(Integer, nullable=False, index=True)
    
    # Estimativa vs real
    estimated_tokens = Column(Integer, nullable=True)
    estimation_accuracy = Column(Float, nullable=True)  # % de precisão da estimativa
    
    # Custos (para relatórios financeiros)
    cost_per_token = Column(Float, default=0.0, nullable=False)
    total_cost = Column(Float, default=0.0, nullable=False)
    
    # Metadados da requisição
    user_agent = Column(String(500), nullable=True)
    ip_address = Column(String(45), nullable=True, index=True)
    country_code = Column(String(2), nullable=True)  # Geolocalização
    
    # Performance
    response_time_ms = Column(Integer, nullable=True)
    queue_time_ms = Column(Integer, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    
    # Status da requisição
    status_code = Column(Integer, nullable=False, index=True)
    error_message = Column(Text, nullable=True)
    error_type = Column(String(100), nullable=True, index=True)
    
    # Flags de controle
    is_cached = Column(Boolean, default=False, nullable=False)
    is_retry = Column(Boolean, default=False, nullable=False)
    retry_count = Column(Integer, default=0, nullable=False)
    
    # Dados da requisição (para auditoria)
    request_data = Column(Text, nullable=True)  # JSON serializado
    response_data = Column(Text, nullable=True)  # JSON serializado
    
    # Índices compostos para performance
    __table_args__ = (
        Index('idx_user_date', 'user_id', 'created_at'),
        Index('idx_model_date', 'model', 'created_at'),
        Index('idx_status_date', 'status_code', 'created_at'),
        Index('idx_user_model_date', 'user_id', 'model', 'created_at'),
    )
    
    def __repr__(self):
        return f"<TokenUsage(id={self.id}, user_id={self.user_id}, tokens={self.total_tokens}, model='{self.model}')>"
    
    @classmethod
    def create_from_request(
        cls, 
        user_id: int, 
        request_data: Dict[str, Any], 
        response_data: Dict[str, Any],
        performance_metrics: Optional[Dict[str, Any]] = None
    ) -> 'TokenUsage':
        """Cria registro de uso a partir de dados de requisição e resposta"""
        
        usage = response_data.get('usage', {})
        performance = performance_metrics or {}
        
        # Calcular precisão da estimativa
        estimated = request_data.get('estimated_tokens', 0)
        actual = usage.get('total_tokens', 0)
        accuracy = None
        if estimated > 0 and actual > 0:
            accuracy = min(100.0, (min(estimated, actual) / max(estimated, actual)) * 100)
        
        return cls(
            user_id=user_id,
            request_id=request_data.get('request_id'),
            session_id=request_data.get('session_id'),
            model=request_data.get('model', 'unknown'),
            endpoint=request_data.get('endpoint', '/v1/chat/completions'),
            method=request_data.get('method', 'POST'),
            
            # Tokens
            prompt_tokens=usage.get('prompt_tokens', 0),
            completion_tokens=usage.get('completion_tokens', 0),
            total_tokens=usage.get('total_tokens', 0),
            estimated_tokens=estimated,
            estimation_accuracy=accuracy,
            
            # Custos
            cost_per_token=response_data.get('cost_per_token', 0.0),
            total_cost=response_data.get('total_cost', 0.0),
            
            # Metadados
            user_agent=request_data.get('user_agent'),
            ip_address=request_data.get('ip_address'),
            country_code=request_data.get('country_code'),
            
            # Performance
            response_time_ms=performance.get('response_time_ms'),
            queue_time_ms=performance.get('queue_time_ms'),
            processing_time_ms=performance.get('processing_time_ms'),
            
            # Status
            status_code=response_data.get('status_code', 200),
            error_message=response_data.get('error'),
            error_type=response_data.get('error_type'),
            
            # Flags
            is_cached=performance.get('is_cached', False),
            is_retry=performance.get('is_retry', False),
            retry_count=performance.get('retry_count', 0),
            
            # Dados brutos (para auditoria)
            request_data=request_data.get('raw_request'),
            response_data=response_data.get('raw_response')
        )
    
    @property
    def is_successful(self) -> bool:
        """Verifica se a requisição foi bem-sucedida"""
        return 200 <= self.status_code < 300
    
    @property
    def is_error(self) -> bool:
        """Verifica se houve erro na requisição"""
        return self.status_code >= 400
    
    def calculate_efficiency_score(self) -> float:
        """Calcula score de eficiência da requisição"""
        score = 100.0
        
        # Penalizar por tempo de resposta alto
        if self.response_time_ms:
            if self.response_time_ms > 10000:  # > 10s
                score -= 30
            elif self.response_time_ms > 5000:  # > 5s
                score -= 15
            elif self.response_time_ms > 2000:  # > 2s
                score -= 5
        
        # Penalizar por erros
        if self.is_error:
            score -= 50
        
        # Penalizar por retries
        score -= (self.retry_count * 10)
        
        # Bonificar por cache hit
        if self.is_cached:
            score += 10
        
        # Bonificar por estimativa precisa
        if self.estimation_accuracy and self.estimation_accuracy > 90:
            score += 5
        
        return max(0.0, min(100.0, score))
```

## Serviços Principais

### Serviço de Proxy (services/proxy_service.py)

```python
import asyncio
import aiohttp
import time
import json
import uuid
from typing import Dict, Any, Optional, Tuple
from flask import current_app, request
from datetime import datetime

from ..models.user import User
from ..models.token_usage import TokenUsage
from .token_service import TokenService
from .alert_service import AlertService
from .cache_service import CacheService
from .audit_service import AuditService
from ..utils.helpers import generate_request_id, extract_user_from_request, estimate_tokens
from ..utils.exceptions import (
    UserNotFoundError, 
    InsufficientTokensError, 
    LiteLLMError,
    RateLimitError
)
from ..config.settings import config

class ProxyService:
    """Serviço principal do proxy inteligente"""
    
    def __init__(self):
        self.token_service = TokenService()
        self.alert_service = AlertService()
        self.cache_service = CacheService()
        self.audit_service = AuditService()
        self.litellm_base_url = config.litellm.base_url
        
        # Métricas em memória
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'total_tokens_processed': 0,
            'cache_hits': 0,
            'cache_misses': 0
        }
    
    async def process_request(self, request_data: Dict[str, Any]) -> Tuple[Dict[str, Any], int]:
        """
        Processa requisição completa com controle de tokens
        
        Args:
            request_data: Dados da requisição HTTP
            
        Returns:
            Tuple com (response_data, status_code)
        """
        start_time = time.time()
        request_id = generate_request_id()
        
        # Incrementar métricas
        self.metrics['total_requests'] += 1
        
        try:
            # 1. Extrair e validar usuário
            user_email = extract_user_from_request(request_data)
            if not user_email:
                raise UserNotFoundError("Usuário não identificado na requisição")
            
            # 2. Obter ou criar usuário
            user = await self.token_service.get_or_create_user_async(user_email)
            if not user:
                raise UserNotFoundError(f"Erro ao processar usuário: {user_email}")
            
            # 3. Verificar status do usuário
            if not user.is_active:
                await self.audit_service.log_blocked_request(
                    user_id=user.id,
                    reason=f"Usuário com status: {user.status.value}",
                    request_id=request_id
                )
                return {
                    "error": f"Conta {user.status.value}. Contate o suporte.",
                    "code": "ACCOUNT_SUSPENDED"
                }, 403
            
            # 4. Verificar rate limiting
            if not await self._check_rate_limit(user.id):
                raise RateLimitError("Rate limit excedido")
            
            # 5. Verificar cache
            cache_key = self._generate_cache_key(request_data)
            cached_response = await self.cache_service.get(cache_key)
            
            if cached_response:
                self.metrics['cache_hits'] += 1
                await self._log_cached_usage(user, request_data, cached_response, request_id)
                return cached_response, 200
            
            self.metrics['cache_misses'] += 1
            
            # 6. Estimar tokens da requisição
            estimated_tokens = estimate_tokens(request_data)
            
            # 7. Verificar disponibilidade de tokens
            if not user.can_use_tokens(estimated_tokens):
                await self.alert_service.send_block_alert(user)
                await self.audit_service.log_blocked_request(
                    user_id=user.id,
                    reason="Tokens insuficientes",
                    request_id=request_id,
                    estimated_tokens=estimated_tokens
                )
                
                return {
                    "error": "Limite de tokens esgotado",
                    "code": "INSUFFICIENT_TOKENS",
                    "details": {
                        "used": user.current_usage,
                        "limit": user.monthly_limit,
                        "additional": user.additional_tokens,
                        "estimated_needed": estimated_tokens
                    }
                }, 429
            
            # 8. Fazer requisição para LiteLLM
            response_data, status_code, performance_metrics = await self._forward_request(
                request_data, request_id
            )
            
            # 9. Processar resposta bem-sucedida
            if status_code == 200 and 'usage' in response_data:
                await self._process_successful_response(
                    user, request_data, response_data, performance_metrics, request_id
                )
                
                # Cache da resposta se apropriado
                if self._should_cache_response(request_data, response_data):
                    await self.cache_service.set(cache_key, response_data, ttl=300)
            
            # 10. Processar resposta com erro
            elif status_code >= 400:
                await self._process_error_response(
                    user, request_data, response_data, performance_metrics, request_id
                )
            
            # Atualizar métricas
            if status_code < 400:
                self.metrics['successful_requests'] += 1
            else:
                self.metrics['failed_requests'] += 1
            
            return response_data, status_code
            
        except Exception as e:
            self.metrics['failed_requests'] += 1
            current_app.logger.error(f"Erro no proxy: {e}", extra={
                'request_id': request_id,
                'user_email': user_email if 'user_email' in locals() else None,
                'error_type': type(e).__name__
            })
            
            return {
                "error": "Erro interno do servidor",
                "code": "INTERNAL_ERROR",
                "request_id": request_id
            }, 500
        
        finally:
            # Log de performance
            total_time = (time.time() - start_time) * 1000
            current_app.logger.info(f"Request processed", extra={
                'request_id': request_id,
                'total_time_ms': total_time,
                'status_code': status_code if 'status_code' in locals() else None
            })
    
    async def _forward_request(
        self, 
        request_data: Dict[str, Any], 
        request_id: str
    ) -> Tuple[Dict[str, Any], int, Dict[str, Any]]:
        """Encaminha requisição para LiteLLM"""
        
        start_time = time.time()
        
        try:
            url = f"{self.litellm_base_url}/v1/chat/completions"
            headers = {
                'Content-Type': 'application/json',
                'Authorization': request_data.get('authorization', ''),
                'X-Request-ID': request_id,
                'User-Agent': 'IA-SOLARIS-Proxy/1.0'
            }
            
            # Preparar payload
            payload = {
                'model': request_data.get('model', 'gpt-3.5-turbo'),
                'messages': request_data.get('messages', []),
                'temperature': request_data.get('temperature', 0.7),
                'max_tokens': request_data.get('max_tokens'),
                'stream': request_data.get('stream', False)
            }
            
            # Remover campos None
            payload = {k: v for k, v in payload.items() if v is not None}
            
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=config.litellm.timeout)
            ) as session:
                async with session.post(url, json=payload, headers=headers) as response:
                    response_data = await response.json()
                    
                    # Métricas de performance
                    performance_metrics = {
                        'response_time_ms': int((time.time() - start_time) * 1000),
                        'litellm_status': response.status,
                        'is_cached': False,
                        'is_retry': False,
                        'retry_count': 0
                    }
                    
                    return response_data, response.status, performance_metrics
                    
        except asyncio.TimeoutError:
            raise LiteLLMError("Timeout na requisição para LiteLLM")
        except aiohttp.ClientError as e:
            raise LiteLLMError(f"Erro de conexão com LiteLLM: {e}")
        except Exception as e:
            raise LiteLLMError(f"Erro inesperado: {e}")
    
    async def _process_successful_response(
        self,
        user: User,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        performance_metrics: Dict[str, Any],
        request_id: str
    ):
        """Processa resposta bem-sucedida"""
        
        usage = response_data.get('usage', {})
        actual_tokens = usage.get('total_tokens', 0)
        
        # Consumir tokens reais
        success = await self.token_service.consume_tokens_async(user.id, actual_tokens)
        if not success:
            current_app.logger.error(f"Falha ao consumir tokens para usuário {user.id}")
        
        # Atualizar métricas globais
        self.metrics['total_tokens_processed'] += actual_tokens
        
        # Registrar uso no histórico
        usage_record = TokenUsage.create_from_request(
            user_id=user.id,
            request_data={
                **request_data,
                'request_id': request_id,
                'estimated_tokens': request_data.get('estimated_tokens', 0)
            },
            response_data=response_data,
            performance_metrics=performance_metrics
        )
        
        await self.token_service.save_usage_record_async(usage_record)
        
        # Verificar e enviar alertas
        await self._check_and_send_alerts(user)
        
        # Log de auditoria
        await self.audit_service.log_successful_request(
            user_id=user.id,
            request_id=request_id,
            tokens_used=actual_tokens,
            model=request_data.get('model'),
            cost=response_data.get('total_cost', 0.0)
        )
    
    async def _process_error_response(
        self,
        user: User,
        request_data: Dict[str, Any],
        response_data: Dict[str, Any],
        performance_metrics: Dict[str, Any],
        request_id: str
    ):
        """Processa resposta com erro"""
        
        # Registrar erro no histórico (sem consumir tokens)
        usage_record = TokenUsage.create_from_request(
            user_id=user.id,
            request_data={
                **request_data,
                'request_id': request_id
            },
            response_data=response_data,
            performance_metrics=performance_metrics
        )
        
        await self.token_service.save_usage_record_async(usage_record)
        
        # Log de auditoria
        await self.audit_service.log_failed_request(
            user_id=user.id,
            request_id=request_id,
            error_message=response_data.get('error', 'Unknown error'),
            error_code=response_data.get('code'),
            status_code=performance_metrics.get('litellm_status', 500)
        )
    
    async def _check_and_send_alerts(self, user: User):
        """Verifica e envia alertas baseados no uso atual"""
        
        # Alerta de 80%
        if user.should_send_alert_80():
            await self.alert_service.send_usage_alert(user, 80)
            await self.token_service.mark_alert_sent_async(user.id, '80')
        
        # Alerta de 95%
        elif user.should_send_alert_95():
            await self.alert_service.send_usage_alert(user, 95)
            await self.token_service.mark_alert_sent_async(user.id, '95')
    
    async def _check_rate_limit(self, user_id: int) -> bool:
        """Verifica rate limiting por usuário"""
        key = f"rate_limit:user:{user_id}"
        current_count = await self.cache_service.get(key) or 0
        
        if current_count >= config.security.rate_limit_per_minute:
            return False
        
        await self.cache_service.increment(key, ttl=60)
        return True
    
    def _generate_cache_key(self, request_data: Dict[str, Any]) -> str:
        """Gera chave de cache para a requisição"""
        # Cache baseado em modelo, mensagens e parâmetros
        cache_data = {
            'model': request_data.get('model'),
            'messages': request_data.get('messages', []),
            'temperature': request_data.get('temperature', 0.7),
            'max_tokens': request_data.get('max_tokens')
        }
        
        # Hash do conteúdo para gerar chave única
        import hashlib
        content = json.dumps(cache_data, sort_keys=True)
        return f"proxy_cache:{hashlib.md5(content.encode()).hexdigest()}"
    
    def _should_cache_response(
        self, 
        request_data: Dict[str, Any], 
        response_data: Dict[str, Any]
    ) -> bool:
        """Determina se resposta deve ser cacheada"""
        
        # Não cachear se temperatura alta (respostas muito variáveis)
        if request_data.get('temperature', 0.7) > 0.8:
            return False
        
        # Não cachear se streaming
        if request_data.get('stream', False):
            return False
        
        # Não cachear se houve erro
        if 'error' in response_data:
            return False
        
        # Não cachear respostas muito grandes
        if len(str(response_data)) > 10000:  # 10KB
            return False
        
        return True
    
    async def _log_cached_usage(
        self,
        user: User,
        request_data: Dict[str, Any],
        cached_response: Dict[str, Any],
        request_id: str
    ):
        """Registra uso de resposta cacheada"""
        
        # Ainda consome tokens mesmo sendo cache
        usage = cached_response.get('usage', {})
        tokens = usage.get('total_tokens', 0)
        
        if tokens > 0:
            await self.token_service.consume_tokens_async(user.id, tokens)
            
            # Registrar no histórico com flag de cache
            usage_record = TokenUsage.create_from_request(
                user_id=user.id,
                request_data={
                    **request_data,
                    'request_id': request_id
                },
                response_data=cached_response,
                performance_metrics={
                    'response_time_ms': 50,  # Cache é rápido
                    'is_cached': True,
                    'is_retry': False,
                    'retry_count': 0
                }
            )
            
            await self.token_service.save_usage_record_async(usage_record)
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do proxy"""
        return {
            **self.metrics,
            'cache_hit_rate': (
                self.metrics['cache_hits'] / 
                (self.metrics['cache_hits'] + self.metrics['cache_misses'])
                if (self.metrics['cache_hits'] + self.metrics['cache_misses']) > 0 
                else 0
            ),
            'success_rate': (
                self.metrics['successful_requests'] / self.metrics['total_requests']
                if self.metrics['total_requests'] > 0
                else 0
            )
        }
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do serviço de proxy"""
        checks = {}
        
        # Verificar LiteLLM
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.litellm_base_url}/health",
                    timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    checks['litellm'] = {
                        'status': 'healthy' if response.status == 200 else 'unhealthy',
                        'response_time_ms': 0  # Calcular se necessário
                    }
        except Exception as e:
            checks['litellm'] = {
                'status': 'unhealthy',
                'error': str(e)
            }
        
        # Verificar serviços dependentes
        checks['token_service'] = await self.token_service.health_check()
        checks['cache_service'] = await self.cache_service.health_check()
        
        # Status geral
        overall_status = 'healthy' if all(
            check.get('status') == 'healthy' 
            for check in checks.values()
        ) else 'unhealthy'
        
        return {
            'status': overall_status,
            'checks': checks,
            'metrics': self.get_metrics()
        }
```

---

**Autor:** Manus AI  
**Data:** Janeiro 2024  
**Versão:** 1.0

