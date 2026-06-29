import { ExternalLink, Package, Clock, Box } from 'lucide-react'
import { formatPrice } from '../../utils/helpers'

export function PriceCompare({ platforms, model }) {
  return (
    <div className="card">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">🏪 各平台价格对比</h3>

      <div className="overflow-x-auto">
        <table className="min-w-full divide-y divide-gray-200">
          <thead>
            <tr>
              <th className="table-header">平台</th>
              <th className="table-header">价格</th>
              <th className="table-header">折合人民币</th>
              <th className="table-header">库存</th>
              <th className="table-header">MOQ</th>
              <th className="table-header">交期</th>
              <th className="table-header">操作</th>
            </tr>
          </thead>
          <tbody className="divide-y divide-gray-200">
            {platforms.map((platform, index) => (
              <tr key={index} className="hover:bg-gray-50">
                <td className="table-cell font-medium">{platform.name}</td>
                <td className="table-cell">
                  {formatPrice(platform.price, platform.currency)}
                </td>
                <td className="table-cell font-medium">
                  {formatPrice(platform.price_cny || platform.price)}
                </td>
                <td className="table-cell">
                  <div className="flex items-center space-x-1">
                    <Box className="w-4 h-4 text-gray-400" />
                    {platform.stock ? (
                      <span className="text-green-600">{platform.stock}+</span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </div>
                </td>
                <td className="table-cell">{platform.moq}</td>
                <td className="table-cell">
                  <div className="flex items-center space-x-1">
                    <Clock className="w-4 h-4 text-gray-400" />
                    {platform.lead_time ? (
                      <span>{platform.lead_time}天</span>
                    ) : (
                      <span className="text-gray-400">-</span>
                    )}
                  </div>
                </td>
                <td className="table-cell">
                  {platform.product_url ? (
                    <a
                      href={platform.product_url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:text-blue-700 flex items-center"
                    >
                      查看 <ExternalLink className="w-4 h-4 ml-1" />
                    </a>
                  ) : (
                    <span className="text-gray-400">-</span>
                  )}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}