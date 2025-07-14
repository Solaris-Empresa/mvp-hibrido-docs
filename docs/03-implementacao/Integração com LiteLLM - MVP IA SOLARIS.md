# Integração com LiteLLM - MVP IA SOLARIS

## Visão Geral

Este documento detalha a integração completa entre o Proxy Inteligente da IA SOLARIS e o LiteLLM, que atua como um proxy unificado para múltiplos provedores de IA. O LiteLLM permite que o sistema acesse diferentes modelos (OpenAI, Anthropic, Google, etc.) através de uma API padronizada, facilitando a implementação e manutenção.

## Arquitetura de Integração

### Fluxo de Dados

```
LibreChat → Proxy IA SOLARIS → LiteLLM → Provedores IA
     ↑           ↓                ↓           ↓
     └── Resposta ← Controle ← Normalização ← Resposta
                    Tokens
```

### Componentes da Integração

1. **Proxy IA SOLARIS:** Controle de tokens e auditoria
2. **LiteLLM:** Normalização e roteamento de APIs
3. **Provedores IA:** OpenAI, Anthropic, Google, etc.
4. **Banco de Dados:** Logs e métricas compartilhadas
5. **Redis:** Cache compartilhado

## Configuração do LiteLLM

### Arquivo de Configuração Principal

**Arquivo: database/litellm-config.yaml**

```yaml
# Configuração completa do LiteLLM para IA SOLARIS
model_list:
  # === OPENAI MODELS ===
  - model_name: gpt-4
    litellm_params:
      model: openai/gpt-4
      api_key: os.environ/OPENAI_API_KEY
      max_tokens: 4096
      temperature: 0.7
      timeout: 600
    model_info:
      mode: chat
      supports_function_calling: true
      supports_vision: false
      input_cost_per_token: 0.00003
      output_cost_per_token: 0.00006
      max_input_tokens: 8192
      max_output_tokens: 4096
      
  - model_name: gpt-4-turbo
    litellm_params:
      model: openai/gpt-4-turbo-preview
      api_key: os.environ/OPENAI_API_KEY
      max_tokens: 4096
      temperature: 0.7
      timeout: 600
    model_info:
      mode: chat
      supports_function_calling: true
      supports_vision: true
      input_cost_per_token: 0.00001
      output_cost_per_token: 0.00003
      max_input_tokens: 128000
      max_output_tokens: 4096
      
  - model_name: gpt-4o
    litellm_params:
      model: openai/gpt-4o
      api_key: os.environ/OPENAI_API_KEY
      max_tokens: 4096
      temperature: 0.7
      timeout: 600
    model_info:
      mode: chat
      supports_function_calling: true
      supports_vision: true
      input_cost_per_token: 0.000005
      output_cost_per_token: 0.000015
      max_input_tokens: 128000
      max_output_tokens: 4096
      
  - model_name: gpt-3.5-turbo
    litellm_params:
      model: openai/gpt-3.5-turbo
      api_key: os.environ/OPENAI_API_KEY
      max_tokens: 4096
      temperature: 0.7
      timeout: 300
    model_info:
      mode: chat
      supports_function_calling: true
      supports_vision: false
      input_cost_per_token: 0.0000005
      output_cost_per_token: 0.0000015
      max_input_tokens: 16385
      max_output_tokens: 4096

  # === ANTHROPIC MODELS ===
  - model_name: claude-3-opus
    litellm_params:
      model: anthropic/claude-3-opus-20240229
      api_key: os.environ/ANTHROPIC_API_KEY
      max_tokens: 4096
      temperature: 0.7
      timeout: 600
    model_info:
      mode: chat
      supports_function_calling: true
      supports_vision: true
      input_cost_per_token: 0.000015
      output_cost_per_token: 0.000075
      max_input_tokens: 200000
      max_output_tokens: 4096
      
  - model_name: claude-3-sonnet
    litellm_params:
      model: anthropic/claude-3-sonnet-20240229
      api_key: os.environ/ANTHROPIC_API_KEY
      max_tokens: 4096
      temperature: 0.7
      timeout: 600
    model_info:
      mode: chat
      supports_function_calling: true
      supports_vision: true
      input_cost_per_token: 0.000003
      output_cost_per_token: 0.000015
      max_input_tokens: 200000
      max_output_tokens: 4096
      
  - model_name: claude-3-haiku
    litellm_params:
      model: anthropic/claude-3-haiku-20240307
      api_key: os.environ/ANTHROPIC_API_KEY
      max_tokens: 4096
      temperature: 0.7
      timeout: 300
    model_info:
      mode: chat
      supports_function_calling: false
      supports_vision: true
      input_cost_per_token: 0.00000025
      output_cost_per_token: 0.00000125
      max_input_tokens: 200000
      max_output_tokens: 4096

  # === GOOGLE MODELS ===
  - model_name: gemini-pro
    litellm_params:
      model: gemini/gemini-pro
      api_key: os.environ/GOOGLE_API_KEY
      max_tokens: 2048
      temperature: 0.7
      timeout: 600
    model_info:
      mode: chat
      supports_function_calling: true
      supports_vision: false
      input_cost_per_token: 0.0000005
      output_cost_per_token: 0.0000015
      max_input_tokens: 30720
      max_output_tokens: 2048
      
  - model_name: gemini-pro-vision
    litellm_params:
      model: gemini/gemini-pro-vision
      api_key: os.environ/GOOGLE_API_KEY
      max_tokens: 2048
      temperature: 0.7
      timeout: 600
    model_info:
      mode: chat
      supports_function_calling: false
      supports_vision: true
      input_cost_per_token: 0.0000005
      output_cost_per_token: 0.0000015
      max_input_tokens: 12288
      max_output_tokens: 2048

# === ROUTER SETTINGS ===
router_settings:
  # Estratégia de roteamento
  routing_strategy: simple-shuffle  # simple-shuffle, least-busy, latency-based
  
  # Grupos de modelos para load balancing
  model_group_alias:
    gpt-4-group:
      - gpt-4
      - gpt-4-turbo
      - gpt-4o
    claude-group:
      - claude-3-opus
      - claude-3-sonnet
      - claude-3-haiku
    budget-group:
      - gpt-3.5-turbo
      - claude-3-haiku
      - gemini-pro
    vision-group:
      - gpt-4-turbo
      - gpt-4o
      - claude-3-opus
      - claude-3-sonnet
      - claude-3-haiku
      - gemini-pro-vision
  
  # Configuração de fallback
  fallbacks:
    - gpt-4: ["gpt-4-turbo", "gpt-4o", "claude-3-opus"]
    - gpt-4-turbo: ["gpt-4o", "gpt-4", "claude-3-sonnet"]
    - gpt-4o: ["gpt-4-turbo", "gpt-4", "claude-3-sonnet"]
    - claude-3-opus: ["claude-3-sonnet", "gpt-4", "gpt-4-turbo"]
    - claude-3-sonnet: ["claude-3-haiku", "gpt-3.5-turbo", "gemini-pro"]
    - claude-3-haiku: ["gpt-3.5-turbo", "gemini-pro"]
    - gemini-pro: ["gpt-3.5-turbo", "claude-3-haiku"]
    - gemini-pro-vision: ["gpt-4o", "claude-3-opus", "claude-3-sonnet"]
  
  # Rate limiting global
  rpm: 1000  # requests per minute
  tpm: 500000  # tokens per minute
  
  # Configuração de retry
  num_retries: 3
  request_timeout: 600
  retry_delay: 1
  exponential_backoff: true
  
  # Load balancing
  cooldown_time: 1  # seconds between requests to same model
  
  # Health checks
  health_check_interval: 60  # seconds
  unhealthy_threshold: 3  # consecutive failures

# === LITELLM SETTINGS ===
litellm_settings:
  # Logging
  set_verbose: true
  json_logs: true
  log_level: INFO
  
  # Database integration
  database_url: os.environ/DATABASE_URL
  database_type: postgresql
  store_model_in_db: true
  
  # Callbacks para integração com IA SOLARIS
  success_callback: ["langfuse", "prometheus", "ia_solaris_webhook"]
  failure_callback: ["langfuse", "prometheus", "ia_solaris_webhook"]
  
  # Cost tracking
  track_cost_per_model: true
  cost_per_token: true
  
  # Security
  master_key: os.environ/LITELLM_MASTER_KEY
  ui_access_mode: "admin_only"
  
  # Performance
  redis_host: redis
  redis_port: 6379
  redis_password: os.environ/REDIS_PASSWORD
  cache_responses: true
  cache_kwargs:
    ttl: 300  # 5 minutes
    
  # Custom headers
  headers:
    X-LiteLLM-Version: "1.0.0"
    X-Service-Name: "IA-SOLARIS"
    X-Environment: os.environ/ENVIRONMENT

# === GENERAL SETTINGS ===
general_settings:
  completion_model: gpt-3.5-turbo  # modelo padrão
  disable_spend_logs: false
  disable_master_key_return: true
  enforce_user_param: false
  
  # Alertas e limites
  alerting:
    - slack_webhook: os.environ/SLACK_WEBHOOK_URL
    - email: os.environ/ALERT_EMAIL
  
  budget_and_rate_limits:
    - model: "*"
      max_budget: 1000  # USD por mês
      budget_duration: "1mo"
    - model: "gpt-4"
      rpm: 100
      tpm: 50000
    - model: "claude-3-opus"
      rpm: 50
      tpm: 25000

# === WEBHOOKS PARA INTEGRAÇÃO ===
webhooks:
  ia_solaris_webhook:
    url: "http://proxy-inteligente:5000/api/webhooks/litellm"
    headers:
      Authorization: "Bearer ${WEBHOOK_SECRET}"
      Content-Type: "application/json"
    events:
      - "request_start"
      - "request_end"
      - "request_error"
      - "model_fallback"
      - "rate_limit_hit"

# === ENVIRONMENT VARIABLES ===
environment_variables:
  # API Keys
  OPENAI_API_KEY: os.environ/OPENAI_API_KEY
  ANTHROPIC_API_KEY: os.environ/ANTHROPIC_API_KEY
  GOOGLE_API_KEY: os.environ/GOOGLE_API_KEY
  
  # Database
  DATABASE_URL: os.environ/DATABASE_URL
  
  # Redis
  REDIS_HOST: redis
  REDIS_PORT: 6379
  REDIS_PASSWORD: os.environ/REDIS_PASSWORD
  
  # Security
  LITELLM_MASTER_KEY: os.environ/LITELLM_MASTER_KEY
  LITELLM_SALT_KEY: os.environ/LITELLM_SALT_KEY
  WEBHOOK_SECRET: os.environ/WEBHOOK_SECRET
  
  # Monitoring
  SLACK_WEBHOOK_URL: os.environ/SLACK_WEBHOOK_URL
  ALERT_EMAIL: os.environ/ALERT_EMAIL
  
  # Environment
  ENVIRONMENT: os.environ/ENVIRONMENT
```

