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
    materialCode: '',
    procedureCode: '',
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
        formData.materialCode || null,
        formData.procedureCode || null,
        formData.question,
        apiConversationHistory.length > 0 ? apiConversationHistory : null,
        excludedSources.length > 0 ? excludedSources : null
      )
      
      // 쿼리 정보도 함께 전달 (재검색용)
      const queryInfo = {
        materialCode: formData.materialCode,
        procedureCode: formData.procedureCode,
        question: formData.question
      }
      onSubmit(result, queryInfo)
      
      // 질문 입력란 초기화 (코드는 유지)
      setFormData(prev => ({
        ...prev,
        question: ''
      }))
    } catch (error) {
      onError(error.message)
    } finally {
      onLoading(false)
    }
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-5">
      {/* 질문 입력 (필수) */}
      <div>
        <label htmlFor="question" className="block text-sm font-medium text-gray-700 mb-1.5">
          질문 <span className="text-red-500">*</span>
        </label>
        <textarea
          id="question"
          name="question"
          value={formData.question}
          onChange={handleChange}
          placeholder="예: 좌측 혈관에만 수가신청을 한경우 수가 신청을 어떻게 해야해"
          rows="3"
          className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors outline-none resize-none"
          required
        />
        <p className="mt-1 text-xs text-gray-500">
          학습된 문서를 기반으로 답변합니다. 재료코드/시술코드는 선택사항입니다.
        </p>
      </div>

      {/* 재료코드 입력 (선택사항) */}
      <div>
        <label htmlFor="materialCode" className="block text-sm font-medium text-gray-700 mb-1.5">
          재료코드 <span className="text-gray-400 text-xs">(선택사항)</span>
        </label>
        <input
          type="text"
          id="materialCode"
          name="materialCode"
          value={formData.materialCode}
          onChange={handleChange}
          placeholder="예: A12345"
          className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors outline-none"
        />
      </div>

      {/* 시술코드 입력 (선택사항) */}
      <div>
        <label htmlFor="procedureCode" className="block text-sm font-medium text-gray-700 mb-1.5">
          시술코드 <span className="text-gray-400 text-xs">(선택사항)</span>
        </label>
        <input
          type="text"
          id="procedureCode"
          name="procedureCode"
          value={formData.procedureCode}
          onChange={handleChange}
          placeholder="예: N2095"
          className="w-full px-4 py-2.5 border border-gray-300 rounded-md focus:border-blue-500 focus:ring-1 focus:ring-blue-500 transition-colors outline-none"
        />
      </div>

      {/* 제출 버튼 */}
      <button
        type="submit"
        className="w-full bg-blue-600 hover:bg-blue-700 text-white font-medium py-3 px-6 rounded-md shadow-sm hover:shadow transition-all duration-150"
      >
        질문하기
      </button>
    </form>
  )
}

export default QueryForm
