-- Script de inicialização do banco de dados IA SOLARIS
-- Este script é executado automaticamente quando o container PostgreSQL é criado

-- Criar extensões necessárias
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";
CREATE EXTENSION IF NOT EXISTS "btree_gin";

-- Configurar timezone
SET timezone = 'America/Sao_Paulo';

-- Criar schema para o sistema
CREATE SCHEMA IF NOT EXISTS ia_solaris;

-- Comentários do banco
COMMENT ON DATABASE ia_solaris IS 'Banco de dados do sistema IA SOLARIS - MVP Híbrido de Controle de Tokens';
COMMENT ON SCHEMA ia_solaris IS 'Schema principal do sistema IA SOLARIS';

-- Criar função para atualizar timestamp automaticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Criar função para gerar IDs únicos
CREATE OR REPLACE FUNCTION generate_unique_id()
RETURNS TEXT AS $$
BEGIN
    RETURN 'ia_' || replace(uuid_generate_v4()::text, '-', '');
END;
$$ language 'plpgsql';

-- Criar tabela de configurações do sistema
CREATE TABLE IF NOT EXISTS system_config (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    key VARCHAR(100) UNIQUE NOT NULL,
    value TEXT,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Trigger para atualizar updated_at
CREATE TRIGGER update_system_config_updated_at 
    BEFORE UPDATE ON system_config 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Inserir configurações padrão
INSERT INTO system_config (key, value, description) VALUES
    ('system_name', 'IA SOLARIS', 'Nome do sistema'),
    ('version', '1.0.0', 'Versão atual do sistema'),
    ('default_tokens_per_user', '1000', 'Tokens padrão para novos usuários'),
    ('conversion_factor', '0.376', 'Fator de conversão de tokens'),
    ('alert_threshold_80', '0.8', 'Limite para alerta de 80%'),
    ('alert_threshold_95', '0.95', 'Limite para alerta de 95%'),
    ('credits_email', 'creditos@iasolaris.com.br', 'Email para compra de créditos'),
    ('max_requests_per_minute', '60', 'Máximo de requisições por minuto por usuário'),
    ('session_timeout', '3600', 'Timeout de sessão em segundos'),
    ('enable_email_notifications', 'true', 'Habilitar notificações por email'),
    ('enable_auto_blocking', 'true', 'Habilitar bloqueio automático'),
    ('smtp_server', 'smtp.gmail.com', 'Servidor SMTP padrão'),
    ('smtp_port', '587', 'Porta SMTP padrão'),
    ('from_email', 'noreply@iasolaris.com.br', 'Email remetente padrão'),
    ('from_name', 'IA SOLARIS', 'Nome remetente padrão')
ON CONFLICT (key) DO NOTHING;

-- Criar índices para performance
CREATE INDEX IF NOT EXISTS idx_system_config_key ON system_config(key);
CREATE INDEX IF NOT EXISTS idx_system_config_created_at ON system_config(created_at);

-- Comentários nas tabelas
COMMENT ON TABLE system_config IS 'Configurações gerais do sistema IA SOLARIS';
COMMENT ON COLUMN system_config.key IS 'Chave única da configuração';
COMMENT ON COLUMN system_config.value IS 'Valor da configuração';
COMMENT ON COLUMN system_config.description IS 'Descrição da configuração';

-- Criar usuário para aplicação (se não existir)
DO $$
BEGIN
    IF NOT EXISTS (SELECT FROM pg_catalog.pg_roles WHERE rolname = 'ia_solaris_app') THEN
        CREATE ROLE ia_solaris_app WITH LOGIN PASSWORD 'ia_solaris_app_2025';
    END IF;
END
$$;

-- Conceder permissões
GRANT USAGE ON SCHEMA ia_solaris TO ia_solaris_app;
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA ia_solaris TO ia_solaris_app;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA ia_solaris TO ia_solaris_app;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA ia_solaris TO ia_solaris_app;

-- Configurar permissões padrão para objetos futuros
ALTER DEFAULT PRIVILEGES IN SCHEMA ia_solaris GRANT ALL ON TABLES TO ia_solaris_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA ia_solaris GRANT ALL ON SEQUENCES TO ia_solaris_app;
ALTER DEFAULT PRIVILEGES IN SCHEMA ia_solaris GRANT ALL ON FUNCTIONS TO ia_solaris_app;

-- Log de inicialização
INSERT INTO system_config (key, value, description) VALUES
    ('database_initialized_at', CURRENT_TIMESTAMP::text, 'Timestamp de inicialização do banco')
ON CONFLICT (key) DO UPDATE SET 
    value = CURRENT_TIMESTAMP::text,
    updated_at = CURRENT_TIMESTAMP;