## Serviço de Integração

### LiteLLM Service (services/litellm_service.py)

```python
import aiohttp
import asyncio
import json
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from enum import Enum

from ..config.settings import config
from ..utils.exceptions import LiteLLMError, ModelNotAvailableError
from ..utils.helpers import generate_request_id, calculate_cost

class ModelStatus(Enum):
    """Status dos modelos no LiteLLM"""
    HEALTHY = "healthy"
    UNHEALTHY = "unhealthy"
    RATE_LIMITED = "rate_limited"
    UNAVAILABLE = "unavailable"

@dataclass
class ModelInfo:
    """Informações de um modelo"""
    name: str
    provider: str
    status: ModelStatus
    last_check: datetime
    response_time_ms: Optional[int] = None
    error_rate: float = 0.0
    cost_per_input_token: float = 0.0
    cost_per_output_token: float = 0.0
    max_tokens: int = 4096
    supports_vision: bool = False
    supports_function_calling: bool = False

class LiteLLMService:
    """Serviço de integração com LiteLLM"""
    
    def __init__(self):
        self.base_url = config.litellm.base_url
        self.timeout = config.litellm.timeout
        self.max_retries = config.litellm.max_retries
        self.retry_delay = config.litellm.retry_delay
        
        # Cache de status dos modelos
        self.model_status_cache: Dict[str, ModelInfo] = {}
        self.last_health_check = None
        
        # Métricas
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'fallback_requests': 0,
            'total_cost': 0.0,
            'avg_response_time': 0.0
        }
    
    async def chat_completion(
        self, 
        model: str, 
        messages: List[Dict[str, Any]], 
        **kwargs
    ) -> Tuple[Dict[str, Any], int, Dict[str, Any]]:
        """
        Faz requisição de chat completion via LiteLLM
        
        Args:
            model: Nome do modelo
            messages: Lista de mensagens
            **kwargs: Parâmetros adicionais
            
        Returns:
            Tuple com (response_data, status_code, metadata)
        """
        start_time = time.time()
        request_id = generate_request_id()
        
        # Incrementar métricas
        self.metrics['total_requests'] += 1
        
        try:
            # Verificar se modelo está disponível
            if not await self._is_model_available(model):
                # Tentar fallback
                fallback_model = await self._get_fallback_model(model)
                if fallback_model:
                    model = fallback_model
                    self.metrics['fallback_requests'] += 1
                else:
                    raise ModelNotAvailableError(f"Modelo {model} indisponível e sem fallback")
            
            # Preparar payload
            payload = {
                'model': model,
                'messages': messages,
                'temperature': kwargs.get('temperature', 0.7),
                'max_tokens': kwargs.get('max_tokens'),
                'stream': kwargs.get('stream', False),
                'user': kwargs.get('user'),
                'tools': kwargs.get('tools'),
                'tool_choice': kwargs.get('tool_choice')
            }
            
            # Remover campos None
            payload = {k: v for k, v in payload.items() if v is not None}
            
            # Fazer requisição
            response_data, status_code = await self._make_request(
                endpoint='/v1/chat/completions',
                payload=payload,
                request_id=request_id
            )
            
            # Calcular métricas
            response_time = (time.time() - start_time) * 1000
            self._update_response_time_metric(response_time)
            
            # Calcular custo
            if status_code == 200 and 'usage' in response_data:
                cost = await self._calculate_request_cost(model, response_data['usage'])
                self.metrics['total_cost'] += cost
                response_data['cost'] = cost
            
            # Atualizar status do modelo
            await self._update_model_status(model, True, response_time)
            
            # Metadata da requisição
            metadata = {
                'request_id': request_id,
                'model_used': model,
                'response_time_ms': int(response_time),
                'litellm_status': status_code,
                'cost': response_data.get('cost', 0.0),
                'fallback_used': model != kwargs.get('original_model', model)
            }
            
            if status_code == 200:
                self.metrics['successful_requests'] += 1
            else:
                self.metrics['failed_requests'] += 1
                await self._update_model_status(model, False)
            
            return response_data, status_code, metadata
            
        except Exception as e:
            self.metrics['failed_requests'] += 1
            await self._update_model_status(model, False)
            
            error_response = {
                'error': str(e),
                'code': 'LITELLM_ERROR',
                'request_id': request_id
            }
            
            metadata = {
                'request_id': request_id,
                'model_used': model,
                'response_time_ms': int((time.time() - start_time) * 1000),
                'error': str(e)
            }
            
            return error_response, 500, metadata
    
    async def _make_request(
        self, 
        endpoint: str, 
        payload: Dict[str, Any], 
        request_id: str
    ) -> Tuple[Dict[str, Any], int]:
        """Faz requisição HTTP para LiteLLM com retry"""
        
        url = f"{self.base_url}{endpoint}"
        headers = {
            'Content-Type': 'application/json',
            'X-Request-ID': request_id,
            'User-Agent': 'IA-SOLARIS-Proxy/1.0'
        }
        
        last_exception = None
        
        for attempt in range(self.max_retries + 1):
            try:
                async with aiohttp.ClientSession(
                    timeout=aiohttp.ClientTimeout(total=self.timeout)
                ) as session:
                    async with session.post(url, json=payload, headers=headers) as response:
                        response_data = await response.json()
                        return response_data, response.status
                        
            except asyncio.TimeoutError as e:
                last_exception = e
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))  # Exponential backoff
                    continue
                    
            except aiohttp.ClientError as e:
                last_exception = e
                if attempt < self.max_retries:
                    await asyncio.sleep(self.retry_delay * (2 ** attempt))
                    continue
                    
            except Exception as e:
                last_exception = e
                break
        
        # Se chegou aqui, todas as tentativas falharam
        raise LiteLLMError(f"Falha após {self.max_retries + 1} tentativas: {last_exception}")
    
    async def _is_model_available(self, model: str) -> bool:
        """Verifica se modelo está disponível"""
        
        # Verificar cache de status
        if model in self.model_status_cache:
            model_info = self.model_status_cache[model]
            
            # Se verificação foi recente e modelo estava saudável
            if (
                datetime.utcnow() - model_info.last_check < timedelta(minutes=5) and
                model_info.status == ModelStatus.HEALTHY
            ):
                return True
        
        # Fazer health check do modelo
        return await self._health_check_model(model)
    
    async def _health_check_model(self, model: str) -> bool:
        """Faz health check de um modelo específico"""
        
        try:
            # Requisição simples para testar o modelo
            test_payload = {
                'model': model,
                'messages': [{'role': 'user', 'content': 'test'}],
                'max_tokens': 1,
                'temperature': 0
            }
            
            start_time = time.time()
            response_data, status_code = await self._make_request(
                endpoint='/v1/chat/completions',
                payload=test_payload,
                request_id=f"health_check_{model}_{int(time.time())}"
            )
            response_time = (time.time() - start_time) * 1000
            
            # Atualizar cache de status
            status = ModelStatus.HEALTHY if status_code == 200 else ModelStatus.UNHEALTHY
            
            self.model_status_cache[model] = ModelInfo(
                name=model,
                provider=self._get_model_provider(model),
                status=status,
                last_check=datetime.utcnow(),
                response_time_ms=int(response_time)
            )
            
            return status_code == 200
            
        except Exception:
            # Marcar modelo como indisponível
            self.model_status_cache[model] = ModelInfo(
                name=model,
                provider=self._get_model_provider(model),
                status=ModelStatus.UNAVAILABLE,
                last_check=datetime.utcnow()
            )
            return False
    
    async def _get_fallback_model(self, original_model: str) -> Optional[str]:
        """Obtém modelo de fallback para um modelo indisponível"""
        
        # Mapeamento de fallbacks
        fallback_map = {
            'gpt-4': ['gpt-4-turbo', 'gpt-4o', 'claude-3-opus'],
            'gpt-4-turbo': ['gpt-4o', 'gpt-4', 'claude-3-sonnet'],
            'gpt-4o': ['gpt-4-turbo', 'gpt-4', 'claude-3-sonnet'],
            'claude-3-opus': ['claude-3-sonnet', 'gpt-4', 'gpt-4-turbo'],
            'claude-3-sonnet': ['claude-3-haiku', 'gpt-3.5-turbo', 'gemini-pro'],
            'claude-3-haiku': ['gpt-3.5-turbo', 'gemini-pro'],
            'gemini-pro': ['gpt-3.5-turbo', 'claude-3-haiku'],
            'gemini-pro-vision': ['gpt-4o', 'claude-3-opus', 'claude-3-sonnet']
        }
        
        fallbacks = fallback_map.get(original_model, [])
        
        # Testar cada fallback
        for fallback in fallbacks:
            if await self._is_model_available(fallback):
                return fallback
        
        return None
    
    def _get_model_provider(self, model: str) -> str:
        """Identifica o provedor do modelo"""
        if model.startswith('gpt-'):
            return 'openai'
        elif model.startswith('claude-'):
            return 'anthropic'
        elif model.startswith('gemini-'):
            return 'google'
        else:
            return 'unknown'
    
    async def _calculate_request_cost(self, model: str, usage: Dict[str, Any]) -> float:
        """Calcula custo da requisição"""
        
        # Tabela de custos por modelo (por 1K tokens)
        cost_table = {
            'gpt-4': {'input': 0.03, 'output': 0.06},
            'gpt-4-turbo': {'input': 0.01, 'output': 0.03},
            'gpt-4o': {'input': 0.005, 'output': 0.015},
            'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
            'claude-3-opus': {'input': 0.015, 'output': 0.075},
            'claude-3-sonnet': {'input': 0.003, 'output': 0.015},
            'claude-3-haiku': {'input': 0.00025, 'output': 0.00125},
            'gemini-pro': {'input': 0.0005, 'output': 0.0015},
            'gemini-pro-vision': {'input': 0.0005, 'output': 0.0015}
        }
        
        costs = cost_table.get(model, {'input': 0.001, 'output': 0.002})  # Default
        
        prompt_tokens = usage.get('prompt_tokens', 0)
        completion_tokens = usage.get('completion_tokens', 0)
        
        input_cost = (prompt_tokens / 1000) * costs['input']
        output_cost = (completion_tokens / 1000) * costs['output']
        
        return input_cost + output_cost
    
    async def _update_model_status(
        self, 
        model: str, 
        success: bool, 
        response_time: Optional[float] = None
    ):
        """Atualiza status de um modelo"""
        
        if model not in self.model_status_cache:
            self.model_status_cache[model] = ModelInfo(
                name=model,
                provider=self._get_model_provider(model),
                status=ModelStatus.HEALTHY if success else ModelStatus.UNHEALTHY,
                last_check=datetime.utcnow()
            )
        else:
            model_info = self.model_status_cache[model]
            model_info.status = ModelStatus.HEALTHY if success else ModelStatus.UNHEALTHY
            model_info.last_check = datetime.utcnow()
            
            if response_time:
                model_info.response_time_ms = int(response_time)
    
    def _update_response_time_metric(self, response_time: float):
        """Atualiza métrica de tempo de resposta médio"""
        current_avg = self.metrics['avg_response_time']
        total_requests = self.metrics['total_requests']
        
        # Média móvel simples
        self.metrics['avg_response_time'] = (
            (current_avg * (total_requests - 1) + response_time) / total_requests
        )
    
    async def get_available_models(self) -> List[Dict[str, Any]]:
        """Retorna lista de modelos disponíveis"""
        
        try:
            response_data, status_code = await self._make_request(
                endpoint='/v1/models',
                payload={},
                request_id=f"list_models_{int(time.time())}"
            )
            
            if status_code == 200:
                models = response_data.get('data', [])
                
                # Enriquecer com informações de status
                for model in models:
                    model_id = model.get('id')
                    if model_id in self.model_status_cache:
                        model_info = self.model_status_cache[model_id]
                        model['status'] = model_info.status.value
                        model['last_check'] = model_info.last_check.isoformat()
                        model['response_time_ms'] = model_info.response_time_ms
                
                return models
            else:
                return []
                
        except Exception:
            return []
    
    async def get_model_info(self, model: str) -> Optional[Dict[str, Any]]:
        """Retorna informações detalhadas de um modelo"""
        
        if model not in self.model_status_cache:
            await self._health_check_model(model)
        
        if model in self.model_status_cache:
            model_info = self.model_status_cache[model]
            return {
                'name': model_info.name,
                'provider': model_info.provider,
                'status': model_info.status.value,
                'last_check': model_info.last_check.isoformat(),
                'response_time_ms': model_info.response_time_ms,
                'error_rate': model_info.error_rate,
                'cost_per_input_token': model_info.cost_per_input_token,
                'cost_per_output_token': model_info.cost_per_output_token,
                'max_tokens': model_info.max_tokens,
                'supports_vision': model_info.supports_vision,
                'supports_function_calling': model_info.supports_function_calling
            }
        
        return None
    
    async def health_check(self) -> Dict[str, Any]:
        """Verifica saúde do serviço LiteLLM"""
        
        try:
            # Health check geral do LiteLLM
            response_data, status_code = await self._make_request(
                endpoint='/health',
                payload={},
                request_id=f"health_check_{int(time.time())}"
            )
            
            litellm_healthy = status_code == 200
            
            # Health check dos modelos principais
            key_models = ['gpt-3.5-turbo', 'gpt-4', 'claude-3-sonnet']
            model_health = {}
            
            for model in key_models:
                model_health[model] = await self._health_check_model(model)
            
            # Status geral
            overall_healthy = litellm_healthy and any(model_health.values())
            
            return {
                'status': 'healthy' if overall_healthy else 'unhealthy',
                'litellm_service': 'healthy' if litellm_healthy else 'unhealthy',
                'models': model_health,
                'metrics': self.get_metrics(),
                'last_check': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            return {
                'status': 'unhealthy',
                'error': str(e),
                'last_check': datetime.utcnow().isoformat()
            }
    
    def get_metrics(self) -> Dict[str, Any]:
        """Retorna métricas do serviço"""
        
        success_rate = 0.0
        if self.metrics['total_requests'] > 0:
            success_rate = (
                self.metrics['successful_requests'] / self.metrics['total_requests']
            ) * 100
        
        fallback_rate = 0.0
        if self.metrics['total_requests'] > 0:
            fallback_rate = (
                self.metrics['fallback_requests'] / self.metrics['total_requests']
            ) * 100
        
        return {
            **self.metrics,
            'success_rate_percent': round(success_rate, 2),
            'fallback_rate_percent': round(fallback_rate, 2),
            'avg_response_time_ms': round(self.metrics['avg_response_time'], 2),
            'total_cost_usd': round(self.metrics['total_cost'], 4),
            'healthy_models': len([
                m for m in self.model_status_cache.values() 
                if m.status == ModelStatus.HEALTHY
            ]),
            'total_models': len(self.model_status_cache)
        }
    
    async def reset_metrics(self):
        """Reseta métricas do serviço"""
        self.metrics = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'fallback_requests': 0,
            'total_cost': 0.0,
            'avg_response_time': 0.0
        }
    
    async def force_model_refresh(self):
        """Força atualização do status de todos os modelos"""
        self.model_status_cache.clear()
        
        # Lista de modelos principais para verificar
        models_to_check = [
            'gpt-4', 'gpt-4-turbo', 'gpt-4o', 'gpt-3.5-turbo',
            'claude-3-opus', 'claude-3-sonnet', 'claude-3-haiku',
            'gemini-pro', 'gemini-pro-vision'
        ]
        
        # Verificar modelos em paralelo
        tasks = [self._health_check_model(model) for model in models_to_check]
        await asyncio.gather(*tasks, return_exceptions=True)
```

