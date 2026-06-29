import { useRef, useState, useEffect } from 'react'
import { Building2, RefreshCw, Search, FileText, Building as BuildingIcon, Star } from 'lucide-react'
import { useApi } from '../../hooks/useApi'
import { api } from '../../services/api'
import { SourcingForm } from './SourcingForm'
import { SupplierTable } from './SupplierTable'
import { SupplierCard } from './SupplierCard'
import { SupplierDetailModal } from './SupplierDetailModal'
import { InterviewGenerator } from './InterviewGenerator'

export function SupplierFinder() {
  const [viewMode, setViewMode] = useState('table') // 'table' | 'card'
  const [selectedSuppliers, setSelectedSuppliers] = useState([])
  const [selectedSupplier, setSelectedSupplier] = useState(null)
  const [sourcingResult, setSourcingResult] = useState(null)
  const [searchProgress, setSearchProgress] = useState(0)
  const interviewGeneratorRef = useRef(null)

  const { data, loading, error, execute: doSourcing } = useApi(api.sourcing)

  // 分阶段进度指示器
  useEffect(() => {
    if (loading) {
      setSearchProgress(0)
      const timer = setInterval(() => {
        setSearchProgress(prev => {
          if (prev >= 3) return 3
          return prev + 1
        })
      }, 8000) // 每 8 秒进入下一阶段
      return () => clearInterval(timer)
    } else {
      setSearchProgress(0)
    }
  }, [loading])

  const progressStages = [
    { icon: Search, title: '搜索供应商', desc: '正在检索相关供应商' },
    { icon: FileText, title: '整理结果', desc: '正在整理供应商信息' },
    { icon: BuildingIcon, title: '查询企业信息', desc: '正在查询企业资质' },
    { icon: Star, title: '生成列表', desc: '正在排序并生成结果' }
  ]

  const handleSourcing = async (requestData) => {
    const result = await doSourcing(requestData)
    if (result) {
      setSourcingResult(result)
      setSelectedSuppliers([])
    }
  }

  const handleReset = () => {
    setSourcingResult(null)
    setSelectedSuppliers([])
  }

  const scrollToInterviewGenerator = () => {
    interviewGeneratorRef.current?.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }

  const suppliers = data?.suppliers || sourcingResult?.suppliers || []
  const material = data?.material || sourcingResult?.material || null
  const searchDetails = data?.search_details || sourcingResult?.search_details || null

  return (
    <div className="space-y-6">
      {/* 标题栏 */}
      <div className="flex items-start justify-between gap-4 rounded-3xl border border-white/70 bg-white/65 p-5 shadow-soft backdrop-blur-xl">
        <div>
          <h1 className="text-2xl font-bold text-slate-950">供应商搜索</h1>
          <p className="text-slate-500 text-sm mt-2">搜索供应商，整理资质与面谈问题。</p>
        </div>
        {sourcingResult && (
          <button onClick={handleReset} className="btn btn-ghost shrink-0">
            <RefreshCw className="w-4 h-4 mr-1" />
            重新搜索
          </button>
        )}
      </div>

      {/* 搜索来源标签 */}
      {data?.search_sources && data.search_sources.length > 0 && (
        <div className="flex items-center gap-2 text-sm">
          <span className="text-gray-500">搜索来源:</span>
          {data.search_sources.map((source, i) => (
            <span key={i} className="px-2 py-0.5 bg-blue-100 text-blue-800 rounded text-xs">
              {source}
            </span>
          ))}
        </div>
      )}

              {/* 搜索详情提示 */}
              {searchDetails && !loading && (
                <div className="text-sm text-amber-700 bg-amber-50 border border-amber-200 rounded-xl px-4 py-3">
                  {searchDetails}
                </div>
              )}

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* 左侧：寻源表单 */}
        <div className="lg:col-span-1">
          <SourcingForm onSubmit={handleSourcing} loading={loading} />
        </div>

        {/* 右侧：结果展示 */}
        <div className="lg:col-span-2 space-y-6">
          {error && (
            <div className="card border-l-4 border-red-500">
              <p className="text-red-600">{error}</p>
            </div>
          )}

          {loading && (
            <div className="card relative overflow-hidden">
              <div className="pointer-events-none absolute right-0 top-0 h-32 w-32 rounded-full bg-blue-300/20 blur-2xl animate-breath" />
              <div className="relative flex items-center justify-center py-8 mb-6">
                <div className="h-14 w-14 rounded-full border-4 border-blue-200 border-t-cyan-500 shadow-glow animate-spin"></div>
              </div>
              <div className="space-y-3">
                {progressStages.map((stage, idx) => {
                  const StageIcon = stage.icon
                  const isActive = idx === searchProgress
                  const isCompleted = idx < searchProgress
                  const isPending = idx > searchProgress

                  return (
                    <div key={idx} className={`flex items-center gap-4 rounded-2xl border p-3 transition-all duration-300 ${
                      isActive ? 'border-cyan-200 bg-cyan-50/80 shadow-glow' :
                      isCompleted ? 'border-emerald-200 bg-emerald-50/80 shadow-sm' :
                      'border-white/60 bg-white/60'
                    }`}>
                      <div className={`w-8 h-8 rounded-full flex items-center justify-center ${
                        isCompleted ? 'bg-emerald-500 text-white' :
                        isActive ? 'bg-gradient-to-br from-blue-600 to-cyan-500 text-white shadow-glow' :
                        'bg-slate-200 text-slate-400'
                      }`}>
                        {isCompleted ? (
                          <span className="text-sm">✓</span>
                        ) : (
                          <StageIcon className="w-4 h-4" />
                        )}
                      </div>
                      <div className="flex-1">
                        <p className={`font-medium ${isActive ? 'text-blue-700' : isCompleted ? 'text-green-700' : 'text-gray-400'}`}>
                          {stage.title}
                        </p>
                        <p className={`text-sm ${isActive ? 'text-blue-600' : isCompleted ? 'text-green-600' : 'text-gray-400'}`}>
                          {stage.desc}
                        </p>
                      </div>
                      {isActive && (
                        <div className="flex gap-1">
                          <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0s' }}></span>
                          <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.1s' }}></span>
                          <span className="w-2 h-2 bg-cyan-400 rounded-full animate-bounce" style={{ animationDelay: '0.2s' }}></span>
                        </div>
                      )}
                    </div>
                  )
                })}
              </div>
              <p className="text-center text-sm text-gray-400 mt-4">
                预计需要 30-60 秒，请耐心等待...
              </p>
            </div>
          )}

          {!loading && suppliers.length > 0 && (
            <>
              {/* 视图切换 */}
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2">
                  <span className="text-gray-700 font-medium">
                    找到 {suppliers.length} 家供应商
                  </span>
                  {data?.material?.model && (
                    <span className="text-sm text-gray-500">
                      (针对 {data.material.model})
                    </span>
                  )}
                </div>
                <div className="flex items-center gap-1 rounded-xl border border-white/70 bg-white/55 p-1 shadow-inner shadow-blue-100/60">
                  <button
                    onClick={() => setViewMode('table')}
                    className={`rounded-lg px-3 py-1.5 text-sm font-medium ${viewMode === 'table' ? 'bg-white shadow text-gray-900' : 'text-gray-500'}`}
                  >
                    表格
                  </button>
                  <button
                    onClick={() => setViewMode('card')}
                    className={`rounded-lg px-3 py-1.5 text-sm font-medium ${viewMode === 'card' ? 'bg-white shadow text-gray-900' : 'text-gray-500'}`}
                  >
                    卡片
                  </button>
                </div>
              </div>

              {/* 供应商列表 */}
              {viewMode === 'table' ? (
                <SupplierTable
                  suppliers={suppliers}
                  selectedSuppliers={selectedSuppliers}
                  onSelectChange={setSelectedSuppliers}
                  onGenerateInterview={scrollToInterviewGenerator}
                />
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {suppliers.map((supplier, index) => (
                    <SupplierCard
                      key={index}
                      supplier={supplier}
                      onViewDetail={() => setSelectedSupplier(supplier)}
                    />
                  ))}
                </div>
              )}

              {/* 面谈问题生成器 */}
              <div ref={interviewGeneratorRef}>
                <InterviewGenerator
                  selectedSuppliers={selectedSuppliers}
                  material={material}
                />
              </div>
            </>
          )}

          {!loading && !suppliers.length && sourcingResult && (
            <div className="card text-center py-16">
              <div className="w-16 h-16 rounded-full bg-yellow-100 flex items-center justify-center mx-auto mb-4">
                <span className="text-3xl">🔍</span>
              </div>
              <p className="text-gray-700 text-lg font-medium">未找到匹配供应商</p>
              <p className="text-sm text-gray-500 mt-2 max-w-md mx-auto">
                AI 联网搜索未能找到与当前物料匹配的供应商，建议调整物料型号或品类后重试
              </p>
              {searchDetails && (
                <div className="mt-4 px-4 py-3 bg-blue-50 rounded-lg border border-blue-200 inline-block">
                  <p className="text-sm text-blue-700">{searchDetails}</p>
                </div>
              )}
              <div className="mt-6 flex flex-col items-center gap-2 text-sm text-gray-400">
                <p>💡 提示：可以尝试更通用的型号或品类搜索</p>
                <p>💡 提示：检查 LLM Token 是否已正确配置</p>
              </div>
            </div>
          )}

          {!loading && !suppliers.length && !sourcingResult && (
            <div className="card text-center py-16">
              <Building2 className="w-16 h-16 text-gray-200 mx-auto mb-4" />
              <p className="text-gray-500 text-lg">填写物料需求开始寻源</p>
              <p className="text-sm text-gray-400 mt-1">
                支持按型号搜索或填写痛点找替代供应商
              </p>
            </div>
          )}
        </div>
      </div>

      {/* 供应商详情弹窗 */}
      <SupplierDetailModal
        isOpen={!!selectedSupplier}
        onClose={() => setSelectedSupplier(null)}
        supplier={selectedSupplier}
      />
    </div>
  )
}
