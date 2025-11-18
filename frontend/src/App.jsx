import { useState } from 'react'
import Sidebar from './components/Sidebar'
import MainView from './components/MainView'
import TreatmentCodeSearch from './components/TreatmentCodeSearch'

function App() {
  const [currentView, setCurrentView] = useState('main') // 'main' 또는 'treatment-code'

  return (
    <div className="min-h-screen relative">
      {/* 배경 이미지 - 채팅하기 탭에서만 표시 */}
      {currentView === 'main' && (
        <div 
          className="fixed inset-0 bg-cover bg-center bg-no-repeat"
          style={{
            backgroundImage: 'url(/images/bg_intro_gm.png)',
            opacity: 0.6,
            zIndex: -1
          }}
        />
      )}
      
      {/* 사이드바 */}
      <Sidebar currentView={currentView} onViewChange={setCurrentView} />

      {/* 메인 컨텐츠 */}
      <div className="ml-64 min-h-screen">
        {currentView === 'main' ? (
          <MainView />
        ) : currentView === 'treatment-code' ? (
          <TreatmentCodeSearch />
        ) : null}
      </div>
    </div>
  )
}

export default App
