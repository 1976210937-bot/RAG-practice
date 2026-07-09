// API请求封装
import axios from 'axios'
import type { User } from '../types'

// 创建axios实例
const api = axios.create({
  baseURL: '/api',
  timeout: 30000,
})

// 请求拦截器：添加token
api.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器：处理错误
api.interceptors.response.use(
  (response) => {
    return response.data
  },
  (error) => {
    if (error.response?.status === 401) {
      // 未授权，清除token并跳转登录页
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      window.location.href = '/login'
    }
    return Promise.reject(error)
  }
)

// ==================== 认证相关API ====================

/** 用户登录 */
export const login = async (username: string, password: string) => {
  return api.post('/auth/login', { username, password })
}

/** 获取当前用户信息 */
export const getCurrentUser = async () => {
  return api.get('/auth/me')
}

/** 用户注册 */
export const register = async (username: string, password: string, email?: string) => {
  return api.post('/auth/register', { username, password, email })
}

// ==================== 文档相关API ====================

/** 获取文档列表 */
export const getDocuments = async (page = 1, pageSize = 10, keyword?: string) => {
  const params: any = { page, page_size: pageSize }
  if (keyword) params.keyword = keyword
  return api.get('/documents', { params })
}

/** 获取文档详情 */
export const getDocument = async (id: number) => {
  return api.get(`/documents/${id}`)
}

/** 上传文档 */
export const uploadDocument = async (title: string, file: File) => {
  const formData = new FormData()
  formData.append('title', title)
  formData.append('file', file)
  return api.post('/documents/upload', formData, {
    headers: {
      'Content-Type': 'multipart/form-data',
    },
  })
}

/** 删除文档 */
export const deleteDocument = async (id: number) => {
  return api.delete(`/documents/${id}`)
}

/** 重新处理文档 */
export const reprocessDocument = async (id: number) => {
  return api.post(`/documents/${id}/reprocess`)
}

// ==================== 对话相关API ====================

/** 获取会话列表 */
export const getConversations = async () => {
  return api.get('/chat/conversations')
}

/** 创建会话 */
export const createConversation = async (title: string) => {
  return api.post('/chat/conversations', { title })
}

/** 获取会话消息 */
export const getConversationMessages = async (conversationId: number) => {
  return api.get(`/chat/conversations/${conversationId}/messages`)
}

/** 删除会话 */
export const deleteConversation = async (conversationId: number) => {
  return api.delete(`/chat/conversations/${conversationId}`)
}

/** 提问 */
export const queryChat = async (question: string, conversationId?: number) => {
  const data: any = { question }
  if (conversationId) data.conversation_id = conversationId
  return api.post('/chat/query', data)
}

// ==================== 管理员相关API ====================

/** 获取仪表盘统计 */
export const getDashboardStats = async () => {
  return api.get('/admin/stats')
}

/** 获取用户列表 */
export const getUsers = async () => {
  return api.get('/admin/users')
}

/** 创建用户 */
export const createUser = async (userData: { username: string; password: string; email?: string; role: string }) => {
  return api.post('/admin/users', userData)
}

/** 更新用户 */
export const updateUser = async (userId: number, userData: any) => {
  return api.put(`/admin/users/${userId}`, userData)
}

/** 删除用户 */
export const deleteUser = async (userId: number) => {
  return api.delete(`/admin/users/${userId}`)
}

// ==================== 工具函数 ====================

/** 获取本地存储的用户信息 */
export const getStoredUser = (): User | null => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    try {
      return JSON.parse(userStr)
    } catch {
      return null
    }
  }
  return null
}

/** 保存用户信息到本地存储 */
export const setStoredUser = (user: User) => {
  localStorage.setItem('user', JSON.stringify(user))
}

/** 清除本地存储的用户信息 */
export const clearStoredUser = () => {
  localStorage.removeItem('token')
  localStorage.removeItem('user')
}

export default api
