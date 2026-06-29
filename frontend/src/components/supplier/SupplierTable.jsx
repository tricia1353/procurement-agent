import { useState } from 'react'
import { Check } from 'lucide-react'

export function SupplierTable({ suppliers, selectedSuppliers, onSelectChange, onGenerateInterview }) {
  const [sortField, setSortField] = useState('credit_score')
  const [sortAsc, setSortAsc] = useState(false)

  const getRiskBadge = (level) => {
    const colors = {
      '低风险': 'bg-green-100 text-green-800',
      '中风险': 'bg-yellow-100 text-yellow-800',
      '高风险': 'bg-red-100 text-red-800',
      '待确认': 'bg-gray-100 text-gray-800'
    }
    return colors[level] || colors['待确认']
  }

  const sortedSuppliers = [...suppliers].sort((a, b) => {
    let valA = a[sortField] || 0
    let valB = b[sortField] || 0
    return sortAsc ? valA - valB : valB - valA
  })

  const handleSort = (field) => {
    if (sortField === field) {
      setSortAsc(!sortAsc)
    } else {
      setSortField(field)
      setSortAsc(false)
    }
  }

  if (suppliers.length === 0) {
    return (
      <div className="card text-center py-12">
        <div className="text-6xl mb-4">🔍</div>
        <p className="text-gray-500">暂无供应商信息</p>
        <p className="text-sm text-gray-400 mt-1">请填写物料需求后开始搜索</p>
      </div>
    )
  }

  return (
    <div className="card overflow-hidden">
      <div className="overflow-x-auto">
        <table className="w-full">
          <thead>
            <tr className="bg-gray-50 border-b border-gray-200">
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600 w-10">
                <input
                  type="checkbox"
                  checked={selectedSuppliers.length > 0 && selectedSuppliers.length === suppliers.length}
                  onChange={(e) => {
                    if (e.target.checked) {
                      onSelectChange(suppliers.map(s => s.name))
                    } else {
                      onSelectChange([])
                    }
                  }}
                  className="w-4 h-4 rounded border-gray-300"
                />
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">供应商名称</th>
              <th
                className="px-4 py-3 text-left text-sm font-medium text-gray-600 cursor-pointer hover:bg-gray-100"
                onClick={() => handleSort('region')}
              >
                地点 {sortField === 'region' && (sortAsc ? '↑' : '↓')}
              </th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">主要优势</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">可供应产品</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">已服务客户</th>
              <th className="px-4 py-3 text-left text-sm font-medium text-gray-600">信息来源</th>
            </tr>
          </thead>
          <tbody>
            {sortedSuppliers.map((supplier, index) => (
              <tr
                key={index}
                className={`border-b border-gray-100 hover:bg-blue-50/30 transition-colors ${
                  index === 0 ? 'bg-blue-50/20' : ''
                }`}
              >
                <td className="px-4 py-3">
                  <input
                    type="checkbox"
                    checked={selectedSuppliers.includes(supplier.name)}
                    onChange={(e) => {
                      if (e.target.checked) {
                        onSelectChange([...selectedSuppliers, supplier.name])
                      } else {
                        onSelectChange(selectedSuppliers.filter(s => s !== supplier.name))
                      }
                    }}
                    className="w-4 h-4 rounded border-gray-300"
                  />
                </td>
                <td className="px-4 py-3">
                  <div className="flex items-center gap-2">
                    <span className="font-medium text-gray-900">{supplier.name}</span>
                  </div>
                  <div className="flex items-center gap-1 mt-1">
                    <span className={`text-xs px-1.5 py-0.5 rounded ${getRiskBadge(supplier.risk_level)}`}>
                      {supplier.risk_level}
                    </span>
                    {supplier.credit_score && (
                      <span className="text-xs text-gray-500">
                        信用: {supplier.credit_score}
                      </span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3 text-sm text-gray-600">{supplier.region}</td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {supplier.advantages.slice(0, 2).map((adv, i) => (
                      <span
                        key={i}
                        className="text-xs px-2 py-0.5 bg-green-50 text-green-700 rounded"
                      >
                        {adv}
                      </span>
                    ))}
                    {supplier.advantages.length > 2 && (
                      <span className="text-xs text-gray-400">+{supplier.advantages.length - 2}</span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {supplier.products.slice(0, 2).map((prod, i) => (
                      <span
                        key={i}
                        className="text-xs px-2 py-0.5 bg-blue-50 text-blue-700 rounded"
                      >
                        {prod}
                      </span>
                    ))}
                    {supplier.products.length > 2 && (
                      <span className="text-xs text-gray-400">+{supplier.products.length - 2}</span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <div className="flex flex-wrap gap-1">
                    {supplier.served_clients.slice(0, 2).map((client, i) => (
                      <span
                        key={i}
                        className="text-xs px-2 py-0.5 bg-purple-50 text-purple-700 rounded"
                      >
                        {client}
                      </span>
                    ))}
                    {supplier.served_clients.length > 2 && (
                      <span className="text-xs text-gray-400">+{supplier.served_clients.length - 2}</span>
                    )}
                  </div>
                </td>
                <td className="px-4 py-3">
                  <span className="text-xs px-2 py-0.5 bg-gray-100 text-gray-600 rounded">
                    {supplier.source}
                  </span>
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {selectedSuppliers.length > 0 && (
        <div className="px-4 py-3 bg-blue-50 border-t border-blue-100">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-2 text-sm text-blue-800">
              <Check className="w-4 h-4" />
              <span>已选择 {selectedSuppliers.length} 家供应商</span>
            </div>
            <div className="flex gap-2">
              <button
                onClick={() => onSelectChange([])}
                className="text-sm text-gray-600 hover:text-gray-800 px-3 py-1 hover:bg-gray-200 rounded"
              >
                清空选择
              </button>
              <button
                onClick={onGenerateInterview}
                className="text-sm text-blue-600 hover:text-blue-800 px-3 py-1 bg-white border border-blue-200 rounded hover:bg-blue-50"
              >
                生成面谈问题 ↓
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
