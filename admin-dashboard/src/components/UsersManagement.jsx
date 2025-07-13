import { useState, useEffect } from 'react'
import { 
  Users, 
  Search, 
  Plus, 
  MoreHorizontal,
  AlertTriangle,
  CheckCircle,
  XCircle,
  Zap,
  Mail,
  Calendar,
  Filter
} from 'lucide-react'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Button } from '@/components/ui/button'
import { Input } from '@/components/ui/input'
import { Badge } from '@/components/ui/badge'
import { 
  Table, 
  TableBody, 
  TableCell, 
  TableHead, 
  TableHeader, 
  TableRow 
} from '@/components/ui/table'
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu'
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog'
import { Label } from '@/components/ui/label'
import { useToast } from '@/hooks/use-toast'

const UsersManagement = ({ apiBase, onRefresh }) => {
  const [users, setUsers] = useState([])
  const [loading, setLoading] = useState(true)
  const [searchTerm, setSearchTerm] = useState('')
  const [filterStatus, setFilterStatus] = useState('all')
  const [selectedUser, setSelectedUser] = useState(null)
  const [showAddTokensDialog, setShowAddTokensDialog] = useState(false)
  const [tokensToAdd, setTokensToAdd] = useState('')
  const [addingTokens, setAddingTokens] = useState(false)
  const [pagination, setPagination] = useState({
    page: 1,
    per_page: 20,
    total: 0,
    pages: 0
  })

  const { toast } = useToast()

  useEffect(() => {
    loadUsers()
  }, [pagination.page, filterStatus])

  const loadUsers = async () => {
    try {
      setLoading(true)
      const params = new URLSearchParams({
        page: pagination.page.toString(),
        per_page: pagination.per_page.toString()
      })

      const response = await fetch(`${apiBase}/admin/users?${params}`)
      if (response.ok) {
        const data = await response.json()
        setUsers(data.users || [])
        setPagination(prev => ({
          ...prev,
          total: data.pagination?.total || 0,
          pages: data.pagination?.pages || 0
        }))
      } else {
        toast({
          title: "Erro",
          description: "Não foi possível carregar os usuários",
          variant: "destructive"
        })
      }
    } catch (error) {
      console.error('Erro ao carregar usuários:', error)
      toast({
        title: "Erro",
        description: "Erro de conexão com o servidor",
        variant: "destructive"
      })
    } finally {
      setLoading(false)
    }
  }

  const handleAddTokens = async () => {
    if (!selectedUser || !tokensToAdd || parseInt(tokensToAdd) <= 0) {
      toast({
        title: "Erro",
        description: "Informe uma quantidade válida de tokens",
        variant: "destructive"
      })
      return
    }

    try {
      setAddingTokens(true)
      const response = await fetch(`${apiBase}/admin/users/${selectedUser.id}/add-tokens`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({
          tokens: parseInt(tokensToAdd),
          reason: 'manual_addition_admin'
        })
      })

      if (response.ok) {
        const data = await response.json()
        toast({
          title: "Sucesso",
          description: `${tokensToAdd} tokens adicionados com sucesso!`
        })
        
        // Atualiza a lista de usuários
        await loadUsers()
        await onRefresh()
        
        // Fecha o dialog
        setShowAddTokensDialog(false)
        setSelectedUser(null)
        setTokensToAdd('')
      } else {
        const errorData = await response.json()
        toast({
          title: "Erro",
          description: errorData.message || "Erro ao adicionar tokens",
          variant: "destructive"
        })
      }
    } catch (error) {
      console.error('Erro ao adicionar tokens:', error)
      toast({
        title: "Erro",
        description: "Erro de conexão com o servidor",
        variant: "destructive"
      })
    } finally {
      setAddingTokens(false)
    }
  }

  const getStatusBadge = (user) => {
    if (user.is_blocked) {
      return <Badge variant="destructive" className="flex items-center space-x-1">
        <XCircle className="w-3 h-3" />
        <span>Bloqueado</span>
      </Badge>
    }
    if (!user.is_active) {
      return <Badge variant="secondary" className="flex items-center space-x-1">
        <AlertTriangle className="w-3 h-3" />
        <span>Inativo</span>
      </Badge>
    }
    if (user.usage_percentage > 90) {
      return <Badge variant="outline" className="text-orange-600 border-orange-600 flex items-center space-x-1">
        <AlertTriangle className="w-3 h-3" />
        <span>Crítico</span>
      </Badge>
    }
    return <Badge variant="outline" className="text-green-600 border-green-600 flex items-center space-x-1">
      <CheckCircle className="w-3 h-3" />
      <span>Ativo</span>
    </Badge>
  }

  const getUsageColor = (percentage) => {
    if (percentage >= 90) return 'text-red-600'
    if (percentage >= 80) return 'text-orange-600'
    if (percentage >= 60) return 'text-yellow-600'
    return 'text-green-600'
  }

  const filteredUsers = users.filter(user => {
    const matchesSearch = user.name?.toLowerCase().includes(searchTerm.toLowerCase()) ||
                         user.email?.toLowerCase().includes(searchTerm.toLowerCase())
    
    const matchesFilter = filterStatus === 'all' ||
                         (filterStatus === 'active' && user.is_active && !user.is_blocked) ||
                         (filterStatus === 'blocked' && user.is_blocked) ||
                         (filterStatus === 'inactive' && !user.is_active)
    
    return matchesSearch && matchesFilter
  })

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-3xl font-bold text-gray-900">Gerenciamento de Usuários</h1>
          <p className="text-gray-600 mt-1">Gerencie usuários e seus tokens</p>
        </div>
      </div>

      {/* Filters */}
      <Card>
        <CardContent className="pt-6">
          <div className="flex flex-col sm:flex-row gap-4">
            <div className="flex-1">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 text-gray-400 w-4 h-4" />
                <Input
                  placeholder="Buscar por nome ou email..."
                  value={searchTerm}
                  onChange={(e) => setSearchTerm(e.target.value)}
                  className="pl-10"
                />
              </div>
            </div>
            <div className="flex gap-2">
              <Button
                variant={filterStatus === 'all' ? 'default' : 'outline'}
                onClick={() => setFilterStatus('all')}
                size="sm"
              >
                Todos
              </Button>
              <Button
                variant={filterStatus === 'active' ? 'default' : 'outline'}
                onClick={() => setFilterStatus('active')}
                size="sm"
              >
                Ativos
              </Button>
              <Button
                variant={filterStatus === 'blocked' ? 'default' : 'outline'}
                onClick={() => setFilterStatus('blocked')}
                size="sm"
              >
                Bloqueados
              </Button>
              <Button
                variant={filterStatus === 'inactive' ? 'default' : 'outline'}
                onClick={() => setFilterStatus('inactive')}
                size="sm"
              >
                Inativos
              </Button>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* Users Table */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center justify-between">
            <span>Usuários ({filteredUsers.length})</span>
            <Button onClick={loadUsers} disabled={loading} size="sm">
              Atualizar
            </Button>
          </CardTitle>
        </CardHeader>
        <CardContent>
          {loading ? (
            <div className="flex items-center justify-center h-32">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>
          ) : filteredUsers.length > 0 ? (
            <Table>
              <TableHeader>
                <TableRow>
                  <TableHead>Usuário</TableHead>
                  <TableHead>Status</TableHead>
                  <TableHead>Tokens</TableHead>
                  <TableHead>Uso</TableHead>
                  <TableHead>Último Acesso</TableHead>
                  <TableHead className="text-right">Ações</TableHead>
                </TableRow>
              </TableHeader>
              <TableBody>
                {filteredUsers.map((user) => (
                  <TableRow key={user.id}>
                    <TableCell>
                      <div className="flex items-center space-x-3">
                        <div className="w-8 h-8 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center">
                          <span className="text-white font-medium text-xs">
                            {user.name ? user.name.charAt(0).toUpperCase() : 'U'}
                          </span>
                        </div>
                        <div>
                          <p className="font-medium">{user.name || 'Usuário'}</p>
                          <p className="text-sm text-gray-500">{user.email}</p>
                        </div>
                      </div>
                    </TableCell>
                    <TableCell>
                      {getStatusBadge(user)}
                    </TableCell>
                    <TableCell>
                      <div>
                        <p className="font-medium">{user.remaining_tokens.toLocaleString()}</p>
                        <p className="text-sm text-gray-500">de {user.total_tokens.toLocaleString()}</p>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="flex items-center space-x-2">
                        <div className="w-16 bg-gray-200 rounded-full h-2">
                          <div 
                            className={`h-2 rounded-full ${
                              user.usage_percentage >= 90 ? 'bg-red-500' :
                              user.usage_percentage >= 80 ? 'bg-orange-500' :
                              user.usage_percentage >= 60 ? 'bg-yellow-500' : 'bg-green-500'
                            }`}
                            style={{ width: `${Math.min(user.usage_percentage, 100)}%` }}
                          />
                        </div>
                        <span className={`text-sm font-medium ${getUsageColor(user.usage_percentage)}`}>
                          {user.usage_percentage.toFixed(1)}%
                        </span>
                      </div>
                    </TableCell>
                    <TableCell>
                      <div className="text-sm">
                        {user.last_activity ? (
                          <div>
                            <p>{new Date(user.last_activity).toLocaleDateString('pt-BR')}</p>
                            <p className="text-gray-500">{new Date(user.last_activity).toLocaleTimeString('pt-BR')}</p>
                          </div>
                        ) : (
                          <span className="text-gray-400">Nunca</span>
                        )}
                      </div>
                    </TableCell>
                    <TableCell className="text-right">
                      <DropdownMenu>
                        <DropdownMenuTrigger asChild>
                          <Button variant="ghost" size="sm">
                            <MoreHorizontal className="w-4 h-4" />
                          </Button>
                        </DropdownMenuTrigger>
                        <DropdownMenuContent align="end">
                          <DropdownMenuItem
                            onClick={() => {
                              setSelectedUser(user)
                              setShowAddTokensDialog(true)
                            }}
                          >
                            <Zap className="w-4 h-4 mr-2" />
                            Adicionar Tokens
                          </DropdownMenuItem>
                          <DropdownMenuItem
                            onClick={() => {
                              window.open(`mailto:${user.email}`, '_blank')
                            }}
                          >
                            <Mail className="w-4 h-4 mr-2" />
                            Enviar Email
                          </DropdownMenuItem>
                        </DropdownMenuContent>
                      </DropdownMenu>
                    </TableCell>
                  </TableRow>
                ))}
              </TableBody>
            </Table>
          ) : (
            <div className="text-center py-8">
              <Users className="w-12 h-12 text-gray-400 mx-auto mb-4" />
              <p className="text-gray-500">Nenhum usuário encontrado</p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* Pagination */}
      {pagination.pages > 1 && (
        <div className="flex items-center justify-between">
          <p className="text-sm text-gray-500">
            Página {pagination.page} de {pagination.pages} ({pagination.total} usuários)
          </p>
          <div className="flex space-x-2">
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPagination(prev => ({ ...prev, page: prev.page - 1 }))}
              disabled={pagination.page <= 1}
            >
              Anterior
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => setPagination(prev => ({ ...prev, page: prev.page + 1 }))}
              disabled={pagination.page >= pagination.pages}
            >
              Próxima
            </Button>
          </div>
        </div>
      )}

      {/* Add Tokens Dialog */}
      <Dialog open={showAddTokensDialog} onOpenChange={setShowAddTokensDialog}>
        <DialogContent>
          <DialogHeader>
            <DialogTitle>Adicionar Tokens</DialogTitle>
            <DialogDescription>
              Adicione tokens para o usuário {selectedUser?.name || selectedUser?.email}
            </DialogDescription>
          </DialogHeader>
          <div className="space-y-4">
            <div>
              <Label htmlFor="tokens">Quantidade de Tokens</Label>
              <Input
                id="tokens"
                type="number"
                placeholder="Ex: 1000"
                value={tokensToAdd}
                onChange={(e) => setTokensToAdd(e.target.value)}
                min="1"
              />
            </div>
            {selectedUser && (
              <div className="p-4 bg-gray-50 rounded-lg">
                <h4 className="font-medium mb-2">Situação Atual:</h4>
                <div className="space-y-1 text-sm">
                  <p>Tokens atuais: {selectedUser.remaining_tokens.toLocaleString()}</p>
                  <p>Total: {selectedUser.total_tokens.toLocaleString()}</p>
                  <p>Uso: {selectedUser.usage_percentage.toFixed(1)}%</p>
                </div>
              </div>
            )}
          </div>
          <DialogFooter>
            <Button
              variant="outline"
              onClick={() => {
                setShowAddTokensDialog(false)
                setSelectedUser(null)
                setTokensToAdd('')
              }}
            >
              Cancelar
            </Button>
            <Button onClick={handleAddTokens} disabled={addingTokens}>
              {addingTokens ? 'Adicionando...' : 'Adicionar Tokens'}
            </Button>
          </DialogFooter>
        </DialogContent>
      </Dialog>
    </div>
  )
}

export default UsersManagement

