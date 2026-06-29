import { MapPin, Star, Shield } from 'lucide-react'
import { getRiskColor } from '../../utils/helpers'

export function SupplierCard({ supplier, onViewDetail }) {
  return (
    <div className="card hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-3">
        <div className="flex-1">
          <div className="flex items-center gap-2">
            <h4 className="font-semibold text-gray-900">{supplier.name}</h4>
            {supplier.match_score >= 85 && (
              <Star className="w-4 h-4 text-yellow-400 fill-yellow-400" />
            )}
          </div>
          <p className="text-sm text-gray-500">{supplier.category}</p>
        </div>
        {supplier.match_score > 0 && (
          <div className="flex items-center gap-1">
            <div className={`text-xs font-bold px-2 py-1 rounded ${
              supplier.match_score >= 85 ? 'bg-green-100 text-green-800' :
              supplier.match_score >= 70 ? 'bg-yellow-100 text-yellow-800' :
              'bg-gray-100 text-gray-800'
            }`}>
              匹配 {supplier.match_score}
            </div>
          </div>
        )}
      </div>

      <div className="space-y-2 text-sm">
        <div className="flex items-center gap-2 text-gray-600">
          <MapPin className="w-4 h-4" />
          <span>{supplier.region}</span>
        </div>

        {supplier.source && (
          <div className="text-gray-500">
            来源: {supplier.source}
          </div>
        )}

        {supplier.certifications && supplier.certifications.length > 0 && (
          <div className="flex flex-wrap gap-1">
            {supplier.certifications.slice(0, 2).map((cert, index) => (
              <span
                key={index}
                className="px-2 py-0.5 bg-blue-100 text-blue-800 text-xs rounded"
              >
                {cert}
              </span>
            ))}
            {supplier.certifications.length > 2 && (
              <span className="text-xs text-gray-400">
                +{supplier.certifications.length - 2}
              </span>
            )}
          </div>
        )}

        {supplier.advantages && supplier.advantages.length > 0 && (
          <div className="text-green-600">
            <span className="font-medium">优势:</span>{' '}
            {supplier.advantages.slice(0, 2).join('、')}
          </div>
        )}

        {supplier.served_clients && supplier.served_clients.length > 0 && (
          <div className="text-gray-500 text-xs">
            客户: {supplier.served_clients.slice(0, 2).join('、')}
            {supplier.served_clients.length > 2 && ' 等'}
          </div>
        )}
      </div>

      <div className="mt-4 pt-4 border-t border-gray-100 flex justify-between items-center">
        <div className="flex items-center gap-2">
          <Shield className="w-3 h-3 text-gray-400" />
          <span className={`px-2 py-0.5 text-xs rounded ${getRiskColor(supplier.risk_level || '待确认')}`}>
            {supplier.risk_level || '待确认'}
          </span>
          {supplier.credit_score && (
            <span className="text-xs text-gray-400">
              信用: {supplier.credit_score}
            </span>
          )}
        </div>
        <button
          onClick={onViewDetail}
          className="text-blue-600 hover:text-blue-700 text-sm font-medium"
        >
          查看详情
        </button>
      </div>
    </div>
  )
}
