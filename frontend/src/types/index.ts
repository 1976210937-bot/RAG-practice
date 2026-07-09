// 类型定义文件
// 用户信息类型
export interface User {
  id: number
  username: string
  email: string | null
  role: 'admin' | 'user'
  is_active: boolean
  created_at: string
}

// 登录响应类型
export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

// 文档类型
export interface Document {
  id: number
  title: string
  file_name: string | null
  file_type: string | null
  file_size: number | null
  chunk_count: number
  status: 'pending' | 'processing' | 'completed' | 'failed'
  uploader_id: number
  uploader_name: string | null
  created_at: string
  updated_at: string
}

// 文档列表响应
export interface DocumentListResponse {
  total: number
  items: Document[]
}

// 会话类型
export interface Conversation {
  id: number
  title: string
  user_id: number
  created_at: string
  updated_at: string
}

// 聊天消息类型
export interface ChatMessage {
  id: number
  conversation_id: int
  role: 'user' | 'assistant'
  content: string
  sources: string | null
  created_at: string
}

// 来源文档类型
export interface SourceDocument {
  document_id: number
  title: string
  content: string
  score: number
}

// 问答响应类型
export interface QueryResponse {
  answer: string
  conversation_id: number
  sources: SourceDocument[]
}

// 仪表盘统计数据类型
export interface DashboardStats {
  user_count: number
  document_count: number
  conversation_count: number
  message_count: number
  today_new_users: number
  today_new_documents: number
  today_new_conversations: number
  today_new_messages: number
}
