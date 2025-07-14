# Interfaces e Frontend - MVP IA SOLARIS

## Visão Geral

Este documento detalha o desenvolvimento completo das interfaces frontend do MVP híbrido de controle de tokens da IA SOLARIS. O sistema inclui um dashboard administrativo em React para gestão de usuários, monitoramento de consumo e configurações do sistema, além de integrações com o LibreChat para experiência transparente do usuário final.

## Arquitetura Frontend

### Stack Tecnológico

- **Framework:** React 18 com TypeScript
- **Build Tool:** Vite para desenvolvimento rápido
- **Styling:** Tailwind CSS + Headless UI
- **State Management:** Zustand para estado global
- **HTTP Client:** Axios com interceptors
- **Charts:** Chart.js + React-Chartjs-2
- **Icons:** Heroicons + Lucide React
- **Forms:** React Hook Form + Zod validation
- **Routing:** React Router v6
- **WebSocket:** Socket.io-client para real-time

### Estrutura do Projeto

```
admin-ia-solaris/
├── public/
│   ├── favicon.ico
│   ├── logo192.png
│   ├── logo512.png
│   └── manifest.json
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Table.tsx
│   │   │   ├── Card.tsx
│   │   │   ├── Badge.tsx
│   │   │   ├── Spinner.tsx
│   │   │   ├── Alert.tsx
│   │   │   └── Layout.tsx
│   │   ├── charts/
│   │   │   ├── LineChart.tsx
│   │   │   ├── BarChart.tsx
│   │   │   ├── PieChart.tsx
│   │   │   ├── AreaChart.tsx
│   │   │   └── MetricCard.tsx
│   │   ├── forms/
│   │   │   ├── UserForm.tsx
│   │   │   ├── TokenForm.tsx
│   │   │   ├── SettingsForm.tsx
│   │   │   └── AlertForm.tsx
│   │   ├── navigation/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── Header.tsx
│   │   │   ├── Breadcrumb.tsx
│   │   │   └── MobileMenu.tsx
│   │   └── features/
│   │       ├── dashboard/
│   │       ├── users/
│   │       ├── analytics/
│   │       ├── settings/
│   │       └── alerts/
│   ├── pages/
│   │   ├── Dashboard.tsx
│   │   ├── Users.tsx
│   │   ├── Analytics.tsx
│   │   ├── Settings.tsx
│   │   ├── Alerts.tsx
│   │   ├── Models.tsx
│   │   ├── Logs.tsx
│   │   └── Login.tsx
│   ├── hooks/
│   │   ├── useAuth.ts
│   │   ├── useApi.ts
│   │   ├── useWebSocket.ts
│   │   ├── useLocalStorage.ts
│   │   ├── useDebounce.ts
│   │   └── usePagination.ts
│   ├── services/
│   │   ├── api.ts
│   │   ├── auth.ts
│   │   ├── websocket.ts
│   │   └── storage.ts
│   ├── stores/
│   │   ├── authStore.ts
│   │   ├── userStore.ts
│   │   ├── analyticsStore.ts
│   │   └── settingsStore.ts
│   ├── types/
│   │   ├── api.ts
│   │   ├── user.ts
│   │   ├── analytics.ts
│   │   └── common.ts
│   ├── utils/
│   │   ├── formatters.ts
│   │   ├── validators.ts
│   │   ├── constants.ts
│   │   ├── helpers.ts
│   │   └── date.ts
│   ├── styles/
│   │   ├── globals.css
│   │   ├── components.css
│   │   └── utilities.css
│   ├── App.tsx
│   ├── main.tsx
│   └── vite-env.d.ts
├── package.json
├── package-lock.json
├── tsconfig.json
├── tsconfig.node.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
├── Dockerfile
├── nginx.conf
└── .env.example
```

## Configuração do Projeto

### Package.json

