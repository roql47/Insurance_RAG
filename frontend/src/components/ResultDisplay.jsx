import SourcesList from './SourcesList'
import { parseAnswer } from '../utils/parseAnswer'

const ResultDisplay = ({ result, excludedSources = [], onExcludeSource, onRequery }) => {
  if (!result) return null

  // 답변 내용 파싱 (테이블과 일반 텍스트 구분)
  const parsedContent = parseAnswer(result.answer)

  return (
    <div className="bg-white rounded-lg shadow-sm overflow-hidden border border-gray-200 mb-6">
      {/* 결과 헤더 */}
      <div className="bg-white border-b border-gray-200 p-6">
        <h2 className="text-xl font-bold text-gray-900 flex items-center gap-2">
          📋 판단 결과
        </h2>
        {(result.material_code || result.procedure_code) && (
          <div className="mt-2 text-sm text-gray-600">
            {result.material_code && (
              <>
                <span className="font-medium">재료코드:</span> {result.material_code}
              </>
            )}
            {result.material_code && result.procedure_code && ' | '}
            {result.procedure_code && (
              <>
                <span className="font-medium">시술코드:</span> {result.procedure_code}
              </>
            )}
          </div>
        )}
        <div className="mt-1 text-sm text-gray-500">
          <span className="font-medium">질문:</span> {result.question}
        </div>
      </div>

      {/* 답변 내용 */}
      <div className="p-6">
        <div className="bg-gray-50 rounded-md p-5 border-l-3 border-blue-500">
          {parsedContent.map((section, index) => {
            if (section.type === 'table') {
              return (
                <div key={index} className="my-4 overflow-x-auto">
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
                  key={index}
                  className="whitespace-pre-wrap font-sans text-gray-800 leading-relaxed text-sm mb-4"
                >
                  {section.content}
                </pre>
              )
            }
          })}
        </div>

        {/* 참고 문서 */}
        {result.sources && result.sources.length > 0 && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <SourcesList 
              sources={result.sources} 
              excludedSources={excludedSources}
              onExclude={onExcludeSource}
              onRequery={onRequery}
            />
          </div>
        )}
      </div>
    </div>
  )
}

export default ResultDisplay
