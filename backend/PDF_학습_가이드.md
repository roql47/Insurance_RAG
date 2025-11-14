# PDF 파일 학습 가이드

## 📄 test.pdf 학습시키기

### 1️⃣ PDF 처리 라이브러리 설치

```cmd
cd C:\Users\roql4\Desktop\Insurance_RAG2\backend
pip install pdfplumber PyMuPDF python-docx
```

### 2️⃣ test.pdf 파일 위치 확인

PDF 파일을 `backend/data/raw/` 폴더에 넣어주세요:

```
backend/
  └─ data/
      └─ raw/
          └─ test.pdf  ← 여기에 파일 넣기
```

또는 다른 위치에 있어도 경로만 지정하면 됩니다.

### 3️⃣ PDF 학습 실행

**방법 1: data/raw/ 폴더에 있는 경우**
```cmd
cd backend\src
python pipeline_pdf.py ../data/raw/test.pdf
```

**방법 2: 다른 위치에 있는 경우**
```cmd
cd backend\src
python pipeline_pdf.py C:\Users\roql4\Desktop\test.pdf
```

### 4️⃣ 실행 결과

성공하면 다음과 같은 출력이 나타납니다:

```
============================================================
PDF 문서 전처리 파이프라인 시작
============================================================
PDF 파일 로드 중: test.pdf
총 페이지 수: 10
PDF 로드 완료: 총 10페이지, 15432자
문서 청크 분할 중...
청크 생성 완료: 18개 청크
임베딩 생성 시작...
임베딩 진행 중: 10/18
임베딩 생성 완료
FAISS 인덱스 생성 중...
FAISS 인덱스 저장 완료: ./data/vector_store/faiss_index.bin
메타데이터 저장 완료: ./data/vector_store/metadata.pkl
총 18개 벡터가 인덱스에 추가되었습니다.
============================================================
PDF 문서 전처리 파이프라인 완료
============================================================

✅ 성공! 이제 'python run_server.py'로 API 서버를 시작할 수 있습니다.
```

### 5️⃣ 서버 시작 및 테스트

```cmd
cd backend
python run_server.py
```

이제 프론트엔드에서 질문을 하면 PDF 내용을 기반으로 답변합니다!

## 🔍 테스트용 간단한 스크립트

PDF가 제대로 로드되는지 테스트:

```cmd
cd backend\src\tools
python document_loader.py ../../data/raw/test.pdf
```

## ⚙️ 옵션 변경

`pipeline_pdf.py`의 청크 크기를 조정하려면:

```python
chunks = self.loader.chunk_document(
    doc_data,
    chunk_size=1000,  # 이 값을 변경 (500-2000 추천)
    overlap=100       # 이 값을 변경 (50-200 추천)
)
```

## 📚 여러 PDF 파일 학습

여러 파일을 순차적으로 학습시키려면:

```cmd
cd backend\src
python pipeline_pdf.py ../data/raw/test1.pdf
python pipeline_pdf.py ../data/raw/test2.pdf
```

⚠️ 주의: 마지막 파일만 인덱스에 남습니다. 여러 파일을 동시에 학습시키려면 별도 스크립트가 필요합니다.

## 🐛 문제 해결

### 오류: ModuleNotFoundError: No module named 'pdfplumber'
→ `pip install pdfplumber PyMuPDF` 실행

### 오류: Unable to locate credentials
→ `.env` 파일에 AWS 키 확인

### PDF 텍스트가 추출되지 않음
→ 스캔본 PDF는 OCR이 필요합니다 (별도 기능 필요)

## 💡 다음 단계

PDF 학습 후:
1. 백엔드 서버 시작: `python run_server.py`
2. 프론트엔드 실행: `cd frontend && npm run dev`
3. 웹 UI에서 PDF 내용에 대해 질문하기