```json
{
  "name": "admin-ia-solaris",
  "private": true,
  "version": "1.0.0",
  "type": "module",
  "scripts": {
    "dev": "vite",
    "build": "tsc && vite build",
    "lint": "eslint . --ext ts,tsx --report-unused-disable-directives --max-warnings 0",
    "preview": "vite preview",
    "test": "vitest",
    "test:ui": "vitest --ui",
    "type-check": "tsc --noEmit"
  },
  "dependencies": {
    "react": "^18.2.0",
    "react-dom": "^18.2.0",
    "react-router-dom": "^6.8.1",
    "react-hook-form": "^7.43.5",
    "react-query": "^3.39.3",
    "@tanstack/react-query": "^4.28.0",
    "zustand": "^4.3.6",
    "axios": "^1.3.4",
    "socket.io-client": "^4.6.1",
    "chart.js": "^4.2.1",
    "react-chartjs-2": "^5.2.0",
    "date-fns": "^2.29.3",
    "clsx": "^1.2.1",
    "tailwind-merge": "^1.10.0",
    "@headlessui/react": "^1.7.13",
    "@heroicons/react": "^2.0.16",
    "lucide-react": "^0.220.0",
    "zod": "^3.21.4",
    "@hookform/resolvers": "^3.0.0",
    "react-hot-toast": "^2.4.0",
    "framer-motion": "^10.10.0"
  },
  "devDependencies": {
    "@types/react": "^18.0.28",
    "@types/react-dom": "^18.0.11",
    "@typescript-eslint/eslint-plugin": "^5.57.1",
    "@typescript-eslint/parser": "^5.57.1",
    "@vitejs/plugin-react": "^4.0.0",
    "autoprefixer": "^10.4.14",
    "eslint": "^8.38.0",
    "eslint-plugin-react-hooks": "^4.6.0",
    "eslint-plugin-react-refresh": "^0.3.4",
    "postcss": "^8.4.21",
    "tailwindcss": "^3.3.0",
    "typescript": "^5.0.2",
    "vite": "^4.3.2",
    "vitest": "^0.30.1",
    "@testing-library/react": "^14.0.0",
    "@testing-library/jest-dom": "^5.16.5"
  }
}
```

### Configuração Vite (vite.config.ts)

```typescript
import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import path from 'path'

export default defineConfig({
  plugins: [react()],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src'),
      '@components': path.resolve(__dirname, './src/components'),
      '@pages': path.resolve(__dirname, './src/pages'),
      '@hooks': path.resolve(__dirname, './src/hooks'),
      '@services': path.resolve(__dirname, './src/services'),
      '@stores': path.resolve(__dirname, './src/stores'),
      '@types': path.resolve(__dirname, './src/types'),
      '@utils': path.resolve(__dirname, './src/utils'),
      '@styles': path.resolve(__dirname, './src/styles')
    }
  },
  server: {
    port: 3000,
    host: true,
    proxy: {
      '/api': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        secure: false
      },
      '/socket.io': {
        target: 'http://localhost:5000',
        changeOrigin: true,
        ws: true
      }
    }
  },
  build: {
    outDir: 'dist',
    sourcemap: true,
    rollupOptions: {
      output: {
        manualChunks: {
          vendor: ['react', 'react-dom', 'react-router-dom'],
          charts: ['chart.js', 'react-chartjs-2'],
          ui: ['@headlessui/react', '@heroicons/react', 'lucide-react']
        }
      }
    }
  },
  define: {
    __APP_VERSION__: JSON.stringify(process.env.npm_package_version)
  }
})
```

### Configuração Tailwind (tailwind.config.js)

```javascript
/** @type {import('tailwindcss').Config} */
export default {
  content: [
    "./index.html",
    "./src/**/*.{js,ts,jsx,tsx}",
  ],
  theme: {
    extend: {
      colors: {
        primary: {
          50: '#eff6ff',
          100: '#dbeafe',
          200: '#bfdbfe',
          300: '#93c5fd',
          400: '#60a5fa',
          500: '#3b82f6',
          600: '#2563eb',
          700: '#1d4ed8',
          800: '#1e40af',
          900: '#1e3a8a',
          950: '#172554'
        },
        success: {
          50: '#f0fdf4',
          100: '#dcfce7',
          200: '#bbf7d0',
          300: '#86efac',
          400: '#4ade80',
          500: '#22c55e',
          600: '#16a34a',
          700: '#15803d',
          800: '#166534',
          900: '#14532d'
        },
        warning: {
          50: '#fffbeb',
          100: '#fef3c7',
          200: '#fde68a',
          300: '#fcd34d',
          400: '#fbbf24',
          500: '#f59e0b',
          600: '#d97706',
          700: '#b45309',
          800: '#92400e',
          900: '#78350f'
        },
        danger: {
          50: '#fef2f2',
          100: '#fee2e2',
          200: '#fecaca',
          300: '#fca5a5',
          400: '#f87171',
          500: '#ef4444',
          600: '#dc2626',
          700: '#b91c1c',
          800: '#991b1b',
          900: '#7f1d1d'
        }
      },
      fontFamily: {
        sans: ['Inter', 'system-ui', 'sans-serif'],
        mono: ['JetBrains Mono', 'monospace']
      },
      animation: {
        'fade-in': 'fadeIn 0.5s ease-in-out',
        'slide-up': 'slideUp 0.3s ease-out',
        'pulse-slow': 'pulse 3s infinite'
      },
      keyframes: {
        fadeIn: {
          '0%': { opacity: '0' },
          '100%': { opacity: '1' }
        },
        slideUp: {
          '0%': { transform: 'translateY(10px)', opacity: '0' },
          '100%': { transform: 'translateY(0)', opacity: '1' }
        }
      }
    },
  },
  plugins: [
    require('@tailwindcss/forms'),
    require('@tailwindcss/typography'),
    require('@tailwindcss/aspect-ratio')
  ],
}
```

