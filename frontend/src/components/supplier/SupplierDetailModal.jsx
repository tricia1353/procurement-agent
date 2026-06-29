import { X, MapPin, Phone, Mail, Shield, Award, Calendar, Users } from 'lucide-react'
import { getRiskColor } from '../../utils/helpers'

export function SupplierDetailModal({ isOpen, onClose, supplier }) {
  if (!isOpen || !supplier) return null

  const isMockData = !supplier.credit_code

  return (
    <div className="modal-overlay" onClick={onClose}>
      <div className="modal-content max-w-2xl" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div className="flex items-center justify-between p-6 border-b border-gray-200">
          <div>
            <h2 className="text-xl font-semibold text-gray-900">{supplier.name}</h2>
            <p className="text-sm text-gray-500 mt-1">
              {supplier.category} | {supplier.region}
            </p>
          </div>
          <button onClick={onClose} className="p-2 hover:bg-gray-100 rounded-lg transition-colors">
            <X className="w-5 h-5 text-gray-500" />
          </button>
        </div>

        {/* Content */}
        <div className="p-6 space-y-6">
          {/* 企业资质 */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500 mb-1">信用评分</p>
              <p className="text-2xl font-bold">{supplier.credit_score || 'N/A'}</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500 mb-1">合作年限</p>
              <p className="text-2xl font-bold">{supplier.cooperation_years || 0}年</p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500 mb-1">风险等级</p>
              <p className={`text-lg font-bold ${getRiskColor(
                supplier.credit_score >= 85 ? '低风险' : supplier.credit_score >= 70 ? '中风险' : '高风险'
              ).replace('text-', '')}`}>
                {supplier.credit_score >= 85 ? '低风险' : supplier.credit_score >= 70 ? '中风险' : '高风险'}
              </p>
            </div>
            <div className="bg-gray-50 rounded-lg p-4">
              <p className="text-sm text-gray-500 mb-1">资质认证</p>
              <p className="text-lg font-bold">{supplier.certifications?.length || 0}项</p>
            </div>
          </div>

          {/* 详细信息 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* 左列 */}
            <div className="space-y-4">
              {/* 基本信息 */}
              <div>
                <h3 className="text-base font-medium text-gray-900 mb-3 flex items-center">
                  <Award className="w-4 h-4 mr-2" />
                  基本信息
                </h3>
                <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">统一信用代码</span>
                    <span className="text-sm text-gray-900">{supplier.credit_code || isMockData ? '（模拟数据）' : '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">法定代表人</span>
                    <span className="text-sm text-gray-900">{supplier.legal_person || '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">注册资本</span>
                    <span className="text-sm text-gray-900">{supplier.registered_capital || '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">成立日期</span>
                    <span className="text-sm text-gray-900">{supplier.established_date || '-'}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-sm text-gray-500">经营状态</span>
                    <span className={`text-sm font-medium ${
                      supplier.business_status === '存续' ? 'text-green-600' : 'text-red-600'
                    }`}>
                      {supplier.business_status || '-'}
                    </span>
                  </div>
                </div>
              </div>

              {/* 联系方式 */}
              <div>
                <h3 className="text-base font-medium text-gray-900 mb-3">联系方式</h3>
                <div className="bg-gray-50 rounded-lg p-4 space-y-2">
                  {supplier.contact?.phone && (
                    <div className="flex items-center space-x-2 text-sm">
                      <Phone className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-900">{supplier.contact.phone}</span>
                    </div>
                  )}
                  {supplier.contact?.email && (
                    <div className="flex items-center space-x-2 text-sm">
                      <Mail className="w-4 h-4 text-gray-400" />
                      <span className="text-gray-900">{supplier.contact.email}</span>
                    </div>
                  )}
                  {supplier.address && (
                    <div className="flex items-start space-x-2 text-sm">
                      <MapPin className="w-4 h-4 text-gray-400 mt-0.5" />
                      <span className="text-gray-900">{supplier.address}</span>
                    </div>
                  )}
                  {!supplier.contact && (
                    <p className="text-sm text-gray-500 italic">
                      联系方式暂未提供（模拟数据）
                    </p>
                  )}
                </div>
              </div>
            </div>

            {/* 右列 */}
            <div className="space-y-4">
              {/* 资质证书 */}
              <div>
                <h3 className="text-base font-medium text-gray-900 mb-3 flex items-center">
                  <Shield className="w-4 h-4 mr-2" />
                  资质证书
                </h3>
                <div className="bg-gray-50 rounded-lg p-4">
                  {supplier.certifications && supplier.certifications.length > 0 ? (
                    <div className="flex flex-wrap gap-2">
                      {supplier.certifications.map((cert, index) => (
                        <span
                          key={index}
                          className="px-3 py-1.5 bg-blue-100 text-blue-800 text-sm rounded-full"
                        >
                          {cert}
                        </span>
                      ))}
                    </div>
                  ) : (
                    <p className="text-sm text-gray-500 italic">暂无资质信息</p>
                  )}
                </div>
              </div>

              {/* 优势与问题 */}
              <div className="space-y-4">
                <div>
                  <h3 className="text-base font-medium text-gray-900 mb-2">主要优势</h3>
                  {supplier.advantages && supplier.advantages.length > 0 ? (
                    <ul className="space-y-1">
                      {supplier.advantages.map((adv, index) => (
                        <li key={index} className="text-sm text-green-700">
                          • {adv}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-gray-500 italic">暂无优势信息</p>
                  )}
                </div>

                <div>
                  <h3 className="text-base font-medium text-gray-900 mb-2">主要问题</h3>
                  {supplier.issues && supplier.issues.length > 0 ? (
                    <ul className="space-y-1">
                      {supplier.issues.map((issue, index) => (
                        <li key={index} className="text-sm text-orange-700">
                          • {issue}
                        </li>
                      ))}
                    </ul>
                  ) : (
                    <p className="text-sm text-gray-500 italic">暂无问题信息</p>
                  )}
                </div>
              </div>
            </div>
          </div>

          {/* 经营范围 */}
          {supplier.business_scope && (
            <div>
              <h3 className="text-base font-medium text-gray-900 mb-2">经营范围</h3>
              <div className="bg-gray-50 rounded-lg p-4">
                <p className="text-sm text-gray-900">{supplier.business_scope}</p>
              </div>
            </div>
          )}
        </div>

        {/* Footer */}
        {isMockData && (
          <div className="px-6 py-4 bg-yellow-50 border-t border-yellow-200">
            <p className="text-sm text-yellow-800">
              <span className="font-medium">注意：</span>
              当前显示为模拟数据。
            </p>
          </div>
        )}
      </div>
    </div>
  )
}