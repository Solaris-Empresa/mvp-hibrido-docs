import { useState, useEffect } from 'react'
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom'
import { Toaster } from '@/components/ui/toaster'
import Sidebar from '@/components/Sidebar'
import Dashboard from '@/components/Dashboard'
import UsersManagement from '@/components/UsersManagement'
import SystemStats from '@/components/SystemStats'
import Settings from '@/components/Settings'
import './App.css'

function App() {
  const [currentPage, setCurrentPage] = useState('dashboard')
  const [systemStats, setSystemStats] = useState(null)
  const [loading, setLoading] = useState(true)

  // Configuração da API base
  const API_BASE = import.meta.env.VITE_API_BASE || 'http://localhost:5000/v1'

  useEffect(() => {
    loadSystemStats()
  }, [])

  const loadSystemStats = async () => {
    try {
      const response = await fetch(`${API_BASE}/admin/stats`)
      if (response.ok) {
        const data = await response.json()
        setSystemStats(data)
      }
    } catch (error) {
      console.error('Erro ao carregar estatísticas:', error)
    } finally {
      setLoading(false)
    }
  }

  const renderCurrentPage = () => {
    switch (currentPage) {
      case 'dashboard':
        return <Dashboard apiBase={API_BASE} systemStats={systemStats} onRefresh={loadSystemStats} />
      case 'users':
        return <UsersManagement apiBase={API_BASE} onRefresh={loadSystemStats} />
      case 'stats':
        return <SystemStats apiBase={API_BASE} systemStats={systemStats} />
      case 'settings':
        return <Settings apiBase={API_BASE} />
      default:
        return <Dashboard apiBase={API_BASE} systemStats={systemStats} onRefresh={loadSystemStats} />
    }
  }

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600">Carregando IA SOLARIS Admin...</p>
        </div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-50 flex">
      <Sidebar 
        currentPage={currentPage} 
        onPageChange={setCurrentPage}
        systemStats={systemStats}
      />
      
      <main className="flex-1 ml-64 p-8">
        <div className="max-w-7xl mx-auto">
          {renderCurrentPage()}
        </div>
      </main>

      <Toaster />
    </div>
  )
}

export default App