## Tipos TypeScript

### Tipos de API (types/api.ts)

```typescript
// Tipos base
export interface ApiResponse<T = any> {
  data: T
  message?: string
  success: boolean
  timestamp: string
}

export interface PaginatedResponse<T> extends ApiResponse<T[]> {
  pagination: {
    page: number
    limit: number
    total: number
    totalPages: number
    hasNext: boolean
    hasPrev: boolean
  }
}

export interface ApiError {
  message: string
  code: string
  details?: Record<string, any>
  timestamp: string
}

// Tipos de usuário
export interface User {
  id: number
  email: string
  name: string
  phone?: string
  status: 'active' | 'suspended' | 'blocked' | 'pending'
  plan: 'basic' | 'pro' | 'enterprise' | 'trial'
  monthlyLimit: number
  currentUsage: number
  additionalTokens: number
  alert80Sent: boolean
  alert95Sent: boolean
  lastAlertDate?: string
  lastLogin?: string
  loginCount: number
  notes?: string
  customAlertThreshold80?: number
  customAlertThreshold95?: number
  emailNotificationsEnabled: boolean
  createdAt: string
  updatedAt: string
}

export interface CreateUserRequest {
  email: string
  name: string
  phone?: string
  plan?: User['plan']
  monthlyLimit?: number
  emailNotificationsEnabled?: boolean
}

export interface UpdateUserRequest extends Partial<CreateUserRequest> {
  status?: User['status']
  additionalTokens?: number
  notes?: string
  customAlertThreshold80?: number
  customAlertThreshold95?: number
}

// Tipos de uso de tokens
export interface TokenUsage {
  id: number
  userId: number
  requestId: string
  sessionId?: string
  model: string
  endpoint: string
  method: string
  promptTokens: number
  completionTokens: number
  totalTokens: number
  estimatedTokens?: number
  estimationAccuracy?: number
  costPerToken: number
  totalCost: number
  userAgent?: string
  ipAddress?: string
  countryCode?: string
  responseTimeMs?: number
  queueTimeMs?: number
  processingTimeMs?: number
  statusCode: number
  errorMessage?: string
  errorType?: string
  isCached: boolean
  isRetry: boolean
  retryCount: number
  requestData?: string
  responseData?: string
  createdAt: string
}

// Tipos de analytics
export interface DashboardMetrics {
  totalUsers: number
  activeUsers: number
  totalTokensUsed: number
  totalCost: number
  avgTokensPerUser: number
  topModels: Array<{
    model: string
    usage: number
    percentage: number
  }>
  usageByDay: Array<{
    date: string
    tokens: number
    cost: number
    users: number
  }>
  alertsSent: {
    alert80: number
    alert95: number
    blocked: number
  }
  systemHealth: {
    proxy: 'healthy' | 'unhealthy'
    litellm: 'healthy' | 'unhealthy'
    database: 'healthy' | 'unhealthy'
    redis: 'healthy' | 'unhealthy'
  }
}

export interface UserAnalytics {
  userId: number
  period: string
  totalTokens: number
  totalCost: number
  requestCount: number
  avgTokensPerRequest: number
  modelUsage: Array<{
    model: string
    tokens: number
    requests: number
    cost: number
  }>
  dailyUsage: Array<{
    date: string
    tokens: number
    requests: number
    cost: number
  }>
  errorRate: number
  avgResponseTime: number
}

// Tipos de configurações
export interface SystemSettings {
  defaultMonthlyLimit: number
  alertThreshold80: number
  alertThreshold95: number
  blockThreshold: number
  maxUserLimit: number
  minUserLimit: number
  emailSettings: {
    smtpHost: string
    smtpPort: number
    smtpUser: string
    fromEmail: string
    fromName: string
    useTls: boolean
  }
  securitySettings: {
    rateLimitPerMinute: number
    rateLimitBurst: number
    corsOrigins: string[]
  }
  litellmSettings: {
    baseUrl: string
    timeout: number
    maxRetries: number
    healthCheckInterval: number
  }
}

// Tipos de alertas
export interface Alert {
  id: number
  userId: number
  type: 'usage_80' | 'usage_95' | 'blocked' | 'system_error' | 'model_error'
  title: string
  message: string
  severity: 'info' | 'warning' | 'error' | 'critical'
  status: 'pending' | 'sent' | 'failed' | 'acknowledged'
  sentAt?: string
  acknowledgedAt?: string
  metadata?: Record<string, any>
  createdAt: string
}

// Tipos de modelos
export interface ModelInfo {
  name: string
  provider: string
  status: 'healthy' | 'unhealthy' | 'rate_limited' | 'unavailable'
  lastCheck: string
  responseTimeMs?: number
  errorRate: number
  costPerInputToken: number
  costPerOutputToken: number
  maxTokens: number
  supportsVision: boolean
  supportsFunctionCalling: boolean
  usage24h: {
    requests: number
    tokens: number
    cost: number
  }
}

// Tipos de logs
export interface AuditLog {
  id: number
  userId?: number
  action: string
  resource: string
  resourceId?: string
  details: Record<string, any>
  ipAddress?: string
  userAgent?: string
  success: boolean
  errorMessage?: string
  createdAt: string
}

// Tipos de WebSocket
export interface WebSocketMessage {
  type: 'user_update' | 'usage_update' | 'alert' | 'system_status' | 'model_status'
  data: any
  timestamp: string
}

export interface RealTimeUpdate {
  type: WebSocketMessage['type']
  payload: any
}
```

