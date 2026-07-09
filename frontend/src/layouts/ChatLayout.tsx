// 用户端布局组件
import { useState } from 'react'
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { MessageSquare, FileText, LogOut, User, Menu, X } from 'lucide-react'
import { getStoredUser, clearStoredUser } from '../api'

interface ChatLayoutProps {
  children: React.ReactNode
}

const ChatLayout = ({ children }: ChatLayoutProps) => {
  const location = useLocation()
  const navigate = useNavigate()
  const user = getStoredUser()
  const [sidebarOpen, setSidebarOpen] = useState(true)

  // 处理退出登录
  const handleLogout = () => {
    clearStoredUser()
    navigate('/login')
  }

  // 导航菜单
  const menuItems = [
    { path: '/chat', label: '智能问答', icon: MessageSquare },
    { path: '/documents', label: '文档中心', icon: FileText },
  ]

  // 如果是管理员，显示管理后台入口
  const isAdmin = user?.role === 'admin'

  return (
    <div className="h-screen flex bg-gray-50">
      {/* 侧边栏 */}
      <div className={`${sidebarOpen ? 'w-64' : 'w-0'} bg-white border-r border-gray-200 flex flex-col transition-all duration-300 overflow-hidden`}>
        {/* Logo区域 */}
        <div className="h-16 flex items-center px-5 border-b border-gray-100">
          <div className="w-8 h-8 bg-blue-600 rounded-lg flex items-center justify-center">
            <MessageSquare className="w-5 h-5 text-white" />
          </div>
          <span className="ml-3 font-bold text-gray-800">知识库问答</span>
        </div>

        {/* 导航菜单 */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname.startsWith(item.path)
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-50 text-blue-600'
                    : 'text-gray-600 hover:bg-gray-50 hover:text-gray-900'
                }`}
              >
                <Icon className="w-5 h-5 mr-3" />
                {item.label}
              </Link>
            )
          })}

          {/* 管理后台入口 */}
          {isAdmin && (
            <Link
              to="/admin"
              className="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium text-gray-600 hover:bg-gray-50 hover:text-gray-900 transition-colors"
            >
              <svg className="w-5 h-5 mr-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10.325 4.317c.426-1.756 2.924-1.756 3.35 0a1.724 1.724 0 002.573 1.066c1.543-.94 3.31.826 2.37 2.37a1.724 1.724 0 001.065 2.572c1.756.426 1.756 2.924 0 3.35a1.724 1.724 0 00-1.066 2.573c.94 1.543-.826 3.31-2.37 2.37a1.724 1.724 0 00-2.572 1.065c-.426 1.756-2.924 1.756-3.35 0a1.724 1.724 0 00-2.573-1.066c-1.543.94-3.31-.826-2.37-2.37a1.724 1.724 0 00-1.065-2.572c-1.756-.426-1.756-2.924 0-3.35a1.724 1.724 0 001.066-2.573c-.94-1.543.826-3.31 2.37-2.37.996.608 2.296.07 2.572-1.065z" />
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
              </svg>
              管理后台
            </Link>
          )}
        </nav>

        {/* 用户信息 */}
        <div className="border-t border-gray-100 p-4">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-gray-200 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-gray-500" />
            </div>
            <div className="ml-3 flex-1 min-w-0">
              <p className="text-sm font-medium text-gray-900 truncate">
                {user?.username}
              </p>
              <p className="text-xs text-gray-500">
                {user?.role === 'admin' ? '管理员' : '普通用户'}
              </p>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 text-gray-400 hover:text-red-500 hover:bg-red-50 rounded-lg transition-colors"
              title="退出登录"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* 顶部栏 */}
        <header className="h-16 bg-white border-b border-gray-200 flex items-center px-4">
          <button
            onClick={() => setSidebarOpen(!sidebarOpen)}
            className="p-2 text-gray-500 hover:bg-gray-100 rounded-lg transition-colors"
          >
            {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
          </button>
          <div className="ml-4">
            <h1 className="text-lg font-semibold text-gray-800">
              {location.pathname.startsWith('/chat') && '智能问答'}
              {location.pathname.startsWith('/documents') && '文档中心'}
            </h1>
          </div>
        </header>

        {/* 内容区 */}
        <main className="flex-1 overflow-hidden">
          {children}
        </main>
      </div>
    </div>
  )
}

export default ChatLayout
