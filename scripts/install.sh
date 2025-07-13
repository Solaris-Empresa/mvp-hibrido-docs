#!/bin/bash

# ===================================
# IA SOLARIS - MVP Híbrido
# Script de Instalação Automática
# ===================================

set -e  # Parar em caso de erro

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Função para logging
log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
    exit 1
}

info() {
    echo -e "${BLUE}[$(date +'%Y-%m-%d %H:%M:%S')] INFO: $1${NC}"
}

# Banner
echo -e "${BLUE}"
cat << "EOF"
 _____ _____    _____  _____ _      _____ ____  _____ _____ 
|_   _|  _  |  |   __||     | |    |  _  |    \|     |   __|
  | | |     |  |__   ||  |  | |    |     |  |  |-   -|__   |
  |_| |__|__|  |_____||_____|_____|__|__|_|____/|_____|_____|
                                                            
           MVP Híbrido - Controle de Tokens
                 Instalação Automática
EOF
echo -e "${NC}"

# Verificar se está rodando como root
if [[ $EUID -eq 0 ]]; then
   error "Este script não deve ser executado como root. Use um usuário normal com sudo."
fi

# Verificar sistema operacional
if [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
else
    error "Sistema operacional não suportado: $OSTYPE"
fi

log "Sistema detectado: $OS"

# Função para verificar se comando existe
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Verificar dependências
check_dependencies() {
    log "Verificando dependências..."
    
    local missing_deps=()
    
    if ! command_exists docker; then
        missing_deps+=("docker")
    fi
    
    if ! command_exists docker-compose; then
        if ! docker compose version >/dev/null 2>&1; then
            missing_deps+=("docker-compose")
        fi
    fi
    
    if ! command_exists git; then
        missing_deps+=("git")
    fi
    
    if ! command_exists curl; then
        missing_deps+=("curl")
    fi
    
    if [ ${#missing_deps[@]} -ne 0 ]; then
        error "Dependências faltando: ${missing_deps[*]}. Por favor, instale-as primeiro."
    fi
    
    log "Todas as dependências estão instaladas ✓"
}

# Verificar se Docker está rodando
check_docker() {
    log "Verificando se Docker está rodando..."
    
    if ! docker info >/dev/null 2>&1; then
        error "Docker não está rodando. Por favor, inicie o Docker primeiro."
    fi
    
    log "Docker está rodando ✓"
}

# Verificar portas disponíveis
check_ports() {
    log "Verificando portas disponíveis..."
    
    local ports=(80 443 3000 4000 5000 5432 6379)
    local busy_ports=()
    
    for port in "${ports[@]}"; do
        if command_exists netstat; then
            if netstat -tuln | grep ":$port " >/dev/null 2>&1; then
                busy_ports+=($port)
            fi
        elif command_exists ss; then
            if ss -tuln | grep ":$port " >/dev/null 2>&1; then
                busy_ports+=($port)
            fi
        elif command_exists lsof; then
            if lsof -i :$port >/dev/null 2>&1; then
                busy_ports+=($port)
            fi
        fi
    done
    
    if [ ${#busy_ports[@]} -ne 0 ]; then
        warn "Portas ocupadas: ${busy_ports[*]}"
        warn "Isso pode causar conflitos. Continue? (y/N)"
        read -r response
        if [[ ! "$response" =~ ^[Yy]$ ]]; then
            error "Instalação cancelada pelo usuário."
        fi
    fi
    
    log "Verificação de portas concluída ✓"
}

# Configurar arquivo .env
setup_env() {
    log "Configurando arquivo de ambiente..."
    
    if [ ! -f .env ]; then
        if [ -f .env.example ]; then
            cp .env.example .env
            log "Arquivo .env criado a partir do .env.example"
        else
            error "Arquivo .env.example não encontrado!"
        fi
    else
        warn "Arquivo .env já existe. Sobrescrever? (y/N)"
        read -r response
        if [[ "$response" =~ ^[Yy]$ ]]; then
            cp .env.example .env
            log "Arquivo .env sobrescrito"
        fi
    fi
    
    # Verificar se OPENAI_API_KEY está configurada
    if ! grep -q "^OPENAI_API_KEY=sk-" .env; then
        warn "OPENAI_API_KEY não está configurada!"
        echo "Por favor, edite o arquivo .env e configure sua chave da OpenAI."
        echo "Pressione Enter para abrir o editor..."
        read -r
        
        if command_exists nano; then
            nano .env
        elif command_exists vim; then
            vim .env
        elif command_exists vi; then
            vi .env
        else
            error "Nenhum editor de texto encontrado. Configure manualmente o arquivo .env"
        fi
    fi
    
    log "Configuração de ambiente concluída ✓"
}

# Construir imagens Docker
build_images() {
    log "Construindo imagens Docker..."
    
    # Construir proxy inteligente
    info "Construindo proxy inteligente..."
    docker build -t ia-solaris-proxy:latest ./proxy-inteligente/proxy-ia-solaris/
    
    # Construir dashboard admin
    info "Construindo dashboard administrativo..."
    docker build -t ia-solaris-admin:latest ./admin-dashboard/admin-ia-solaris/
    
    log "Imagens Docker construídas ✓"
}

# Inicializar banco de dados
init_database() {
    log "Inicializando banco de dados..."
    
    # Iniciar apenas PostgreSQL primeiro
    docker-compose -f database/docker-compose.yml up -d postgres
    
    # Aguardar PostgreSQL ficar pronto
    info "Aguardando PostgreSQL ficar pronto..."
    local max_attempts=30
    local attempt=1
    
    while [ $attempt -le $max_attempts ]; do
        if docker-compose -f database/docker-compose.yml exec -T postgres pg_isready -U ia_solaris_user -d ia_solaris >/dev/null 2>&1; then
            break
        fi
        
        info "Tentativa $attempt/$max_attempts - Aguardando PostgreSQL..."
        sleep 2
        ((attempt++))
    done
    
    if [ $attempt -gt $max_attempts ]; then
        error "PostgreSQL não ficou pronto a tempo"
    fi
    
    log "Banco de dados inicializado ✓"
}

# Iniciar todos os serviços
start_services() {
    log "Iniciando todos os serviços..."
    
    cd database
    docker-compose up -d
    cd ..
    
    # Aguardar todos os serviços ficarem prontos
    info "Aguardando serviços ficarem prontos..."
    sleep 30
    
    # Verificar health checks
    local services=("ia_solaris_postgres" "ia_solaris_redis" "ia_solaris_litellm" "ia_solaris_proxy" "ia_solaris_admin")
    
    for service in "${services[@]}"; do
        info "Verificando $service..."
        local max_attempts=10
        local attempt=1
        
        while [ $attempt -le $max_attempts ]; do
            if docker inspect --format='{{.State.Health.Status}}' "$service" 2>/dev/null | grep -q "healthy"; then
                log "$service está saudável ✓"
                break
            fi
            
            if [ $attempt -eq $max_attempts ]; then
                warn "$service pode não estar funcionando corretamente"
            fi
            
            sleep 3
            ((attempt++))
        done
    done
    
    log "Serviços iniciados ✓"
}

# Verificar instalação
verify_installation() {
    log "Verificando instalação..."
    
    # Testar endpoints
    local endpoints=(
        "http://localhost:5000/v1/health|Proxy IA SOLARIS"
        "http://localhost:4000/health|LiteLLM"
        "http://localhost:3000/health|Dashboard Admin"
        "http://localhost/health|Nginx"
    )
    
    for endpoint_info in "${endpoints[@]}"; do
        IFS='|' read -r endpoint name <<< "$endpoint_info"
        
        info "Testando $name..."
        if curl -f -s "$endpoint" >/dev/null 2>&1; then
            log "$name está respondendo ✓"
        else
            warn "$name não está respondendo"
        fi
    done
    
    log "Verificação concluída ✓"
}

# Mostrar informações finais
show_final_info() {
    echo -e "${GREEN}"
    cat << "EOF"

🎉 INSTALAÇÃO CONCLUÍDA COM SUCESSO! 🎉

EOF
    echo -e "${NC}"
    
    echo "📋 INFORMAÇÕES DE ACESSO:"
    echo ""
    echo "🌐 Dashboard Administrativo:"
    echo "   URL: http://localhost/admin"
    echo "   Descrição: Interface para gerenciar usuários e tokens"
    echo ""
    echo "🔌 API do Proxy IA SOLARIS:"
    echo "   URL: http://localhost/v1"
    echo "   Descrição: Endpoint para integração com LibreChat"
    echo ""
    echo "⚡ LiteLLM (Debug):"
    echo "   URL: http://localhost/litellm"
    echo "   Descrição: Interface do LiteLLM para debug"
    echo ""
    echo "📊 Monitoramento:"
    echo "   Logs: docker-compose -f database/docker-compose.yml logs -f"
    echo "   Status: docker-compose -f database/docker-compose.yml ps"
    echo ""
    echo "🔧 PRÓXIMOS PASSOS:"
    echo ""
    echo "1. Configure o LibreChat para usar: http://localhost/v1"
    echo "2. Acesse o dashboard admin para gerenciar usuários"
    echo "3. Configure emails no arquivo .env se necessário"
    echo "4. Monitore os logs para verificar funcionamento"
    echo ""
    echo "📚 DOCUMENTAÇÃO:"
    echo "   Consulte o arquivo README.md para mais informações"
    echo ""
    echo "🆘 SUPORTE:"
    echo "   Em caso de problemas, execute: ./scripts/troubleshoot.sh"
    echo ""
}

# Função principal
main() {
    log "Iniciando instalação do IA SOLARIS MVP Híbrido..."
    
    # Verificações iniciais
    check_dependencies
    check_docker
    check_ports
    
    # Configuração
    setup_env
    
    # Build e deploy
    build_images
    init_database
    start_services
    
    # Verificação final
    verify_installation
    show_final_info
    
    log "Instalação concluída com sucesso! 🎉"
}

# Executar função principal
main "$@"

