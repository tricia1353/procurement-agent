// 价格追踪页面
// 集成 Mouser API，展示完整产品信息，支持产品对比和LLM推荐

import { useState } from 'react'
import {
  ExternalLink, CheckSquare, Square,
  X, Loader2, CheckCircle2
} from 'lucide-react'
import ReactMarkdown from 'react-markdown'
import { api } from '../../services/api'

// 加载步骤定义
const LLM_STEPS = [
  '正在整理产品对比数据...',
  '正在分析价格竞争力...',
  '正在评估供货能力与风险...',
  '正在生成采购推荐方案...'
]

export function PriceTracker() {
  const [searchModel, setSearchModel] = useState('')
  const [loading, setLoading] = useState(false)
  const [searchData, setSearchData] = useState(null)
  const [error, setError] = useState(null)
  const [selectedProducts, setSelectedProducts] = useState([])
  const [showCompare, setShowCompare] = useState(false)
  const [llmLoading, setLlmLoading] = useState(false)
  const [llmStep, setLlmStep] = useState(0)
  const [llmRecommendation, setLlmRecommendation] = useState(null)

  const handleSearch = async (e) => {
    e.preventDefault()
    if (!searchModel.trim()) return

    const model = searchModel.trim()
    try {
      setLoading(true)
      setError(null)
      setSelectedProducts([])
      setLlmRecommendation(null)
      setShowCompare(false)
      const result = await api.searchPrice(model)
      setSearchData(result)
    } catch (err) {
      console.error('搜索失败:', err)
      setError(err.message || '查询失败')
    } finally {
      setLoading(false)
    }
  }

  const toggleProduct = (product) => {
    const idx = selectedProducts.findIndex(p => p.mouser_part_number === product.mouser_part_number)
    if (idx >= 0) {
      setSelectedProducts(selectedProducts.filter((_, i) => i !== idx))
    } else {
      setSelectedProducts([...selectedProducts, product])
    }
  }

  const isSelected = (product) => {
    return selectedProducts.some(p => p.mouser_part_number === product.mouser_part_number)
  }

  const handleCompare = async () => {
    if (selectedProducts.length < 1) {
      alert('请至少选择1个产品进行分析')
      return
    }
    setShowCompare(true)
    await fetchLLMRecommendation()
  }

  const fetchLLMRecommendation = async () => {
    setLlmLoading(true)
    setLlmRecommendation(null)
    setLlmStep(0)

    // 启动分步动画（每步延迟，不阻塞实际请求）
    const stepTimer = setInterval(() => {
      setLlmStep(prev => Math.min(prev + 1, LLM_STEPS.length - 1))
    }, 3000)

    try {
      // 使用实际产品名称为产品命名
      const productNames = selectedProducts.map(p => p.manufacturer_part_number)
      const productsInfo = selectedProducts.map((p) => `
【${p.manufacturer_part_number}】(${p.mouser_part_number})
- 制造商: ${p.manufacturer}
- 描述: ${p.description}
- 价格梯度: ${p.price_breaks?.slice(0, 5).map(pb => `${pb.quantity}件=${pb.price}`).join(', ') || '无'}
- 现货库存: ${p.availability_in_stock} 件
- 在途库存: ${p.availability_on_order?.map(a => `${a.quantity}件(${a.date?.split('T')[0] || '待定'})`).join(', ') || '无'}
- 最小起订量: ${p.moq} | 订购倍数: ${p.order_multiple}
- 交期: ${p.lead_time || '未知'}
- 封装: ${p.package || '未知'}
- 卷带供应: ${p.reeling ? '是' : '否'}
- RoHS: ${p.rohs_status || '未知'}
- 替代型号: ${p.alternate_packagings?.map(a => a.mfr_part_number).join(', ') || '无'}
- 重量: ${p.unit_weight_kg ? p.unit_weight_kg + ' kg' : '未知'}
`).join('\n')

      const isSingleProduct = selectedProducts.length === 1
      const singleProduct = selectedProducts[0]

      // 根据产品数量调整prompt
      let prompt
      if (isSingleProduct) {
        prompt = `我是一名电子元器件采购工程师，正在查询物料"${searchModel}"。目前Mouser平台返回了以下产品：

${productsInfo}

请从采购角度对这个产品进行分析。

⚠️ 重要：不要输出任何表格！价格等数据已在上方表格中展示。请直接给出理由和结论，格式如下：

**价格评估**
（分析价格梯度的成本优势，不列具体数字）

**供货能力**
（库存、在途、交期评估结论）

**适用场景**
（根据封装、卷带特性推荐生产场景）

**风险提示**
（生命周期、替代方案、供应风险）

**采购建议**
（建议采购时机、数量、价格谈判空间）`
      } else {
        const productListStr = productNames.map((name, i) => `${i + 1}. ${name}`).join('\n')
        prompt = `我是一名电子元器件采购工程师，正在为物料"${searchModel}"选择供应商。以下是Mouser平台返回的产品选项：

可选项：
${productListStr}

详细数据：
${productsInfo}

请从采购角度进行对比分析。

⚠️ 重要：不要输出任何表格！价格等数据已在上方表格中展示。请直接给出理由和结论，格式如下：

**价格竞争力**
（对比各产品的价格优势结论，直接使用产品型号名称而非"产品1"等代称）

**供货能力**
（库存、在途、交期分析结论）

**适用场景**
（根据封装、卷带等特性推荐适用生产场景）

**风险提示**
（生命周期状态、替代方案等）

**推荐结论**
✅ 首选：XXX型号（理由）
🔄 备选：XXX型号（理由）`
      }

      const result = await api.chat(prompt)
      setLlmRecommendation(result.message || result)
    } catch (err) {
      console.error('LLM推荐失败:', err)
      setLlmRecommendation(`⚠️ LLM分析失败: ${err.message}\n\n请检查后端是否配置了LLM API Token。`)
    } finally {
      clearInterval(stepTimer)
      setLlmLoading(false)
    }
  }

  return (
    <div className="space-y-6">
      {/* 搜索区域 */}
      <div className="card relative overflow-hidden">
        <div className="pointer-events-none absolute right-0 top-0 h-28 w-28 rounded-full bg-cyan-300/20 blur-2xl" />
        <div className="relative mb-5 flex items-start justify-between gap-4">
          <div>
            <h2 className="text-2xl font-bold text-slate-950">采购成本分析</h2>
            <p className="mt-2 text-sm text-slate-500">查看阶梯价、库存与交期，辅助采购判断。</p>
          </div>
        </div>

        <form onSubmit={handleSearch} className="relative flex gap-3">
          <div className="flex-1 relative">
            <input
              type="text"
              value={searchModel}
              onChange={(e) => setSearchModel(e.target.value)}
              placeholder="输入物料型号，如: STM32F103C8T6, ESP32-WROOM-32, LM7805"
              className="input-field"
            />
          </div>
          <button type="submit" className="btn btn-primary" disabled={loading}>
            {loading ? '查询中...' : '查询'}
          </button>
        </form>

        {/* 快捷搜索 */}
        <div className="mt-4">
          <p className="text-sm text-gray-500 mb-2">快捷查询：</p>
          <div className="flex flex-wrap gap-2">
            {['STM32F103C8T6', 'ESP32-WROOM-32', 'LM7805', 'ATmega328P'].map((m) => (
              <button
                key={m}
                onClick={() => setSearchModel(m)}
                className="rounded-full border border-white/70 bg-white/70 px-3 py-1 text-sm font-medium text-slate-600 shadow-sm transition-all duration-300 hover:-translate-y-0.5 hover:bg-cyan-50 hover:text-blue-700 hover:shadow-md"
              >
                {m}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* 错误提示 */}
      {error && (
        <div className="card border-l-4 border-red-500">
          <p className="text-red-600">{error}</p>
        </div>
      )}

      {/* 数据来源提示 */}
      {searchData && (
        <div className="text-sm text-slate-500 flex items-center gap-2">
          <span>数据来源: {searchData.data_source || 'Mouser API'}</span>
          {searchData.mouser_configured ? (
            <span className="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded">已配置</span>
          ) : (
            <span className="bg-yellow-100 text-yellow-700 text-xs px-2 py-0.5 rounded">未配置</span>
          )}
          {searchData.total_found > 0 && (
            <span>· 找到 <strong>{searchData.total_found}</strong> 个产品</span>
          )}
        </div>
      )}

      {/* 产品列表 */}
      {searchData && searchData.products && searchData.products.length > 0 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">产品列表</h3>
            <div className="flex items-center gap-3">
              <span className="text-sm text-gray-500">
                已选 {selectedProducts.length} 个
              </span>
              <button
                onClick={handleCompare}
                disabled={selectedProducts.length < 1}
                className="btn btn-primary disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {selectedProducts.length === 1 ? '采购建议' : '对比分析'}
              </button>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            {searchData.products.map((product, index) => (
              <div
                key={index}
                className={`border rounded-lg p-4 cursor-pointer transition-all ${
                  isSelected(product)
                    ? 'border-blue-500 bg-blue-50'
                    : 'border-gray-200 hover:border-gray-300'
                }`}
                onClick={() => toggleProduct(product)}
              >
                <div className="flex items-start gap-3">
                  {/* 选择框 */}
                  <div className="mt-1">
                    {isSelected(product) ? (
                      <CheckSquare className="w-5 h-5 text-blue-600" />
                    ) : (
                      <Square className="w-5 h-5 text-gray-400" />
                    )}
                  </div>

                  {/* 产品图片 */}
                  {product.image_path && (
                    <img
                      src={product.image_path}
                      alt={product.manufacturer_part_number}
                      className="w-16 h-16 object-contain rounded border"
                    />
                  )}

                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-gray-900 truncate">
                      {product.manufacturer_part_number}
                    </p>
                    <p className="text-sm text-gray-500">{product.manufacturer}</p>
                    <p className="text-xs text-gray-400 truncate mt-1">
                      {product.description}
                    </p>

                    {/* 关键指标 */}
                    <div className="flex flex-wrap gap-2 mt-2">
                      {product.price_breaks && product.price_breaks.length > 0 && (
                        <span className="bg-green-100 text-green-700 text-xs px-2 py-0.5 rounded">
                          {product.price_breaks[0].price}
                        </span>
                      )}
                      <span className={`text-xs px-2 py-0.5 rounded ${
                        product.availability_in_stock > 0
                          ? 'bg-blue-100 text-blue-700'
                          : 'bg-gray-100 text-gray-500'
                      }`}>
                        库存: {product.availability_in_stock > 0 ? product.availability_in_stock : '无'}
                      </span>
                      {product.reeling && (
                        <span className="bg-purple-100 text-purple-700 text-xs px-2 py-0.5 rounded">
                          卷带
                        </span>
                      )}
                    </div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* 无结果提示 */}
      {searchData && (!searchData.products || searchData.products.length === 0) && (
        <div className="card bg-gray-50 text-center py-12">
          <p className="text-gray-500 mb-2">未找到匹配的产品</p>
          <p className="text-sm text-gray-400">
            {searchData.mouser_configured
              ? '请检查型号是否正确，或尝试其他关键词'
              : '请先配置 Mouser API Key'}
          </p>
        </div>
      )}

      {/* 对比/分析面板 */}
      {showCompare && selectedProducts.length >= 1 && (
        <div className="card">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-lg font-semibold text-gray-900">
              {selectedProducts.length === 1 ? '产品分析' : '产品对比'}
            </h3>
            <button
              onClick={() => setShowCompare(false)}
              className="p-1 hover:bg-gray-100 rounded"
            >
              <X className="w-5 h-5 text-gray-500" />
            </button>
          </div>

          {/* 对比表格 */}
          <div className="overflow-x-auto">
            <table className="min-w-full border-collapse">
              <thead>
                <tr className="bg-gray-50">
                  <th className="border p-2 text-left text-sm font-medium text-gray-700">对比项</th>
                  {selectedProducts.map((p) => (
                    <th key={p.mouser_part_number} className="border p-2 text-left text-sm font-medium text-gray-900 min-w-[180px]">
                      <div className="flex items-center gap-2">
                        {p.image_path && (
                          <img src={p.image_path} alt="" className="w-8 h-8 object-contain" />
                        )}
                        <div>
                          <p className="font-medium">{p.manufacturer_part_number}</p>
                          <p className="text-xs text-gray-500">{p.mouser_part_number}</p>
                        </div>
                      </div>
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody className="text-sm">
                <tr>
                  <td className="border p-2 bg-gray-50 font-medium">制造商</td>
                  {selectedProducts.map((p) => (
                    <td key={p.mouser_part_number} className="border p-2">{p.manufacturer}</td>
                  ))}
                </tr>
                <tr>
                  <td className="border p-2 bg-gray-50 font-medium">描述</td>
                  {selectedProducts.map((p) => (
                    <td key={p.mouser_part_number} className="border p-2 text-xs">{p.description}</td>
                  ))}
                </tr>
                <tr>
                  <td className="border p-2 bg-gray-50 font-medium">价格梯度</td>
                  {selectedProducts.map((p) => (
                    <td key={p.mouser_part_number} className="border p-2">
                      <div className="space-y-1">
                        {p.price_breaks?.slice(0, 5).map((pb, i) => (
                          <div key={i} className="text-xs">
                            {pb.quantity}+: <span className="font-medium">{pb.price}</span>
                          </div>
                        ))}
                      </div>
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="border p-2 bg-gray-50 font-medium">现货库存</td>
                  {selectedProducts.map((p) => (
                    <td key={p.mouser_part_number} className={`border p-2 font-medium ${
                      p.availability_in_stock > 0 ? 'text-green-600' : 'text-gray-400'
                    }`}>
                      {p.availability_in_stock > 0 ? p.availability_in_stock.toLocaleString() : '无'}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="border p-2 bg-gray-50 font-medium">在途库存</td>
                  {selectedProducts.map((p) => (
                    <td key={p.mouser_part_number} className="border p-2 text-xs">
                      {p.availability_on_order?.length > 0 ? (
                        <div className="space-y-1">
                          {p.availability_on_order.map((a, i) => (
                            <div key={i} className="text-yellow-700">
                              {a.quantity.toLocaleString()} ({a.date?.split('T')[0] || '待定'})
                            </div>
                          ))}
                        </div>
                      ) : (
                        <span className="text-gray-400">无</span>
                      )}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="border p-2 bg-gray-50 font-medium">MOQ / 倍数</td>
                  {selectedProducts.map((p) => (
                    <td key={p.mouser_part_number} className="border p-2">{p.moq} / {p.order_multiple}</td>
                  ))}
                </tr>
                <tr>
                  <td className="border p-2 bg-gray-50 font-medium">交期</td>
                  {selectedProducts.map((p) => (
                    <td key={p.mouser_part_number} className="border p-2">{p.lead_time || '-'}</td>
                  ))}
                </tr>
                <tr>
                  <td className="border p-2 bg-gray-50 font-medium">封装</td>
                  {selectedProducts.map((p) => (
                    <td key={p.mouser_part_number} className="border p-2">{p.package || '-'}</td>
                  ))}
                </tr>
                <tr>
                  <td className="border p-2 bg-gray-50 font-medium">卷带供应</td>
                  {selectedProducts.map((p) => (
                    <td key={p.mouser_part_number} className="border p-2">
                      {p.reeling ? (
                        <span className="text-green-600 font-medium">✓ 是</span>
                      ) : (
                        <span className="text-gray-400">否</span>
                      )}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="border p-2 bg-gray-50 font-medium">RoHS</td>
                  {selectedProducts.map((p) => (
                    <td key={p.mouser_part_number} className="border p-2">
                      {p.rohs_status?.includes('Compliant') ? (
                        <span className="text-green-600">{p.rohs_status}</span>
                      ) : (
                        p.rohs_status || '-'
                      )}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="border p-2 bg-gray-50 font-medium">替代型号</td>
                  {selectedProducts.map((p) => (
                    <td key={p.mouser_part_number} className="border p-2 text-xs">
                      {p.alternate_packagings?.length > 0 ? (
                        <div className="space-y-1">
                          {p.alternate_packagings.map((a) => (
                            <div key={a.mfr_part_number} className="text-blue-600">{a.mfr_part_number}</div>
                          ))}
                        </div>
                      ) : '-'}
                    </td>
                  ))}
                </tr>
                <tr>
                  <td className="border p-2 bg-gray-50 font-medium">产品链接</td>
                  {selectedProducts.map((p) => (
                    <td key={p.mouser_part_number} className="border p-2">
                      {p.product_url && (
                        <a
                          href={p.product_url}
                          target="_blank"
                          rel="noopener noreferrer"
                          className="text-blue-600 hover:text-blue-700 text-xs flex items-center gap-1"
                        >
                          <ExternalLink className="w-3 h-3" />
                          Mouser产品页
                        </a>
                      )}
                    </td>
                  ))}
                </tr>
              </tbody>
            </table>
          </div>

          {/* LLM 推荐 */}
          <div className="mt-6 border-t pt-4">
            <div className="flex items-center gap-2 mb-3">
              <h4 className="font-semibold text-gray-900">采购建议</h4>
            </div>

            {/* 加载中 - 分步进度展示 */}
            {llmLoading && (
              <div className="bg-gray-50 rounded-lg p-6 space-y-3">
                <div className="flex items-center gap-2 text-gray-500 mb-2">
                  <Loader2 className="w-5 h-5 animate-spin text-blue-500" />
                  <span className="text-sm font-medium text-gray-700">正在整理产品数据...</span>
                </div>
                <div className="pl-7 space-y-2">
                  {LLM_STEPS.map((step, index) => (
                    <div key={index} className="flex items-center gap-2">
                      {index < llmStep ? (
                        <CheckCircle2 className="w-4 h-4 text-green-500 flex-shrink-0" />
                      ) : index === llmStep && llmStep < LLM_STEPS.length - 1 ? (
                        <Loader2 className="w-4 h-4 animate-spin text-blue-500 flex-shrink-0" />
                      ) : index === llmStep ? (
                        <Loader2 className="w-4 h-4 animate-spin text-blue-500 flex-shrink-0" />
                      ) : (
                        <div className="w-4 h-4 rounded-full border-2 border-gray-300 flex-shrink-0" />
                      )}
                      <span className={`text-sm ${
                        index < llmStep
                          ? 'text-green-600'
                          : index === llmStep
                          ? 'text-blue-600 font-medium'
                          : 'text-gray-400'
                      }`}>
                        {step}
                      </span>
                    </div>
                  ))}
                </div>
              </div>
            )}

            {/* 推荐结果 - Markdown渲染 */}
            {llmRecommendation && !llmLoading && (
              <div className="bg-white border border-gray-200 rounded-lg p-6">
                <div className="prose prose-sm max-w-none">
                  <ReactMarkdown
                    components={{
                      table: ({ children }) => (
                        <div className="overflow-x-auto my-4">
                          <table className="min-w-full border-collapse border border-gray-200 text-sm">
                            {children}
                          </table>
                        </div>
                      ),
                      thead: ({ children }) => (
                        <thead className="bg-gray-50">{children}</thead>
                      ),
                      tbody: ({ children }) => (
                        <tbody>{children}</tbody>
                      ),
                      tr: ({ children }) => (
                        <tr className="border-b border-gray-200">{children}</tr>
                      ),
                      th: ({ children }) => (
                        <th className="px-4 py-2 text-left font-semibold text-gray-900 border border-gray-200 whitespace-nowrap">
                          {children}
                        </th>
                      ),
                      td: ({ children }) => (
                        <td className="px-4 py-2 text-gray-700 border border-gray-200 align-top">
                          {children}
                        </td>
                      ),
                    }}
                  >
                    {llmRecommendation}
                  </ReactMarkdown>
                </div>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  )
}
