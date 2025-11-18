function Sidebar({ currentView, onViewChange }) {
  const menuItems = [
    { id: 'main', label: '채팅하기', icon: '/images/shortcut05.png' },
    { id: 'treatment-code', label: '치료코드 조회', icon: '/images/shortcut04.png' }
  ]

  const handleMenuClick = (viewId) => {
    onViewChange(viewId)
  }

  return (
    <div className="fixed top-0 left-0 h-screen w-64 bg-white border-r border-stone-200 shadow-sm z-40 flex flex-col">
      {/* 헤더 */}
      <div 
        className="p-6 border-b border-stone-200 bg-cover bg-center bg-no-repeat relative"
        style={{ backgroundImage: 'url(/images/intro_bg.png)' }}
      >
        {/* 어두운 오버레이 */}
        <div className="absolute inset-0 bg-black/20 z-0"></div>
        
        <div className="relative z-10">
          <h2 className="text-base font-bold text-white leading-tight drop-shadow-lg">AI로 보는<br/>보험 삭감 예측 RAG</h2>
          <p className="text-xs text-white/90 mt-2 drop-shadow">Insurance Reduction Prediction</p>
        </div>
      </div>

      {/* 메뉴 리스트 */}
      <nav className="flex-1 overflow-y-auto p-4">
        <div className="space-y-1">
          {menuItems.map((item) => (
            <button
              key={item.id}
              onClick={() => handleMenuClick(item.id)}
              className={`w-full text-left px-4 py-3 text-sm font-medium transition-colors flex items-center gap-3 ${
                currentView === item.id
                  ? 'bg-amber-50 text-stone-900 border-l-4 border-stone-700'
                  : 'text-stone-700 hover:bg-stone-50 border-l-4 border-transparent'
              }`}
            >
              <img src={item.icon} alt={item.label} className="w-5 h-5 object-contain" />
              <span>{item.label}</span>
            </button>
          ))}
        </div>
      </nav>

      {/* 푸터 */}
      <div className="p-4 border-t border-stone-200 bg-stone-50 space-y-3">
        {/* 심평원 바로가기 */}
        <a
          href="https://www.hira.or.kr/"
          target="_blank"
          rel="noopener noreferrer"
          className="relative flex items-center justify-between px-4 py-3 bg-cover bg-center bg-no-repeat border border-stone-200 rounded-lg hover:border-stone-300 transition-all group overflow-hidden"
          style={{ backgroundImage: 'url(/images/image.png)' }}
        >
          {/* 어두운 오버레이 */}
          <div className="absolute inset-0 bg-black/40 group-hover:bg-black/30 transition-colors"></div>
          
          <div className="relative z-10 flex items-center justify-between w-full">
            <span className="text-sm font-medium text-white drop-shadow-lg">심평원 바로가기</span>
            <svg 
              className="w-4 h-4 text-white drop-shadow-lg transition-transform group-hover:translate-x-1" 
              fill="none" 
              stroke="currentColor" 
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14" />
            </svg>
          </div>
        </a>

        {/* 시스템 정보 */}
        <div className="text-xs text-stone-500 space-y-1">
          <div className="flex justify-between items-center">
            <span>상태</span>
            <span className="text-green-600 font-medium">정상</span>
          </div>
          <div className="flex justify-between items-center">
            <span>버전</span>
            <span className="font-mono">v1.0.0</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default Sidebar