## Webhook de Integração

### Webhook Handler (routes/webhook_routes.py)

```python
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import json
import hmac
import hashlib

from ..services.audit_service import AuditService
from ..services.alert_service import AlertService
from ..config.settings import config

webhook_bp = Blueprint('webhooks', __name__, url_prefix='/api/webhooks')

audit_service = AuditService()
alert_service = AlertService()

def verify_webhook_signature(payload: bytes, signature: str) -> bool:
    """Verifica assinatura do webhook"""
    if not config.security.webhook_secret:
        return True  # Desenvolvimento sem verificação
    
    expected_signature = hmac.new(
        config.security.webhook_secret.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()
    
    return hmac.compare_digest(f"sha256={expected_signature}", signature)

@webhook_bp.route('/litellm', methods=['POST'])
async def litellm_webhook():
    """Recebe webhooks do LiteLLM"""
    
    try:
        # Verificar assinatura
        signature = request.headers.get('X-Signature-256', '')
        if not verify_webhook_signature(request.data, signature):
            current_app.logger.warning("Webhook signature verification failed")
            return jsonify({'error': 'Invalid signature'}), 401
        
        # Processar payload
        payload = request.get_json()
        event_type = payload.get('event_type')
        data = payload.get('data', {})
        
        current_app.logger.info(f"Received LiteLLM webhook: {event_type}")
        
        # Processar diferentes tipos de eventos
        if event_type == 'request_start':
            await _handle_request_start(data)
        elif event_type == 'request_end':
            await _handle_request_end(data)
        elif event_type == 'request_error':
            await _handle_request_error(data)
        elif event_type == 'model_fallback':
            await _handle_model_fallback(data)
        elif event_type == 'rate_limit_hit':
            await _handle_rate_limit(data)
        else:
            current_app.logger.warning(f"Unknown webhook event type: {event_type}")
        
        return jsonify({'status': 'processed'}), 200
        
    except Exception as e:
        current_app.logger.error(f"Error processing LiteLLM webhook: {e}")
        return jsonify({'error': 'Internal server error'}), 500

async def _handle_request_start(data: dict):
    """Processa início de requisição"""
    request_id = data.get('request_id')
    user_id = data.get('user_id')
    model = data.get('model')
    
    await audit_service.log_litellm_request_start(
        request_id=request_id,
        user_id=user_id,
        model=model,
        timestamp=datetime.utcnow()
    )

async def _handle_request_end(data: dict):
    """Processa fim de requisição"""
    request_id = data.get('request_id')
    user_id = data.get('user_id')
    model = data.get('model')
    usage = data.get('usage', {})
    cost = data.get('cost', 0.0)
    response_time = data.get('response_time_ms', 0)
    
    await audit_service.log_litellm_request_end(
        request_id=request_id,
        user_id=user_id,
        model=model,
        usage=usage,
        cost=cost,
        response_time_ms=response_time,
        timestamp=datetime.utcnow()
    )

async def _handle_request_error(data: dict):
    """Processa erro de requisição"""
    request_id = data.get('request_id')
    user_id = data.get('user_id')
    model = data.get('model')
    error = data.get('error')
    error_code = data.get('error_code')
    
    await audit_service.log_litellm_request_error(
        request_id=request_id,
        user_id=user_id,
        model=model,
        error=error,
        error_code=error_code,
        timestamp=datetime.utcnow()
    )
    
    # Alertar se muitos erros
    if await _should_alert_on_errors(model):
        await alert_service.send_model_error_alert(model, error)

async def _handle_model_fallback(data: dict):
    """Processa fallback de modelo"""
    request_id = data.get('request_id')
    original_model = data.get('original_model')
    fallback_model = data.get('fallback_model')
    reason = data.get('reason')
    
    await audit_service.log_model_fallback(
        request_id=request_id,
        original_model=original_model,
        fallback_model=fallback_model,
        reason=reason,
        timestamp=datetime.utcnow()
    )
    
    # Alertar administradores sobre fallbacks frequentes
    if await _should_alert_on_fallbacks(original_model):
        await alert_service.send_model_fallback_alert(original_model, reason)

async def _handle_rate_limit(data: dict):
    """Processa rate limit atingido"""
    model = data.get('model')
    limit_type = data.get('limit_type')  # rpm, tpm, budget
    current_usage = data.get('current_usage')
    limit = data.get('limit')
    
    await audit_service.log_rate_limit_hit(
        model=model,
        limit_type=limit_type,
        current_usage=current_usage,
        limit=limit,
        timestamp=datetime.utcnow()
    )
    
    # Alertar sobre rate limits
    await alert_service.send_rate_limit_alert(model, limit_type, current_usage, limit)

async def _should_alert_on_errors(model: str) -> bool:
    """Verifica se deve alertar sobre erros do modelo"""
    # Implementar lógica para detectar muitos erros
    # Por exemplo, mais de 10 erros nos últimos 5 minutos
    return False  # Placeholder

async def _should_alert_on_fallbacks(model: str) -> bool:
    """Verifica se deve alertar sobre fallbacks do modelo"""
    # Implementar lógica para detectar muitos fallbacks
    # Por exemplo, mais de 5 fallbacks nos últimos 10 minutos
    return False  # Placeholder
```

