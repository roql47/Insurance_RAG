# 빠른 시작 가이드 (Quick Start)

이 가이드를 따라하면 10분 안에 시스템을 실행할 수 있습니다.

## 1️⃣ AWS Bedrock 설정 (5분)

### AWS 계정이 없는 경우
1. https://aws.amazon.com/ 접속
2. "Create an AWS Account" 클릭
3. 이메일 및 결제 정보 입력 (프리 티어 사용 가능)

### AWS Bedrock 모델 활성화
1. AWS 콘솔 로그인
2. 검색창에 "Bedrock" 입력 → Amazon Bedrock 선택
3. 좌측 메뉴: **Model access** 클릭
4. **Modify model access** 버튼 클릭
5. 다음 모델 체크:
   - ✅ Anthropic - Claude 4.5 Haiku
   - ✅ Amazon - Titan Embeddings V2
6. **Save changes** 클릭
7. 승인 대기 (수 분 소요)

### API 키 발급
1. IAM 서비스로 이동 (검색창에 "IAM" 입력)
2. 좌측 메뉴: **Users** → **Add users** 클릭
3. 이름: `bedrock-user` 입력
4. **Next** → **Attach policies directly** 선택
5. 검색: `AmazonBedrockFullAccess` 선택
6. **Next** → **Create user**
7. 생성된 사용자 클릭 → **Security credentials** 탭
8. **Create access key** 클릭
9. **Command Line Interface (CLI)** 선택 → **Next**
10. **Create access key**
11. ⚠️ **Access key ID**와 **Secret access key** 복사 (다시 볼 수 없음!)

## 2️⃣ 프로젝트 설정 (3분)

### Python 가상환경 생성
```cmd
cd backend
python -m venv venv
venv\Scripts\activate
```

### 의존성 설치
```cmd
pip install -r requirements.txt
```

### 환경 변수 설정
1. `backend/.env.example` 파일을 복사하여 `.env` 생성:
```cmd
copy .env.example .env
```

2. `.env` 파일 열기 (메모장이나 VSCode)

3. AWS 키 입력:
```env
AWS_ACCESS_KEY_ID=AKIA...  (위에서 복사한 Access Key ID)
AWS_SECRET_ACCESS_KEY=abc123...  (위에서 복사한 Secret Access Key)
AWS_REGION=us-east-1

BEDROCK_MODEL_ID=anthropic.claude-4-5-haiku-20251015-v1:0
EMBEDDING_MODEL_ID=amazon.titan-embed-text-v2:0

VECTOR_STORE_PATH=./data/vector_store
TOP_K_RESULTS=5

API_HOST=0.0.0.0
API_PORT=8000
```

## 3️⃣ 데이터 전처리 (1분)

샘플 데이터로 벡터 인덱스 생성:

```cmd
cd backend
python run_preprocessing.py
```

출력 예시:
```
============================================================
데이터 전처리 파이프라인 시작
============================================================
원본 데이터 로드 완료: 5개 항목
청크 생성 완료: 20개 청크
임베딩 생성 시작...
임베딩 진행 중: 10/20
임베딩 진행 중: 20/20
임베딩 생성 완료
FAISS 인덱스 저장 완료: ./data/vector_store/faiss_index.bin
메타데이터 저장 완료: ./data/vector_store/metadata.pkl
총 20개 벡터가 인덱스에 추가되었습니다.
============================================================
데이터 전처리 파이프라인 완료
============================================================
```

### 💡 새 데이터 추가 (증분 학습) 🆕

나중에 새 PDF를 추가했을 때, 기존 데이터는 유지하고 새 파일만 학습하려면:

```cmd
# 1. data/raw/ 폴더에 새 PDF 파일 추가
# 2. 증분 학습 실행
cd backend
python run_incremental_learning.py
```

**장점:**
- ✅ 새 파일만 학습 → 빠름!
- ✅ 기존 데이터 보존
- ✅ AWS API 비용 절감

자세한 내용: [`backend/증분학습_가이드.md`](backend/증분학습_가이드.md)

## 4️⃣ 프론트엔드 설치 (1분)

### 프론트엔드 의존성 설치
```cmd
cd frontend
npm install
```

설치 완료 메시지:
```
added 193 packages, and audited 194 packages in 30s
```

## 5️⃣ 서버 실행 (1분)

### 백엔드 API 서버 시작
새 CMD 창을 열고:
```cmd
cd backend
python run_server.py
```

서버가 시작되면:
```
============================================================
보험 인정기준 RAG API 서버 시작
============================================================
서버 주소: http://0.0.0.0:8000
API 문서: http://0.0.0.0:8000/docs
API 엔드포인트: http://0.0.0.0:8000/api
============================================================
```

### 프론트엔드 개발 서버 시작
또 다른 CMD 창을 열고:
```cmd
cd frontend
npm run dev
```

Vite 개발 서버가 시작되고 브라우저가 자동으로 열립니다:
```
VITE v5.1.4  ready in 500 ms

  ➜  Local:   http://localhost:5173/
  ➜  Network: use --host to expose
```

## 6️⃣ 테스트 (1분)

### 웹 UI에서 테스트
1. 재료코드: `A12345`
2. 시술코드: `N2095`
3. 질문: `55세 환자가 퇴행성 고관절염으로 수술받는 경우 삭감될까요?`
4. "판단 요청" 클릭

### 또는 API로 직접 테스트
```cmd
curl -X POST "http://localhost:8000/api/query" ^
  -H "Content-Type: application/json" ^
  -d "{\"material_code\": \"A12345\", \"procedure_code\": \"N2095\", \"question\": \"삭감될까요?\"}"
```

## ✅ 성공!

이제 보험 인정기준 RAG 시스템이 실행되었습니다!

## 🔧 문제 해결

### AWS 자격증명 오류
```
UnrecognizedClientException
```
→ `.env` 파일의 AWS 키 확인

### Bedrock 접근 오류
```
AccessDeniedException
```
→ AWS 콘솔에서 Bedrock 모델 활성화 확인
→ IAM 사용자에게 `AmazonBedrockFullAccess` 권한 부여 확인

### FAISS 인덱스 오류
```
FAISS 인덱스가 로드되지 않았습니다
```
→ `python run_preprocessing.py` 먼저 실행

### 포트 충돌
```
Address already in use
```
→ `.env`에서 `API_PORT=8001`로 변경

## 📚 다음 단계

- 실제 심평원 데이터로 교체: `backend/data/raw/` 폴더에 JSON 파일 추가
- API 문서 확인: http://localhost:8000/docs
- 코드 커스터마이징: `backend/src/agent/answer_agent.py`의 시스템 프롬프트 수정

## 💰 비용 확인

AWS Billing 콘솔에서 실시간 비용 확인:
1. AWS 콘솔 → Billing and Cost Management
2. Bills → Bedrock 항목 확인

샘플 데이터 테스트는 $0.05 미만으로 가능합니다.

