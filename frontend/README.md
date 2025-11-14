# 보험 인정기준 RAG - 프론트엔드

React + Vite + Tailwind CSS로 구현된 모던 웹 UI

## 🎨 기술 스택

- **React 18**: 컴포넌트 기반 UI 라이브러리
- **Vite**: 초고속 빌드 도구
- **Tailwind CSS**: 유틸리티 우선 CSS 프레임워크
- **Axios**: HTTP 클라이언트

## 📁 프로젝트 구조

```
src/
├── components/          # React 컴포넌트
│   ├── QueryForm.jsx        # 질의 입력 폼
│   ├── ResultDisplay.jsx    # 결과 표시
│   ├── SourcesList.jsx      # 참고 문서 목록
│   └── LoadingSpinner.jsx   # 로딩 스피너
├── api/                # API 클라이언트
│   └── client.js           # axios 설정 및 API 함수
├── hooks/              # 커스텀 훅
│   └── useInsuranceQuery.js # 질의 훅
├── App.jsx             # 메인 앱 컴포넌트
├── main.jsx            # 엔트리 포인트
└── index.css           # Tailwind CSS imports
```

## 🚀 시작하기

### 1. 의존성 설치
```bash
npm install
```

### 2. 개발 서버 실행
```bash
npm run dev
```

개발 서버가 `http://localhost:5173`에서 실행됩니다.

### 3. 프로덕션 빌드
```bash
npm run build
```

빌드된 파일은 `dist/` 폴더에 생성됩니다.

### 4. 프로덕션 프리뷰
```bash
npm run preview
```

## 🔧 환경 변수

`.env` 파일을 생성하여 API 서버 URL을 설정할 수 있습니다:

```env
VITE_API_URL=http://localhost:8000/api
```

## 🎨 주요 기능

### 컴포넌트

#### QueryForm
- 재료코드, 시술코드, 질문 입력
- 폼 유효성 검사
- API 호출 및 에러 처리

#### ResultDisplay
- AI 답변 표시
- 마크다운 스타일 텍스트 렌더링
- 참고 문서 목록

#### SourcesList
- 검색된 문서 목록
- 유사도 점수 표시
- 문서 타입별 구분

#### LoadingSpinner
- 애니메이션 로딩 효과
- 진행 상태 표시

### API 클라이언트

`src/api/client.js`는 다음 기능을 제공합니다:

- **queryInsuranceCriteria**: 보험 인정기준 질의
- **preprocessData**: 데이터 전처리 트리거
- **healthCheck**: 서버 헬스 체크

### 커스텀 훅

`useInsuranceQuery`: 질의 상태 관리를 위한 훅

```javascript
const { loading, error, result, submitQuery, reset } = useInsuranceQuery()
```

## 🎨 Tailwind CSS 커스터마이징

`tailwind.config.js`에서 커스텀 색상과 애니메이션을 정의:

```javascript
theme: {
  extend: {
    colors: {
      primary: {...},
      secondary: {...}
    },
    animation: {
      'fade-in': 'fadeIn 0.5s ease-in-out',
      'progress': 'progress 2s ease-in-out infinite',
    }
  }
}
```

## 📱 반응형 디자인

모든 컴포넌트는 모바일, 태블릿, 데스크톱에 최적화되어 있습니다:

- 모바일: 320px - 640px
- 태블릿: 641px - 1024px
- 데스크톱: 1025px 이상

## 🔍 개발 팁

### Hot Module Replacement (HMR)
Vite는 파일 저장 시 자동으로 브라우저를 새로고침합니다.

### React DevTools
Chrome/Firefox 확장 프로그램을 사용하여 컴포넌트 상태를 디버깅할 수 있습니다.

### Tailwind CSS IntelliSense
VSCode 확장 프로그램을 설치하면 자동 완성을 사용할 수 있습니다.

## 🐛 문제 해결

### CORS 오류
백엔드 서버가 실행 중인지 확인하세요:
```bash
cd ../backend
python run_server.py
```

### API 연결 오류
`.env` 파일에서 API URL을 확인하세요.

### 빌드 오류
node_modules를 삭제하고 재설치:
```bash
rm -rf node_modules
npm install
```

## 📄 라이선스

MIT License

