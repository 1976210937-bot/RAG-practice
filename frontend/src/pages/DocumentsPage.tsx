// 文档中心页面组件
import { useState, useEffect } from 'react'
import { Search, FileText, Clock, Database } from 'lucide-react'
import { getDocuments } from '../api'
import type { Document } from '../types'

const DocumentsPage = () => {
  const [documents, setDocuments] = useState<Document[]>([])
  const [total, setTotal] = useState(0)
  const [page, setPage] = useState(1)
  const [pageSize] = useState(10)
  const [keyword, setKeyword] = useState('')
  const [loading, setLoading] = useState(false)

  // 加载文档列表
  const loadDocuments = async () => {
    setLoading(true)
    try {
      const data = await getDocuments(page, pageSize, keyword) as any
      setDocuments(data.items)
      setTotal(data.total)
    } catch (err) {
      console.error('加载文档列表失败:', err)
    } finally {
      setLoading(false)
    }
  }

  // 初始化
  useEffect(() => {
    loadDocuments()
  }, [page])

  // 搜索
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    setPage(1)
    loadDocuments()
  }

  // 格式化文件大小
  const formatFileSize = (bytes: number | null) => {
    if (!bytes) return '-'
    if (bytes < 1024) return bytes + ' B'
    if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
    return (bytes / (1024 * 1024)).toFixed(2) + ' MB'
  }

  // 格式化日期
  const formatDate = (dateStr: string) => {
    return new Date(dateStr).toLocaleString('zh-CN')
  }

  // 获取状态标签
  const getStatusBadge = (status: string) => {
    const statusMap: Record<string, { text: string; className: string }> = {
      pending: { text: '待处理', className: 'bg-yellow-100 text-yellow-700' },
      processing: { text: '处理中', className: 'bg-blue-100 text-blue-700' },
      completed: { text: '已完成', className: 'bg-green-100 text-green-700' },
      failed: { text: '失败', className: 'bg-red-100 text-red-700' },
    }
    const s = statusMap[status] || { text: status, className: 'bg-gray-100 text-gray-700' }
    return (
      <span className={`px-2 py-0.5 rounded-full text-xs font-medium ${s.className}`}>
        {s.text}
      </span>
    )
  }

  // 总页数
  const totalPages = Math.ceil(total / pageSize)

  return (
    <div className="h-full overflow-y-auto p-6">
      <div className="max-w-6xl mx-auto">
        {/* 页面标题 */}
        <div className="mb-6">
          <h1 className="text-2xl font-bold text-gray-800">文档中心</h1>
          <p className="text-gray-500 mt-1">浏览和搜索知识库中的文档</p>
        </div>

        {/* 搜索栏 */}
        <form onSubmit={handleSearch} className="mb-6">
          <div className="relative">
            <Search className="absolute left-4 top-1/2 -translate-y-1/2 w-5 h-5 text-gray-400" />
            <input
              type="text"
              value={keyword}
              onChange={(e) => setKeyword(e.target.value)}
              placeholder="搜索文档标题..."
              className="w-full pl-12 pr-4 py-3 bg-white border border-gray-200 rounded-xl focus:ring-2 focus:ring-blue-100 focus:border-blue-400 outline-none transition-all"
            />
          </div>
        </form>

        {/* 文档列表 */}
        {loading ? (
          <div className="text-center py-12">
            <div className="inline-block w-8 h-8 border-2 border-blue-600 border-t-transparent rounded-full animate-spin" />
            <p className="text-gray-500 mt-4">加载中...</p>
          </div>
        ) : documents.length === 0 ? (
          <div className="text-center py-16 bg-white rounded-2xl border border-gray-200">
            <FileText className="w-16 h-16 text-gray-300 mx-auto mb-4" />
            <p className="text-gray-500">暂无文档</p>
          </div>
        ) : (
          <div className="space-y-3">
            {documents.map((doc) => (
              <div
                key={doc.id}
                className="bg-white border border-gray-200 rounded-xl p-5 hover:shadow-md transition-shadow"
              >
                <div className="flex items-start gap-4">
                  {/* 图标 */}
                  <div className="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center flex-shrink-0">
                    <FileText className="w-6 h-6 text-blue-600" />
                  </div>

                  {/* 内容 */}
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-3 mb-1">
                      <h3 className="text-lg font-medium text-gray-900 truncate">
                        {doc.title}
                      </h3>
                      {getStatusBadge(doc.status)}
                    </div>
                    <p className="text-sm text-gray-500 truncate">
                      {doc.file_name || '无文件名'}
                    </p>
                    <div className="flex items-center gap-4 mt-3 text-xs text-gray-400">
                      <span className="flex items-center gap-1">
                        <Database className="w-3.5 h-3.5" />
                        {doc.chunk_count} 个文本块
                      </span>
                      <span className="flex items-center gap-1">
                        <Clock className="w-3.5 h-3.5" />
                        {formatDate(doc.created_at)}
                      </span>
                      <span>上传者：{doc.uploader_name || '-'}</span>
                      <span>大小：{formatFileSize(doc.file_size)}</span>
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}

        {/* 分页 */}
        {totalPages > 1 && (
          <div className="flex justify-center items-center gap-2 mt-8">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-4 py-2 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              上一页
            </button>
            <span className="text-sm text-gray-500">
              第 {page} / {totalPages} 页，共 {total} 条
            </span>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-4 py-2 border border-gray-200 rounded-lg text-sm text-gray-600 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              下一页
            </button>
          </div>
        )}
      </div>
    </div>
  )
}

export default DocumentsPage
