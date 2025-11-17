"""
기존 FAISS 인덱스로부터 BM25 인덱스 재생성
"""

import os
import pickle
import sys
from dotenv import load_dotenv

# 프로젝트 루트를 Python 경로에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools.bm25_retriever import BM25Retriever

# 환경 변수 로드
load_dotenv()


def rebuild_bm25_index():
    """FAISS 메타데이터로부터 BM25 인덱스 재생성"""
    
    print("=" * 60)
    print("BM25 인덱스 재생성 시작")
    print("=" * 60)
    
    # 경로 설정
    vector_store_path = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
    metadata_path = os.path.join(vector_store_path, "metadata.pkl")
    
    # 1. 기존 메타데이터 로드
    print("\n1. 기존 메타데이터 로드 중...")
    if not os.path.exists(metadata_path):
        print(f"오류: 메타데이터 파일이 없습니다: {metadata_path}")
        print("먼저 데이터 전처리를 실행해주세요.")
        return
    
    with open(metadata_path, 'rb') as f:
        metadata_list = pickle.load(f)
    
    print(f"[OK] {len(metadata_list)}개 문서 로드 완료")
    
    # 2. 문서 텍스트와 메타데이터 추출
    print("\n2. 문서 추출 중...")
    documents = []
    metadata_only = []
    
    for item in metadata_list:
        documents.append(item['text'])
        metadata_only.append(item['metadata'])
    
    print(f"[OK] {len(documents)}개 문서 추출 완료")
    
    # 3. BM25 인덱스 생성
    print("\n3. BM25 인덱스 생성 중...")
    retriever = BM25Retriever()
    retriever.build_index(documents, metadata_only)
    
    print("[OK] BM25 인덱스 생성 완료")
    
    # 4. 인덱스 저장
    print("\n4. BM25 인덱스 저장 중...")
    retriever.save_index()
    
    print("[OK] BM25 인덱스 저장 완료")
    
    # 5. 테스트 검색
    print("\n5. 테스트 검색 실행...")
    test_queries = [
        "10mm 이상의 비파열성 뇌동맥류",
        "10mm 미만",
        "LM과 LAD 스텐트"
    ]
    
    for query in test_queries:
        print(f"\n쿼리: '{query}'")
        results = retriever.search(query, top_k=3)
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"  [{i}] 점수: {result['score']:.4f} | 타입: {result['metadata'].get('type', 'N/A')}")
                print(f"      {result['text'][:80]}...")
        else:
            print("  검색 결과 없음")
    
    print("\n" + "=" * 60)
    print("BM25 인덱스 재생성 완료!")
    print("=" * 60)
    print("\n하이브리드 검색을 사용할 준비가 되었습니다.")
    print("백엔드 서버를 재시작하여 새로운 검색 기능을 사용하세요.")


if __name__ == "__main__":
    try:
        rebuild_bm25_index()
    except Exception as e:
        print(f"\n오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

