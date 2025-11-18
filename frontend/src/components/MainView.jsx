import { useState } from 'react'
import { queryInsuranceCriteria } from '../api/client'
import ConversationHistory from './ConversationHistory'
import LoadingSpinner from './LoadingSpinner'

function MainView() {
  const [query, setQuery] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [conversations, setConversations] = useState([])
  const [excludedSources, setExcludedSources] = useState([])
  const [lastQuery, setLastQuery] = useState(null)

  const handleSubmit = async (e) => {
    e.preventDefault()
    if (!query.trim() || loading) return

    const currentQuery = query
    setLoading(true)
    setLastQuery({ question: currentQuery })

    try {
      // 대화 히스토리를 API 형식으로 변환
      const apiConversationHistory = conversations.map(conv => [
        { role: 'user', content: conv.question },
        { role: 'assistant', content: conv.answer }
      ]).flat()

      const response = await queryInsuranceCriteria(
        currentQuery,
        apiConversationHistory.length > 0 ? apiConversationHistory : null,
        excludedSources
      )
      
      setConversations(prev => [...prev, response])
      setQuery('')
      setError(null)
    } catch (err) {
      console.error('Error:', err)
      setError(err.message || '오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }

  const handleClearHistory = () => {
    setConversations([])
    setQuery('')
    setError(null)
    setExcludedSources([])
    setLastQuery(null)
  }

  const handleExcludeSource = (sourceText) => {
    setExcludedSources(prev => [...prev, sourceText])
  }

  const handleRequery = async () => {
    if (!lastQuery || excludedSources.length === 0) return
    
    setLoading(true)
    try {
      // 대화 히스토리를 API 형식으로 변환
      const apiConversationHistory = conversations.map(conv => [
        { role: 'user', content: conv.question },
        { role: 'assistant', content: conv.answer }
      ]).flat()

      const result = await queryInsuranceCriteria(
        lastQuery.question,
        apiConversationHistory.length > 0 ? apiConversationHistory : null,
        excludedSources
      )
      
      setConversations(prev => [...prev, result])
      setExcludedSources([]) // 재검색 후 제외 목록 초기화
      setError(null)
    } catch (err) {
      setError(err.message || '오류가 발생했습니다.')
    } finally {
      setLoading(false)
    }
  }

  // 대화가 시작되었는지 여부
  const hasConversations = conversations.length > 0

  return (
    <div className="flex flex-col h-screen">
      {/* 검색창 영역 - 대화 전: 중앙 / 대화 후: 상단 */}
      <div
        className={`transition-all duration-700 ease-out ${
          hasConversations
            ? 'bg-white border-b border-stone-200 shadow-md'
            : 'flex-1 flex items-center justify-center'
        }`}
      >
        <div className={`${hasConversations ? 'max-w-6xl w-full mx-auto p-4' : 'w-full max-w-2xl px-4'}`}>
          {/* 대화 시작 후 헤더 정보 */}
          {hasConversations && (
            <div className="flex items-center justify-between mb-3 animate-fadeIn">
              <h1 className="text-xl font-bold text-transparent bg-clip-text bg-gradient-to-r from-stone-800 to-stone-600">
                AI로 보는 보험 삭감 예측 RAG
              </h1>
              <button
                onClick={handleClearHistory}
                className="px-4 py-2 bg-stone-100 hover:bg-stone-200 text-stone-700 rounded-lg text-sm font-medium transition-colors duration-200"
              >
                대화 초기화
              </button>
            </div>
          )}

          {/* 검색창 */}
          <form onSubmit={handleSubmit} className="relative">
            <div
              className={`bg-white rounded-full shadow-2xl border border-stone-200 flex items-center gap-3 transition-all duration-500 ${
                hasConversations
                  ? 'px-5 py-3 hover:shadow-lg'
                  : 'px-5 py-3 hover:shadow-3xl hover:scale-[1.02]'
              }`}
            >
              <input
                type="text"
                value={query}
                onChange={(e) => setQuery(e.target.value)}
                placeholder={hasConversations ? "추가 질문을 입력하세요..." : "보험 인정기준에 대해 질문하세요..."}
                className={`flex-1 outline-none text-stone-700 placeholder-stone-400 bg-transparent transition-all duration-300 ${
                  hasConversations ? 'text-base' : 'text-base'
                }`}
                disabled={loading}
              />
              <button
                type="submit"
                disabled={!query.trim() || loading}
                className={`rounded-full transition-all duration-200 ${
                  hasConversations ? 'p-2' : 'p-2.5'
                } ${
                  query.trim() && !loading
                    ? 'bg-gradient-to-r from-stone-700 to-stone-800 hover:from-stone-800 hover:to-stone-900 text-white shadow-lg hover:shadow-xl'
                    : 'bg-stone-200 text-stone-400 cursor-not-allowed'
                }`}
              >
                {loading ? (
                  <svg className={hasConversations ? "animate-spin h-5 w-5" : "animate-spin h-5 w-5"} xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                    <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                    <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                  </svg>
                ) : (
                  <svg className={hasConversations ? "h-5 w-5" : "h-5 w-5"} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
                  </svg>
                )}
              </button>
            </div>
          </form>

        </div>
      </div>

      {/* 대화 시작 전 Footer - 화면 맨 아래 고정 */}
      {!hasConversations && (
        <div className="py-4 bg-stone-50 border-t border-stone-200">
          <div className="max-w-2xl mx-auto px-4 text-center">
            <p className="text-base text-stone-600 font-semibold mb-1">
              중앙대학교광명병원 AI 프롬프톤 & AWS supported
            </p>
            <p className="text-xs text-stone-500">
              © 2025 Insurance RAG System. All rights reserved.
            </p>
          </div>
        </div>
      )}

      {/* 대화 히스토리 영역 - 답변이 있을 때만 표시 */}
      {hasConversations && (
        <div className="flex-1 overflow-y-auto p-4 sm:p-6 bg-stone-50/30">
          <div className="max-w-6xl mx-auto">
            {/* Error State */}
            {error && (
              <div className="mb-4 animate-slideInDown">
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-start gap-3">
                    <svg className="h-5 w-5 text-red-600 mt-0.5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <div className="flex-1">
                      <h3 className="text-sm font-semibold text-red-900 mb-1">오류 발생</h3>
                      <p className="text-sm text-red-700">{error}</p>
                    </div>
                  </div>
                </div>
              </div>
            )}

            {/* Conversation History - 애니메이션 적용 */}
            <div className="animate-slideInDown">
              <ConversationHistory 
                conversations={conversations}
                onClearHistory={handleClearHistory}
                excludedSources={excludedSources}
                onExcludeSource={handleExcludeSource}
                onRequery={handleRequery}
              />
            </div>

            {/* Loading State */}
            {loading && (
              <div className="animate-slideInDown">
                <LoadingSpinner />
              </div>
            )}

            {/* Footer - 대화 중일 때 하단에 표시 */}
            <div className="mt-8 pt-4 border-t border-stone-200 text-center">
              <p className="text-base text-stone-600 font-semibold mb-1">
                중앙대학교광명병원 AI 프롬프톤 & AWS supported
              </p>
              <p className="text-xs text-stone-500">
                © 2025 Insurance RAG System. All rights reserved.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}

export default MainView