## Serviços e API

### Cliente API (services/api.ts)

```typescript
import axios, { AxiosInstance, AxiosRequestConfig, AxiosResponse } from 'axios'
import { toast } from 'react-hot-toast'
import { ApiResponse, ApiError, PaginatedResponse } from '@types/api'

class ApiClient {
  private client: AxiosInstance
  private baseURL: string

  constructor() {
    this.baseURL = import.meta.env.VITE_API_BASE_URL || '/api'
    
    this.client = axios.create({
      baseURL: this.baseURL,
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json'
      }
    })

    this.setupInterceptors()
  }

  private setupInterceptors() {
    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        // Adicionar token de autenticação
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }

        // Adicionar request ID para tracking
        config.headers['X-Request-ID'] = this.generateRequestId()

        return config
      },
      (error) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor
    this.client.interceptors.response.use(
      (response: AxiosResponse<ApiResponse>) => {
        return response
      },
      (error) => {
        this.handleApiError(error)
        return Promise.reject(error)
      }
    )
  }

  private generateRequestId(): string {
    return `req_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
  }

  private handleApiError(error: any) {
    if (error.response) {
      const { status, data } = error.response
      
      switch (status) {
        case 401:
          // Token expirado ou inválido
          localStorage.removeItem('auth_token')
          window.location.href = '/login'
          toast.error('Sessão expirada. Faça login novamente.')
          break
          
        case 403:
          toast.error('Acesso negado. Você não tem permissão para esta ação.')
          break
          
        case 404:
          toast.error('Recurso não encontrado.')
          break
          
        case 429:
          toast.error('Muitas requisições. Tente novamente em alguns minutos.')
          break
          
        case 500:
          toast.error('Erro interno do servidor. Tente novamente mais tarde.')
          break
          
        default:
          const message = data?.message || 'Erro inesperado'
          toast.error(message)
      }
    } else if (error.request) {
      toast.error('Erro de conexão. Verifique sua internet.')
    } else {
      toast.error('Erro inesperado. Tente novamente.')
    }
  }

  // Métodos HTTP genéricos
  async get<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.get<ApiResponse<T>>(url, config)
    return response.data
  }

  async post<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.post<ApiResponse<T>>(url, data, config)
    return response.data
  }

  async put<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.put<ApiResponse<T>>(url, data, config)
    return response.data
  }

  async patch<T = any>(url: string, data?: any, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.patch<ApiResponse<T>>(url, data, config)
    return response.data
  }

  async delete<T = any>(url: string, config?: AxiosRequestConfig): Promise<ApiResponse<T>> {
    const response = await this.client.delete<ApiResponse<T>>(url, config)
    return response.data
  }

  // Métodos específicos da API

  // Usuários
  async getUsers(params?: {
    page?: number
    limit?: number
    search?: string
    status?: string
    plan?: string
  }): Promise<PaginatedResponse<User>> {
    return this.get('/admin/users', { params })
  }

  async getUser(id: number): Promise<ApiResponse<User>> {
    return this.get(`/admin/users/${id}`)
  }

  async createUser(data: CreateUserRequest): Promise<ApiResponse<User>> {
    return this.post('/admin/users', data)
  }

  async updateUser(id: number, data: UpdateUserRequest): Promise<ApiResponse<User>> {
    return this.patch(`/admin/users/${id}`, data)
  }

  async deleteUser(id: number): Promise<ApiResponse<void>> {
    return this.delete(`/admin/users/${id}`)
  }

  async addTokensToUser(id: number, amount: number, reason?: string): Promise<ApiResponse<User>> {
    return this.post(`/admin/users/${id}/tokens`, { amount, reason })
  }

  async resetUserUsage(id: number): Promise<ApiResponse<User>> {
    return this.post(`/admin/users/${id}/reset-usage`)
  }

  // Analytics
  async getDashboardMetrics(period?: string): Promise<ApiResponse<DashboardMetrics>> {
    return this.get('/admin/analytics/dashboard', { params: { period } })
  }

  async getUserAnalytics(userId: number, period?: string): Promise<ApiResponse<UserAnalytics>> {
    return this.get(`/admin/analytics/users/${userId}`, { params: { period } })
  }

  async getUsageHistory(params?: {
    userId?: number
    model?: string
    startDate?: string
    endDate?: string
    page?: number
    limit?: number
  }): Promise<PaginatedResponse<TokenUsage>> {
    return this.get('/admin/analytics/usage', { params })
  }

  // Configurações
  async getSettings(): Promise<ApiResponse<SystemSettings>> {
    return this.get('/admin/settings')
  }

  async updateSettings(data: Partial<SystemSettings>): Promise<ApiResponse<SystemSettings>> {
    return this.patch('/admin/settings', data)
  }

  async testEmailSettings(email: string): Promise<ApiResponse<void>> {
    return this.post('/admin/settings/test-email', { email })
  }

  // Alertas
  async getAlerts(params?: {
    userId?: number
    type?: string
    status?: string
    page?: number
    limit?: number
  }): Promise<PaginatedResponse<Alert>> {
    return this.get('/admin/alerts', { params })
  }

  async acknowledgeAlert(id: number): Promise<ApiResponse<Alert>> {
    return this.post(`/admin/alerts/${id}/acknowledge`)
  }

  async sendTestAlert(userId: number, type: string): Promise<ApiResponse<void>> {
    return this.post('/admin/alerts/test', { userId, type })
  }

  // Modelos
  async getModels(): Promise<ApiResponse<ModelInfo[]>> {
    return this.get('/admin/models')
  }

  async getModelInfo(modelName: string): Promise<ApiResponse<ModelInfo>> {
    return this.get(`/admin/models/${modelName}`)
  }

  async refreshModels(): Promise<ApiResponse<void>> {
    return this.post('/admin/models/refresh')
  }

  // Logs
  async getAuditLogs(params?: {
    userId?: number
    action?: string
    resource?: string
    startDate?: string
    endDate?: string
    page?: number
    limit?: number
  }): Promise<PaginatedResponse<AuditLog>> {
    return this.get('/admin/logs/audit', { params })
  }

  async exportLogs(params: {
    startDate: string
    endDate: string
    format: 'csv' | 'json'
  }): Promise<Blob> {
    const response = await this.client.get('/admin/logs/export', {
      params,
      responseType: 'blob'
    })
    return response.data
  }

  // Health checks
  async getSystemHealth(): Promise<ApiResponse<any>> {
    return this.get('/health')
  }

  async getLiteLLMHealth(): Promise<ApiResponse<any>> {
    return this.get('/admin/litellm/health')
  }

  // Autenticação
  async login(email: string, password: string): Promise<ApiResponse<{ token: string, user: any }>> {
    return this.post('/auth/login', { email, password })
  }

  async logout(): Promise<ApiResponse<void>> {
    return this.post('/auth/logout')
  }

  async refreshToken(): Promise<ApiResponse<{ token: string }>> {
    return this.post('/auth/refresh')
  }

  async getProfile(): Promise<ApiResponse<any>> {
    return this.get('/auth/profile')
  }
}

