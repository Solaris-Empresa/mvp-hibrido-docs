import os
import sys
# DON'T CHANGE THIS !!!
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from flask import Flask, send_from_directory, jsonify
from flask_cors import CORS
from src.models.token_control import db
from src.routes.user import user_bp
from src.routes.proxy_routes import proxy_bp
import logging

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

app = Flask(__name__, static_folder=os.path.join(os.path.dirname(__file__), 'static'))

# Configurações
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'ia-solaris-mvp-secret-key-2025')

# Configuração do banco de dados
database_url = os.getenv('DATABASE_URL')
if database_url:
    app.config['SQLALCHEMY_DATABASE_URI'] = database_url
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(os.path.dirname(__file__), 'database', 'app.db')}"

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configurar CORS
CORS(app, origins="*")

# Registrar blueprints
app.register_blueprint(user_bp, url_prefix='/api')
app.register_blueprint(proxy_bp, url_prefix='/v1')  # Compatível com OpenAI API

# Inicializar banco de dados
db.init_app(app)

with app.app_context():
    db.create_all()
    
    # Criar configurações padrão
    from src.models.token_control import SystemConfig
    
    # Configurações padrão do sistema
    default_configs = [
        ('default_tokens_per_user', '1000', 'Tokens padrão para novos usuários'),
        ('conversion_factor', '0.376', 'Fator de conversão de tokens'),
        ('alert_threshold_80', '0.8', 'Limite para alerta de 80%'),
        ('alert_threshold_95', '0.95', 'Limite para alerta de 95%'),
        ('credits_email', 'creditos@iasolaris.com.br', 'Email para compra de créditos'),
        ('system_name', 'IA SOLARIS', 'Nome do sistema'),
    ]
    
    for key, value, description in default_configs:
        existing = SystemConfig.query.filter_by(key=key).first()
        if not existing:
            config = SystemConfig(key=key, value=value, description=description)
            db.session.add(config)
    
    try:
        db.session.commit()
    except:
        db.session.rollback()

@app.route('/', defaults={'path': ''})
@app.route('/<path:path>')
def serve(path):
    static_folder_path = app.static_folder
    if static_folder_path is None:
        return "Static folder not configured", 404

    if path != "" and os.path.exists(os.path.join(static_folder_path, path)):
        return send_from_directory(static_folder_path, path)
    else:
        index_path = os.path.join(static_folder_path, 'index.html')
        if os.path.exists(index_path):
            return send_from_directory(static_folder_path, 'index.html')
        else:
            # Retorna informações da API se não houver frontend
            return jsonify({
                'name': 'IA SOLARIS - Proxy Inteligente',
                'version': '1.0.0',
                'description': 'MVP Híbrido para Controle de Tokens por Usuário',
                'endpoints': {
                    'health': '/v1/health',
                    'chat': '/v1/chat/completions',
                    'models': '/v1/models',
                    'user_info': '/v1/user/info',
                    'admin': '/v1/admin/*'
                },
                'documentation': 'https://github.com/Solaris-Empresa/mvp-hibrido-docs'
            })

@app.errorhandler(404)
def not_found(error):
    return jsonify({
        'error': 'not_found',
        'message': 'Endpoint não encontrado'
    }), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({
        'error': 'internal_error',
        'message': 'Erro interno do servidor'
    }), 500

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    debug = os.getenv('DEBUG', 'false').lower() == 'true'
    
    print(f"🚀 Iniciando IA SOLARIS Proxy Inteligente na porta {port}")
    print(f"📊 Debug mode: {debug}")
    print(f"🔗 Health check: http://localhost:{port}/v1/health")
    print(f"💬 Chat endpoint: http://localhost:{port}/v1/chat/completions")
    
    app.run(host='0.0.0.0', port=port, debug=debug)
