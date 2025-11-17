const SourcesList = ({ sources, excludedSources = [], onExclude, onRequery }) => {
  if (!sources || sources.length === 0) return null

  return (
    <div>
      <div className="flex items-center justify-between mb-3">
        <h3 className="text-lg font-bold text-gray-800 flex items-center gap-2">
          📚 참고 문서
        </h3>
        {excludedSources.length > 0 && onRequery && (
          <button
            onClick={onRequery}
            className="px-4 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors text-sm font-medium"
          >
            🔄 다시 검색 ({excludedSources.length}개 제외)
          </button>
        )}
      </div>
      <div className="space-y-3">
        {sources.map((source, index) => {
          const isExcluded = excludedSources.includes(source.text)
          return (
            <div
              key={index}
              className={`rounded-md p-4 border transition-colors ${
                isExcluded 
                  ? 'bg-red-50 border-red-200 opacity-60' 
                  : 'bg-gray-50 border-gray-200 hover:border-gray-300'
              }`}
            >
              <div className="flex items-start justify-between gap-4">
                <div className="flex-1">
                <div className="font-semibold text-gray-900 text-sm mb-1">
                  [{index + 1}] {source.type || '문서'}
                </div>
                {source.pdf_title && (
                  <div className="text-sm font-medium text-gray-700 mb-1">
                    {source.pdf_title}
                  </div>
                )}
                {source.filename && source.filename !== 'Unknown' && (
                  <div className="text-xs text-gray-500 mb-1 truncate" title={source.filename}>
                    📄 {source.filename}
                  </div>
                )}
                {(source.재료명 || source.재료코드) && (
                  <div className="text-sm text-gray-600">
                    {source.재료명 && <span className="font-medium">{source.재료명}</span>}
                    {source.재료코드 && <span className="text-gray-400"> ({source.재료코드})</span>}
                  </div>
                )}
                {(source.시술명 || source.시술코드) && (
                  <div className="text-sm text-gray-600 mt-0.5">
                    {source.시술명 && <span className="font-medium">{source.시술명}</span>}
                    {source.시술코드 && <span className="text-gray-400"> ({source.시술코드})</span>}
                  </div>
                )}
              </div>
              <div className="flex-shrink-0 flex items-center gap-2">
                <span className="inline-flex items-center px-2.5 py-1 rounded text-xs font-medium bg-gray-200 text-gray-700">
                  유사도: {(1 / (1 + source.score)).toFixed(3)}
                </span>
                {onExclude && !isExcluded && (
                  <button
                    onClick={() => onExclude(source.text)}
                    className="px-3 py-1 bg-red-100 text-red-700 rounded text-xs font-medium hover:bg-red-200 transition-colors"
                    title="이 문서를 제외하고 다시 검색"
                  >
                    ✕ 제외
                  </button>
                )}
                {isExcluded && (
                  <span className="px-3 py-1 bg-red-200 text-red-800 rounded text-xs font-medium">
                    제외됨
                  </span>
                )}
              </div>
            </div>
          </div>
        )})}
      </div>
    </div>
  )
}

export default SourcesList