// Instância singleton
export const apiClient = new ApiClient()
export default apiClient
```

### WebSocket Service (services/websocket.ts)

```typescript
import { io, Socket } from 'socket.io-client'
import { WebSocketMessage, RealTimeUpdate } from '@types/api'

type EventCallback = (data: any) => void

class WebSocketService {
  private socket: Socket | null = null
  private reconnectAttempts = 0
  private maxReconnectAttempts = 5
  private reconnectDelay = 1000
  private eventCallbacks: Map<string, EventCallback[]> = new Map()

  connect(token?: string) {
    if (this.socket?.connected) {
      return
    }

    const url = import.meta.env.VITE_WS_URL || window.location.origin
    
    this.socket = io(url, {
      auth: {
        token: token || localStorage.getItem('auth_token')
      },
      transports: ['websocket', 'polling'],
      timeout: 20000,
      forceNew: true
    })

    this.setupEventListeners()
  }

  disconnect() {
    if (this.socket) {
      this.socket.disconnect()
      this.socket = null
    }
    this.eventCallbacks.clear()
    this.reconnectAttempts = 0
  }

  private setupEventListeners() {
    if (!this.socket) return

    this.socket.on('connect', () => {
      console.log('WebSocket connected')
      this.reconnectAttempts = 0
      this.triggerCallbacks('connected', { connected: true })
    })

    this.socket.on('disconnect', (reason) => {
      console.log('WebSocket disconnected:', reason)
      this.triggerCallbacks('disconnected', { connected: false, reason })
      
      if (reason === 'io server disconnect') {
        // Servidor desconectou, tentar reconectar
        this.handleReconnect()
      }
    })

    this.socket.on('connect_error', (error) => {
      console.error('WebSocket connection error:', error)
      this.triggerCallbacks('error', { error: error.message })
      this.handleReconnect()
    })

    // Eventos específicos da aplicação
    this.socket.on('user_update', (data) => {
      this.triggerCallbacks('user_update', data)
    })

    this.socket.on('usage_update', (data) => {
      this.triggerCallbacks('usage_update', data)
    })

    this.socket.on('alert', (data) => {
      this.triggerCallbacks('alert', data)
    })

    this.socket.on('system_status', (data) => {
      this.triggerCallbacks('system_status', data)
    })

    this.socket.on('model_status', (data) => {
      this.triggerCallbacks('model_status', data)
    })

    this.socket.on('real_time_metrics', (data) => {
      this.triggerCallbacks('real_time_metrics', data)
    })
  }

