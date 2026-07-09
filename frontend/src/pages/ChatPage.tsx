// 智能问答页面组件
import { useState, useEffect, useRef } from 'react'
import { Send, Plus, Trash2, MessageCircle, Loader2 } from 'lucide-react'
import {
  getConversations,
  createConversation,
  deleteConversation,
  getConversationMessages,
  queryChat
} from '../api'
import type { Conversation, ChatMessage, SourceDocument } from '../types'

const ChatPage = () => {
  const [conversations, setConversations] = useState<Conversation[]>([])
  const [currentConversationId, setCurrentConversationId] = useState<number | null>(null)
  const [messages, setMessages] = useState<ChatMessage[]>([])
  const [inputValue, setInputValue] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // 加载会话列表
  const loadConversations = async () => {
    try {
      const data = await getConversations() as Conversation[]
      setConversations(data)
    } catch (err) {
      console.error('加载会话列表失败:', err)
    }
  }

  // 加载会话消息
  const loadMessages = async (convId: number) => {
    try {
      const data = await getConversationMessages(convId) as ChatMessage[]
      setMessages(data)
      setCurrentConversationId(convId)
    } catch (err) {
      console.error('加载消息失败:', err)
    }
  }

  // 初始化
  useEffect(() => {
    loadConversations()
  }, [])

  // 滚动到底部
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // 新建会话
  const handleNewConversation = async () => {
    try {
      const conv = await createConversation('新对话') as Conversation
      setConversations([conv, ...conversations])
      setCurrentConversationId(conv.id)
      setMessages([])
    } catch (err) {
      console.error('创建会话失败:', err)
    }
  }

  // 删除会话
  const handleDeleteConversation = async (convId: number, e: React.MouseEvent) => {
    e.stopPropagation()
    if (!confirm('确定要删除这个会话吗？')) return
    try {
      await deleteConversation(convId)
      setConversations(conversations.filter(c => c.id !== convId))
      if (currentConversationId === convId) {
        setCurrentConversationId(null)
        setMessages([])
      }
    } catch (err) {
      console.error('删除会话失败:', err)
    }
  }

  // 发送消息
  const handleSend = async () => {
    if (!inputValue.trim() || loading) return

    const question = inputValue.trim()
    setInputValue('')
    setLoading(true)

    // 临时添加用户消息
    const tempUserMsg: ChatMessage = {
      id: Date.now(),
      conversation_id: currentConversationId || 0,
      role: 'user',
      content: question,
      sources: null,
      created_at: new Date().toISOString()
    }
    setMessages([...messages, tempUserMsg])

    try {
      const result = await queryChat(question, currentConversationId || undefined) as any
      
      // 添加助手消息
      const assistantMsg: ChatMessage = {
        id: Date.now() + 1,
        conversation_id: result.conversation_id,
        role: 'assistant',
        content: result.answer,
        sources: JSON.stringify(result.sources || []),
        created_at: new Date().toISOString()
      }
      
      setMessages(prev => [...prev.filter(m => m.id !== tempUserMsg.id), assistantMsg])
      
      // 如果是新会话，刷新会话列表
      if (!currentConversationId) {
        setCurrentConversationId(result.conversation_id)
        loadConversations()
      } else {
        // 重新加载消息以获得正确的ID
        loadMessages(result.conversation_id)
      }
    } catch (err: any) {
      console.error('发送消息失败:', err)
      // 移除临时消息，添加错误提示
      setMessages(prev => prev.filter(m => m.id !== tempUserMsg.id))
      alert('发送失败，请稍后重试')
    } finally {
      setLoading(false)
    }
  }

  // 回车发送
  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault()
      handleSend()
    }
  }

  // 解析来源文档
  const parseSources = (sources: string | null): SourceDocument[] => {
    if (!sources) return []
    try {
      return JSON.parse(sources)
    } catch {
      return []
    }
  }

  return (
    <div className="h-full flex">
      {/* 左侧会话列表 */}
      <div className="w-64 bg-white border-r border-gray-200 flex flex-col">
        <div className="p-4">
          <button
            onClick={handleNewConversation}
            className="w-full flex items-center justify-center gap-2 px-4 py-2.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors"
          >
            <Plus className="w-5 h-5" />
            新建对话
          </button>
        </div>

        <div className="flex-1 overflow-y-auto px-3 pb-4 space-y-1">
          {conversations.length === 0 ? (
            <div className="text-center text-gray-400 text-sm py-8">
              暂无对话，点击上方按钮开始
            </div>
          ) : (
            conversations.map((conv) => (
              <div
                key={conv.id}
                onClick={() => loadMessages(conv.id)}
                className={`group flex items-center px-3 py-2.5 rounded-lg cursor-pointer transition-colors ${
                  currentConversationId === conv.id
                    ? 'bg-blue-50 text-blue-600'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <MessageCircle className="w-4 h-4 mr-2 flex-shrink-0" />
                <span className="flex-1 truncate text-sm">{conv.title}</span>
                <button
                  onClick={(e) => handleDeleteConversation(conv.id, e)}
                  className="opacity-0 group-hover:opacity-100 p-1 text-gray-400 hover:text-red-500 transition-all"
                >
                  <Trash2 className="w-4 h-4" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>

      {/* 右侧聊天区域 */}
      <div className="flex-1 flex flex-col bg-gray-50">
        {/* 消息区域 */}
        <div className="flex-1 overflow-y-auto p-6">
          {messages.length === 0 ? (
            <div className="h-full flex flex-col items-center justify-center text-center">
              <div className="w-20 h-20 bg-blue-100 rounded-full flex items-center justify-center mb-6">
                <MessageCircle className="w-10 h-10 text-blue-600" />
              </div>
              <h2 className="text-2xl font-bold text-gray-800 mb-2">企业知识库助手</h2>
              <p className="text-gray-500 max-w-md">
                您好！我是您的企业知识库智能助手，您可以向我询问任何关于企业知识库的问题。
              </p>
            </div>
          ) : (
            <div className="max-w-4xl mx-auto space-y-6">
              {messages.map((msg) => (
                <div
                  key={msg.id}
                  className={`flex ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div className={`max-w-3xl ${msg.role === 'user' ? 'order-2' : 'order-1'}`}>
                    <div
                      className={`px-4 py-3 rounded-2xl whitespace-pre-wrap ${
                        msg.role === 'user'
                          ? 'bg-blue-600 text-white rounded-br-md'
                          : 'bg-white text-gray-800 border border-gray-200 rounded-bl-md shadow-sm'
                      }`}
                    >
                      {msg.content}
                    </div>
                    
                    {/* 引用来源 */}
                    {msg.role === 'assistant' && parseSources(msg.sources).length > 0 && (
                      <div className="mt-2 flex flex-wrap gap-2">
                        {parseSources(msg.sources).slice(0, 3).map((src, idx) => (
                          <span
                            key={idx}
                            className="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded"
                          >
                            来源：{src.title}
                          </span>
                        ))}
                      </div>
                    )}
                  </div>
                </div>
              ))}
              
              {/* 加载中提示 */}
              {loading && (
                <div className="flex justify-start">
                  <div className="px-4 py-3 bg-white border border-gray-200 rounded-2xl rounded-bl-md shadow-sm">
                    <Loader2 className="w-5 h-5 text-blue-600 animate-spin" />
                  </div>
                </div>
              )}
              
              <div ref={messagesEndRef} />
            </div>
          )}
        </div>

        {/* 输入区域 */}
        <div className="border-t border-gray-200 bg-white p-4">
          <div className="max-w-4xl mx-auto">
            <div className="flex items-end gap-3 bg-gray-50 rounded-2xl border border-gray-200 p-2 focus-within:border-blue-400 focus-within:ring-2 focus-within:ring-blue-100 transition-all">
              <textarea
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                onKeyDown={handleKeyDown}
                placeholder="请输入您的问题..."
                rows={1}
                className="flex-1 bg-transparent px-3 py-2 resize-none outline-none text-gray-800 placeholder-gray-400 max-h-32"
                style={{ minHeight: '40px' }}
              />
              <button
                onClick={handleSend}
                disabled={!inputValue.trim() || loading}
                className="p-2.5 bg-blue-600 text-white rounded-xl hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
              >
                {loading ? (
                  <Loader2 className="w-5 h-5 animate-spin" />
                ) : (
                  <Send className="w-5 h-5" />
                )}
              </button>
            </div>
            <p className="text-xs text-gray-400 text-center mt-2">
              按 Enter 发送，Shift + Enter 换行
            </p>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatPage
