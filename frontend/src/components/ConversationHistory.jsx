import SourcesList from './SourcesList'
import { parseAnswer } from '../utils/parseAnswer'

const ConversationHistory = ({ conversations, onClearHistory }) => {
  if (!conversations || conversations.length === 0) {
    return null
  }

  return (
    <div className="space-y-4">
      {/* Clear History 버튼 */}
      <div className="flex justify-between items-center mb-4">
        <h2 className="text-xl font-bold text-gray-900">💬 대화 내역</h2>
        <button
          onClick={onClearHistory}
          className="text-sm text-red-600 hover:text-red-700 font-medium px-4 py-2 rounded-md hover:bg-red-50 transition-colors"
        >
          대화 초기화
        </button>
      </div>

      {/* 대화 목록 */}
      {conversations.map((conversation, index) => (
        <div key={index} className="bg-white rounded-lg shadow-sm border border-gray-200 overflow-hidden">
          {/* 사용자 질문 */}
          <div className="bg-blue-50 border-b border-gray-200 p-4">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-blue-600 rounded-full flex items-center justify-center text-white font-semibold">
                  Q
                </div>
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium text-gray-500 mb-1">질문</div>
                <p className="text-gray-900 whitespace-pre-wrap">{conversation.question}</p>
                {(conversation.material_code || conversation.procedure_code) && (
                  <div className="mt-2 text-sm text-gray-600">
                    {conversation.material_code && (
                      <>
                        <span className="font-medium">재료코드:</span> {conversation.material_code}
                      </>
                    )}
                    {conversation.material_code && conversation.procedure_code && ' | '}
                    {conversation.procedure_code && (
                      <>
                        <span className="font-medium">시술코드:</span> {conversation.procedure_code}
                      </>
                    )}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* AI 답변 */}
          <div className="p-4">
            <div className="flex items-start gap-3">
              <div className="flex-shrink-0">
                <div className="w-8 h-8 bg-green-600 rounded-full flex items-center justify-center text-white font-semibold">
                  A
                </div>
              </div>
              <div className="flex-1">
                <div className="text-sm font-medium text-gray-500 mb-2">답변</div>
                <div className="bg-gray-50 rounded-md p-4 border-l-3 border-green-500">
                  {parseAnswer(conversation.answer).map((section, sIndex) => {
                    if (section.type === 'table') {
                      return (
                        <div key={sIndex} className="my-4 overflow-x-auto">
                          <table className="min-w-full border-collapse border border-gray-300 text-sm">
                            <thead>
                              <tr className="bg-blue-50">
                                {section.content.headers.map((header, hIndex) => (
                                  <th
                                    key={hIndex}
                                    className="border border-gray-300 px-4 py-2 text-left font-semibold text-gray-700"
                                  >
                                    {header}
                                  </th>
                                ))}
                              </tr>
                            </thead>
                            <tbody>
                              {section.content.rows.map((row, rIndex) => (
                                <tr key={rIndex} className={rIndex % 2 === 0 ? 'bg-white' : 'bg-gray-50'}>
                                  {row.map((cell, cIndex) => (
                                    <td
                                      key={cIndex}
                                      className="border border-gray-300 px-4 py-2 text-gray-800"
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
                          className="whitespace-pre-wrap font-sans text-gray-800 leading-relaxed text-sm mb-4"
                        >
                          {section.content}
                        </pre>
                      )
                    }
                  })}
                </div>

                {/* 참고 문서 */}
                {conversation.sources && conversation.sources.length > 0 && (
                  <div className="mt-4 pt-4 border-t border-gray-200">
                    <SourcesList sources={conversation.sources} />
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>
      ))}
    </div>
  )
}

export default ConversationHistory

