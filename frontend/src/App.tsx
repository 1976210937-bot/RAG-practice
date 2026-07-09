// 应用主组件
import { Routes, Route, Navigate } from 'react-router-dom'
import Login from './pages/Login'
import ChatLayout from './layouts/ChatLayout'
import AdminLayout from './layouts/AdminLayout'
import ChatPage from './pages/ChatPage'
import DocumentsPage from './pages/DocumentsPage'
import AdminDashboard from './pages/admin/Dashboard'
import AdminUsers from './pages/admin/Users'
import AdminDocuments from './pages/admin/Documents'
import { getStoredUser } from './api'

// 受保护的路由组件
const ProtectedRoute = ({ children, requireAdmin = false }: { children: JSX.Element; requireAdmin?: boolean }) => {
  const user = getStoredUser()
  
  if (!user) {
    return <Navigate to="/login" replace />
  }
  
  if (requireAdmin && user.role !== 'admin') {
    return <Navigate to="/chat" replace />
  }
  
  return children
}

function App() {
  return (
    <Routes>
      {/* 登录页 */}
      <Route path="/login" element={<Login />} />
      
      {/* 用户端 - 问答页面 */}
      <Route
        path="/chat"
        element={
          <ProtectedRoute>
            <ChatLayout>
              <ChatPage />
            </ChatLayout>
          </ProtectedRoute>
        }
      />
      
      {/* 用户端 - 文档列表 */}
      <Route
        path="/documents"
        element={
          <ProtectedRoute>
            <ChatLayout>
              <DocumentsPage />
            </ChatLayout>
          </ProtectedRoute>
        }
      />
      
      {/* 管理后台 - 仪表盘 */}
      <Route
        path="/admin"
        element={
          <ProtectedRoute requireAdmin>
            <AdminLayout>
              <AdminDashboard />
            </AdminLayout>
          </ProtectedRoute>
        }
      />
      
      {/* 管理后台 - 用户管理 */}
      <Route
        path="/admin/users"
        element={
          <ProtectedRoute requireAdmin>
            <AdminLayout>
              <AdminUsers />
            </AdminLayout>
          </ProtectedRoute>
        }
      />
      
      {/* 管理后台 - 文档管理 */}
      <Route
        path="/admin/documents"
        element={
          <ProtectedRoute requireAdmin>
            <AdminLayout>
              <AdminDocuments />
            </AdminLayout>
          </ProtectedRoute>
        }
      />
      
      {/* 默认重定向 */}
      <Route path="/" element={<Navigate to="/chat" replace />} />
      <Route path="*" element={<Navigate to="/chat" replace />} />
    </Routes>
  )
}

export default App
