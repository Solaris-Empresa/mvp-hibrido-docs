import { useState, useEffect } from 'react'
import { 
  Users, 
  Zap, 
  TrendingUp, 
  AlertTriangle,
  RefreshCw,
  DollarSign,
  Activity,
  Clock
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Badge } from '@/components/ui/badge'
import { Progress } from '@/components/ui/progress'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, BarChart, Bar } from 'recharts'

const Dashboard = ({ apiBase, systemStats, onRefresh }) => {
  const [recentUsers, setRecentUsers] = useState([])
  const [loading, setLoading] = useState(false)
  const [usageData, setUsageData] = useState([])

  useEffect(() => {
    loadRecentUsers()
    generateMockUsageData()
  }, [])

  const loadRecentUsers = async () => {
    try {
      const response = await fetch(`${apiBase}/admin/users?per_page=5`)
      if (response.ok) {
        const data = await response.json()
        setRecentUsers(data.users || [])
      }
    } catch (error) {
      console.error('Erro ao carregar usuários recentes:', error)
    }
  }

  const generateMockUsageData = () => {
    // Dados simulados para o gráfico
    const data = []
    const today = new Date()
    
    for (let i = 6; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(date.getDate() - i)
      
      data.push({
        date: date.toLocaleDateString('pt-BR', { day: '2-digit', month: '2-digit' }),
        tokens: Math.floor(Math.random() * 5000) + 2000,
        users: Math.floor(Math.random() * 50) + 20
      })
    }
    
    setUsageData(data)
  }

  const handleRefresh = async () => {
    setLoading(true)
    await onRefresh()
    await loadRecentUsers()
    setLoading(false)
  }

  const getUsagePercentage = () => {
    if (!systemStats?.tokens) return 0
    const { total_distributed, total_used } = systemStats.tokens
    return total_distributed > 0 ? (total_used / total_distributed) * 100 : 0
  }

  const getStatusBadge = (user) => {
    if (user.is_blocked) {
      return <Badge variant="destructive">Bloqueado</Badge>
    }
    if (!user.is_active) {
      return <Badge variant="secondary">Inativo</Badge>
    }
    if (user.usage_percentage > 90) {
      return <Badge variant="outline" className="text-orange-600 border-orange-600">Crítico</Badge>
    }
    return <Badge variant="outline" className="text-green-600 border-green-600">Ativo</Badge>
  }

  if (!systemStats) {
    return (
      <div className="flex items-center justify-center h-64">
        <div className="text-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando dashboard...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Dashboard</h1>
          <p className="text-gray-600 mt-1">Visão geral do sistema IA SOLARIS</p>
        </div>
        <Button 
          onClick={handleRefresh} 
          disabled={loading}
          className="flex items-center space-x-2"
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          <span>Atualizar</span>
        </Button>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Total de Usuários</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStats.users.total}</div>
            <p className="text-xs text-muted-foreground">
              {systemStats.users.active} ativos
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tokens Distribuídos</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">
              {systemStats.tokens.total_distributed.toLocaleString()}
            </div>
            <p className="text-xs text-muted-foreground">
              {systemStats.tokens.total_used.toLocaleString()} consumidos
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Usuários Bloqueados</CardTitle>
            <AlertTriangle className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-red-600">
              {systemStats.users.blocked}
            </div>
            <p className="text-xs text-muted-foreground">
              {systemStats.users.total > 0 
                ? ((systemStats.users.blocked / systemStats.users.total) * 100).toFixed(1)
                : 0}% do total
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Transações Hoje</CardTitle>
            <Activity className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{systemStats.activity.transactions_today}</div>
            <p className="text-xs text-muted-foreground">
              Atividade do dia
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Usage Overview */}
      <Card>
        <CardHeader>
          <CardTitle>Uso Geral de Tokens</CardTitle>
          <CardDescription>
            Percentual de tokens consumidos vs distribuídos
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <span className="text-sm font-medium">
                {systemStats.tokens.total_used.toLocaleString()} / {systemStats.tokens.total_distributed.toLocaleString()} tokens
              </span>
              <span className="text-sm text-muted-foreground">
                {getUsagePercentage().toFixed(1)}%
              </span>
            </div>
            <Progress value={getUsagePercentage()} className="w-full" />
            <div className="flex justify-between text-xs text-muted-foreground">
              <span>Tokens restantes: {systemStats.tokens.total_remaining.toLocaleString()}</span>
              <span>
                {getUsagePercentage() > 80 ? 'Alto uso' : 
                 getUsagePercentage() > 50 ? 'Uso moderado' : 'Uso baixo'}
              </span>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Uso de Tokens (7 dias)</CardTitle>
            <CardDescription>Consumo diário de tokens</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={usageData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip 
                  formatter={(value, name) => [
                    value.toLocaleString(), 
                    name === 'tokens' ? 'Tokens' : 'Usuários'
                  ]}
                />
                <Line 
                  type="monotone" 
                  dataKey="tokens" 
                  stroke="#3b82f6" 
                  strokeWidth={2}
                  dot={{ fill: '#3b82f6' }}
                />
              </LineChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Usuários Ativos (7 dias)</CardTitle>
            <CardDescription>Número de usuários ativos por dia</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={usageData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip 
                  formatter={(value) => [value, 'Usuários']}
                />
                <Bar dataKey="users" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Recent Users */}
      <Card>
        <CardHeader>
          <CardTitle>Usuários Recentes</CardTitle>
          <CardDescription>Últimos usuários cadastrados no sistema</CardDescription>
        </CardHeader>
        <CardContent>
          {recentUsers.length > 0 ? (
            <div className="space-y-4">
              {recentUsers.map((user) => (
                <div key={user.id} className="flex items-center justify-between p-4 border rounded-lg">
                  <div className="flex items-center space-x-4">
                    <div className="w-10 h-10 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                      <span className="text-white font-medium text-sm">
                        {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
                      </span>
                    </div>
                    <div>
                      <p className="font-medium">{user.name || 'Usuário'}</p>
                      <p className="text-sm text-gray-500">{user.email}</p>
                    </div>
                  </div>
                  <div className="flex items-center space-x-4">
                    <div className="text-right">
                      <p className="text-sm font-medium">
                        {user.remaining_tokens.toLocaleString()} tokens
                      </p>
                      <p className="text-xs text-gray-500">
                        {user.usage_percentage.toFixed(1)}% usado
                      </p>
                    </div>
                    {getStatusBadge(user)}
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div className="text-center py-8">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Nenhum usuário encontrado</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}

export default Dashboard