## Monitoramento e Métricas

### Dashboard de Modelos

```python
# routes/admin_routes.py - Adicionar endpoints para monitoramento

@admin_bp.route('/models/status', methods=['GET'])
async def get_models_status():
    """Retorna status de todos os modelos"""
    
    litellm_service = LiteLLMService()
    models = await litellm_service.get_available_models()
    
    return jsonify({
        'models': models,
        'metrics': litellm_service.get_metrics(),
        'last_update': datetime.utcnow().isoformat()
    })

@admin_bp.route('/models/<model_name>/info', methods=['GET'])
async def get_model_info(model_name: str):
    """Retorna informações detalhadas de um modelo"""
    
    litellm_service = LiteLLMService()
    model_info = await litellm_service.get_model_info(model_name)
    
    if not model_info:
        return jsonify({'error': 'Model not found'}), 404
    
    return jsonify(model_info)

@admin_bp.route('/models/refresh', methods=['POST'])
async def refresh_models():
    """Força atualização do status dos modelos"""
    
    litellm_service = LiteLLMService()
    await litellm_service.force_model_refresh()
    
    return jsonify({'status': 'Models refreshed successfully'})

@admin_bp.route('/litellm/health', methods=['GET'])
async def litellm_health():
    """Health check do LiteLLM"""
    
    litellm_service = LiteLLMService()
    health_status = await litellm_service.health_check()
    
    status_code = 200 if health_status['status'] == 'healthy' else 503
    return jsonify(health_status), status_code
```

