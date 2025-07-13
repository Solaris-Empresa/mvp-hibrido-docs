from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import uuid

db = SQLAlchemy()

class UserAccount(db.Model):
    """Modelo para contas de usuário com controle de tokens"""
    __tablename__ = 'user_accounts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    librechat_user_id = db.Column(db.String(255), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    name = db.Column(db.String(255), nullable=True)
    
    # Controle de tokens
    total_tokens = db.Column(db.Integer, default=1000, nullable=False)
    used_tokens = db.Column(db.Integer, default=0, nullable=False)
    
    # Configurações de alerta
    alert_threshold_80 = db.Column(db.Float, default=0.8, nullable=False)
    alert_threshold_95 = db.Column(db.Float, default=0.95, nullable=False)
    
    # Status da conta
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_blocked = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    last_activity = db.Column(db.DateTime, nullable=True)
    
    # Relacionamentos
    transactions = db.relationship('TokenTransaction', backref='user_account', lazy=True, cascade='all, delete-orphan')
    alerts = db.relationship('UserAlert', backref='user_account', lazy=True, cascade='all, delete-orphan')
    
    @property
    def remaining_tokens(self):
        """Calcula tokens restantes"""
        return max(0, self.total_tokens - self.used_tokens)
    
    @property
    def usage_percentage(self):
        """Calcula percentual de uso"""
        if self.total_tokens == 0:
            return 100.0
        return (self.used_tokens / self.total_tokens) * 100
    
    @property
    def should_alert_80(self):
        """Verifica se deve alertar 80%"""
        return self.usage_percentage >= (self.alert_threshold_80 * 100)
    
    @property
    def should_alert_95(self):
        """Verifica se deve alertar 95%"""
        return self.usage_percentage >= (self.alert_threshold_95 * 100)
    
    @property
    def should_block(self):
        """Verifica se deve bloquear"""
        return self.remaining_tokens <= 0
    
    def can_consume_tokens(self, tokens_needed):
        """Verifica se pode consumir tokens"""
        return (
            self.is_active and 
            not self.is_blocked and 
            self.remaining_tokens >= tokens_needed
        )
    
    def consume_tokens(self, tokens_used, model_used=None, request_id=None, cost_usd=None):
        """Consome tokens e registra transação"""
        if not self.can_consume_tokens(tokens_used):
            raise ValueError("Tokens insuficientes ou conta bloqueada")
        
        # Atualiza contadores
        self.used_tokens += tokens_used
        self.last_activity = datetime.utcnow()
        
        # Verifica se deve bloquear
        if self.should_block:
            self.is_blocked = True
        
        # Registra transação
        transaction = TokenTransaction(
            user_account_id=self.id,
            tokens_used=tokens_used,
            model_used=model_used,
            request_id=request_id,
            cost_usd=cost_usd
        )
        
        db.session.add(transaction)
        return transaction
    
    def add_tokens(self, tokens_to_add, reason="manual_addition"):
        """Adiciona tokens à conta"""
        self.total_tokens += tokens_to_add
        
        # Remove bloqueio se havia
        if self.is_blocked and self.remaining_tokens > 0:
            self.is_blocked = False
        
        # Registra transação de crédito
        transaction = TokenTransaction(
            user_account_id=self.id,
            tokens_used=-tokens_to_add,  # Negativo indica crédito
            model_used="credit",
            request_id=reason
        )
        
        db.session.add(transaction)
        return transaction
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'librechat_user_id': self.librechat_user_id,
            'email': self.email,
            'name': self.name,
            'total_tokens': self.total_tokens,
            'used_tokens': self.used_tokens,
            'remaining_tokens': self.remaining_tokens,
            'usage_percentage': round(self.usage_percentage, 2),
            'is_active': self.is_active,
            'is_blocked': self.is_blocked,
            'should_alert_80': self.should_alert_80,
            'should_alert_95': self.should_alert_95,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
            'last_activity': self.last_activity.isoformat() if self.last_activity else None
        }


class TokenTransaction(db.Model):
    """Modelo para transações de tokens"""
    __tablename__ = 'token_transactions'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_account_id = db.Column(db.String(36), db.ForeignKey('user_accounts.id'), nullable=False, index=True)
    
    # Detalhes da transação
    tokens_used = db.Column(db.Integer, nullable=False)  # Negativo para créditos
    model_used = db.Column(db.String(100), nullable=True)
    request_id = db.Column(db.String(255), nullable=True)
    cost_usd = db.Column(db.Numeric(10, 6), nullable=True)
    
    # Metadados
    prompt_tokens = db.Column(db.Integer, nullable=True)
    completion_tokens = db.Column(db.Integer, nullable=True)
    total_tokens = db.Column(db.Integer, nullable=True)
    
    # Timestamp
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'user_account_id': self.user_account_id,
            'tokens_used': self.tokens_used,
            'model_used': self.model_used,
            'request_id': self.request_id,
            'cost_usd': float(self.cost_usd) if self.cost_usd else None,
            'prompt_tokens': self.prompt_tokens,
            'completion_tokens': self.completion_tokens,
            'total_tokens': self.total_tokens,
            'created_at': self.created_at.isoformat()
        }


class UserAlert(db.Model):
    """Modelo para alertas de usuário"""
    __tablename__ = 'user_alerts'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_account_id = db.Column(db.String(36), db.ForeignKey('user_accounts.id'), nullable=False, index=True)
    
    # Tipo de alerta
    alert_type = db.Column(db.String(50), nullable=False)  # '80_percent', '95_percent', 'blocked'
    alert_message = db.Column(db.Text, nullable=True)
    
    # Status
    is_sent = db.Column(db.Boolean, default=False, nullable=False)
    is_resolved = db.Column(db.Boolean, default=False, nullable=False)
    
    # Timestamps
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    sent_at = db.Column(db.DateTime, nullable=True)
    resolved_at = db.Column(db.DateTime, nullable=True)
    
    def mark_as_sent(self):
        """Marca alerta como enviado"""
        self.is_sent = True
        self.sent_at = datetime.utcnow()
    
    def mark_as_resolved(self):
        """Marca alerta como resolvido"""
        self.is_resolved = True
        self.resolved_at = datetime.utcnow()
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'user_account_id': self.user_account_id,
            'alert_type': self.alert_type,
            'alert_message': self.alert_message,
            'is_sent': self.is_sent,
            'is_resolved': self.is_resolved,
            'created_at': self.created_at.isoformat(),
            'sent_at': self.sent_at.isoformat() if self.sent_at else None,
            'resolved_at': self.resolved_at.isoformat() if self.resolved_at else None
        }


class SystemConfig(db.Model):
    """Modelo para configurações do sistema"""
    __tablename__ = 'system_config'
    
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    key = db.Column(db.String(100), unique=True, nullable=False)
    value = db.Column(db.Text, nullable=True)
    description = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    
    @staticmethod
    def get_config(key, default=None):
        """Obtém configuração por chave"""
        config = SystemConfig.query.filter_by(key=key).first()
        return config.value if config else default
    
    @staticmethod
    def set_config(key, value, description=None):
        """Define configuração"""
        config = SystemConfig.query.filter_by(key=key).first()
        if config:
            config.value = value
            if description:
                config.description = description
        else:
            config = SystemConfig(key=key, value=value, description=description)
            db.session.add(config)
        
        db.session.commit()
        return config
    
    def to_dict(self):
        """Converte para dicionário"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'description': self.description,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }

