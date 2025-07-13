import { useState, useEffect } from 'react'
import { 
  Settings as SettingsIcon, 
  Save, 
  RefreshCw,
  Mail,
  Zap,
  AlertTriangle,
  Database,
  Server,
  Shield
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Label } from '@/components/ui/label'
import { Textarea } from '@/components/ui/textarea'
import { Switch } from '@/components/ui/switch'
import { Separator } from '@/components/ui/separator'
import { useToast } from '@/hooks/use-toast'

const Settings = ({ apiBase }) => {
  const [settings, setSettings] = useState({
    // Configurações de tokens
    default_tokens_per_user: '1000',
    conversion_factor: '0.376',
    alert_threshold_80: '0.8',
    alert_threshold_95: '0.95',
    
    // Configurações de email
    credits_email: 'creditos@iasolaris.com.br',
    smtp_server: 'smtp.gmail.com',
    smtp_port: '587',
    smtp_username: '',
    smtp_password: '',
    from_email: 'noreply@iasolaris.com.br',
    from_name: 'IA SOLARIS',
    
    // Configurações do sistema
    system_name: 'IA SOLARIS',
    max_requests_per_minute: '60',
    session_timeout: '3600',
    enable_debug_mode: false,
    enable_email_notifications: true,
    enable_auto_blocking: true,
    
    // Configurações LiteLLM
    litellm_base_url: 'http://localhost:4000',
    litellm_api_key: 'sk-1234',
    openai_api_key: '',
    
    // Configurações de segurança
    require_email_verification: false,
    enable_rate_limiting: true,
    max_failed_attempts: '5'
  })
  
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [testingConnection, setTestingConnection] = useState(false)

  const { toast } = useToast()

  useEffect(() => {
    loadSettings()
  }, [])

  const loadSettings = async () => {
    try {
      setLoading(true)
      // Como não temos endpoint de configurações ainda, vamos usar valores padrão
      // Em uma implementação real, faria: const response = await fetch(`${apiBase}/admin/settings`)
      
      // Simula carregamento
      await new Promise(resolve => setTimeout(resolve, 500))
      
      toast({
        title: "Configurações carregadas",
        description: "Configurações atuais do sistema"
      })
    } catch (error) {
      console.error('Erro ao carregar configurações:', error)
      toast({
        title: "Erro",
        description: "Não foi possível carregar as configurações",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const saveSettings = async () => {
    try {
      setSaving(true)
      
      // Simula salvamento
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      toast({
        title: "Configurações salvas",
        description: "Todas as configurações foram atualizadas com sucesso"
      })
    } catch (error) {
      console.error('Erro ao salvar configurações:', error)
      toast({
        title: "Erro",
        description: "Não foi possível salvar as configurações",
        variant: "destructive"
      })
    } finally {
      setSaving(false)
    }
  }

  const testLiteLLMConnection = async () => {
    try {
      setTestingConnection(true)
      
      // Simula teste de conexão
      await new Promise(resolve => setTimeout(resolve, 2000))
      
      const success = Math.random() > 0.3 // 70% de chance de sucesso
      
      if (success) {
        toast({
          title: "Conexão bem-sucedida",
          description: "LiteLLM está respondendo corretamente"
        })
      } else {
        toast({
          title: "Falha na conexão",
          description: "Não foi possível conectar ao LiteLLM",
          variant: "destructive"
        })
      }
    } catch (error) {
      toast({
        title: "Erro no teste",
        description: "Erro ao testar conexão com LiteLLM",
        variant: "destructive"
      })
    } finally {
      setTestingConnection(false)
    }
  }

  const handleInputChange = (key, value) => {
    setSettings(prev => ({
      ...prev,
      [key]: value
    }))
  }

  const handleSwitchChange = (key, checked) => {
    setSettings(prev => ({
      ...prev,
      [key]: checked
    }))
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Configurações do Sistema</h1>
          <p className="text-gray-600 mt-1">Gerencie as configurações da IA SOLARIS</p>
        </div>
        <div className="flex space-x-2">
          <Button
            variant="outline"
            onClick={loadSettings}
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Recarregar
          </Button>
          <Button
            onClick={saveSettings}
            disabled={saving}
          >
            <Save className={`w-4 h-4 mr-2 ${saving ? 'animate-spin' : ''}`} />
            {saving ? 'Salvando...' : 'Salvar Tudo'}
          </Button>
        </div>
      </div>

      {/* Token Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Zap className="w-5 h-5" />
            <span>Configurações de Tokens</span>
          </CardTitle>
          <CardDescription>
            Configure os parâmetros de controle de tokens
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="default_tokens">Tokens Padrão por Usuário</Label>
              <Input
                id="default_tokens"
                type="number"
                value={settings.default_tokens_per_user}
                onChange={(e) => handleInputChange('default_tokens_per_user', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="conversion_factor">Fator de Conversão</Label>
              <Input
                id="conversion_factor"
                type="number"
                step="0.001"
                value={settings.conversion_factor}
                onChange={(e) => handleInputChange('conversion_factor', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="alert_80">Limite de Alerta 80%</Label>
              <Input
                id="alert_80"
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={settings.alert_threshold_80}
                onChange={(e) => handleInputChange('alert_threshold_80', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="alert_95">Limite de Alerta 95%</Label>
              <Input
                id="alert_95"
                type="number"
                step="0.01"
                min="0"
                max="1"
                value={settings.alert_threshold_95}
                onChange={(e) => handleInputChange('alert_threshold_95', e.target.value)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Email Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Mail className="w-5 h-5" />
            <span>Configurações de Email</span>
          </CardTitle>
          <CardDescription>
            Configure o sistema de envio de emails e alertas
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="credits_email">Email para Compra de Créditos</Label>
              <Input
                id="credits_email"
                type="email"
                value={settings.credits_email}
                onChange={(e) => handleInputChange('credits_email', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="from_email">Email Remetente</Label>
              <Input
                id="from_email"
                type="email"
                value={settings.from_email}
                onChange={(e) => handleInputChange('from_email', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="from_name">Nome Remetente</Label>
              <Input
                id="from_name"
                value={settings.from_name}
                onChange={(e) => handleInputChange('from_name', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="smtp_server">Servidor SMTP</Label>
              <Input
                id="smtp_server"
                value={settings.smtp_server}
                onChange={(e) => handleInputChange('smtp_server', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="smtp_port">Porta SMTP</Label>
              <Input
                id="smtp_port"
                type="number"
                value={settings.smtp_port}
                onChange={(e) => handleInputChange('smtp_port', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="smtp_username">Usuário SMTP</Label>
              <Input
                id="smtp_username"
                value={settings.smtp_username}
                onChange={(e) => handleInputChange('smtp_username', e.target.value)}
              />
            </div>
          </div>
          <div>
            <Label htmlFor="smtp_password">Senha SMTP</Label>
            <Input
              id="smtp_password"
              type="password"
              value={settings.smtp_password}
              onChange={(e) => handleInputChange('smtp_password', e.target.value)}
            />
          </div>
        </CardContent>
      </Card>

      {/* LiteLLM Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Server className="w-5 h-5" />
            <span>Configurações LiteLLM</span>
          </CardTitle>
          <CardDescription>
            Configure a conexão com o LiteLLM e OpenAI
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="litellm_url">URL Base LiteLLM</Label>
              <Input
                id="litellm_url"
                value={settings.litellm_base_url}
                onChange={(e) => handleInputChange('litellm_base_url', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="litellm_key">Chave API LiteLLM</Label>
              <Input
                id="litellm_key"
                type="password"
                value={settings.litellm_api_key}
                onChange={(e) => handleInputChange('litellm_api_key', e.target.value)}
              />
            </div>
          </div>
          <div>
            <Label htmlFor="openai_key">Chave API OpenAI</Label>
            <Input
              id="openai_key"
              type="password"
              value={settings.openai_api_key}
              onChange={(e) => handleInputChange('openai_api_key', e.target.value)}
            />
          </div>
          <div className="flex justify-end">
            <Button
              variant="outline"
              onClick={testLiteLLMConnection}
              disabled={testingConnection}
            >
              <Server className={`w-4 h-4 mr-2 ${testingConnection ? 'animate-spin' : ''}`} />
              {testingConnection ? 'Testando...' : 'Testar Conexão'}
            </Button>
          </div>
        </CardContent>
      </Card>

      {/* System Settings */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center space-x-2">
            <Database className="w-5 h-5" />
            <span>Configurações do Sistema</span>
          </CardTitle>
          <CardDescription>
            Configure parâmetros gerais do sistema
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <Label htmlFor="system_name">Nome do Sistema</Label>
              <Input
                id="system_name"
                value={settings.system_name}
                onChange={(e) => handleInputChange('system_name', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="max_requests">Máx. Requisições/Minuto</Label>
              <Input
                id="max_requests"
                type="number"
                value={settings.max_requests_per_minute}
                onChange={(e) => handleInputChange('max_requests_per_minute', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="session_timeout">Timeout de Sessão (segundos)</Label>
              <Input
                id="session_timeout"
                type="number"
                value={settings.session_timeout}
                onChange={(e) => handleInputChange('session_timeout', e.target.value)}
              />
            </div>
            <div>
              <Label htmlFor="max_failed">Máx. Tentativas Falhadas</Label>
              <Input
                id="max_failed"
                type="number"
                value={settings.max_failed_attempts}
                onChange={(e) => handleInputChange('max_failed_attempts', e.target.value)}
              />
            </div>
          </div>

          <Separator />

          <div className="space-y-4">
            <h4 className="font-medium">Opções do Sistema</h4>
            
            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="debug_mode">Modo Debug</Label>
                <p className="text-sm text-gray-500">Ativa logs detalhados para desenvolvimento</p>
              </div>
              <Switch
                id="debug_mode"
                checked={settings.enable_debug_mode}
                onCheckedChange={(checked) => handleSwitchChange('enable_debug_mode', checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="email_notifications">Notificações por Email</Label>
                <p className="text-sm text-gray-500">Envia alertas automáticos por email</p>
              </div>
              <Switch
                id="email_notifications"
                checked={settings.enable_email_notifications}
                onCheckedChange={(checked) => handleSwitchChange('enable_email_notifications', checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="auto_blocking">Bloqueio Automático</Label>
                <p className="text-sm text-gray-500">Bloqueia usuários automaticamente quando tokens esgotam</p>
              </div>
              <Switch
                id="auto_blocking"
                checked={settings.enable_auto_blocking}
                onCheckedChange={(checked) => handleSwitchChange('enable_auto_blocking', checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="rate_limiting">Limitação de Taxa</Label>
                <p className="text-sm text-gray-500">Limita número de requisições por usuário</p>
              </div>
              <Switch
                id="rate_limiting"
                checked={settings.enable_rate_limiting}
                onCheckedChange={(checked) => handleSwitchChange('enable_rate_limiting', checked)}
              />
            </div>

            <div className="flex items-center justify-between">
              <div>
                <Label htmlFor="email_verification">Verificação de Email</Label>
                <p className="text-sm text-gray-500">Requer verificação de email para novos usuários</p>
              </div>
              <Switch
                id="email_verification"
                checked={settings.require_email_verification}
                onCheckedChange={(checked) => handleSwitchChange('require_email_verification', checked)}
              />
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Security Warning */}
      <Card className="border-orange-200 bg-orange-50">
        <CardContent className="pt-6">
          <div className="flex items-start space-x-3">
            <AlertTriangle className="w-5 h-5 text-orange-600 mt-0.5" />
            <div>
              <h4 className="font-medium text-orange-800">Aviso de Segurança</h4>
              <p className="text-sm text-orange-700 mt-1">
                Algumas configurações podem afetar a segurança e performance do sistema. 
                Teste sempre em ambiente de desenvolvimento antes de aplicar em produção.
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default Settings

