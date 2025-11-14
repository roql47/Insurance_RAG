const LoadingSpinner = () => {
  return (
    <div className="bg-white rounded-lg shadow-sm p-8 text-center border border-gray-200 mb-6">
      <div className="flex flex-col items-center justify-center space-y-4">
        {/* 스피너 */}
        <div className="w-12 h-12 border-3 border-gray-200 border-t-blue-600 rounded-full animate-spin"></div>

        {/* 로딩 텍스트 */}
        <div className="space-y-1">
          <p className="text-base font-semibold text-gray-800">
            AI가 인정기준을 분석하고 있습니다...
          </p>
          <p className="text-sm text-gray-600">
            Claude 4.5 Haiku가 관련 문서를 검색하고 답변을 생성 중입니다
          </p>
        </div>

        {/* 진행 바 */}
        <div className="w-full max-w-md bg-gray-200 rounded-full h-1.5 overflow-hidden">
          <div className="h-full bg-blue-600 rounded-full animate-progress"></div>
        </div>
      </div>
    </div>
  )
}

export default LoadingSpinner
