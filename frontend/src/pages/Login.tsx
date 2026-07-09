// 登录页面组件
import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login, register, setStoredUser } from '../api'
import type { LoginResponse } from '../types'

const Login = () => {
  const navigate = useNavigate()
  const [username, setUsername] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const [isRegister, setIsRegister] = useState(false)
  const [email, setEmail] = useState('')

  // 处理登录
  const handleLogin = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    if (!username || !password) {
      setError('请输入用户名和密码')
      return
    }
    
    setLoading(true)
    try {
      const result = await login(username, password) as LoginResponse
      localStorage.setItem('token', result.access_token)
      setStoredUser(result.user)
      
      // 根据角色跳转
      if (result.user.role === 'admin') {
        navigate('/admin')
      } else {
        navigate('/chat')
      }
    } catch (err: any) {
      setError(err.response?.data?.detail || '登录失败，请检查用户名和密码')
    } finally {
      setLoading(false)
    }
  }

  // 处理注册
  const handleRegister = async (e: React.FormEvent) => {
    e.preventDefault()
    setError('')
    
    if (!username || !password) {
      setError('请输入用户名和密码')
      return
    }
    
    if (password.length < 6) {
      setError('密码长度不能少于6位')
      return
    }
    
    setLoading(true)
    try {
      await register(username, password, email)
      // 注册成功后自动登录
      const result = await login(username, password) as LoginResponse
      localStorage.setItem('token', result.access_token)
      setStoredUser(result.user)
      navigate('/chat')
    } catch (err: any) {
      setError(err.response?.data?.detail || '注册失败')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 flex items-center justify-center p-4">
      <div className="w-full max-w-md">
        {/* Logo和标题 */}
        <div className="text-center mb-8">
          <div className="inline-flex items-center justify-center w-16 h-16 bg-blue-600 rounded-2xl mb-4">
            <svg className="w-8 h-8 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6.253v13m0-13C10.832 5.477 9.246 5 7.5 5S4.168 5.477 3 6.253v13C4.168 18.477 5.754 18 7.5 18s3.332.477 4.5 1.253m0-13C13.168 5.477 14.754 5 16.5 5c1.747 0 3.332.477 4.5 1.253v13C19.832 18.477 18.247 18 16.5 18c-1.746 0-3.332.477-4.5 1.253" />
            </svg>
          </div>
          <h1 className="text-2xl font-bold text-gray-800">企业知识库问答系统</h1>
          <p className="text-gray-500 mt-2">
            {isRegister ? '创建新账号' : '欢迎回来，请登录您的账号'}
          </p>
        </div>

        {/* 登录表单 */}
        <div className="bg-white rounded-2xl shadow-xl p-8">
          <form onSubmit={isRegister ? handleRegister : handleLogin}>
            {error && (
              <div className="mb-4 p-3 bg-red-50 border border-red-200 text-red-600 rounded-lg text-sm">
                {error}
              </div>
            )}

            <div className="mb-4">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                用户名
              </label>
              <input
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none"
                placeholder="请输入用户名"
                disabled={loading}
              />
            </div>

            {isRegister && (
              <div className="mb-4">
                <label className="block text-sm font-medium text-gray-700 mb-2">
                  邮箱（可选）
                </label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none"
                  placeholder="请输入邮箱"
                  disabled={loading}
                />
              </div>
            )}

            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-700 mb-2">
                密码
              </label>
              <input
                type="password"
                value={password}
                onChange={(e) => setPassword(e.target.value)}
                className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent transition-all outline-none"
                placeholder="请输入密码"
                disabled={loading}
              />
            </div>

            <button
              type="submit"
              disabled={loading}
              className="w-full py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 focus:ring-4 focus:ring-blue-200 transition-all disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? '处理中...' : isRegister ? '注册' : '登录'}
            </button>
          </form>

          <div className="mt-6 text-center">
            <span className="text-gray-500 text-sm">
              {isRegister ? '已有账号？' : '没有账号？'}
            </span>
            <button
              onClick={() => {
                setIsRegister(!isRegister)
                setError('')
              }}
              className="text-blue-600 text-sm font-medium hover:underline ml-1"
            >
              {isRegister ? '去登录' : '去注册'}
            </button>
          </div>

          {/* 默认账号提示 */}
          {!isRegister && (
            <div className="mt-6 pt-6 border-t border-gray-100">
              <p className="text-xs text-gray-400 text-center">
                默认管理员账号：admin / 123456
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  )
}

export default Login
