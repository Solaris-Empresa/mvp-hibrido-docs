import requests
import json
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from flask import current_app
from src.models.token_control import db, UserAccount, TokenTransaction, UserAlert
from src.services.litellm_service import LiteLLMService
from src.services.email_service import EmailService

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ProxyService:
    """Serviço principal do proxy inteligente"""
    
    def __init__(self):
        self.litellm_service = LiteLLMService()
        self.email_service = EmailService()
        
        # Configurações padrão
        self.default_tokens_per_user = 1000
        self.conversion_factor = 0.376  # Fator de conversão baseado na análise
        
    def get_or_create_user(self, librechat_user_id: str, email: str = None, name: str = None) -> UserAccount:
        """Obtém ou cria usuário no sistema"""
        try:
            # Busca usuário existente
            user = UserAccount.query.filter_by(librechat_user_id=librechat_user_id).first()
            
            if not user:
                # Cria novo usuário
                user = UserAccount(
                    librechat_user_id=librechat_user_id,
                    email=email or f"user_{librechat_user_id}@iasolaris.com.br",
                    name=name or f"Usuário {librechat_user_id[:8]}",
                    total_tokens=self.default_tokens_per_user
                )
                db.session.add(user)
                db.session.commit()
                
                logger.info(f"Novo usuário criado: {user.email} (ID: {user.id})")
            
            return user
            
        except Exception as e:
            logger.error(f"Erro ao obter/criar usuário {librechat_user_id}: {str(e)}")
            db.session.rollback()
            raise
    
    def estimate_tokens_needed(self, request_data: Dict[str, Any]) -> int:
        """Estima tokens necessários para a requisição"""
        try:
            # Extrai mensagens da requisição
            messages = request_data.get('messages', [])
            model = request_data.get('model', 'gpt-3.5-turbo')
            
            # Calcula tokens aproximados baseado no texto
            total_chars = 0
            for message in messages:
                content = message.get('content', '')
                if isinstance(content, str):
                    total_chars += len(content)
                elif isinstance(content, list):
                    # Para mensagens com imagens/conteúdo misto
                    for item in content:
                        if isinstance(item, dict) and item.get('type') == 'text':
                            total_chars += len(item.get('text', ''))
            
            # Estimativa conservadora: 4 chars = 1 token
            estimated_tokens = max(100, total_chars // 4)
            
            # Adiciona margem de segurança para resposta
            if 'gpt-4' in model.lower():
                estimated_tokens = int(estimated_tokens * 1.5)  # GPT-4 usa mais tokens
            else:
                estimated_tokens = int(estimated_tokens * 1.2)  # Margem para resposta
            
            logger.info(f"Tokens estimados para modelo {model}: {estimated_tokens}")
            return estimated_tokens
            
        except Exception as e:
            logger.error(f"Erro ao estimar tokens: {str(e)}")
            return 500  # Estimativa conservadora em caso de erro
    
    def check_user_limits(self, user: UserAccount, tokens_needed: int) -> Tuple[bool, str]:
        """Verifica se usuário pode consumir tokens"""
        try:
            # Verifica se conta está ativa
            if not user.is_active:
                return False, "Conta desativada"
            
            # Verifica se está bloqueado
            if user.is_blocked:
                return False, "Conta bloqueada por excesso de uso"
            
            # Verifica se tem tokens suficientes
            if user.remaining_tokens < tokens_needed:
                return False, f"Tokens insuficientes. Disponível: {user.remaining_tokens}, Necessário: {tokens_needed}"
            
            return True, "OK"
            
        except Exception as e:
            logger.error(f"Erro ao verificar limites do usuário {user.id}: {str(e)}")
            return False, "Erro interno do sistema"
    
    def process_openai_request(self, user: UserAccount, request_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Processa requisição para OpenAI via LiteLLM"""
        try:
            # Estima tokens necessários
            tokens_needed = self.estimate_tokens_needed(request_data)
            
            # Verifica limites do usuário
            can_proceed, message = self.check_user_limits(user, tokens_needed)
            if not can_proceed:
                return False, {
                    'error': 'insufficient_tokens',
                    'message': message,
                    'user_info': {
                        'remaining_tokens': user.remaining_tokens,
                        'total_tokens': user.total_tokens,
                        'usage_percentage': user.usage_percentage
                    }
                }
            
            # Faz requisição via LiteLLM
            success, response_data = self.litellm_service.make_request(request_data)
            
            if success:
                # Extrai informações de uso real
                usage = response_data.get('usage', {})
                actual_tokens = usage.get('total_tokens', tokens_needed)
                
                # Aplica fator de conversão
                converted_tokens = int(actual_tokens * self.conversion_factor)
                
                # Registra consumo
                transaction = user.consume_tokens(
                    tokens_used=converted_tokens,
                    model_used=request_data.get('model'),
                    request_id=response_data.get('id'),
                    cost_usd=self.calculate_cost(actual_tokens, request_data.get('model'))
                )
                
                # Salva no banco
                db.session.commit()
                
                # Verifica se precisa enviar alertas
                self.check_and_send_alerts(user)
                
                logger.info(f"Requisição processada para usuário {user.email}. Tokens consumidos: {converted_tokens}")
                
                # Adiciona informações de uso à resposta
                response_data['ia_solaris_usage'] = {
                    'tokens_consumed': converted_tokens,
                    'remaining_tokens': user.remaining_tokens,
                    'usage_percentage': user.usage_percentage,
                    'transaction_id': transaction.id
                }
                
                return True, response_data
            else:
                return False, response_data
                
        except Exception as e:
            logger.error(f"Erro ao processar requisição OpenAI para usuário {user.id}: {str(e)}")
            db.session.rollback()
            return False, {
                'error': 'internal_error',
                'message': 'Erro interno do sistema'
            }
    
    def calculate_cost(self, tokens: int, model: str) -> float:
        """Calcula custo em USD baseado no modelo"""
        # Preços por 1K tokens (aproximados)
        pricing = {
            'gpt-3.5-turbo': 0.002,
            'gpt-4': 0.03,
            'gpt-4-turbo': 0.01,
            'gpt-4o': 0.005,
            'claude-3-sonnet': 0.003,
            'claude-3-opus': 0.015
        }
        
        # Busca preço do modelo (padrão para gpt-3.5-turbo)
        price_per_1k = pricing.get(model, 0.002)
        
        return (tokens / 1000) * price_per_1k
    
    def check_and_send_alerts(self, user: UserAccount):
        """Verifica e envia alertas necessários"""
        try:
            current_time = datetime.utcnow()
            
            # Verifica alerta de 80%
            if user.should_alert_80:
                # Verifica se já foi enviado nas últimas 24h
                recent_alert = UserAlert.query.filter_by(
                    user_account_id=user.id,
                    alert_type='80_percent'
                ).filter(
                    UserAlert.created_at > current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                ).first()
                
                if not recent_alert:
                    self.send_alert_80_percent(user)
            
            # Verifica alerta de 95%
            if user.should_alert_95:
                recent_alert = UserAlert.query.filter_by(
                    user_account_id=user.id,
                    alert_type='95_percent'
                ).filter(
                    UserAlert.created_at > current_time.replace(hour=0, minute=0, second=0, microsecond=0)
                ).first()
                
                if not recent_alert:
                    self.send_alert_95_percent(user)
            
            # Verifica bloqueio
            if user.should_block and not user.is_blocked:
                user.is_blocked = True
                db.session.commit()
                self.send_alert_blocked(user)
                
        except Exception as e:
            logger.error(f"Erro ao verificar alertas para usuário {user.id}: {str(e)}")
    
    def send_alert_80_percent(self, user: UserAccount):
        """Envia alerta de 80% de consumo"""
        try:
            alert = UserAlert(
                user_account_id=user.id,
                alert_type='80_percent',
                alert_message=f"Você consumiu 80% dos seus tokens. Restam {user.remaining_tokens} tokens."
            )
            db.session.add(alert)
            
            # Envia email
            success = self.email_service.send_alert_80_percent(user)
            if success:
                alert.mark_as_sent()
            
            db.session.commit()
            logger.info(f"Alerta 80% enviado para usuário {user.email}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar alerta 80% para usuário {user.id}: {str(e)}")
    
    def send_alert_95_percent(self, user: UserAccount):
        """Envia alerta de 95% de consumo"""
        try:
            alert = UserAlert(
                user_account_id=user.id,
                alert_type='95_percent',
                alert_message=f"ATENÇÃO: Você consumiu 95% dos seus tokens. Restam apenas {user.remaining_tokens} tokens."
            )
            db.session.add(alert)
            
            # Envia email
            success = self.email_service.send_alert_95_percent(user)
            if success:
                alert.mark_as_sent()
            
            db.session.commit()
            logger.info(f"Alerta 95% enviado para usuário {user.email}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar alerta 95% para usuário {user.id}: {str(e)}")
    
    def send_alert_blocked(self, user: UserAccount):
        """Envia alerta de conta bloqueada"""
        try:
            alert = UserAlert(
                user_account_id=user.id,
                alert_type='blocked',
                alert_message="Sua conta foi bloqueada por esgotamento de tokens."
            )
            db.session.add(alert)
            
            # Envia email
            success = self.email_service.send_alert_blocked(user)
            if success:
                alert.mark_as_sent()
            
            db.session.commit()
            logger.info(f"Alerta de bloqueio enviado para usuário {user.email}")
            
        except Exception as e:
            logger.error(f"Erro ao enviar alerta de bloqueio para usuário {user.id}: {str(e)}")
    
    def get_user_stats(self, user: UserAccount) -> Dict[str, Any]:
        """Obtém estatísticas do usuário"""
        try:
            # Busca transações recentes
            recent_transactions = TokenTransaction.query.filter_by(
                user_account_id=user.id
            ).order_by(TokenTransaction.created_at.desc()).limit(10).all()
            
            # Calcula estatísticas
            total_transactions = TokenTransaction.query.filter_by(user_account_id=user.id).count()
            
            return {
                'user_info': user.to_dict(),
                'recent_transactions': [t.to_dict() for t in recent_transactions],
                'total_transactions': total_transactions,
                'daily_usage': self.calculate_daily_usage(user),
                'monthly_projection': self.calculate_monthly_projection(user)
            }
            
        except Exception as e:
            logger.error(f"Erro ao obter estatísticas do usuário {user.id}: {str(e)}")
            return {'error': 'Erro ao obter estatísticas'}
    
    def calculate_daily_usage(self, user: UserAccount) -> int:
        """Calcula uso médio diário"""
        try:
            from sqlalchemy import func
            from datetime import timedelta
            
            # Últimos 7 dias
            seven_days_ago = datetime.utcnow() - timedelta(days=7)
            
            result = db.session.query(
                func.sum(TokenTransaction.tokens_used)
            ).filter(
                TokenTransaction.user_account_id == user.id,
                TokenTransaction.created_at >= seven_days_ago,
                TokenTransaction.tokens_used > 0  # Apenas débitos
            ).scalar()
            
            total_usage = result or 0
            return int(total_usage / 7)  # Média diária
            
        except Exception as e:
            logger.error(f"Erro ao calcular uso diário para usuário {user.id}: {str(e)}")
            return 0
    
    def calculate_monthly_projection(self, user: UserAccount) -> int:
        """Calcula projeção mensal baseada no uso atual"""
        daily_usage = self.calculate_daily_usage(user)
        return daily_usage * 30

