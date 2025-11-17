"""
BM25 키워드 검색 툴
정확한 키워드 매칭을 위한 BM25 알고리즘 기반 검색
"""

import os
import pickle
from typing import List, Dict, Any
import numpy as np
from rank_bm25 import BM25Okapi
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


class BM25Retriever:
    """BM25 키워드 검색 클래스"""
    
    def __init__(self):
        """초기화 및 BM25 인덱스 로드"""
        self.vector_store_path = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
        self.bm25 = None
        self.corpus = None
        self.metadata = None
        self._load_index()
    
    def _tokenize(self, text: str) -> List[str]:
        """
        텍스트를 토큰화
        
        Args:
            text: 입력 텍스트
            
        Returns:
            토큰 리스트
        """
        # 한국어 토큰화: 공백 기반 + 특수문자 유지
        # 숫자와 단위(mm, cm 등)를 함께 유지
        tokens = text.lower().split()
        return tokens
    
    def _load_index(self):
        """BM25 인덱스 및 메타데이터 로드"""
        bm25_path = os.path.join(self.vector_store_path, "bm25_index.pkl")
        
        try:
            if os.path.exists(bm25_path):
                with open(bm25_path, 'rb') as f:
                    data = pickle.load(f)
                    self.bm25 = data['bm25']
                    self.corpus = data['corpus']
                    self.metadata = data['metadata']
                print(f"BM25 인덱스 로드 완료: {len(self.corpus)}개 문서")
            else:
                print(f"경고: BM25 인덱스 파일이 없습니다: {bm25_path}")
                print("rebuild_bm25_index.py를 실행하여 인덱스를 생성해주세요.")
        except Exception as e:
            print(f"BM25 인덱스 로드 중 오류 발생: {str(e)}")
    
    def search(
        self, 
        query: str, 
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        질문과 관련된 문서를 BM25로 검색
        
        Args:
            query: 검색 질문
            top_k: 반환할 결과 수
            
        Returns:
            검색 결과 리스트 (각 결과는 text, metadata, score 포함)
        """
        if self.bm25 is None or self.corpus is None:
            return []
        
        try:
            # 1. 질문 토큰화
            query_tokens = self._tokenize(query)
            
            # 2. BM25 점수 계산
            scores = self.bm25.get_scores(query_tokens)
            
            # 3. 상위 k개 문서 선택
            top_indices = np.argsort(scores)[::-1][:top_k]
            
            # 4. 결과 구성
            results = []
            for rank, idx in enumerate(top_indices):
                if scores[idx] > 0:  # 점수가 0보다 큰 것만
                    # 점수 정규화 (0-1 범위로, 최대값 기준)
                    max_score = scores[top_indices[0]] if len(top_indices) > 0 else 1.0
                    normalized_score = scores[idx] / max_score if max_score > 0 else 0.0
                    
                    results.append({
                        "text": self.corpus[idx],
                        "metadata": self.metadata[idx],
                        "score": float(normalized_score),
                        "raw_score": float(scores[idx]),
                        "rank": rank + 1
                    })
            
            return results
            
        except Exception as e:
            print(f"BM25 검색 중 오류 발생: {str(e)}")
            return []
    
    def build_index(self, documents: List[str], metadata_list: List[Dict[str, Any]]):
        """
        문서 리스트로부터 BM25 인덱스 생성
        
        Args:
            documents: 문서 텍스트 리스트
            metadata_list: 각 문서의 메타데이터 리스트
        """
        try:
            # 토큰화된 문서 리스트 생성
            tokenized_corpus = [self._tokenize(doc) for doc in documents]
            
            # BM25 인덱스 생성
            self.bm25 = BM25Okapi(tokenized_corpus)
            self.corpus = documents
            self.metadata = metadata_list
            
            print(f"BM25 인덱스 생성 완료: {len(documents)}개 문서")
            
        except Exception as e:
            print(f"BM25 인덱스 생성 중 오류 발생: {str(e)}")
            raise
    
    def save_index(self):
        """BM25 인덱스를 파일로 저장"""
        if self.bm25 is None:
            print("저장할 BM25 인덱스가 없습니다.")
            return
        
        bm25_path = os.path.join(self.vector_store_path, "bm25_index.pkl")
        
        try:
            os.makedirs(self.vector_store_path, exist_ok=True)
            
            data = {
                'bm25': self.bm25,
                'corpus': self.corpus,
                'metadata': self.metadata
            }
            
            with open(bm25_path, 'wb') as f:
                pickle.dump(data, f)
            
            print(f"BM25 인덱스 저장 완료: {bm25_path}")
            
        except Exception as e:
            print(f"BM25 인덱스 저장 중 오류 발생: {str(e)}")
            raise


# 테스트용 메인 함수
if __name__ == "__main__":
    print("=" * 60)
    print("BM25 검색기 테스트")
    print("=" * 60)
    
    # 샘플 문서로 테스트
    documents = [
        "직경 10mm 이상의 비파열성 뇌동맥류에 Flow-diverter 사용 시 급여 인정",
        "직경 10mm 미만의 비파열성 뇌동맥류는 제외",
        "LM과 LAD에 스텐트 삽입 시 단일혈관 및 추가혈관 수가 산정"
    ]
    
    metadata = [
        {"type": "급여기준", "id": 1},
        {"type": "제외사항", "id": 2},
        {"type": "수가산정", "id": 3}
    ]
    
    # BM25 인덱스 생성
    retriever = BM25Retriever()
    retriever.build_index(documents, metadata)
    
    # 테스트 검색
    print("\n테스트 1: '10mm 이상 뇌동맥류'")
    results = retriever.search("10mm 이상 뇌동맥류", top_k=3)
    for i, result in enumerate(results, 1):
        print(f"\n[{i}] 점수: {result['score']:.4f} (raw: {result['raw_score']:.2f})")
        print(f"문서: {result['text']}")
    
    print("\n테스트 2: '10mm 미만'")
    results = retriever.search("10mm 미만", top_k=3)
    for i, result in enumerate(results, 1):
        print(f"\n[{i}] 점수: {result['score']:.4f} (raw: {result['raw_score']:.2f})")
        print(f"문서: {result['text']}")

