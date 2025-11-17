import { useState } from 'react'
import { queryInsuranceCriteria } from '../api/client'

/**
 * 보험 인정기준 질의 커스텀 훅
 */
export const useInsuranceQuery = () => {
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [result, setResult] = useState(null)

  const submitQuery = async (question, conversationHistory = null) => {
    setLoading(true)
    setError(null)
    setResult(null)

    try {
      const data = await queryInsuranceCriteria(question, conversationHistory)
      setResult(data)
      return data
    } catch (err) {
      const errorMessage = err.message || '알 수 없는 오류가 발생했습니다.'
      setError(errorMessage)
      throw err
    } finally {
      setLoading(false)
    }
  }

  const reset = () => {
    setLoading(false)
    setError(null)
    setResult(null)
  }

  return {
    loading,
    error,
    result,
    submitQuery,
    reset,
  }
}

export default useInsuranceQuery

