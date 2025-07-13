#!/bin/bash

# ===================================
# IA SOLARIS - MVP Híbrido
# Script de Troubleshooting
# ===================================

set -e

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() {
    echo -e "${GREEN}[$(date +'%Y-%m-%d %H:%M:%S')] $1${NC}"
}

warn() {
    echo -e "${YELLOW}[$(date +'%Y-%m-%d %H:%M:%S')] WARNING: $1${NC}"
}

error() {
    echo -e "${RED}[$(date +'%Y-%m-%d %H:%M:%S')] ERROR: $1${NC}"
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
                                                            
           MVP Híbrido - Troubleshooting
EOF
echo -e "${NC}"

# Verificar status dos containers
check_containers() {
    log "Verificando status dos containers..."
    
    echo "📊 STATUS DOS CONTAINERS:"
    docker-compose -f database/docker-compose.yml ps
    echo ""
    
    # Verificar containers com problemas
    local problematic_containers=$(docker-compose -f database/docker-compose.yml ps --filter "status=exited" --format "table {{.Service}}")
    
    if [ -n "$problematic_containers" ] && [ "$problematic_containers" != "SERVICE" ]; then
        warn "Containers com problemas detectados!"
        echo "$problematic_containers"
    else
        log "Todos os containers estão rodando ✓"
    fi
}

# Verificar logs dos serviços
check_logs() {
    log "Verificando logs dos serviços..."
    
    local services=("postgres" "redis" "litellm" "proxy-ia-solaris" "admin-dashboard" "nginx")
    
    for service in "${services[@]}"; do
        echo ""
        echo "📋 LOGS DO $service (últimas 10 linhas):"
        echo "----------------------------------------"
        docker-compose -f database/docker-compose.yml logs --tail=10 "$service" 2>/dev/null || warn "Serviço $service não encontrado"
    done
}

# Verificar conectividade de rede
check_network() {
    log "Verificando conectividade de rede..."
    
    local endpoints=(
        "http://localhost:5432|PostgreSQL"
        "http://localhost:6379|Redis"
        "http://localhost:4000/health|LiteLLM"
        "http://localhost:5000/v1/health|Proxy IA SOLARIS"
        "http://localhost:3000/health|Dashboard Admin"
        "http://localhost/health|Nginx"
    )
    
    echo "🌐 TESTE DE CONECTIVIDADE:"
    for endpoint_info in "${endpoints[@]}"; do
        IFS='|' read -r endpoint name <<< "$endpoint_info"
        
        printf "%-20s: " "$name"
        if curl -f -s --max-time 5 "$endpoint" >/dev/null 2>&1; then
            echo -e "${GREEN}✓ OK${NC}"
        else
            echo -e "${RED}✗ FALHA${NC}"
        fi
    done
}

# Verificar uso de recursos
check_resources() {
    log "Verificando uso de recursos..."
    
    echo "💾 USO DE RECURSOS:"
    echo "CPU e Memória dos containers:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.MemPerc}}" 2>/dev/null || warn "Não foi possível obter estatísticas"
    
    echo ""
    echo "💿 ESPAÇO EM DISCO:"
    df -h | grep -E "(Filesystem|/dev/)" || warn "Não foi possível verificar espaço em disco"
    
    echo ""
    echo "🐳 IMAGENS DOCKER:"
    docker images --format "table {{.Repository}}\t{{.Tag}}\t{{.Size}}" | grep -E "(REPOSITORY|ia-solaris|postgres|redis|nginx|litellm)"
}

# Verificar configurações
check_config() {
    log "Verificando configurações..."
    
    echo "⚙️ CONFIGURAÇÕES:"
    
    # Verificar arquivo .env
    if [ -f .env ]; then
        echo "✓ Arquivo .env encontrado"
        
        # Verificar variáveis críticas
        local critical_vars=("OPENAI_API_KEY" "DATABASE_URL" "REDIS_URL")
        for var in "${critical_vars[@]}"; do
            if grep -q "^$var=" .env && ! grep -q "^$var=$" .env && ! grep -q "^$var=your-" .env; then
                echo "✓ $var configurada"
            else
                warn "$var não configurada ou com valor padrão"
            fi
        done
    else
        error "Arquivo .env não encontrado!"
    fi
    
    echo ""
    echo "📁 ESTRUTURA DE ARQUIVOS:"
    local required_files=(
        "database/docker-compose.yml"
        "database/litellm-config.yaml"
        "database/nginx.conf"
        "proxy-inteligente/proxy-ia-solaris/Dockerfile"
        "admin-dashboard/admin-ia-solaris/Dockerfile"
    )
    
    for file in "${required_files[@]}"; do
        if [ -f "$file" ]; then
            echo "✓ $file"
        else
            warn "✗ $file não encontrado"
        fi
    done
}

# Verificar portas
check_ports() {
    log "Verificando portas..."
    
    echo "🔌 PORTAS EM USO:"
    local ports=(80 443 3000 4000 5000 5432 6379)
    
    for port in "${ports[@]}"; do
        printf "Porta %-5s: " "$port"
        if command -v netstat >/dev/null 2>&1; then
            if netstat -tuln | grep ":$port " >/dev/null 2>&1; then
                echo -e "${GREEN}EM USO${NC}"
            else
                echo -e "${YELLOW}LIVRE${NC}"
            fi
        elif command -v ss >/dev/null 2>&1; then
            if ss -tuln | grep ":$port " >/dev/null 2>&1; then
                echo -e "${GREEN}EM USO${NC}"
            else
                echo -e "${YELLOW}LIVRE${NC}"
            fi
        else
            echo -e "${BLUE}N/A${NC}"
        fi
    done
}

# Executar testes de API
test_api() {
    log "Executando testes de API..."
    
    echo "🧪 TESTES DE API:"
    
    # Teste 1: Health check do proxy
    printf "Health check proxy: "
    if response=$(curl -s -w "%{http_code}" http://localhost:5000/v1/health 2>/dev/null); then
        http_code="${response: -3}"
        if [ "$http_code" = "200" ]; then
            echo -e "${GREEN}✓ OK${NC}"
        else
            echo -e "${RED}✗ HTTP $http_code${NC}"
        fi
    else
        echo -e "${RED}✗ FALHA${NC}"
    fi
    
    # Teste 2: LiteLLM models
    printf "LiteLLM models: "
    if response=$(curl -s -w "%{http_code}" http://localhost:4000/v1/models 2>/dev/null); then
        http_code="${response: -3}"
        if [ "$http_code" = "200" ]; then
            echo -e "${GREEN}✓ OK${NC}"
        else
            echo -e "${RED}✗ HTTP $http_code${NC}"
        fi
    else
        echo -e "${RED}✗ FALHA${NC}"
    fi
    
    # Teste 3: Dashboard admin
    printf "Dashboard admin: "
    if response=$(curl -s -w "%{http_code}" http://localhost:3000/ 2>/dev/null); then
        http_code="${response: -3}"
        if [ "$http_code" = "200" ]; then
            echo -e "${GREEN}✓ OK${NC}"
        else
            echo -e "${RED}✗ HTTP $http_code${NC}"
        fi
    else
        echo -e "${RED}✗ FALHA${NC}"
    fi
}

# Soluções comuns
show_solutions() {
    echo ""
    echo -e "${BLUE}🔧 SOLUÇÕES PARA PROBLEMAS COMUNS:${NC}"
    echo ""
    
    echo "❌ PROBLEMA: Containers não iniciam"
    echo "💡 SOLUÇÃO:"
    echo "   1. Verificar se Docker está rodando: docker info"
    echo "   2. Verificar portas ocupadas: netstat -tuln | grep -E ':(80|443|3000|4000|5000|5432|6379)'"
    echo "   3. Reiniciar containers: docker-compose -f database/docker-compose.yml restart"
    echo ""
    
    echo "❌ PROBLEMA: Erro de conexão com banco"
    echo "💡 SOLUÇÃO:"
    echo "   1. Verificar logs do PostgreSQL: docker-compose -f database/docker-compose.yml logs postgres"
    echo "   2. Verificar variáveis de ambiente no .env"
    echo "   3. Reiniciar apenas o banco: docker-compose -f database/docker-compose.yml restart postgres"
    echo ""
    
    echo "❌ PROBLEMA: API não responde"
    echo "💡 SOLUÇÃO:"
    echo "   1. Verificar logs do proxy: docker-compose -f database/docker-compose.yml logs proxy-ia-solaris"
    echo "   2. Verificar se OPENAI_API_KEY está configurada"
    echo "   3. Testar LiteLLM diretamente: curl http://localhost:4000/health"
    echo ""
    
    echo "❌ PROBLEMA: Dashboard não carrega"
    echo "💡 SOLUÇÃO:"
    echo "   1. Verificar logs do nginx: docker-compose -f database/docker-compose.yml logs nginx"
    echo "   2. Verificar se admin-dashboard está rodando"
    echo "   3. Limpar cache do navegador"
    echo ""
    
    echo "❌ PROBLEMA: Emails não são enviados"
    echo "💡 SOLUÇÃO:"
    echo "   1. Verificar configurações SMTP no .env"
    echo "   2. Testar credenciais de email"
    echo "   3. Verificar logs do proxy para erros de email"
    echo ""
}

# Comandos úteis
show_useful_commands() {
    echo ""
    echo -e "${BLUE}📋 COMANDOS ÚTEIS:${NC}"
    echo ""
    
    echo "🔄 REINICIAR SERVIÇOS:"
    echo "   Todos: docker-compose -f database/docker-compose.yml restart"
    echo "   Proxy: docker-compose -f database/docker-compose.yml restart proxy-ia-solaris"
    echo "   Admin: docker-compose -f database/docker-compose.yml restart admin-dashboard"
    echo ""
    
    echo "📊 MONITORAMENTO:"
    echo "   Status: docker-compose -f database/docker-compose.yml ps"
    echo "   Logs: docker-compose -f database/docker-compose.yml logs -f [serviço]"
    echo "   Recursos: docker stats"
    echo ""
    
    echo "🗄️ BANCO DE DADOS:"
    echo "   Conectar: docker-compose -f database/docker-compose.yml exec postgres psql -U ia_solaris_user -d ia_solaris"
    echo "   Backup: docker-compose -f database/docker-compose.yml exec postgres pg_dump -U ia_solaris_user ia_solaris > backup.sql"
    echo ""
    
    echo "🧹 LIMPEZA:"
    echo "   Parar tudo: docker-compose -f database/docker-compose.yml down"
    echo "   Remover volumes: docker-compose -f database/docker-compose.yml down -v"
    echo "   Limpar imagens: docker system prune -a"
    echo ""
}

# Menu interativo
show_menu() {
    echo ""
    echo -e "${BLUE}🔍 DIAGNÓSTICO IA SOLARIS${NC}"
    echo ""
    echo "Escolha uma opção:"
    echo "1) Verificação completa"
    echo "2) Status dos containers"
    echo "3) Logs dos serviços"
    echo "4) Teste de conectividade"
    echo "5) Uso de recursos"
    echo "6) Verificar configurações"
    echo "7) Verificar portas"
    echo "8) Testes de API"
    echo "9) Soluções comuns"
    echo "10) Comandos úteis"
    echo "0) Sair"
    echo ""
    read -p "Digite sua escolha [0-10]: " choice
    
    case $choice in
        1)
            check_containers
            check_network
            check_config
            check_ports
            test_api
            ;;
        2) check_containers ;;
        3) check_logs ;;
        4) check_network ;;
        5) check_resources ;;
        6) check_config ;;
        7) check_ports ;;
        8) test_api ;;
        9) show_solutions ;;
        10) show_useful_commands ;;
        0) 
            log "Saindo..."
            exit 0
            ;;
        *)
            warn "Opção inválida!"
            show_menu
            ;;
    esac
}

# Função principal
main() {
    if [ $# -eq 0 ]; then
        # Modo interativo
        while true; do
            show_menu
            echo ""
            read -p "Pressione Enter para continuar ou Ctrl+C para sair..."
        done
    else
        # Modo comando
        case $1 in
            "check") check_containers && check_network && check_config ;;
            "logs") check_logs ;;
            "test") test_api ;;
            "help") show_solutions && show_useful_commands ;;
            *) 
                echo "Uso: $0 [check|logs|test|help]"
                echo "Ou execute sem parâmetros para modo interativo"
                ;;
        esac
    fi
}

# Executar
main "$@"

