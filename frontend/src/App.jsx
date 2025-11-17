import { useState } from 'react'
import QueryForm from './components/QueryForm'
import ResultDisplay from './components/ResultDisplay'
import LoadingSpinner from './components/LoadingSpinner'
import ConversationHistory from './components/ConversationHistory'
import { queryInsuranceCriteria } from './api/client'

function App() {
  const [result, setResult] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [conversations, setConversations] = useState([]) // 대화 히스토리
  const [excludedSources, setExcludedSources] = useState([]) // 제외된 문서 텍스트 목록
  const [lastQuery, setLastQuery] = useState(null) // 마지막 쿼리 정보 (재검색용)

  const handleQuerySubmit = (queryResult, queryInfo) => {
    setResult(queryResult)
    setError(null)
    
    // 마지막 쿼리 정보 저장 (재검색용)
    if (queryInfo) {
      setLastQuery(queryInfo)
    }
    
    // 대화 히스토리에 추가
    setConversations(prev => [...prev, queryResult])
  }

  const handleLoading = (isLoading) => {
    setLoading(isLoading)
  }

  const handleError = (errorMessage) => {
    setError(errorMessage)
    setResult(null)
  }

  const handleClearHistory = () => {
    setConversations([])
    setResult(null)
    setError(null)
    setExcludedSources([])
    setLastQuery(null)
  }

  const handleExcludeSource = (sourceText) => {
    setExcludedSources(prev => [...prev, sourceText])
  }

  const handleRequery = async () => {
    if (!lastQuery || excludedSources.length === 0) return
    
    handleLoading(true)
    try {
      // 대화 히스토리를 API 형식으로 변환
      const apiConversationHistory = conversations.map(conv => [
        { role: 'user', content: conv.question },
        { role: 'assistant', content: conv.answer }
      ]).flat()

      const result = await queryInsuranceCriteria(
        lastQuery.materialCode || null,
        lastQuery.procedureCode || null,
        lastQuery.question,
        apiConversationHistory.length > 0 ? apiConversationHistory : null,
        excludedSources
      )
      
      setResult(result)
      setConversations(prev => [...prev, result])
      setExcludedSources([]) // 재검색 후 제외 목록 초기화
      setError(null)
    } catch (error) {
      handleError(error.message)
    } finally {
      handleLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gray-50 p-4 sm:p-6 lg:p-8">
      <div className="max-w-5xl mx-auto">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-sm overflow-hidden mb-6 border border-gray-200">
          <div className="bg-white border-b border-gray-200 p-6 sm:p-8">
            <div className="flex items-center gap-3 mb-2">
              <span className="text-3xl">🏥</span>
              <div>
                <h1 className="text-2xl sm:text-3xl font-bold text-gray-900">
                  보험 인정기준 RAG 시스템
                </h1>
                <p className="mt-1 text-gray-600 text-sm sm:text-base">
                  심평원 보험 인정기준 기반 삭감 여부 판단
                </p>
              </div>
            </div>
          </div>

          {/* Query Form */}
          <div className="p-6 sm:p-8">
            <QueryForm
              onSubmit={handleQuerySubmit}
              onLoading={handleLoading}
              onError={handleError}
              conversationHistory={conversations}
              excludedSources={excludedSources}
            />
          </div>
        </div>

        {/* Loading State */}
        {loading && <LoadingSpinner />}

        {/* Error State */}
        {error && (
          <div className="bg-white rounded-lg p-6 sm:p-8 shadow-sm border border-red-300 mb-6">
            <div className="flex items-start gap-4">
              <div className="flex-shrink-0">
                <svg className="h-6 w-6 text-red-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
              <div className="flex-1">
                <h3 className="text-lg font-semibold text-red-900 mb-1">오류 발생</h3>
                <p className="text-red-700 whitespace-pre-wrap text-sm">{error}</p>
              </div>
            </div>
          </div>
        )}

        {/* Conversation History */}
        {conversations.length > 0 && !loading && (
          <ConversationHistory 
            conversations={conversations}
            onClearHistory={handleClearHistory}
            excludedSources={excludedSources}
            onExcludeSource={handleExcludeSource}
            onRequery={handleRequery}
          />
        )}

        {/* Footer */}
        <div className="mt-8 text-center">
          <p className="text-gray-500 text-sm">
            © 2025 보험 인정기준 RAG 시스템 | Powered by Claude 4.5 Haiku & AWS Bedrock
          </p>
        </div>
      </div>
    </div>
  )
}

export default App
