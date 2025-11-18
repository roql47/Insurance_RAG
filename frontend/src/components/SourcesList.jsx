const SourcesList = ({ sources, excludedSources = [], onExclude, onRequery }) => {
  if (!sources || sources.length === 0) return null

  // 유사도가 높은 순으로 정렬 (score가 작을수록 유사도가 높음)
  const sortedSources = [...sources].sort((a, b) => {
    const similarityA = 1 / (1 + a.score)
    const similarityB = 1 / (1 + b.score)
    return similarityB - similarityA  // 높은 유사도가 먼저 오도록
  })

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-base font-bold text-stone-800 flex items-center gap-2">
          📚 참고 문서
        </h3>
        {excludedSources.length > 0 && onRequery && (
          <button
            onClick={onRequery}
            className="px-3 py-1.5 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-xs font-medium shadow-sm"
          >
            🔄 다시 검색 ({excludedSources.length}개 제외)
          </button>
        )}
      </div>
      <div className="space-y-3">
        {sortedSources.map((source, index) => {
          const isExcluded = excludedSources.includes(source.text)
          return (
            <div
              key={index}
              className={`rounded-lg p-3 border transition-colors ${
                isExcluded 
                  ? 'bg-red-50 border-red-200 opacity-60' 
                  : 'bg-white border-stone-200 hover:border-stone-300 hover:shadow-sm'
              }`}
            >
              <div className="space-y-2">
                {/* 문서 정보 */}
                <div>
                  <div className="font-semibold text-stone-900 text-sm mb-1">
                    [{index + 1}] {source.type || '문서'}
                  </div>
                  {source.pdf_title && (
                    <div className="text-sm font-medium text-stone-700 mb-1">
                      {source.pdf_title}
                    </div>
                  )}
                  {source.filename && source.filename !== 'Unknown' && (
                    <div className="text-xs text-stone-500 mb-1 truncate" title={source.filename}>
                      📄 {source.filename}
                    </div>
                  )}
                  {(source.재료명 || source.재료코드) && (
                    <div className="text-sm text-stone-600">
                      {source.재료명 && <span className="font-medium">{source.재료명}</span>}
                      {source.재료코드 && <span className="text-stone-400"> ({source.재료코드})</span>}
                    </div>
                  )}
                  {(source.시술명 || source.시술코드) && (
                    <div className="text-sm text-stone-600 mt-0.5">
                      {source.시술명 && <span className="font-medium">{source.시술명}</span>}
                      {source.시술코드 && <span className="text-stone-400"> ({source.시술코드})</span>}
                    </div>
                  )}
                </div>

                {/* 유사도와 버튼 - 별도 행 */}
                <div className="flex items-center justify-between gap-2 pt-2 border-t border-stone-100">
                  <span className="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-stone-100 text-stone-700">
                    유사도: {(1 / (1 + source.score)).toFixed(3)}
                  </span>
                  {onExclude && !isExcluded && (
                    <button
                      onClick={() => onExclude(source.text)}
                      className="px-2.5 py-1 bg-red-100 text-red-700 rounded text-xs font-medium hover:bg-red-200 transition-colors flex-shrink-0"
                      title="이 문서를 제외하고 다시 검색"
                    >
                      ✕ 제외
                    </button>
                  )}
                  {isExcluded && (
                    <span className="px-2.5 py-1 bg-red-200 text-red-800 rounded text-xs font-medium flex-shrink-0">
                      제외됨
                    </span>
                  )}
                </div>
              </div>
            </div>
          )
        })}
      </div>
    </div>
  )
}

export default SourcesList
