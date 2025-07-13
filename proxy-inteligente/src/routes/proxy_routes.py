from flask import Blueprint, request, jsonify, current_app
from functools import wraps
import logging
import json
from datetime import datetime
from src.models.token_control import db, UserAccount
from src.services.proxy_service import ProxyService

# Configurar logging
logger = logging.getLogger(__name__)

# Criar blueprint
proxy_bp = Blueprint('proxy', __name__)

# Instanciar serviço
proxy_service = ProxyService()

def extract_user_info(request):
    """Extrai informações do usuário da requisição"""
    try:
        # Tenta extrair do header Authorization
        auth_header = request.headers.get('Authorization', '')
        if auth_header.startswith('Bearer '):
            # Aqui você pode decodificar o JWT se necessário
            token = auth_header[7:]
            # Por simplicidade, vamos usar um ID de usuário do header
            user_id = request.headers.get('X-User-ID')
            user_email = request.headers.get('X-User-Email')
            user_name = request.headers.get('X-User-Name')
            
            if not user_id:
                # Fallback: usar um ID baseado no token ou IP
                user_id = request.headers.get('X-Forwarded-For', request.remote_addr)
                user_email = f"user_{user_id}@iasolaris.com.br"
            
            return user_id, user_email, user_name
        
        # Fallback para desenvolvimento
        return "dev_user_001", "dev@iasolaris.com.br", "Usuário Desenvolvimento"
        
    except Exception as e:
        logger.error(f"Erro ao extrair informações do usuário: {str(e)}")
        return None, None, None

