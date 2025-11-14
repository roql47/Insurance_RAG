# 보험 인정기준 RAG 시스템

심평원 보험 인정기준을 기반으로 보험재료코드 및 시술행위코드의 삭감 여부를 판단하는 RAG(Retrieval-Augmented Generation) 시스템입니다.

## 🏗️ 시스템 아키텍처

```
Insurance_RAG/
 ├ backend/
 │   ├ data/
 │   │   ├ raw/                      # 원본 데이터 (JSON/CSV)
 │   │   ├ processed/                # 전처리된 데이터
 │   │   └ vector_store/             # FAISS 벡터 인덱스
 │   ├ src/
 │   │   ├ tools/                    # 에이전트 툴
 │   │   │   ├ embedder_tool.py      # AWS Titan Embeddings
 │   │   │   └ faiss_retriever.py    # FAISS 벡터 검색
 │   │   ├ agent/                    # 에이전트 정의
 │   │   │   └ answer_agent.py       # Claude 4.5 Haiku 에이전트
 │   │   ├ pipeline.py               # 데이터 전처리 파이프라인
 │   │   └ api/
 │   │       ├ main.py               # FastAPI 서버
 │   │       └ routes.py             # API 엔드포인트
 │   ├ run_server.py                 # 서버 실행 스크립트
 │   ├ run_preprocessing.py          # 전처리 실행 스크립트
 │   └ requirements.txt              # Python 의존성
 ├ frontend/                         # React + Vite + Tailwind CSS
 │   ├ src/
 │   │   ├ components/               # React 컴포넌트
 │   │   ├ api/                      # API 클라이언트
 │   │   ├ hooks/                    # 커스텀 훅
 │   │   ├ App.jsx                   # 메인 앱
 │   │   └ main.jsx                  # 엔트리 포인트
 │   ├ package.json                  # Node.js 의존성
 │   ├ vite.config.js                # Vite 설정
 │   └ tailwind.config.js            # Tailwind CSS 설정
 └ README.md
```

## 🚀 주요 기능

- **AWS Bedrock + Claude 4.5 Haiku**: 최신 AI 모델을 통한 정확한 판단
- **AWS Titan Embeddings V2**: 1024차원 벡터로 의미 기반 검색
- **FAISS 벡터 검색**: 빠르고 효율적인 유사도 검색
- **FastAPI**: 고성능 REST API
- **React + Vite + Tailwind CSS**: 모던하고 반응형 웹 UI

## 📋 사전 요구사항

### 1. Python 환경
- Python 3.9 이상

### 2. Node.js 환경
- Node.js 18.0 이상
- npm 또는 yarn

### 3. AWS 계정 및 Bedrock 설정

