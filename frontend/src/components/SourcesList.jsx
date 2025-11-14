const SourcesList = ({ sources }) => {
  if (!sources || sources.length === 0) return null

  return (
    <div>
      <h3 className="text-lg font-bold text-gray-800 mb-3 flex items-center gap-2">
        📚 참고 문서
      </h3>
      <div className="space-y-3">
        {sources.map((source, index) => (
          <div
            key={index}
            className="bg-gray-50 rounded-md p-4 border border-gray-200 hover:border-gray-300 transition-colors"
          >
            <div className="flex items-start justify-between gap-4">
              <div className="flex-1">
                <div className="font-semibold text-gray-900 text-sm mb-1">
                  [{index + 1}] {source.type || '문서'}
                </div>
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
              <div className="flex-shrink-0">
                <span className="inline-flex items-center px-2.5 py-1 rounded text-xs font-medium bg-gray-200 text-gray-700">
                  유사도: {(1 / (1 + source.score)).toFixed(3)}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}

export default SourcesList
