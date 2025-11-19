import SourcesList from './SourcesList'
import { parseAnswer } from '../utils/parseAnswer'

const ConversationHistory = ({ 
  conversations, 
  onClearHistory, 
  excludedSources = [], 
  onExcludeSource, 
  onRequery 
}) => {
  if (!conversations || conversations.length === 0) {
    return null
  }

  // 최신 대화가 위에 표시되도록 역순으로 정렬
  const reversedConversations = [...conversations].reverse()
  
  // 역순이므로 최신 대화는 index 0
  const isLastConversation = (index) => index === 0

  return (
    <div className="space-y-8">
      {/* 대화 목록 */}
      {reversedConversations.map((conversation, index) => (
        <div key={index} className="space-y-6">
          {/* 사용자 메시지 (오른쪽) */}
          <div className="flex justify-end gap-3">
            <div className="max-w-5xl flex-1">
              <div className="bg-stone-100 rounded-2xl rounded-tr-sm px-5 py-4 shadow-sm">
                <p className="text-stone-900 text-base whitespace-pre-wrap leading-relaxed">{conversation.question}</p>
                {(conversation.material_code || conversation.procedure_code) && (
                  <div className="mt-3 pt-3 border-t border-stone-200 text-xs text-stone-600">
                    {conversation.material_code && (
                      <span className="mr-3">
                        <span className="font-medium">재료:</span> {conversation.material_code}
                      </span>
                    )}
                    {conversation.procedure_code && (
                      <span>
                        <span className="font-medium">시술:</span> {conversation.procedure_code}
                      </span>
                    )}
                  </div>
                )}
              </div>
              <div className="text-xs text-stone-400 mt-2 text-right">사용자</div>
            </div>
            {/* 사용자 프로필 이미지 */}
            <div className="flex-shrink-0">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-stone-400 to-stone-600 flex items-center justify-center text-white font-semibold shadow-md">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path fillRule="evenodd" d="M10 9a3 3 0 100-6 3 3 0 000 6zm-7 9a7 7 0 1114 0H3z" clipRule="evenodd" />
                </svg>
              </div>
            </div>
          </div>

          {/* AI 답변 (왼쪽) */}
          <div className="flex justify-start gap-3">
            {/* AI 프로필 이미지 */}
            <div className="flex-shrink-0">
              <div className="w-10 h-10 rounded-full bg-gradient-to-br from-blue-500 to-purple-600 flex items-center justify-center text-white font-bold shadow-md">
                <svg className="w-6 h-6" fill="currentColor" viewBox="0 0 20 20">
                  <path d="M13 7H7v6h6V7z" />
                  <path fillRule="evenodd" d="M7 2a1 1 0 012 0v1h2V2a1 1 0 112 0v1h2a2 2 0 012 2v2h1a1 1 0 110 2h-1v2h1a1 1 0 110 2h-1v2a2 2 0 01-2 2h-2v1a1 1 0 11-2 0v-1H9v1a1 1 0 11-2 0v-1H5a2 2 0 01-2-2v-2H2a1 1 0 110-2h1V9H2a1 1 0 010-2h1V5a2 2 0 012-2h2V2zM5 5h10v10H5V5z" clipRule="evenodd" />
                </svg>
              </div>
            </div>

            <div className="max-w-5xl flex-1">
              <div className="bg-white rounded-2xl rounded-tl-sm px-5 py-4 shadow-md border border-stone-200">
                {parseAnswer(conversation.answer).map((section, sIndex) => {
                  if (section.type === 'table') {
                    return (
                      <div key={sIndex} className="my-4 overflow-x-auto">
                        <table className="min-w-full border-collapse border border-stone-300 text-sm">
                          <thead>
                            <tr className="bg-stone-50">
                              {section.content.headers.map((header, hIndex) => (
                                <th
                                  key={hIndex}
                                  className="border border-stone-300 px-4 py-2 text-left font-semibold text-stone-700"
                                >
                                  {header}
                                </th>
                              ))}
                            </tr>
                          </thead>
                          <tbody>
                            {section.content.rows.map((row, rIndex) => (
                              <tr key={rIndex} className={rIndex % 2 === 0 ? 'bg-white' : 'bg-stone-50'}>
                                {row.map((cell, cIndex) => (
                                  <td
                                    key={cIndex}
                                    className="border border-stone-300 px-4 py-2 text-stone-800"
                                  >
                                    {cell}
                                  </td>
                                ))}
                              </tr>
                            ))}
                          </tbody>
                        </table>
                      </div>
                    )
                  } else {
                    return (
                      <pre
                        key={sIndex}
                        className="whitespace-pre-wrap font-sans text-stone-800 leading-relaxed text-base"
                      >
                        {section.content}
                      </pre>
                    )
                  }
                })}
              </div>

              <div className="text-xs text-stone-400 mt-2">AI 상담원</div>

              {/* 참고 문서 */}
              {conversation.sources && conversation.sources.length > 0 && (
                <div className="mt-4 p-4 bg-amber-50 rounded-xl border border-amber-200 shadow-sm">
                  <SourcesList 
                    sources={conversation.sources}
                    excludedSources={isLastConversation(index) ? excludedSources : []}
                    onExclude={isLastConversation(index) ? onExcludeSource : null}
                    onRequery={isLastConversation(index) ? onRequery : null}
                  />
                </div>
              )}
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default ConversationHistory