  private handleReconnect() {
    if (this.reconnectAttempts >= this.maxReconnectAttempts) {
      console.error('Max reconnection attempts reached')
      this.triggerCallbacks('max_reconnect_attempts', {})
      return
    }

    this.reconnectAttempts++
    const delay = this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1)

    console.log(`Attempting to reconnect in ${delay}ms (attempt ${this.reconnectAttempts})`)

    setTimeout(() => {
      if (this.socket && !this.socket.connected) {
        this.socket.connect()
      }
    }, delay)
  }

  private triggerCallbacks(event: string, data: any) {
    const callbacks = this.eventCallbacks.get(event) || []
    callbacks.forEach(callback => {
      try {
        callback(data)
      } catch (error) {
        console.error(`Error in WebSocket callback for event ${event}:`, error)
      }
    })
  }

  // Métodos públicos para gerenciar eventos
  on(event: string, callback: EventCallback) {
    if (!this.eventCallbacks.has(event)) {
      this.eventCallbacks.set(event, [])
    }
    this.eventCallbacks.get(event)!.push(callback)
  }

  off(event: string, callback?: EventCallback) {
    if (!callback) {
      this.eventCallbacks.delete(event)
      return
    }

    const callbacks = this.eventCallbacks.get(event) || []
    const index = callbacks.indexOf(callback)
    if (index > -1) {
      callbacks.splice(index, 1)
    }
  }

  emit(event: string, data: any) {
    if (this.socket?.connected) {
      this.socket.emit(event, data)
    }
  }

  // Métodos específicos da aplicação
  subscribeToUserUpdates(callback: EventCallback) {
    this.on('user_update', callback)
  }

  subscribeToUsageUpdates(callback: EventCallback) {
    this.on('usage_update', callback)
  }

  subscribeToAlerts(callback: EventCallback) {
    this.on('alert', callback)
  }

  subscribeToSystemStatus(callback: EventCallback) {
    this.on('system_status', callback)
  }

  subscribeToModelStatus(callback: EventCallback) {
    this.on('model_status', callback)
  }

  subscribeToRealTimeMetrics(callback: EventCallback) {
    this.on('real_time_metrics', callback)
  }

  // Getters
  get connected(): boolean {
    return this.socket?.connected || false
  }

  get id(): string | undefined {
    return this.socket?.id
  }
}

// Instância singleton
export const wsService = new WebSocketService()
export default wsService
```

## Stores (Zustand)

### Auth Store (stores/authStore.ts)

```typescript
import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import { apiClient } from '@services/api'
import { wsService } from '@services/websocket'