def require_user(f):
    """Decorator para garantir que o usuário está autenticado"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        user_id, user_email, user_name = extract_user_info(request)
        
        if not user_id:
            return jsonify({
                'error': 'authentication_required',
                'message': 'Autenticação necessária'
            }), 401
        
        try:
            # Obtém ou cria usuário
            user = proxy_service.get_or_create_user(user_id, user_email, user_name)
            request.current_user = user
            
        except Exception as e:
            logger.error(f"Erro ao obter usuário: {str(e)}")
            return jsonify({
                'error': 'user_error',
                'message': 'Erro ao processar usuário'
            }), 500
        
        return f(*args, **kwargs)
    
    return decorated_function

@proxy_bp.route('/health', methods=['GET'])
def health_check():
    """Endpoint de health check"""
    try:
        # Testa conexão com banco
        db.session.execute('SELECT 1')
        
        # Testa LiteLLM
        litellm_status, litellm_message = proxy_service.litellm_service.test_connection()
        
        return jsonify({
            'status': 'healthy',
            'timestamp': datetime.utcnow().isoformat(),
            'database': 'connected',
            'litellm': {
                'status': 'connected' if litellm_status else 'disconnected',
                'message': litellm_message
            }
        })
        
    except Exception as e:
        logger.error(f"Health check falhou: {str(e)}")
        return jsonify({
            'status': 'unhealthy',
            'error': str(e)
        }), 500

@proxy_bp.route('/chat/completions', methods=['POST'])
@require_user
def chat_completions():
    """Endpoint principal para interceptar requisições de chat"""
    try:
        user = request.current_user
        request_data = request.get_json()
        
        if not request_data:
            return jsonify({
                'error': 'invalid_request',
                'message': 'Dados da requisição inválidos'
            }), 400
        
        # Valida requisição
        is_valid, validation_message = proxy_service.litellm_service.validate_request(request_data)
        if not is_valid:
            return jsonify({
                'error': 'validation_error',
                'message': validation_message
            }), 400
        
        # Processa requisição
        success, response_data = proxy_service.process_openai_request(user, request_data)
        
        if success:
            return jsonify(response_data)
        else:
            # Verifica se é erro de tokens insuficientes
            if response_data.get('error') == 'insufficient_tokens':
                return jsonify(response_data), 402  # Payment Required
            else:
                return jsonify(response_data), 500
                
    except Exception as e:
        logger.error(f"Erro no endpoint chat/completions: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Erro interno do servidor'
        }), 500

@proxy_bp.route('/user/info', methods=['GET'])
@require_user
def get_user_info():
    """Obtém informações do usuário atual"""
    try:
        user = request.current_user
        stats = proxy_service.get_user_stats(user)
        
        return jsonify(stats)
        
    except Exception as e:
        logger.error(f"Erro ao obter informações do usuário: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Erro ao obter informações do usuário'
        }), 500

@proxy_bp.route('/user/usage', methods=['GET'])
@require_user
def get_user_usage():
    """Obtém estatísticas de uso do usuário"""
    try:
        user = request.current_user
        
        # Parâmetros de consulta
        limit = request.args.get('limit', 50, type=int)
        offset = request.args.get('offset', 0, type=int)
        
        # Busca transações
        from src.models.token_control import TokenTransaction
        transactions = TokenTransaction.query.filter_by(
            user_account_id=user.id
        ).order_by(
            TokenTransaction.created_at.desc()
        ).offset(offset).limit(limit).all()
        
        return jsonify({
            'user_id': user.id,
            'transactions': [t.to_dict() for t in transactions],
            'summary': {
                'total_tokens': user.total_tokens,
                'used_tokens': user.used_tokens,
                'remaining_tokens': user.remaining_tokens,
                'usage_percentage': user.usage_percentage
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter uso do usuário: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Erro ao obter estatísticas de uso'
        }), 500

@proxy_bp.route('/user/alerts', methods=['GET'])
@require_user
def get_user_alerts():
    """Obtém alertas do usuário"""
    try:
        user = request.current_user
        
        from src.models.token_control import UserAlert
        alerts = UserAlert.query.filter_by(
            user_account_id=user.id
        ).order_by(
            UserAlert.created_at.desc()
        ).limit(20).all()
        
        return jsonify({
            'alerts': [alert.to_dict() for alert in alerts]
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter alertas do usuário: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Erro ao obter alertas'
        }), 500

@proxy_bp.route('/models', methods=['GET'])
def get_available_models():
    """Obtém modelos disponíveis"""
    try:
        success, models = proxy_service.litellm_service.get_available_models()
        
        if success:
            return jsonify({
                'data': [{'id': model, 'object': 'model'} for model in models]
            })
        else:
            # Fallback com modelos padrão
            default_models = [
                'gpt-3.5-turbo',
                'gpt-4',
                'gpt-4-turbo',
                'gpt-4o'
            ]
            return jsonify({
                'data': [{'id': model, 'object': 'model'} for model in default_models]
            })
            
    except Exception as e:
        logger.error(f"Erro ao obter modelos: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Erro ao obter modelos disponíveis'
        }), 500

@proxy_bp.route('/admin/users', methods=['GET'])
def admin_list_users():
    """Lista todos os usuários (endpoint administrativo)"""
    try:
        # TODO: Adicionar autenticação de admin
        
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        users = UserAccount.query.paginate(
            page=page,
            per_page=per_page,
            error_out=False
        )
        
        return jsonify({
            'users': [user.to_dict() for user in users.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': users.total,
                'pages': users.pages
            }
        })
        
    except Exception as e:
        logger.error(f"Erro ao listar usuários: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Erro ao listar usuários'
        }), 500

@proxy_bp.route('/admin/users/<user_id>/add-tokens', methods=['POST'])
def admin_add_tokens(user_id):
    """Adiciona tokens a um usuário (endpoint administrativo)"""
    try:
        # TODO: Adicionar autenticação de admin
        
        data = request.get_json()
        tokens_to_add = data.get('tokens', 0)
        reason = data.get('reason', 'manual_addition')
        
        if tokens_to_add <= 0:
            return jsonify({
                'error': 'invalid_amount',
                'message': 'Quantidade de tokens deve ser positiva'
            }), 400
        
        # Busca usuário
        user = UserAccount.query.get(user_id)
        if not user:
            return jsonify({
                'error': 'user_not_found',
                'message': 'Usuário não encontrado'
            }), 404
        
        # Adiciona tokens
        transaction = user.add_tokens(tokens_to_add, reason)
        db.session.commit()
        
        # Envia email de confirmação
        proxy_service.email_service.send_credits_purchased_confirmation(
            user, tokens_to_add, transaction.id
        )
        
        logger.info(f"Admin adicionou {tokens_to_add} tokens ao usuário {user.email}")
        
        return jsonify({
            'success': True,
            'message': f'{tokens_to_add} tokens adicionados com sucesso',
            'user': user.to_dict(),
            'transaction_id': transaction.id
        })
        
    except Exception as e:
        logger.error(f"Erro ao adicionar tokens: {str(e)}")
        db.session.rollback()
        return jsonify({
            'error': 'internal_error',
            'message': 'Erro ao adicionar tokens'
        }), 500

@proxy_bp.route('/admin/stats', methods=['GET'])
def admin_get_stats():
    """Obtém estatísticas gerais do sistema"""
    try:
        # TODO: Adicionar autenticação de admin
        
        from sqlalchemy import func
        from src.models.token_control import TokenTransaction
        
        # Estatísticas básicas
        total_users = UserAccount.query.count()
        active_users = UserAccount.query.filter_by(is_active=True).count()
        blocked_users = UserAccount.query.filter_by(is_blocked=True).count()
        
        # Estatísticas de tokens
        total_tokens_distributed = db.session.query(
            func.sum(UserAccount.total_tokens)
        ).scalar() or 0
        
        total_tokens_used = db.session.query(
            func.sum(UserAccount.used_tokens)
        ).scalar() or 0
        
        # Transações hoje
        from datetime import date
        today = date.today()
        transactions_today = TokenTransaction.query.filter(
            func.date(TokenTransaction.created_at) == today
        ).count()
        
        return jsonify({
            'users': {
                'total': total_users,
                'active': active_users,
                'blocked': blocked_users
            },
            'tokens': {
                'total_distributed': total_tokens_distributed,
                'total_used': total_tokens_used,
                'total_remaining': total_tokens_distributed - total_tokens_used
            },
            'activity': {
                'transactions_today': transactions_today
            },
            'timestamp': datetime.utcnow().isoformat()
        })
        
    except Exception as e:
        logger.error(f"Erro ao obter estatísticas: {str(e)}")
        return jsonify({
            'error': 'internal_error',
            'message': 'Erro ao obter estatísticas'
        }), 500

# Middleware para CORS
@proxy_bp.after_request
def after_request(response):
    """Adiciona headers CORS"""
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID,X-User-Email,X-User-Name')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

@proxy_bp.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    """Handle preflight OPTIONS requests"""
    response = jsonify({'status': 'ok'})
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization,X-User-ID,X-User-Email,X-User-Name')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

