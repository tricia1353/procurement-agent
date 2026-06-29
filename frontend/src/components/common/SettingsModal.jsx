import { useState } from 'react'
import { X, Check } from 'lucide-react'

export function SettingsModal({ isOpen, onClose, onSave, initialValues }) {
  const [llmToken, setLlmToken] = useState(initialValues.llmToken || '')
  const [mouserApiKey, setMouserApiKey] = useState(initialValues.mouserApiKey || '')
  const [showPassword, setShowPassword] = useState({ llm: false, mouser: false })
  const [saved, setSaved] = useState(false)

  const handleSave = () => {
    onSave({ llmToken, mouserApiKey })
    setSaved(true)
    setTimeout(() => {
      setSaved(false)
      onClose()
    }, 800)
  }

  const handleTogglePassword = (field) => {
    setShowPassword((prev) => ({ ...prev, [field]: !prev[field] }))
  }

  if (!isOpen) return null

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">API 设置</h2>
            <p className="text-sm text-gray-500">配置外部服务密钥</p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Body */}
        <div className="p-6 space-y-6">
          {/* 百度 AI Studio */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-medium text-gray-900">百度 AI Studio</h3>
              <a
                href="https://aistudio.baidu.com/account/accessToken"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                获取 Token
              </a>
            </div>
            <p className="text-sm text-gray-500">用于采购建议和面谈问题生成</p>
            <div className="relative">
              <input
                type={showPassword.llm ? 'text' : 'password'}
                value={llmToken}
                onChange={(e) => setLlmToken(e.target.value)}
                placeholder="输入你的百度 AI Studio Access Token"
                className="input-field pr-10"
              />
              <button
                onClick={() => handleTogglePassword('llm')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPassword.llm ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
            <div className="bg-gray-50 rounded-lg p-3 text-sm text-gray-600">
              <p><strong>获取方式：</strong>访问 <a href="https://aistudio.baidu.com/account/accessToken" target="_blank" rel="noopener noreferrer" className="text-blue-600">百度 AI Studio</a> → Access Token → 复制</p>
            </div>
          </div>

          {/* Mouser */}
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <h3 className="text-base font-medium text-gray-900">Mouser API</h3>
              <a
                href="https://www.mouser.cn/api-hub/"
                target="_blank"
                rel="noopener noreferrer"
                className="text-sm text-blue-600 hover:text-blue-700"
              >
                获取 Key
              </a>
            </div>
            <p className="text-sm text-gray-500">用于查询实时价格、库存和物料信息</p>
            <div className="relative">
              <input
                type={showPassword.mouser ? 'text' : 'password'}
                value={mouserApiKey}
                onChange={(e) => setMouserApiKey(e.target.value)}
                placeholder="输入你的 Mouser API Key"
                className="input-field pr-10"
              />
              <button
                onClick={() => handleTogglePassword('mouser')}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400 hover:text-gray-600"
              >
                {showPassword.mouser ? '👁️' : '👁️‍🗨️'}
              </button>
            </div>
            <p className="text-xs text-gray-500">申请成功后会发送邮件到注册邮箱，可在邮箱里查询</p>
          </div>
        </div>

        {/* Footer */}
        <div className="flex items-center justify-between px-6 py-4 bg-gray-50 border-t border-gray-200">
          <span className="text-sm text-gray-500">Key 仅存储在本地浏览器</span>
          <div className="flex space-x-2">
            <button onClick={onClose} className="btn btn-secondary">
              取消
            </button>
            <button onClick={handleSave} className="btn btn-primary">
              {saved ? (
                <>
                  <Check className="w-4 h-4 mr-2" />
                  已保存
                </>
              ) : (
                '保存设置'
              )}
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}