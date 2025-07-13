import os
import requests
import json
import logging
from typing import Dict, Any, Tuple, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

class LiteLLMService:
    """Serviço para integração com LiteLLM"""
    
    def __init__(self):
        # Configurações do LiteLLM
        self.litellm_base_url = os.getenv('LITELLM_BASE_URL', 'http://localhost:4000')
        self.litellm_api_key = os.getenv('LITELLM_API_KEY', 'sk-1234')
        
        # Configurações OpenAI (fallback direto)
        self.openai_api_key = os.getenv('OPENAI_API_KEY')
        self.openai_base_url = 'https://api.openai.com/v1'
        
        # Headers padrão
        self.headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.litellm_api_key}'
        }
        
        # Timeout padrão
        self.timeout = 120  # 2 minutos
    
    def make_request(self, request_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Faz requisição via LiteLLM ou OpenAI direto"""
        try:
            # Tenta primeiro via LiteLLM
            success, response = self._make_litellm_request(request_data)
            
            if success:
                return True, response
            
            # Se LiteLLM falhar, tenta OpenAI direto
            logger.warning("LiteLLM falhou, tentando OpenAI direto")
            return self._make_openai_direct_request(request_data)
            
        except Exception as e:
            logger.error(f"Erro geral na requisição: {str(e)}")
            return False, {
                'error': 'request_failed',
                'message': 'Falha na comunicação com serviços de IA'
            }
    
    def _make_litellm_request(self, request_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Faz requisição via LiteLLM"""
        try:
            url = f"{self.litellm_base_url}/chat/completions"
            
            # Prepara dados da requisição
            payload = self._prepare_request_payload(request_data)
            
            logger.info(f"Fazendo requisição LiteLLM para modelo: {payload.get('model')}")
            
            # Faz requisição
            response = requests.post(
                url,
                headers=self.headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"Requisição LiteLLM bem-sucedida. Tokens: {response_data.get('usage', {}).get('total_tokens', 'N/A')}")
                return True, response_data
            else:
                logger.error(f"Erro LiteLLM: {response.status_code} - {response.text}")
                return False, {
                    'error': 'litellm_error',
                    'status_code': response.status_code,
                    'message': response.text
                }
                
        except requests.exceptions.Timeout:
            logger.error("Timeout na requisição LiteLLM")
            return False, {'error': 'timeout', 'message': 'Timeout na requisição'}
        except requests.exceptions.ConnectionError:
            logger.error("Erro de conexão com LiteLLM")
            return False, {'error': 'connection_error', 'message': 'Erro de conexão com LiteLLM'}
        except Exception as e:
            logger.error(f"Erro inesperado LiteLLM: {str(e)}")
            return False, {'error': 'unexpected_error', 'message': str(e)}
    
    def _make_openai_direct_request(self, request_data: Dict[str, Any]) -> Tuple[bool, Dict[str, Any]]:
        """Faz requisição direta para OpenAI (fallback)"""
        try:
            if not self.openai_api_key:
                return False, {
                    'error': 'no_api_key',
                    'message': 'Chave da OpenAI não configurada'
                }
            
            url = f"{self.openai_base_url}/chat/completions"
            
            headers = {
                'Content-Type': 'application/json',
                'Authorization': f'Bearer {self.openai_api_key}'
            }
            
            # Prepara dados da requisição
            payload = self._prepare_request_payload(request_data)
            
            logger.info(f"Fazendo requisição OpenAI direta para modelo: {payload.get('model')}")
            
            # Faz requisição
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                response_data = response.json()
                logger.info(f"Requisição OpenAI direta bem-sucedida. Tokens: {response_data.get('usage', {}).get('total_tokens', 'N/A')}")
                return True, response_data
            else:
                logger.error(f"Erro OpenAI: {response.status_code} - {response.text}")
                return False, {
                    'error': 'openai_error',
                    'status_code': response.status_code,
                    'message': response.text
                }
                
        except Exception as e:
            logger.error(f"Erro inesperado OpenAI: {str(e)}")
            return False, {'error': 'unexpected_error', 'message': str(e)}
    
    def _prepare_request_payload(self, request_data: Dict[str, Any]) -> Dict[str, Any]:
        """Prepara payload da requisição"""
        # Copia dados básicos
        payload = {
            'model': request_data.get('model', 'gpt-3.5-turbo'),
            'messages': request_data.get('messages', []),
            'temperature': request_data.get('temperature', 0.7),
            'max_tokens': request_data.get('max_tokens'),
            'top_p': request_data.get('top_p'),
            'frequency_penalty': request_data.get('frequency_penalty'),
            'presence_penalty': request_data.get('presence_penalty'),
            'stream': request_data.get('stream', False)
        }
        
        # Remove valores None
        payload = {k: v for k, v in payload.items() if v is not None}
        
        return payload
    
    def test_connection(self) -> Tuple[bool, str]:
        """Testa conexão com LiteLLM"""
        try:
            url = f"{self.litellm_base_url}/health"
            
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                return True, "LiteLLM conectado com sucesso"
            else:
                return False, f"LiteLLM retornou status {response.status_code}"
                
        except requests.exceptions.ConnectionError:
            return False, "Não foi possível conectar ao LiteLLM"
        except Exception as e:
            return False, f"Erro ao testar LiteLLM: {str(e)}"
    
    def get_available_models(self) -> Tuple[bool, list]:
        """Obtém lista de modelos disponíveis"""
        try:
            url = f"{self.litellm_base_url}/models"
            
            response = requests.get(
                url,
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                models = data.get('data', [])
                return True, [model.get('id') for model in models]
            else:
                return False, []
                
        except Exception as e:
            logger.error(f"Erro ao obter modelos: {str(e)}")
            return False, []
    
    def estimate_cost(self, tokens: int, model: str) -> float:
        """Estima custo baseado no modelo e tokens"""
        # Preços por 1K tokens (valores aproximados em USD)
        pricing = {
            'gpt-3.5-turbo': 0.002,
            'gpt-3.5-turbo-16k': 0.004,
            'gpt-4': 0.03,
            'gpt-4-32k': 0.06,
            'gpt-4-turbo': 0.01,
            'gpt-4o': 0.005,
            'gpt-4o-mini': 0.0015,
            'claude-3-sonnet': 0.003,
            'claude-3-opus': 0.015,
            'claude-3-haiku': 0.00025
        }
        
        # Busca preço do modelo
        price_per_1k = pricing.get(model, 0.002)  # Default para gpt-3.5-turbo
        
        return (tokens / 1000) * price_per_1k
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Obtém informações sobre um modelo específico"""
        model_info = {
            'gpt-3.5-turbo': {
                'provider': 'openai',
                'max_tokens': 4096,
                'context_window': 16385,
                'cost_per_1k_tokens': 0.002
            },
            'gpt-4': {
                'provider': 'openai',
                'max_tokens': 8192,
                'context_window': 8192,
                'cost_per_1k_tokens': 0.03
            },
            'gpt-4-turbo': {
                'provider': 'openai',
                'max_tokens': 4096,
                'context_window': 128000,
                'cost_per_1k_tokens': 0.01
            },
            'gpt-4o': {
                'provider': 'openai',
                'max_tokens': 4096,
                'context_window': 128000,
                'cost_per_1k_tokens': 0.005
            }
        }
        
        return model_info.get(model, {
            'provider': 'unknown',
            'max_tokens': 4096,
            'context_window': 4096,
            'cost_per_1k_tokens': 0.002
        })
    
    def validate_request(self, request_data: Dict[str, Any]) -> Tuple[bool, str]:
        """Valida dados da requisição"""
        try:
            # Verifica campos obrigatórios
            if 'messages' not in request_data:
                return False, "Campo 'messages' é obrigatório"
            
            messages = request_data['messages']
            if not isinstance(messages, list) or len(messages) == 0:
                return False, "Campo 'messages' deve ser uma lista não vazia"
            
            # Verifica estrutura das mensagens
            for i, message in enumerate(messages):
                if not isinstance(message, dict):
                    return False, f"Mensagem {i} deve ser um objeto"
                
                if 'role' not in message:
                    return False, f"Mensagem {i} deve ter campo 'role'"
                
                if 'content' not in message:
                    return False, f"Mensagem {i} deve ter campo 'content'"
                
                if message['role'] not in ['system', 'user', 'assistant']:
                    return False, f"Mensagem {i} tem role inválido: {message['role']}"
            
            # Verifica modelo
            model = request_data.get('model', 'gpt-3.5-turbo')
            if not isinstance(model, str):
                return False, "Campo 'model' deve ser uma string"
            
            return True, "Requisição válida"
            
        except Exception as e:
            return False, f"Erro na validação: {str(e)}"