## Troubleshooting e Debugging

### Logs Estruturados

```python
# utils/litellm_logger.py

import logging
import json
from datetime import datetime
from typing import Dict, Any

class LiteLLMLogger:
    """Logger especializado para integração LiteLLM"""
    
    def __init__(self):
        self.logger = logging.getLogger('litellm_integration')
    
    def log_request(
        self, 
        request_id: str, 
        model: str, 
        user_id: int, 
        payload: Dict[str, Any]
    ):
        """Log de requisição enviada"""
        self.logger.info("LiteLLM request sent", extra={
            'event_type': 'litellm_request',
            'request_id': request_id,
            'model': model,
            'user_id': user_id,
            'payload_size': len(json.dumps(payload)),
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def log_response(
        self, 
        request_id: str, 
        model: str, 
        status_code: int, 
        response_time_ms: int,
        usage: Dict[str, Any] = None
    ):
        """Log de resposta recebida"""
        self.logger.info("LiteLLM response received", extra={
            'event_type': 'litellm_response',
            'request_id': request_id,
            'model': model,
            'status_code': status_code,
            'response_time_ms': response_time_ms,
            'usage': usage,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def log_error(
        self, 
        request_id: str, 
        model: str, 
        error: str, 
        error_type: str = None
    ):
        """Log de erro"""
        self.logger.error("LiteLLM error", extra={
            'event_type': 'litellm_error',
            'request_id': request_id,
            'model': model,
            'error': error,
            'error_type': error_type,
            'timestamp': datetime.utcnow().isoformat()
        })
    
    def log_fallback(
        self, 
        request_id: str, 
        original_model: str, 
        fallback_model: str, 
        reason: str
    ):
        """Log de fallback de modelo"""
        self.logger.warning("Model fallback triggered", extra={
            'event_type': 'model_fallback',
            'request_id': request_id,
            'original_model': original_model,
            'fallback_model': fallback_model,
            'reason': reason,
            'timestamp': datetime.utcnow().isoformat()
        })
```