interface User {
  id: number
  email: string
  name: string
  role: 'admin' | 'user'
  permissions: string[]
}

interface AuthState {
  user: User | null
  token: string | null
  isAuthenticated: boolean
  isLoading: boolean
  error: string | null
}

interface AuthActions {
  login: (email: string, password: string) => Promise<void>
  logout: () => void
  refreshToken: () => Promise<void>
  clearError: () => void
  setLoading: (loading: boolean) => void
}

export const useAuthStore = create<AuthState & AuthActions>()(
  persist(
    (set, get) => ({
      // Estado inicial
      user: null,
      token: null,
      isAuthenticated: false,
      isLoading: false,
      error: null,

      // Ações
      login: async (email: string, password: string) => {
        set({ isLoading: true, error: null })
        
        try {
          const response = await apiClient.login(email, password)
          const { token, user } = response.data

          // Salvar token no localStorage
          localStorage.setItem('auth_token', token)

          // Conectar WebSocket
          wsService.connect(token)

          set({
            user,
            token,
            isAuthenticated: true,
            isLoading: false,
            error: null
          })
        } catch (error: any) {
          set({
            isLoading: false,
            error: error.response?.data?.message || 'Erro ao fazer login'
          })
          throw error
        }
      },

      logout: () => {
        // Remover token
        localStorage.removeItem('auth_token')
        
        // Desconectar WebSocket
        wsService.disconnect()

        // Fazer logout na API (fire and forget)
        apiClient.logout().catch(() => {})

        set({
          user: null,
          token: null,
          isAuthenticated: false,
          error: null
        })
      },

      refreshToken: async () => {
        try {
          const response = await apiClient.refreshToken()
          const { token } = response.data

          localStorage.setItem('auth_token', token)

          set({ token })
        } catch (error) {
          // Token inválido, fazer logout
          get().logout()
          throw error
        }
      },

      clearError: () => {
        set({ error: null })
      },

      setLoading: (loading: boolean) => {
        set({ isLoading: loading })
      }
    }),
    {
      name: 'auth-storage',
      partialize: (state) => ({
        user: state.user,
        token: state.token,
        isAuthenticated: state.isAuthenticated
      })
    }
  )
)

// Hook para verificar permissões
export const usePermissions = () => {
  const user = useAuthStore(state => state.user)
  
  const hasPermission = (permission: string): boolean => {
    if (!user) return false
    return user.permissions.includes(permission) || user.role === 'admin'
  }

  const hasAnyPermission = (permissions: string[]): boolean => {
    return permissions.some(permission => hasPermission(permission))
  }

  const hasAllPermissions = (permissions: string[]): boolean => {
    return permissions.every(permission => hasPermission(permission))
  }

  return {
    hasPermission,
    hasAnyPermission,
    hasAllPermissions,
    isAdmin: user?.role === 'admin'
  }
}
```

### User Store (stores/userStore.ts)

```typescript
import { create } from 'zustand'
import { apiClient } from '@services/api'
import { wsService } from '@services/websocket'
import { User, CreateUserRequest, UpdateUserRequest, PaginatedResponse } from '@types/api'

interface UserState {
  users: User[]
  selectedUser: User | null
  totalUsers: number
  currentPage: number
  totalPages: number
  isLoading: boolean
  error: string | null
  filters: {
    search: string
    status: string
    plan: string
  }
}

interface UserActions {
  fetchUsers: (page?: number) => Promise<void>
  fetchUser: (id: number) => Promise<void>
  createUser: (data: CreateUserRequest) => Promise<User>
  updateUser: (id: number, data: UpdateUserRequest) => Promise<User>
  deleteUser: (id: number) => Promise<void>
  addTokensToUser: (id: number, amount: number, reason?: string) => Promise<User>
  resetUserUsage: (id: number) => Promise<User>
  setFilters: (filters: Partial<UserState['filters']>) => void
  setSelectedUser: (user: User | null) => void
  clearError: () => void
}

