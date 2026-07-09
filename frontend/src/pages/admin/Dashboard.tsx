// 管理后台 - 数据概览仪表盘页面
import { useState, useEffect } from 'react'
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  PieChart,
  Pie,
  Cell,
  Legend
} from 'recharts'
import {
  Users,
  FileText,
  MessageSquare,
  MessageCircle,
  TrendingUp,
  UserPlus,
  Upload,
  Activity
} from 'lucide-react'
import { getDashboardStats } from '../../api'
import type { DashboardStats } from '../../types'

const AdminDashboard = () => {
  const [stats, setStats] = useState<DashboardStats | null>(null)
  const [loading, setLoading] = useState(true)

  // 加载统计数据
  const loadStats = async () => {
    setLoading(true)
    try {
      const data = await getDashboardStats() as DashboardStats
      setStats(data)
    } catch (err) {
      console.error('加载统计数据失败:', err)
    } finally {
      setLoading(false)
    }
  }

  useEffect(() => {
    loadStats()
  }, [])

  // 饼图颜色
  const COLORS = ['#3b82f6', '#10b981', '#f59e0b', '#ef4444']

  // 今日数据饼图
  const todayPieData = stats ? [
    { name: '新增用户', value: stats.today_new_users, color: '#3b82f6' },
    { name: '新增文档', value: stats.today_new_documents, color: '#10b981' },
    { name: '新会话', value: stats.today_new_conversations, color: '#f59e0b' },
    { name: '新消息', value: stats.today_new_messages, color: '#ef4444' },
  ] : []

  // 总数柱状图数据
  const totalBarData = stats ? [
    { name: '用户', count: stats.user_count, today: stats.today_new_users },
    { name: '文档', count: stats.document_count, today: stats.today_new_documents },
    { name: '会话', count: stats.conversation_count, today: stats.today_new_conversations },
    { name: '消息', count: stats.message_count, today: stats.today_new_messages },
  ] : []

  // 统计卡片数据
  const statCards = stats ? [
    {
      title: '用户总数',
      value: stats.user_count,
      today: stats.today_new_users,
      icon: Users,
      color: 'bg-blue-500',
      bgColor: 'bg-blue-50',
      textColor: 'text-blue-600',
    },
    {
      title: '文档总数',
      value: stats.document_count,
      today: stats.today_new_documents,
      icon: FileText,
      color: 'bg-green-500',
      bgColor: 'bg-green-50',
      textColor: 'text-green-600',
    },
    {
      title: '会话总数',
      value: stats.conversation_count,
      today: stats.today_new_conversations,
      icon: MessageSquare,
      color: 'bg-amber-500',
      bgColor: 'bg-amber-50',
      textColor: 'text-amber-600',
    },
    {
      title: '消息总数',
      value: stats.message_count,
      today: stats.today_new_messages,
      icon: MessageCircle,
      color: 'bg-rose-500',
      bgColor: 'bg-rose-50',
      textColor: 'text-rose-600',
    },
  ] : []

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96">
        <div className="text-center">
          <div className="inline-block w-10 h-10 border-4 border-blue-600 border-t-transparent rounded-full animate-spin" />
          <p className="text-gray-500 mt-4">加载中...</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      {/* 页面标题 */}
      <div className="mb-6">
        <h1 className="text-2xl font-bold text-gray-800">数据概览</h1>
        <p className="text-gray-500 mt-1">查看系统整体运行数据统计</p>
      </div>

      {/* 统计卡片 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
        {statCards.map((card, index) => {
          const Icon = card.icon
          return (
            <div
              key={index}
              className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100"
            >
              <div className="flex items-start justify-between">
                <div>
                  <p className="text-sm text-gray-500 mb-1">{card.title}</p>
                  <p className="text-3xl font-bold text-gray-800">{card.value}</p>
                  <div className="flex items-center mt-2 text-sm">
                    <TrendingUp className="w-4 h-4 text-green-500 mr-1" />
                    <span className="text-gray-500">
                      今日新增 <span className={card.textColor + ' font-medium'}>{card.today}</span>
                    </span>
                  </div>
                </div>
                <div className={`w-12 h-12 ${card.bgColor} rounded-xl flex items-center justify-center`}>
                  <Icon className={`w-6 h-6 ${card.textColor}`} />
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {/* 图表区域 */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 总数柱状图 */}
        <div className="lg:col-span-2 bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2 mb-6">
            <Activity className="w-5 h-5 text-blue-600" />
            <h2 className="text-lg font-semibold text-gray-800">数据总量统计</h2>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={totalBarData} margin={{ top: 10, right: 30, left: 0, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#f0f0f0" />
                <XAxis dataKey="name" tick={{ fill: '#6b7280', fontSize: 13 }} />
                <YAxis tick={{ fill: '#6b7280', fontSize: 13 }} />
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                    boxShadow: '0 4px 6px -1px rgba(0,0,0,0.1)'
                  }}
                />
                <Legend />
                <Bar dataKey="count" name="总数" fill="#3b82f6" radius={[4, 4, 0, 0]} />
                <Bar dataKey="today" name="今日新增" fill="#10b981" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* 今日数据饼图 */}
        <div className="bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
          <div className="flex items-center gap-2 mb-6">
            <UserPlus className="w-5 h-5 text-green-600" />
            <h2 className="text-lg font-semibold text-gray-800">今日新增占比</h2>
          </div>
          <div className="h-72">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={todayPieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={50}
                  outerRadius={80}
                  paddingAngle={2}
                  dataKey="value"
                >
                  {todayPieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '8px',
                  }}
                />
                <Legend
                  verticalAlign="bottom"
                  height={36}
                  formatter={(value) => <span className="text-sm text-gray-600">{value}</span>}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* 快捷操作 */}
      <div className="mt-8 bg-white rounded-2xl p-6 shadow-sm border border-gray-100">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">快捷操作</h2>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
          <button className="flex flex-col items-center justify-center p-5 bg-blue-50 rounded-xl hover:bg-blue-100 transition-colors">
            <Upload className="w-8 h-8 text-blue-600 mb-2" />
            <span className="text-sm font-medium text-blue-700">上传文档</span>
          </button>
          <button className="flex flex-col items-center justify-center p-5 bg-green-50 rounded-xl hover:bg-green-100 transition-colors">
            <UserPlus className="w-8 h-8 text-green-600 mb-2" />
            <span className="text-sm font-medium text-green-700">添加用户</span>
          </button>
          <button className="flex flex-col items-center justify-center p-5 bg-amber-50 rounded-xl hover:bg-amber-100 transition-colors">
            <FileText className="w-8 h-8 text-amber-600 mb-2" />
            <span className="text-sm font-medium text-amber-700">文档管理</span>
          </button>
          <button className="flex flex-col items-center justify-center p-5 bg-rose-50 rounded-xl hover:bg-rose-100 transition-colors">
            <Users className="w-8 h-8 text-rose-600 mb-2" />
            <span className="text-sm font-medium text-rose-700">用户管理</span>
          </button>
        </div>
      </div>
    </div>
  )
}

export default AdminDashboard