### Scripts de Diagnóstico

```bash
#!/bin/bash
# scripts/diagnose-litellm.sh

echo "🔍 Diagnóstico da Integração LiteLLM"

# Verificar se LiteLLM está rodando
echo "📡 Verificando LiteLLM..."
if curl -f http://localhost:4000/health >/dev/null 2>&1; then
    echo "✅ LiteLLM está respondendo"
else
    echo "❌ LiteLLM não está respondendo"
    echo "📋 Logs do LiteLLM:"
    docker-compose logs litellm | tail -20
fi

# Testar modelos principais
echo "🤖 Testando modelos principais..."
models=("gpt-3.5-turbo" "gpt-4" "claude-3-sonnet")

for model in "${models[@]}"; do
    echo "Testando $model..."
    response=$(curl -s -w "%{http_code}" -o /tmp/model-test.json \
        -H "Content-Type: application/json" \
        -d "{\"model\":\"$model\",\"messages\":[{\"role\":\"user\",\"content\":\"test\"}],\"max_tokens\":1}" \
        http://localhost:4000/v1/chat/completions)
    
    if [ "$response" = "200" ]; then
        echo "✅ $model: OK"
    else
        echo "❌ $model: FALHA (HTTP $response)"
        cat /tmp/model-test.json
    fi
done

# Verificar métricas
echo "📊 Métricas do Proxy..."
curl -s http://localhost:5000/api/admin/litellm/health | jq '.'

echo "🏁 Diagnóstico concluído"
```

---

**Autor:** Manus AI  
**Data:** Janeiro 2024  
**Versão:** 1.0

