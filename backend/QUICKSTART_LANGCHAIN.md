# 🚀 LangChain 빠른 시작 가이드

LangChain으로 마이그레이션된 보험 인정기준 RAG 시스템 빠른 시작 가이드입니다.

## ⚡ 3분 만에 시작하기

### 1단계: 패키지 설치

```bash
cd backend
pip install -r requirements.txt
```

### 2단계: 환경 변수 설정

`.env` 파일이 다음 내용을 포함하는지 확인:

```bash
AWS_ACCESS_KEY_ID=your_access_key
AWS_SECRET_ACCESS_KEY=your_secret_key
AWS_REGION=us-east-1
BEDROCK_MODEL_ID=anthropic.claude-4-5-haiku-20251015-v1:0
```

### 3단계: 벡터 인덱스 확인

```bash
ls data/vector_store/

# 다음 파일들이 있어야 함:
# - faiss_index.bin
# - bm25_index.pkl
# - metadata.pkl
```

없으면 생성:
```bash
python run_preprocessing.py data/raw
```

### 4단계: 테스트

```bash
python test_langchain.py
```

### 5단계: 서버 실행

```bash
python run_server.py
```

**완료! 🎉** 이제 `http://localhost:8000`에서 API를 사용할 수 있습니다.

---

## 💡 사용 예제

### Python에서 직접 사용

```python
from src.agent.langchain_agent import answer_insurance_query_langchain

# 질문
result = answer_insurance_query_langchain(
    question="RCA와 LAD에 스텐트를 삽입한 경우 수가는?"
)

print(result['answer'])
print(f"참고 문서: {len(result['sources'])}개")
```

### API 호출

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "RCA와 LAD에 스텐트를 삽입한 경우 수가 산정은 어떻게 하나요?"
  }'
```

### 대화 기록과 함께 사용

```bash
curl -X POST "http://localhost:8000/query" \
  -H "Content-Type: application/json" \
  -d '{
    "question": "그럼 세 개 혈관에는?",
    "conversation_history": [
      {"role": "user", "content": "스텐트 삽입술 인정기준은?"},
      {"role": "assistant", "content": "...이전 답변..."}
    ]
  }'
```

---

## 🔧 설정 옵션

### 환경 변수

| 변수 | 설명 | 기본값 |
|------|------|--------|
| `USE_LANGCHAIN` | LangChain 사용 여부 | `true` |
| `AWS_REGION` | AWS 리전 | `us-east-1` |
| `BEDROCK_MODEL_ID` | Bedrock 모델 ID | `anthropic.claude-4-5-haiku` |
| `VECTOR_STORE_PATH` | 벡터 저장소 경로 | `./data/vector_store` |

### LangChain 비활성화

기존 방식으로 되돌리기:

```bash
# .env에 추가
USE_LANGCHAIN=false
```

또는:

```bash
export USE_LANGCHAIN=false
python run_server.py
```

---

## 📊 LangChain vs 기존 방식

| 항목 | 기존 | LangChain |
|------|------|-----------|
| 코드 | 500줄 | 150줄 |
| 대화 관리 | 수동 | 자동 |
| 에러 처리 | 수동 | 내장 |
| 확장성 | 어려움 | 쉬움 |
| 응답 시간 | 2-3초 | 2.5-4초 |

---

## 🐛 문제 해결

### ImportError: No module named 'langchain'

```bash
pip install langchain langchain-aws langchain-community
```

### 검색 결과가 없음

```bash
# 인덱스 재생성
python run_preprocessing.py data/raw
```

### 응답이 느림

```bash
# 기존 방식으로 전환
export USE_LANGCHAIN=false
python run_server.py
```

---

## 📚 더 알아보기

- [LangChain 마이그레이션 가이드](LANGCHAIN_MIGRATION.md) - 상세한 마이그레이션 내용
- [메인 README](../README.md) - 전체 프로젝트 문서
- [PDF 학습 가이드](PDF_학습_가이드.md) - 문서 추가 방법
- [증분학습 가이드](증분학습_가이드.md) - 점진적 학습 방법

---

## ✨ 주요 개선사항

✅ 코드 70% 감소  
✅ 대화 기록 자동 관리  
✅ RAG 전용 최적화  
✅ 에러 처리 및 재시도 내장  
✅ 확장 용이  
✅ 프로덕션 레디  

---

**즐거운 코딩 되세요! 🚀**

