import { useState, useEffect } from 'react'
import { 
  BarChart3, 
  TrendingUp, 
  Users, 
  Zap, 
  DollarSign,
  Calendar,
  Download,
  RefreshCw
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { 
  LineChart, 
  Line, 
  XAxis, 
  YAxis, 
  CartesianGrid, 
  Tooltip, 
  ResponsiveContainer, 
  BarChart, 
  Bar,
  PieChart,
  Pie,
  Cell
} from 'recharts'

const SystemStats = ({ apiBase, systemStats }) => {
  const [loading, setLoading] = useState(false)
  const [timeRange, setTimeRange] = useState('7d')
  const [chartData, setChartData] = useState([])
  const [userDistribution, setUserDistribution] = useState([])

  useEffect(() => {
    generateMockData()
  }, [timeRange])

  const generateMockData = () => {
    // Dados simulados para demonstração
    const days = timeRange === '7d' ? 7 : timeRange === '30d' ? 30 : 90
    const data = []
    const today = new Date()
    
    for (let i = days - 1; i >= 0; i--) {
      const date = new Date(today)
      date.setDate(date.getDate() - i)
      
      data.push({
        date: date.toLocaleDateString('pt-BR', { 
          day: '2-digit', 
          month: '2-digit',
          ...(days > 30 && { year: '2-digit' })
        }),
        tokens_used: Math.floor(Math.random() * 5000) + 2000,
        new_users: Math.floor(Math.random() * 10) + 2,
        active_users: Math.floor(Math.random() * 50) + 20,
        revenue: Math.floor(Math.random() * 500) + 200
      })
    }
    
    setChartData(data)

    // Distribuição de usuários por status
    if (systemStats) {
      setUserDistribution([
        { name: 'Ativos', value: systemStats.users.active, color: '#10b981' },
        { name: 'Bloqueados', value: systemStats.users.blocked, color: '#ef4444' },
        { name: 'Inativos', value: systemStats.users.total - systemStats.users.active - systemStats.users.blocked, color: '#6b7280' }
      ])
    }
  }

  const handleExport = () => {
    // Simula exportação de dados
    const csvContent = "data:text/csv;charset=utf-8," + 
      "Data,Tokens Usados,Novos Usuários,Usuários Ativos,Receita\n" +
      chartData.map(row => `${row.date},${row.tokens_used},${row.new_users},${row.active_users},${row.revenue}`).join("\n")
    
    const encodedUri = encodeURI(csvContent)
    const link = document.createElement("a")
    link.setAttribute("href", encodedUri)
    link.setAttribute("download", `ia_solaris_stats_${timeRange}.csv`)
    document.body.appendChild(link)
    link.click()
    document.body.removeChild(link)
  }

  const calculateGrowth = (data, field) => {
    if (data.length < 2) return 0
    const current = data[data.length - 1][field]
    const previous = data[data.length - 2][field]
    return previous > 0 ? ((current - previous) / previous * 100) : 0
  }

  const totalTokensUsed = chartData.reduce((sum, item) => sum + item.tokens_used, 0)
  const totalNewUsers = chartData.reduce((sum, item) => sum + item.new_users, 0)
  const totalRevenue = chartData.reduce((sum, item) => sum + item.revenue, 0)
  const avgActiveUsers = chartData.length > 0 ? chartData.reduce((sum, item) => sum + item.active_users, 0) / chartData.length : 0

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Estatísticas do Sistema</h1>
          <p className="text-gray-600 mt-1">Análise detalhada de uso e performance</p>
        </div>
        <div className="flex items-center space-x-2">
          <Button
            variant="outline"
            size="sm"
            onClick={handleExport}
          >
            <Download className="w-4 h-4 mr-2" />
            Exportar
          </Button>
          <Button
            variant="outline"
            size="sm"
            onClick={generateMockData}
            disabled={loading}
          >
            <RefreshCw className={`w-4 h-4 mr-2 ${loading ? 'animate-spin' : ''}`} />
            Atualizar
          </Button>
        </div>
      </div>

      {/* Time Range Selector */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex space-x-2">
            {[
              { value: '7d', label: '7 dias' },
              { value: '30d', label: '30 dias' },
              { value: '90d', label: '90 dias' }
            ].map((range) => (
              <Button
                key={range.value}
                variant={timeRange === range.value ? 'default' : 'outline'}
                size="sm"
                onClick={() => setTimeRange(range.value)}
              >
                {range.label}
              </Button>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Tokens Consumidos</CardTitle>
            <Zap className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalTokensUsed.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              {calculateGrowth(chartData, 'tokens_used') > 0 ? '+' : ''}
              {calculateGrowth(chartData, 'tokens_used').toFixed(1)}% vs período anterior
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Novos Usuários</CardTitle>
            <Users className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{totalNewUsers}</div>
            <p className="text-xs text-muted-foreground">
              {calculateGrowth(chartData, 'new_users') > 0 ? '+' : ''}
              {calculateGrowth(chartData, 'new_users').toFixed(1)}% vs período anterior
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Usuários Ativos (Média)</CardTitle>
            <TrendingUp className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">{Math.round(avgActiveUsers)}</div>
            <p className="text-xs text-muted-foreground">
              {calculateGrowth(chartData, 'active_users') > 0 ? '+' : ''}
              {calculateGrowth(chartData, 'active_users').toFixed(1)}% vs período anterior
            </p>
          </CardContent>
        </Card>

        <Card>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium">Receita Estimada</CardTitle>
            <DollarSign className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold">R$ {totalRevenue.toLocaleString()}</div>
            <p className="text-xs text-muted-foreground">
              {calculateGrowth(chartData, 'revenue') > 0 ? '+' : ''}
              {calculateGrowth(chartData, 'revenue').toFixed(1)}% vs período anterior
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Charts */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card>
          <CardHeader>
            <CardTitle>Consumo de Tokens</CardTitle>
            <CardDescription>Tokens consumidos ao longo do tempo</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <LineChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip 
                  formatter={(value) => [value.toLocaleString(), 'Tokens']}
                />
                <Line 
                  type="monotone" 
                  dataKey="tokens_used" 
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
            <CardTitle>Usuários Ativos</CardTitle>
            <CardDescription>Número de usuários ativos por dia</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip 
                  formatter={(value) => [value, 'Usuários']}
                />
                <Bar dataKey="active_users" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Novos Usuários</CardTitle>
            <CardDescription>Crescimento da base de usuários</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={chartData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip 
                  formatter={(value) => [value, 'Novos Usuários']}
                />
                <Bar dataKey="new_users" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Distribuição de Usuários</CardTitle>
            <CardDescription>Status atual dos usuários</CardDescription>
          </CardHeader>
          <CardContent>
            <ResponsiveContainer width="100%" height={300}>
              <PieChart>
                <Pie
                  data={userDistribution}
                  cx="50%"
                  cy="50%"
                  labelLine={false}
                  label={({ name, percent }) => `${name} ${(percent * 100).toFixed(0)}%`}
                  outerRadius={80}
                  fill="#8884d8"
                  dataKey="value"
                >
                  {userDistribution.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip />
              </PieChart>
            </ResponsiveContainer>
          </CardContent>
        </Card>
      </div>

      {/* Detailed Stats Table */}
      <Card>
        <CardHeader>
          <CardTitle>Dados Detalhados</CardTitle>
          <CardDescription>Estatísticas diárias do período selecionado</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full text-sm">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-2">Data</th>
                  <th className="text-right p-2">Tokens Usados</th>
                  <th className="text-right p-2">Novos Usuários</th>
                  <th className="text-right p-2">Usuários Ativos</th>
                  <th className="text-right p-2">Receita (R$)</th>
                </tr>
              </thead>
              <tbody>
                {chartData.slice(-10).map((row, index) => (
                  <tr key={index} className="border-b hover:bg-gray-50">
                    <td className="p-2 font-medium">{row.date}</td>
                    <td className="p-2 text-right">{row.tokens_used.toLocaleString()}</td>
                    <td className="p-2 text-right">{row.new_users}</td>
                    <td className="p-2 text-right">{row.active_users}</td>
                    <td className="p-2 text-right">R$ {row.revenue.toLocaleString()}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>
    </div>
  )
}

export default SystemStats