#### AWS 계정 생성
1. [AWS 콘솔](https://aws.amazon.com/)에서 계정 생성
2. 결제 정보 등록 (프리 티어 사용 가능)

#### AWS Bedrock 활성화
1. AWS 콘솔 로그인
2. **Amazon Bedrock** 서비스로 이동
3. 좌측 메뉴에서 **Model access** 클릭
4. 다음 모델 활성화:
   - **Anthropic Claude 4.5 Haiku** (`anthropic.claude-4-5-haiku-20251015-v1:0`)
   - **Amazon Titan Embeddings V2** (`amazon.titan-embed-text-v2:0`)
5. 요청 제출 후 승인 대기 (보통 수 분 내 승인)

#### IAM 사용자 생성 및 API 키 발급
1. IAM 서비스로 이동
2. **Users** → **Add user** 클릭
3. 사용자 이름 입력 (예: `bedrock-user`)
4. **Access key - Programmatic access** 선택
5. 권한 설정:
   - **Attach existing policies directly** 선택
   - `AmazonBedrockFullAccess` 정책 연결
6. 생성 완료 후 **Access Key ID**와 **Secret Access Key** 저장 (⚠️ 한 번만 표시됨)

## 🔧 설치 방법

### 1. 저장소 클론
```bash
cd Insurance_RAG2
```

### 2. Python 가상환경 생성 (권장)
```bash
cd backend
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. 의존성 설치
```bash
pip install -r requirements.txt
```

### 4. 환경 변수 설정
`.env.example`을 복사하여 `.env` 파일 생성:

```bash
copy .env.example .env
```

`.env` 파일을 열어 AWS 자격증명 입력:

```env
# AWS Bedrock 설정
AWS_ACCESS_KEY_ID=your_access_key_here
AWS_SECRET_ACCESS_KEY=your_secret_key_here
AWS_REGION=us-east-1

# Bedrock 모델 설정
BEDROCK_MODEL_ID=anthropic.claude-4-5-haiku-20251015-v1:0
EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0

# 벡터 스토어 설정
VECTOR_STORE_PATH=./data/vector_store
TOP_K_RESULTS=5

# API 설정
API_HOST=0.0.0.0
API_PORT=8000
```

## 📊 데이터 전처리

### 1. 샘플 데이터로 테스트
기본 제공되는 샘플 데이터로 시작:

```bash
cd src
python pipeline.py
```

### 2. 실제 데이터 추가
`backend/data/raw/` 폴더에 JSON 파일을 추가하고 다음 형식으로 작성:

```json
[
  {
    "id": "1",
    "재료코드": "A12345",
    "재료명": "인공고관절(세라믹)",
    "시술코드": "N2095",
    "시술명": "고관절 전치환술",
    "인정기준": "...",
    "제외사항": "...",
    "근거법령": "...",
    "심사기준": "...",
    "참고사항": "..."
  }
]
```

### 3. 증분 학습 (Incremental Learning) 🆕

기존 학습 데이터를 유지하면서 **새로운 PDF만 추가로 학습**할 수 있습니다!

#### 사용 방법

1. **새 PDF 추가**: `backend/data/raw/` 폴더에 PDF 파일 추가
2. **증분 학습 실행**:
   ```bash
   cd backend
   python run_incremental_learning.py
   ```

#### 주요 명령어

```bash
# 새로운 PDF만 학습 (기본)
python run_incremental_learning.py

# 처리된 파일 목록 확인
python run_incremental_learning.py --list

# 이미 처리된 파일도 다시 학습
python run_incremental_learning.py --force

# 처리된 파일 목록 초기화 (전체 재학습 준비)
python run_incremental_learning.py --reset
```

#### 장점

- ✅ **시간 절약**: 새 파일만 학습하므로 빠름
- ✅ **비용 절감**: AWS API 호출 최소화
- ✅ **데이터 보존**: 기존 학습 데이터 유지

자세한 내용은 [`backend/증분학습_가이드.md`](backend/증분학습_가이드.md)를 참고하세요.

## 🖥️ 실행 방법

### 1. 백엔드 API 서버 시작
```bash
cd backend
python run_server.py
```

서버가 `http://localhost:8000`에서 실행됩니다.
- API 문서: `http://localhost:8000/docs`
- API 엔드포인트: `http://localhost:8000/api`

### 2. 프론트엔드 개발 서버 시작

#### 2-1. 프론트엔드 의존성 설치 (최초 1회)
```bash
cd frontend
npm install
```

#### 2-2. 개발 서버 시작
```bash
npm run dev
```

Vite 개발 서버가 `http://localhost:5173`에서 실행됩니다.
브라우저가 자동으로 열립니다.

#### 2-3. 프로덕션 빌드 (선택사항)
```bash
npm run build
npm run preview
```

## 🔍 사용 방법

### 웹 UI 사용
1. 재료코드 입력 (예: `A12345`)
2. 시술코드 입력 (예: `N2095`)
3. 질문 입력 (예: "이 재료와 시술이 삭감될 가능성이 있나요?")
4. "판단 요청" 버튼 클릭
5. AI가 인정기준을 분석하여 결과 표시

### API 직접 호출
```bash
curl -X POST "http://localhost:8000/api/query" \
  -H "Content-Type: application/json" \
  -d '{
    "material_code": "A12345",
    "procedure_code": "N2095",
    "question": "55세 환자가 퇴행성 고관절염으로 수술받는 경우 삭감될까요?"
  }'
```

### Python으로 호출
```python
import requests

response = requests.post(
    "http://localhost:8000/api/query",
    json={
        "material_code": "A12345",
        "procedure_code": "N2095",
        "question": "이 재료와 시술이 삭감될 가능성이 있나요?"
    }
)

result = response.json()
print(result["answer"])
```

## 📚 API 엔드포인트

### POST `/api/query`
보험 인정기준 질의

**요청:**
```json
{
  "material_code": "A12345",
  "procedure_code": "N2095",
  "question": "삭감 여부 질문"
}
```

**응답:**
```json
{
  "answer": "판단 결과 및 근거",
  "sources": [
    {
      "type": "인정기준",
      "재료코드": "A12345",
      "재료명": "인공고관절",
      "시술코드": "N2095",
      "시술명": "고관절 전치환술",
      "score": 0.15
    }
  ],
  "material_code": "A12345",
  "procedure_code": "N2095",
  "question": "..."
}
```

### POST `/api/preprocess`
데이터 전처리 실행

**요청:**
```json
{
  "data_path": "./data/raw/sample_criteria.json"
}
```

### GET `/api/health`
헬스 체크

## 🧪 테스트

### 임베딩 툴 테스트
```bash
cd backend/src/tools
python embedder_tool.py
```

### 검색 툴 테스트
```bash
cd backend/src/tools
python faiss_retriever.py
```

### 에이전트 테스트
```bash
cd backend/src/agent
python answer_agent.py
```

## 💰 비용 안내

AWS Bedrock 사용 비용 (2025년 기준):
- **Claude 4.5 Haiku**: 입력 $0.80/1M 토큰, 출력 $4.00/1M 토큰
- **Titan Embeddings V2**: $0.0002/1K 토큰

샘플 데이터(5개 항목) 전처리: 약 $0.01
질의 1회당: 약 $0.01-0.02

프리 티어로 충분히 테스트 가능합니다.

## 🛠️ 트러블슈팅

### AWS 자격증명 오류
```
ClientError: An error occurred (UnrecognizedClientException)
```
→ `.env` 파일의 `AWS_ACCESS_KEY_ID`와 `AWS_SECRET_ACCESS_KEY` 확인

### Bedrock 모델 접근 오류
```
AccessDeniedException: Could not access model
```
→ AWS 콘솔에서 Bedrock Model Access 확인 및 활성화

### FAISS 인덱스 없음
```
경고: FAISS 인덱스 파일이 없습니다
```
→ `python pipeline.py`로 데이터 전처리 먼저 실행

### CORS 오류
→ API 서버가 실행 중인지 확인
→ `frontend/index.html`의 `API_BASE_URL` 확인

## 📝 TODO

- [ ] 실제 심평원 데이터 수집 및 전처리
- [ ] 다중 문서 검색 성능 최적화
- [ ] 사용자 피드백 기반 답변 개선
- [ ] 프론트엔드 React/Vue 마이그레이션
- [ ] 로깅 및 모니터링 추가
- [ ] Docker 컨테이너화
- [ ] CI/CD 파이프라인 구축

## 📄 라이선스

MIT License

## 👥 기여

이슈 및 PR 환영합니다!

## 📧 문의

프로젝트 관련 문의사항은 이슈로 등록해주세요.

