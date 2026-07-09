// 管理后台布局组件
import { Link, useLocation, useNavigate } from 'react-router-dom'
import { LayoutDashboard, Users, FileText, LogOut, User, ArrowLeft } from 'lucide-react'
import { getStoredUser, clearStoredUser } from '../api'

interface AdminLayoutProps {
  children: React.ReactNode
}

const AdminLayout = ({ children }: AdminLayoutProps) => {
  const location = useLocation()
  const navigate = useNavigate()
  const user = getStoredUser()

  // 处理退出登录
  const handleLogout = () => {
    clearStoredUser()
    navigate('/login')
  }

  // 导航菜单
  const menuItems = [
    { path: '/admin', label: '数据概览', icon: LayoutDashboard },
    { path: '/admin/users', label: '用户管理', icon: Users },
    { path: '/admin/documents', label: '文档管理', icon: FileText },
  ]

  return (
    <div className="h-screen flex bg-gray-100">
      {/* 侧边栏 */}
      <div className="w-64 bg-slate-800 flex flex-col">
        {/* Logo区域 */}
        <div className="h-16 flex items-center px-5 border-b border-slate-700">
          <div className="w-8 h-8 bg-blue-500 rounded-lg flex items-center justify-center">
            <LayoutDashboard className="w-5 h-5 text-white" />
          </div>
          <span className="ml-3 font-bold text-white">管理后台</span>
        </div>

        {/* 导航菜单 */}
        <nav className="flex-1 px-3 py-4 space-y-1">
          {menuItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center px-4 py-2.5 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-blue-600 text-white'
                    : 'text-slate-300 hover:bg-slate-700 hover:text-white'
                }`}
              >
                <Icon className="w-5 h-5 mr-3" />
                {item.label}
              </Link>
            )
          })}

          {/* 返回前台 */}
          <Link
            to="/chat"
            className="flex items-center px-4 py-2.5 rounded-lg text-sm font-medium text-slate-300 hover:bg-slate-700 hover:text-white transition-colors mt-8"
          >
            <ArrowLeft className="w-5 h-5 mr-3" />
            返回前台
          </Link>
        </nav>

        {/* 用户信息 */}
        <div className="border-t border-slate-700 p-4">
          <div className="flex items-center">
            <div className="w-10 h-10 bg-slate-600 rounded-full flex items-center justify-center">
              <User className="w-5 h-5 text-slate-300" />
            </div>
            <div className="ml-3 flex-1 min-w-0">
              <p className="text-sm font-medium text-white truncate">
                {user?.username}
              </p>
              <p className="text-xs text-slate-400">管理员</p>
            </div>
            <button
              onClick={handleLogout}
              className="p-2 text-slate-400 hover:text-red-400 hover:bg-red-900/30 rounded-lg transition-colors"
              title="退出登录"
            >
              <LogOut className="w-5 h-5" />
            </button>
          </div>
        </div>
      </div>

      {/* 主内容区 */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* 内容区 */}
        <main className="flex-1 overflow-auto p-6">
          {children}
        </main>
      </div>
    </div>
  )
}

export default AdminLayout
