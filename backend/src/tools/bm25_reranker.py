"""
BM25 점수 기반 로컬 리랭크 (API 키 불필요)
"""
from typing import List, Dict, Any
from rank_bm25 import BM25Okapi
import re


class BM25Reranker:
    """BM25 점수로 재정렬하는 로컬 리랭커"""
    
    def __init__(self):
        """초기화"""
        print("[OK] BM25Reranker 초기화 (로컬, API 키 불필요)")
    
    def _tokenize(self, text: str) -> List[str]:
        """
        텍스트 토크나이징
        
        Args:
            text: 토크나이징할 텍스트
            
        Returns:
            토큰 리스트
        """
        # 한글(2자 이상), 영문(3자 이상), 숫자 추출
        tokens = re.findall(r'[가-힣]{2,}|[a-zA-Z]{3,}|\d+', text.lower())
        return tokens
    
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        BM25로 문서 재정렬
        
        Args:
            query: 검색 질문
            documents: 검색 결과 리스트 (각 문서는 'text'와 'metadata' 포함)
            top_k: 반환할 상위 결과 수
            
        Returns:
            재정렬된 검색 결과 리스트
        """
        if not documents:
            return []
        
        # 문서가 top_k보다 적으면 그냥 반환
        if len(documents) <= top_k:
            print(f"[BM25 Rerank] 문서 수({len(documents)})가 top_k({top_k}) 이하, 재정렬 스킵")
            return documents
        
        print(f"[BM25 Rerank] {len(documents)}개 문서 재정렬 시작...")
        
        try:
            # 1. 문서 토크나이징
            doc_texts = [doc['text'] for doc in documents]
            tokenized_docs = [self._tokenize(text) for text in doc_texts]
            
            # 빈 문서 필터링 (토큰이 없는 경우)
            valid_docs = []
            valid_tokenized = []
            for doc, tokens in zip(documents, tokenized_docs):
                if tokens:
                    valid_docs.append(doc)
                    valid_tokenized.append(tokens)
            
            if not valid_tokenized:
                print("[WARNING] 토큰이 없는 문서들, 원본 반환")
                return documents[:top_k]
            
            # 2. BM25 인덱스 생성
            bm25 = BM25Okapi(valid_tokenized)
            
            # 3. 쿼리 토크나이징 및 점수 계산
            tokenized_query = self._tokenize(query)
            
            if not tokenized_query:
                print("[WARNING] 쿼리에 토큰이 없음, 원본 반환")
                return documents[:top_k]
            
            scores = bm25.get_scores(tokenized_query)
            
            # 4. 점수와 문서 매핑
            scored_docs = []
            for doc, score in zip(valid_docs, scores):
                doc_copy = doc.copy()
                doc_copy['rerank_score'] = float(score)
                
                # 기존 점수 보존
                if 'score' in doc:
                    doc_copy['original_score'] = doc['score']
                
                # BM25 점수를 새 점수로 설정
                doc_copy['score'] = float(score)
                scored_docs.append(doc_copy)
            
            # 5. 점수로 정렬
            scored_docs.sort(key=lambda x: x['rerank_score'], reverse=True)
            
            # 6. rank 재할당
            for i, doc in enumerate(scored_docs[:top_k], 1):
                doc['rank'] = i
            
            print(f"[BM25 Rerank] ✅ {len(documents)}개 → {min(top_k, len(scored_docs))}개 선별 완료")
            top_scores = [f"{d['rerank_score']:.2f}" for d in scored_docs[:3]]
            print(f"    상위 3개 점수: {top_scores}")
            
            return scored_docs[:top_k]
            
        except Exception as e:
            print(f"[ERROR] BM25 Rerank 중 오류: {str(e)}")
            print("    원본 검색 결과 반환")
            return documents[:top_k]


# 싱글톤 인스턴스
_bm25_reranker = None


def get_bm25_reranker():
    """BM25 리랭커 싱글톤 인스턴스 반환"""
    global _bm25_reranker
    if _bm25_reranker is None:
        _bm25_reranker = BM25Reranker()
    return _bm25_reranker


# 테스트용 메인 함수
if __name__ == "__main__":
    # 테스트 데이터
    test_docs = [
        {
            "text": "경피적 관상동맥 스텐트 삽입술 시 스텐트 2개 이상 사용 시 급여 인정 기준",
            "score": 0.8,
            "metadata": {"source": "doc1"}
        },
        {
            "text": "비파열성 뇌동맥류의 치료 방법과 보험 적용 범위",
            "score": 0.7,
            "metadata": {"source": "doc2"}
        },
        {
            "text": "관상동맥 협착증 진단을 위한 검사 절차",
            "score": 0.6,
            "metadata": {"source": "doc3"}
        },
        {
            "text": "스텐트 삽입 후 항혈소판제 복용 기간",
            "score": 0.5,
            "metadata": {"source": "doc4"}
        }
    ]
    
    reranker = get_bm25_reranker()
    
    print("\n테스트 쿼리: '스텐트 2개 사용 조건'")
    print("=" * 60)
    
    results = reranker.rerank(
        query="스텐트 2개 사용 조건",
        documents=test_docs,
        top_k=2
    )
    
    print("\n결과:")
    for i, doc in enumerate(results, 1):
        print(f"\n[{i}] 점수: {doc['rerank_score']:.4f} (원본: {doc.get('original_score', 0):.2f})")
        print(f"    내용: {doc['text'][:50]}...")

