import { useState } from 'react'
import { MessageCircle, ChevronDown, ChevronUp, Copy, Check, Download } from 'lucide-react'
import { useApi } from '../../hooks/useApi'
import { api } from '../../services/api'

const CATEGORY_ICONS = {
  '企业基本情况': '🏢',
  '产品与质量': '📦',
  '商务条款': '💰',
  '风险点': '⚠️',
  '技术能力': '🔧',
  '服务支持': '🤝',
  '其他': '📋'
}

const PRIORITY_COLORS = {
  'high': 'border-red-200 bg-red-50',
  'medium': 'border-yellow-200 bg-yellow-50',
  'low': 'border-gray-200 bg-gray-50'
}

const PRIORITY_LABELS = {
  'high': '高',
  'medium': '中',
  'low': '低'
}

export function InterviewGenerator({ selectedSuppliers, material, onQuestionsGenerated }) {
  const [focusAreas, setFocusAreas] = useState(['价格', '交期', '质量'])
  const [expandedSupplier, setExpandedSupplier] = useState(null)
  const [copied, setCopied] = useState(null)
  const [generatedQuestions, setGeneratedQuestions] = useState(null)

  const { loading, error, execute: generateQuestions } = useApi(api.generateInterviewQuestions)

  const focusOptions = ['价格', '起订量', '交期', '质量', '资质', '服务', '技术支持']

  const toggleFocusArea = (area) => {
    if (focusAreas.includes(area)) {
      setFocusAreas(focusAreas.filter(a => a !== area))
    } else {
      setFocusAreas([...focusAreas, area])
    }
  }

  const handleGenerate = async () => {
    if (selectedSuppliers.length === 0) return

    let result
    try {
      result = await generateQuestions({
        suppliers: selectedSuppliers,
        material: material,
        focus_areas: focusAreas
      })
    } catch {
      return
    }

    if (result) {
      setGeneratedQuestions(result)
      onQuestionsGenerated?.(result)
      setExpandedSupplier(selectedSuppliers[0])
    }
  }

  const copyToClipboard = (text) => {
    navigator.clipboard.writeText(text)
    setCopied(text)
    setTimeout(() => setCopied(null), 2000)
  }

  const downloadQuestions = () => {
    if (!generatedQuestions) return

    let content = `供应商面谈问题清单\n`
    content += `生成时间: ${new Date().toLocaleString()}\n`
    content += `物料: ${material?.model || '未指定'} (${material?.category || '未指定'})\n`
    content += `${'='.repeat(50)}\n\n`

    Object.entries(generatedQuestions.questions_by_supplier || {}).forEach(([supplier, questions]) => {
      content += `【${supplier}】\n`
      questions.forEach((q, i) => {
        content += `  [${q.priority === 'high' ? '★' : q.priority === 'medium' ? '○' : '□'}] ${q.question}\n`
        if (q.context) content += `      背景: ${q.context}\n`
      })
      content += '\n'
    })

    if (generatedQuestions.common_questions?.length > 0) {
      content += `【通用问题】\n`
      generatedQuestions.common_questions.forEach((q, i) => {
        content += `  [${q.priority === 'high' ? '★' : q.priority === 'medium' ? '○' : '□'}] ${q.question}\n`
      })
    }

    const blob = new Blob([content], { type: 'text/plain;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = `面谈问题_${material?.model || '供应商'}_${new Date().toISOString().slice(0, 10)}.txt`
    a.click()
    URL.revokeObjectURL(url)
  }

  if (selectedSuppliers.length === 0) {
    return (
      <div className="card text-center py-8">
        <MessageCircle className="w-10 h-10 text-gray-300 mx-auto mb-3" />
        <p className="text-gray-500">请先勾选供应商</p>
        <p className="text-sm text-gray-400">勾选后可生成面谈问题清单</p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      {/* 关注领域选择 */}
      <div className="card">
        <div className="flex items-center justify-between mb-3">
          <h3 className="font-medium text-gray-800">🎯 重点关注领域</h3>
          <span className="text-xs text-gray-500">已选 {focusAreas.length} 项</span>
        </div>
        <div className="flex flex-wrap gap-2">
          {focusOptions.map(area => (
            <button
              key={area}
              onClick={() => toggleFocusArea(area)}
              className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                focusAreas.includes(area)
                  ? 'bg-blue-100 border-blue-300 text-blue-800'
                  : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-gray-300'
              }`}
            >
              {area}
            </button>
          ))}
        </div>
        {error && (
          <div className="mb-3 p-3 bg-red-50 border border-red-200 rounded-lg text-sm text-red-700">
            {error}
          </div>
        )}
        <button
          onClick={handleGenerate}
          disabled={loading || focusAreas.length === 0}
          className="btn btn-primary w-full mt-4"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              生成中...
            </span>
          ) : (
            `生成 ${selectedSuppliers.length} 家供应商的面谈问题`
          )}
        </button>
      </div>

      {/* 生成的问题 */}
      {generatedQuestions && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="font-medium text-gray-800">📋 面谈问题清单</h3>
            <button
              onClick={downloadQuestions}
              className="btn btn-ghost text-sm"
            >
              <Download className="w-4 h-4 mr-1" />
              导出
            </button>
          </div>

          {/* 按供应商分组展示 */}
          <div className="space-y-3">
            {Object.entries(generatedQuestions.questions_by_supplier || {}).map(([supplier, questions]) => (
              <div key={supplier} className="border border-gray-200 rounded-lg overflow-hidden">
                <button
                  onClick={() => setExpandedSupplier(expandedSupplier === supplier ? null : supplier)}
                  className="w-full px-4 py-3 bg-gray-50 flex items-center justify-between hover:bg-gray-100 transition-colors"
                >
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900">{supplier}</span>
                    <span className="text-xs text-gray-500">({questions.length} 个问题)</span>
                  </div>
                  {expandedSupplier === supplier ? (
                    <ChevronUp className="w-4 h-4 text-gray-500" />
                  ) : (
                    <ChevronDown className="w-4 h-4 text-gray-500" />
                  )}
                </button>

                {expandedSupplier === supplier && (
                  <div className="p-4 space-y-2">
                    {questions.map((q, i) => (
                      <div
                        key={i}
                        className={`p-3 border-l-4 rounded ${PRIORITY_COLORS[q.priority] || PRIORITY_COLORS['medium']}`}
                      >
                        <div className="flex items-start justify-between gap-2">
                          <div className="flex-1">
                            <div className="flex items-center gap-2 mb-1">
                              <span className="text-sm">
                                {CATEGORY_ICONS[q.category] || '📋'}
                              </span>
                              <span className="text-xs text-gray-500">{q.category}</span>
                              <span className={`text-xs px-1.5 py-0.5 rounded ${
                                q.priority === 'high' ? 'bg-red-100 text-red-700' :
                                q.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                                'bg-gray-100 text-gray-700'
                              }`}>
                                {PRIORITY_LABELS[q.priority] || '中'}优先
                              </span>
                            </div>
                            <p className="text-gray-800">{q.question}</p>
                            {q.context && (
                              <p className="text-xs text-gray-500 mt-1 italic">
                                背景: {q.context}
                              </p>
                            )}
                          </div>
                          <button
                            onClick={() => copyToClipboard(q.question)}
                            className="p-1 hover:bg-white rounded"
                          >
                            {copied === q.question ? (
                              <Check className="w-4 h-4 text-green-600" />
                            ) : (
                              <Copy className="w-4 h-4 text-gray-400" />
                            )}
                          </button>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>

          {/* 通用问题 */}
          {generatedQuestions.common_questions?.length > 0 && (
            <div className="mt-4 p-4 bg-blue-50 rounded-lg border border-blue-200">
              <h4 className="font-medium text-blue-900 mb-2">💡 通用问题</h4>
              <div className="space-y-2">
                {generatedQuestions.common_questions.map((q, i) => (
                  <div key={i} className="text-sm text-blue-800 flex items-start gap-2">
                    <span>•</span>
                    <span>{q.question}</span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  )
}