export const useUserStore = create<UserState & UserActions>((set, get) => ({
  // Estado inicial
  users: [],
  selectedUser: null,
  totalUsers: 0,
  currentPage: 1,
  totalPages: 1,
  isLoading: false,
  error: null,
  filters: {
    search: '',
    status: '',
    plan: ''
  },

  // Ações
  fetchUsers: async (page = 1) => {
    set({ isLoading: true, error: null })
    
    try {
      const { filters } = get()
      const response = await apiClient.getUsers({
        page,
        limit: 20,
        search: filters.search || undefined,
        status: filters.status || undefined,
        plan: filters.plan || undefined
      })

      set({
        users: response.data,
        totalUsers: response.pagination.total,
        currentPage: response.pagination.page,
        totalPages: response.pagination.totalPages,
        isLoading: false
      })
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Erro ao carregar usuários'
      })
    }
  },

  fetchUser: async (id: number) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await apiClient.getUser(id)
      set({
        selectedUser: response.data,
        isLoading: false
      })
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Erro ao carregar usuário'
      })
    }
  },

  createUser: async (data: CreateUserRequest) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await apiClient.createUser(data)
      const newUser = response.data

      // Adicionar à lista local
      set(state => ({
        users: [newUser, ...state.users],
        totalUsers: state.totalUsers + 1,
        isLoading: false
      }))

      return newUser
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Erro ao criar usuário'
      })
      throw error
    }
  },

  updateUser: async (id: number, data: UpdateUserRequest) => {
    set({ isLoading: true, error: null })
    
    try {
      const response = await apiClient.updateUser(id, data)
      const updatedUser = response.data

      // Atualizar na lista local
      set(state => ({
        users: state.users.map(user => 
          user.id === id ? updatedUser : user
        ),
        selectedUser: state.selectedUser?.id === id ? updatedUser : state.selectedUser,
        isLoading: false
      }))

      return updatedUser
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Erro ao atualizar usuário'
      })
      throw error
    }
  },

  deleteUser: async (id: number) => {
    set({ isLoading: true, error: null })
    
    try {
      await apiClient.deleteUser(id)

      // Remover da lista local
      set(state => ({
        users: state.users.filter(user => user.id !== id),
        totalUsers: state.totalUsers - 1,
        selectedUser: state.selectedUser?.id === id ? null : state.selectedUser,
        isLoading: false
      }))
    } catch (error: any) {
      set({
        isLoading: false,
        error: error.response?.data?.message || 'Erro ao excluir usuário'
      })
      throw error
    }
  },

  addTokensToUser: async (id: number, amount: number, reason?: string) => {
    try {
      const response = await apiClient.addTokensToUser(id, amount, reason)
      const updatedUser = response.data

      // Atualizar na lista local
      set(state => ({
        users: state.users.map(user => 
          user.id === id ? updatedUser : user
        ),
        selectedUser: state.selectedUser?.id === id ? updatedUser : state.selectedUser
      }))

      return updatedUser
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Erro ao adicionar tokens'
      })
      throw error
    }
  },

  resetUserUsage: async (id: number) => {
    try {
      const response = await apiClient.resetUserUsage(id)
      const updatedUser = response.data

      // Atualizar na lista local
      set(state => ({
        users: state.users.map(user => 
          user.id === id ? updatedUser : user
        ),
        selectedUser: state.selectedUser?.id === id ? updatedUser : state.selectedUser
      }))

      return updatedUser
    } catch (error: any) {
      set({
        error: error.response?.data?.message || 'Erro ao resetar uso'
      })
      throw error
    }
  },

  setFilters: (newFilters: Partial<UserState['filters']>) => {
    set(state => ({
      filters: { ...state.filters, ...newFilters }
    }))
    
    // Recarregar usuários com novos filtros
    get().fetchUsers(1)
  },

  setSelectedUser: (user: User | null) => {
    set({ selectedUser: user })
  },

  clearError: () => {
    set({ error: null })
  }
}))

// Configurar WebSocket para atualizações em tempo real
wsService.subscribeToUserUpdates((data) => {
  const { users, selectedUser } = useUserStore.getState()
  
  if (data.type === 'user_updated') {
    const updatedUser = data.user
    
    useUserStore.setState({
      users: users.map(user => 
        user.id === updatedUser.id ? updatedUser : user
      ),
      selectedUser: selectedUser?.id === updatedUser.id ? updatedUser : selectedUser
    })
  } else if (data.type === 'user_created') {
    const newUser = data.user
    
    useUserStore.setState({
      users: [newUser, ...users],
      totalUsers: useUserStore.getState().totalUsers + 1
    })
  } else if (data.type === 'user_deleted') {
    const deletedUserId = data.userId
    
    useUserStore.setState({
      users: users.filter(user => user.id !== deletedUserId),
      totalUsers: useUserStore.getState().totalUsers - 1,
      selectedUser: selectedUser?.id === deletedUserId ? null : selectedUser
    })
  }
})
```

---

**Autor:** Manus AI  
**Data:** Janeiro 2024  
**Versão:** 1.0

