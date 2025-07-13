import { 
  LayoutDashboard, 
  Users, 
  BarChart3, 
  Settings, 
  Zap,
  AlertCircle,
  CheckCircle,
  XCircle
} from 'lucide-react'
import { cn } from '@/lib/utils'

const Sidebar = ({ currentPage, onPageChange, systemStats }) => {
  const menuItems = [
    {
      id: 'dashboard',
      label: 'Dashboard',
      icon: LayoutDashboard,
      description: 'Visão geral do sistema'
    },
    {
      id: 'users',
      label: 'Usuários',
      icon: Users,
      description: 'Gerenciar usuários e tokens'
    },
    {
      id: 'stats',
      label: 'Estatísticas',
      icon: BarChart3,
      description: 'Relatórios detalhados'
    },
    {
      id: 'settings',
      label: 'Configurações',
      icon: Settings,
      description: 'Configurações do sistema'
    }
  ]

  const getStatusColor = () => {
    if (!systemStats) return 'text-gray-400'
    
    const { users } = systemStats
    const blockedPercentage = users.total > 0 ? (users.blocked / users.total) * 100 : 0
    
    if (blockedPercentage > 20) return 'text-red-500'
    if (blockedPercentage > 10) return 'text-yellow-500'
    return 'text-green-500'
  }

  const getStatusIcon = () => {
    if (!systemStats) return AlertCircle
    
    const { users } = systemStats
    const blockedPercentage = users.total > 0 ? (users.blocked / users.total) * 100 : 0
    
    if (blockedPercentage > 20) return XCircle
    if (blockedPercentage > 10) return AlertCircle
    return CheckCircle
  }

  const StatusIcon = getStatusIcon()

  return (
    <div className="fixed left-0 top-0 h-full w-64 bg-white border-r border-gray-200 shadow-sm">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-gradient-to-br from-blue-600 to-purple-600 rounded-lg flex items-center justify-center">
            <Zap className="w-6 h-6 text-white" />
          </div>
          <div>
            <h1 className="text-xl font-bold text-gray-900">IA SOLARIS</h1>
            <p className="text-sm text-gray-500">Admin Dashboard</p>
          </div>
        </div>
      </div>

      {/* Status Card */}
      {systemStats && (
        <div className="p-4 mx-4 mt-4 bg-gray-50 rounded-lg border">
          <div className="flex items-center justify-between mb-2">
            <span className="text-sm font-medium text-gray-700">Status do Sistema</span>
            <StatusIcon className={cn("w-4 h-4", getStatusColor())} />
          </div>
          <div className="space-y-1">
            <div className="flex justify-between text-xs">
              <span className="text-gray-600">Usuários Ativos</span>
              <span className="font-medium">{systemStats.users.active}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-gray-600">Bloqueados</span>
              <span className="font-medium text-red-600">{systemStats.users.blocked}</span>
            </div>
            <div className="flex justify-between text-xs">
              <span className="text-gray-600">Tokens Restantes</span>
              <span className="font-medium">{systemStats.tokens.total_remaining.toLocaleString()}</span>
            </div>
          </div>
        </div>
      )}

      {/* Navigation */}
      <nav className="mt-6 px-4">
        <ul className="space-y-2">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = currentPage === item.id
            
            return (
              <li key={item.id}>
                <button
                  onClick={() => onPageChange(item.id)}
                  className={cn(
                    "w-full flex items-center space-x-3 px-3 py-2.5 rounded-lg text-left transition-all duration-200",
                    isActive
                      ? "bg-blue-50 text-blue-700 border border-blue-200"
                      : "text-gray-700 hover:bg-gray-50 hover:text-gray-900"
                  )}
                >
                  <Icon className={cn(
                    "w-5 h-5",
                    isActive ? "text-blue-600" : "text-gray-500"
                  )} />
                  <div className="flex-1">
                    <div className={cn(
                      "font-medium",
                      isActive ? "text-blue-700" : "text-gray-900"
                    )}>
                      {item.label}
                    </div>
                    <div className="text-xs text-gray-500 mt-0.5">
                      {item.description}
                    </div>
                  </div>
                </button>
              </li>
            )
          })}
        </ul>
      </nav>

      {/* Footer */}
      <div className="absolute bottom-0 left-0 right-0 p-4 border-t border-gray-200">
        <div className="text-center">
          <p className="text-xs text-gray-500">MVP Híbrido v1.0</p>
          <p className="text-xs text-gray-400 mt-1">Controle de Tokens</p>
        </div>
      </div>
    </div>
  )
}

export default Sidebar

