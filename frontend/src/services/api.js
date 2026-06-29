import axios from 'axios'
import { getStoredKey } from '../hooks/useLocalStorage'

// API 基础配置
const apiClient = axios.create({
  baseURL: '/api',
  timeout: 180000, // 3分钟超时（联网搜索需要较长时间）
  headers: {
    'Content-Type': 'application/json'
  }
})

// 请求拦截器：添加 API Key
apiClient.interceptors.request.use((config) => {
  const keys = getStoredKey('jintian_api_keys') || {}
  if (keys.llmToken) {
    config.headers['X-LLM-Token'] = keys.llmToken
  }
  if (keys.mouserApiKey) {
    config.headers['X-Mouser-Key'] = keys.mouserApiKey
  }
  return config
})

// 响应拦截器：统一错误处理
apiClient.interceptors.response.use(
  (response) => response.data,
  (error) => {
    console.error('API Error:', error)
    return Promise.reject(error)
  }
)

// ==================== API 函数 ====================

export const api = {
  // 健康检查
  getHealth: () => apiClient.get('/health'),

  // 价格查询
  searchPrice: (model, options = {}) => apiClient.get('/price/search', {
    params: {
      model,
      include_history: options.includeHistory || false
    }
  }),

  getPriceTrend: (model, days = 180) => apiClient.get('/price/trend', {
    params: { model, days }
  }),

  getPriceHistory: (model, days = 30) => apiClient.get('/price/history', {
    params: { model, days }
  }),

  // 监控管理
  getWatchList: () => apiClient.get('/price/watch-list'),

  addToWatchList: (model) => apiClient.post('/price/watch-list/add', null, {
    params: { model }
  }),

  removeFromWatchList: (model) => apiClient.post('/price/watch-list/remove', null, {
    params: { model }
  }),

  // 调度器
  getSchedulerStatus: () => apiClient.get('/price/scheduler/status'),
  getSchedulerLogs: (limit = 20) => apiClient.get('/price/scheduler/logs', { params: { limit } }),
  startScheduler: (hour = 9, minute = 0) => apiClient.post('/price/scheduler/start', null, { params: { hour, minute } }),
  stopScheduler: () => apiClient.post('/price/scheduler/stop'),

  // 统计
  getStatistics: () => apiClient.get('/price/statistics'),
  getTrackedModels: () => apiClient.get('/price/models'),

  // 供应商寻源
  searchSuppliers: (data) => apiClient.post('/supplier/search', data),
  getSupplierDetail: (name) => apiClient.get('/supplier/detail', { params: { name } }),
  checkQualification: (name, certifications) =>
    apiClient.get('/supplier/check-qualification', {
      params: { name, certifications: certifications.join(',') }
    }),

  // 智能寻源
  sourcing: (data) => apiClient.post('/supplier/sourcing', data),
  generateInterviewQuestions: (data) => apiClient.post('/supplier/interview-questions', data),

  // 智能对话（价格追踪 AI 分析使用）
  chat: (message, context = null) => apiClient.post('/chat', { message, context })
}

export default api