import { useState } from 'react'
import { queryInsuranceCriteria } from '../api/client'

const QueryForm = ({ 
  onSubmit, 
  onLoading, 
  onError, 
  conversationHistory = [],
  excludedSources = []
}) => {
  const [formData, setFormData] = useState({
    question: '',
  })

  const handleChange = (e) => {
    const { name, value } = e.target
    setFormData((prev) => ({
      ...prev,
      [name]: value,
    }))
  }

  const handleSubmit = async (e) => {
    e.preventDefault()

    if (!formData.question) {
      onError('질문을 입력해주세요.')
      return
    }

    onLoading(true)
    try {
      // 대화 히스토리를 API 형식으로 변환
      const apiConversationHistory = conversationHistory.map(conv => [
        { role: 'user', content: conv.question },
        { role: 'assistant', content: conv.answer }
      ]).flat()

      const result = await queryInsuranceCriteria(
        formData.question,
        apiConversationHistory.length > 0 ? apiConversationHistory : null,
        excludedSources.length > 0 ? excludedSources : null
      )
      
      // 쿼리 정보도 함께 전달 (재검색용)
      const queryInfo = {
        question: formData.question
      }
      onSubmit(result, queryInfo)
      
      // 질문 입력란 초기화
      setFormData({
        question: ''
      })
    } catch (error) {
      onError(error.message)
    } finally {
      onLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="flex items-end gap-2">
      {/* 질문 입력 */}
      <div className="flex-1">
        <textarea
          id="question"
          name="question"
          value={formData.question}
          onChange={handleChange}
          placeholder="메시지를 입력하세요..."
          rows="1"
          className="w-full px-3 py-2 text-sm border border-stone-300 rounded-lg focus:border-stone-500 focus:ring-2 focus:ring-stone-200 transition-all outline-none resize-none bg-white"
          required
          onKeyDown={(e) => {
            if (e.key === 'Enter' && !e.shiftKey) {
              e.preventDefault()
              handleSubmit(e)
            }
          }}
        />
      </div>

      {/* 전송 버튼 */}
      <button
        type="submit"
        className="flex-shrink-0 bg-stone-700 hover:bg-stone-800 text-white p-2 rounded-lg transition-colors shadow-sm"
        aria-label="전송"
      >
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
        </svg>
      </button>
    </form>
  )
}

export default QueryForm
