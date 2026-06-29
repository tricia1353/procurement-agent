import { useState } from 'react'
import { X } from 'lucide-react'

const CATEGORIES = [
  '芯片/IC', '液晶/显示屏', '面板', 'PCB', '被动元件', '连接器', 'RF模块', '非标件', '其他'
]

const PAIN_POINT_OPTIONS = [
  '价格贵', '起订量多', '交期长', '质量不稳定', '保供风险', '资质不全', '服务差'
]

const REQUIREMENT_OPTIONS = [
  '可提供参考规格书', '接受替代品牌', '小批量订单', '账期支持', '技术支持', '样品测试'
]

const REGIONS = ['深圳', '上海', '东莞', '杭州', '苏州', '南京', '北京', '成都', '不限']

export function SourcingForm({ onSubmit, loading }) {
  const [material, setMaterial] = useState({
    model: '',
    category: '芯片/IC',
    spec: '',
    annual_usage: '',
    pain_points: [],
    requirements: [],
    accept_substitute: true
  })
  const [currentSupplier, setCurrentSupplier] = useState('')
  const [preferredRegions, setPreferredRegions] = useState([])
  const [customPainPoint, setCustomPainPoint] = useState('')
  const [customRequirement, setCustomRequirement] = useState('')

  const toggleArrayItem = (arr, setArr, item) => {
    if (arr.includes(item)) {
      setArr(arr.filter(i => i !== item))
    } else {
      setArr([...arr, item])
    }
  }

  const handleAddCustomPainPoint = () => {
    if (customPainPoint.trim() && !material.pain_points.includes(customPainPoint.trim())) {
      setMaterial({ ...material, pain_points: [...material.pain_points, customPainPoint.trim()] })
      setCustomPainPoint('')
    }
  }

  const handleAddCustomRequirement = () => {
    if (customRequirement.trim() && !material.requirements.includes(customRequirement.trim())) {
      setMaterial({ ...material, requirements: [...material.requirements, customRequirement.trim()] })
      setCustomRequirement('')
    }
  }

  const handleSubmit = () => {
    onSubmit({
      material: {
        ...material,
        annual_usage: material.annual_usage ? parseInt(material.annual_usage) : null
      },
      current_supplier: currentSupplier || null,
      preferred_regions: preferredRegions.filter(r => r !== '不限')
    })
  }

  return (
    <div className="card">
      <div className="mb-4">
        <h2 className="text-lg font-semibold text-gray-900">供应商条件</h2>
      </div>

      <div className="space-y-4">
        {/* 物料信息 */}
        <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
          <div className="mb-3">
            <span className="font-medium text-gray-800">物料信息</span>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            <div>
              <label className="block text-sm text-gray-600 mb-1">物料型号</label>
              <input
                type="text"
                value={material.model}
                onChange={(e) => setMaterial({ ...material, model: e.target.value })}
                placeholder="如: RF模块 KBD600 433M"
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">物料类别</label>
              <select
                value={material.category}
                onChange={(e) => setMaterial({ ...material, category: e.target.value })}
                className="select-field"
              >
                {CATEGORIES.map(c => <option key={c} value={c}>{c}</option>)}
              </select>
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">规格参数</label>
              <input
                type="text"
                value={material.spec}
                onChange={(e) => setMaterial({ ...material, spec: e.target.value })}
                placeholder="如: 433MHz, 10mW"
                className="input-field"
              />
            </div>

            <div>
              <label className="block text-sm text-gray-600 mb-1">年用量</label>
              <input
                type="number"
                value={material.annual_usage}
                onChange={(e) => setMaterial({ ...material, annual_usage: e.target.value })}
                placeholder="如: 1000000"
                className="input-field"
              />
            </div>
          </div>
        </div>

        {/* 当前痛点 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            当前痛点
          </label>
          <div className="flex flex-wrap gap-2">
            {PAIN_POINT_OPTIONS.map(point => (
              <button
                key={point}
                onClick={() => toggleArrayItem(material.pain_points, (pts) => setMaterial({ ...material, pain_points: pts }), point)}
                className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                  material.pain_points.includes(point)
                    ? 'bg-orange-100 border-orange-300 text-orange-800'
                    : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-gray-300'
                }`}
              >
                {point}
              </button>
            ))}
          </div>
          <div className="flex gap-2 mt-2">
            <input
              type="text"
              value={customPainPoint}
              onChange={(e) => setCustomPainPoint(e.target.value)}
              placeholder="添加其他痛点..."
              className="input-field flex-1 text-sm"
              onKeyPress={(e) => e.key === 'Enter' && handleAddCustomPainPoint()}
            />
            <button onClick={handleAddCustomPainPoint} className="btn btn-ghost text-sm">
              添加
            </button>
          </div>
          {material.pain_points.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {material.pain_points.map(p => (
                <span
                  key={p}
                  className="inline-flex items-center gap-1 px-2 py-0.5 bg-orange-100 text-orange-800 text-xs rounded"
                >
                  {p}
                  <X className="w-3 h-3 cursor-pointer" onClick={() => toggleArrayItem(material.pain_points, (pts) => setMaterial({ ...material, pain_points: pts }), p)} />
                </span>
              ))}
            </div>
          )}
        </div>

        {/* 采购要求 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            采购要求
          </label>
          <div className="flex flex-wrap gap-2">
            {REQUIREMENT_OPTIONS.map(req => (
              <button
                key={req}
                onClick={() => toggleArrayItem(material.requirements, (reqs) => setMaterial({ ...material, requirements: reqs }), req)}
                className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                  material.requirements.includes(req)
                    ? 'bg-green-100 border-green-300 text-green-800'
                    : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-gray-300'
                }`}
              >
                {req}
              </button>
            ))}
          </div>
          <div className="flex gap-2 mt-2">
            <input
              type="text"
              value={customRequirement}
              onChange={(e) => setCustomRequirement(e.target.value)}
              placeholder="添加其他要求..."
              className="input-field flex-1 text-sm"
              onKeyPress={(e) => e.key === 'Enter' && handleAddCustomRequirement()}
            />
            <button onClick={handleAddCustomRequirement} className="btn btn-ghost text-sm">
              添加
            </button>
          </div>
          {material.requirements.length > 0 && (
            <div className="flex flex-wrap gap-1 mt-2">
              {material.requirements.map(r => (
                <span
                  key={r}
                  className="inline-flex items-center gap-1 px-2 py-0.5 bg-green-100 text-green-800 text-xs rounded"
                >
                  {r}
                  <X className="w-3 h-3 cursor-pointer" onClick={() => toggleArrayItem(material.requirements, (reqs) => setMaterial({ ...material, requirements: reqs }), r)} />
                </span>
              ))}
            </div>
          )}
        </div>

        {/* 当前供应商（可选） */}
        <div className="p-4 bg-gray-50 rounded-lg border border-gray-200">
          <div className="flex items-center gap-2 mb-2">
            <span className="font-medium text-gray-700">当前供应商（希望替代）</span>
            <span className="text-xs text-gray-400">可选</span>
          </div>
          <input
            type="text"
            value={currentSupplier}
            onChange={(e) => setCurrentSupplier(e.target.value)}
            placeholder="如: 粤盛"
            className="input-field"
          />
          {currentSupplier && (
            <p className="text-sm text-blue-600 mt-1">
              将搜索可替代「{currentSupplier}」的其他供应商
            </p>
          )}
        </div>

        {/* 期望地区 */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            期望地区
          </label>
          <div className="flex flex-wrap gap-2">
            {REGIONS.map(region => (
              <button
                key={region}
                onClick={() => toggleArrayItem(preferredRegions, setPreferredRegions, region)}
                className={`px-3 py-1 text-sm rounded-full border transition-colors ${
                  preferredRegions.includes(region)
                    ? 'bg-blue-100 border-blue-300 text-blue-800'
                    : 'bg-gray-50 border-gray-200 text-gray-600 hover:border-gray-300'
                }`}
              >
                {region}
              </button>
            ))}
          </div>
        </div>

        {/* 提交按钮 */}
        <button
          onClick={handleSubmit}
          disabled={loading}
          className="btn btn-primary w-full"
        >
          {loading ? (
            <span className="flex items-center justify-center gap-2">
              <svg className="animate-spin w-4 h-4" viewBox="0 0 24 24">
                <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" />
                <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z" />
              </svg>
              正在搜索供应商...
            </span>
          ) : (
'开始搜索'
          )}
        </button>
      </div>
    </div>
  )
}
