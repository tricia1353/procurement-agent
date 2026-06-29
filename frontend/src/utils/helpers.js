/**
 * 工具函数
 */

/**
 * 格式化价格（不自动换算）
 * 直接返回原始价格和币种
 */
export function formatPrice(price, currency = null) {
  if (price === null || price === undefined || price === '') return '-'

  // 如果价格已经是字符串（如 "¥60.68"），直接返回
  if (typeof price === 'string') {
    return price
  }

  // 如果是数字，转换为2位小数
  const formatted = parseFloat(price).toFixed(2)

  // 如果提供了币种，添加符号
  const symbols = {
    CNY: '¥',
    RMB: '¥',
    USD: '$',
    EUR: '€'
  }

  const symbol = currency ? (symbols[currency.toUpperCase()] || '') : ''
  return `${symbol}${formatted}`
}

/**
 * 格式化价格梯度
 * 返回完整的 "价格 币种" 格式
 */
export function formatPriceBreak(priceBreak) {
  if (!priceBreak) return '-'
  const price = priceBreak.price || '-'
  const currency = priceBreak.currency || ''
  return currency ? `${price} ${currency}` : price
}

/**
 * 格式化日期
 */
export function formatDate(date, format = 'YYYY-MM-DD') {
  if (!date) return '-'

  const d = new Date(date)
  const year = d.getFullYear()
  const month = String(d.getMonth() + 1).padStart(2, '0')
  const day = String(d.getDate()).padStart(2, '0')
  const hours = String(d.getHours()).padStart(2, '0')
  const minutes = String(d.getMinutes()).padStart(2, '0')

  return format
    .replace('YYYY', year)
    .replace('MM', month)
    .replace('DD', day)
    .replace('HH', hours)
    .replace('mm', minutes)
}

/**
 * 格式化数字
 */
export function formatNumber(num) {
  if (num === null || num === undefined) return '-'
  if (num >= 10000) {
    return `${(num / 10000).toFixed(1)}万`
  }
  return num.toLocaleString()
}

/**
 * 解析 LLM 返回的 JSON
 */
export function safeJsonParse(str) {
  if (!str) return null

  try {
    // 去除 markdown 代码块
    let content = str.trim()
    if (content.startsWith('```json')) content = content.slice(7)
    if (content.startsWith('```')) content = content.slice(3)
    if (content.endsWith('```')) content = content.slice(0, -3)

    return JSON.parse(content.trim())
  } catch {
    return null
  }
}

/**
 * 防抖函数
 */
export function debounce(func, wait) {
  let timeout
  return function executedFunction(...args) {
    const later = () => {
      clearTimeout(timeout)
      func(...args)
    }
    clearTimeout(timeout)
    timeout = setTimeout(later, wait)
  }
}

/**
 * 复制到剪贴板
 */
export async function copyToClipboard(text) {
  try {
    await navigator.clipboard.writeText(text)
    return true
  } catch {
    // 降级方案
    const textarea = document.createElement('textarea')
    textarea.value = text
    document.body.appendChild(textarea)
    textarea.select()
    document.execCommand('copy')
    document.body.removeChild(textarea)
    return true
  }
}

/**
 * 下载文件
 */
export function downloadFile(content, filename, type = 'text/plain') {
  const blob = new Blob([content], { type })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = filename
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
}

/**
 * 趋势颜色
 */
export function getTrendColor(trend) {
  if (!trend) return 'text-gray-500'
  const t = trend.toLowerCase()
  if (t.includes('下降') || t.includes('down')) return 'text-green-600'
  if (t.includes('上涨') || t.includes('up')) return 'text-red-600'
  return 'text-gray-500'
}

/**
 * 风险等级颜色
 */
export function getRiskColor(risk) {
  if (!risk) return 'bg-gray-100 text-gray-800'
  const r = risk.toLowerCase()
  if (r.includes('低')) return 'bg-green-100 text-green-800'
  if (r.includes('中')) return 'bg-yellow-100 text-yellow-800'
  if (r.includes('高')) return 'bg-red-100 text-red-800'
  return 'bg-gray-100 text-gray-800'
}

/**
 * 从价格字符串提取数值
 */
export function extractPriceValue(priceStr) {
  if (!priceStr) return 0
  const numStr = priceStr.replace(/[¥$€RMBUSDEURCNY]/g, '').trim()
  return parseFloat(numStr) || 0
}

/**
 * 获取币种符号
 */
export function getCurrencySymbol(currency) {
  const symbols = {
    CNY: '¥',
    RMB: '¥',
    USD: '$',
    EUR: '€',
    GBP: '£',
    JPY: '¥'
  }
  return symbols[currency?.toUpperCase()] || currency || ''
}