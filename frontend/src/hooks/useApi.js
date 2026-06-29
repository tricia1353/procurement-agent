import { useState, useCallback } from 'react'

/**
 * API 调用 hook
 *
 * 使用方式：
 * const { data, loading, error, execute } = useApi(apiFunction)
 *
 * const result = await execute(params)
 */
export function useApi(apiFunction) {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const execute = useCallback(async (...args) => {
    setLoading(true)
    setError(null)

    try {
      const result = await apiFunction(...args)
      setData(result)
      return result
    } catch (err) {
      const errorMessage = err.response?.data?.detail || err.message || '请求失败'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }, [apiFunction])

  const reset = useCallback(() => {
    setData(null)
    setError(null)
    setLoading(false)
  }, [])

  return { data, loading, error, execute, reset }
}