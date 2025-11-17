"""
하이브리드 검색 툴
FAISS 벡터 검색과 BM25 키워드 검색을 결합하여 정확도 향상
"""

import os
from typing import List, Dict, Any
from dotenv import load_dotenv

from tools.faiss_retriever import FAISSRetriever
from tools.bm25_retriever import BM25Retriever
from tools.query_expander import get_query_expander
from tools.reranker import get_reranker

# 환경 변수 로드
load_dotenv()


class HybridRetriever:
    """하이브리드 검색 클래스 (FAISS + BM25)"""
    
    def __init__(
        self,
        vector_weight: float = 0.7,
        bm25_weight: float = 0.3,
        use_rrf: bool = False,
        use_reranker: bool = True
    ):
        """
        초기화
        
        Args:
            vector_weight: 벡터 검색 가중치 (기본 0.7)
            bm25_weight: BM25 검색 가중치 (기본 0.3)
            use_rrf: Reciprocal Rank Fusion 사용 여부
            use_reranker: Cohere Rerank 사용 여부 (기본 True)
        """
        self.faiss_retriever = FAISSRetriever()
        self.bm25_retriever = BM25Retriever()
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self.use_rrf = use_rrf
        self.rrf_k = 60  # RRF 상수
        self.use_reranker = use_reranker
        
        # Reranker 초기화 (use_reranker가 True일 때만)
        if self.use_reranker:
            try:
                self.reranker = get_reranker()
            except Exception as e:
                print(f"⚠️  Reranker 초기화 실패: {e}")
                print("   → Reranking 없이 계속 진행합니다.")
                self.use_reranker = False
    
    def _reciprocal_rank_fusion(
        self,
        vector_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Reciprocal Rank Fusion (RRF)으로 결과 통합
        
        RRF(d) = Σ 1 / (k + rank(d))
        
        Args:
            vector_results: 벡터 검색 결과
            bm25_results: BM25 검색 결과
            
        Returns:
            통합된 검색 결과
        """
        # 문서별 RRF 점수 계산
        doc_scores = {}
        
        # 벡터 검색 결과 처리
        for result in vector_results:
            doc_id = id(result['text'])  # 문서 고유 ID
            rank = result['rank']
            rrf_score = 1.0 / (self.rrf_k + rank)
            
            if doc_id not in doc_scores:
                doc_scores[doc_id] = {
                    'result': result,
                    'rrf_score': 0.0,
                    'vector_score': result['score'],
                    'bm25_score': 0.0
                }
            doc_scores[doc_id]['rrf_score'] += rrf_score * self.vector_weight
            doc_scores[doc_id]['vector_score'] = result['score']
        
        # BM25 검색 결과 처리
        for result in bm25_results:
            doc_id = id(result['text'])
            rank = result['rank']
            rrf_score = 1.0 / (self.rrf_k + rank)
            
            if doc_id not in doc_scores:
                doc_scores[doc_id] = {
                    'result': result,
                    'rrf_score': 0.0,
                    'vector_score': 0.0,
                    'bm25_score': result['score']
                }
            doc_scores[doc_id]['rrf_score'] += rrf_score * self.bm25_weight
            doc_scores[doc_id]['bm25_score'] = result['score']
        
        # RRF 점수로 정렬
        sorted_docs = sorted(
            doc_scores.values(),
            key=lambda x: x['rrf_score'],
            reverse=True
        )
        
        # 결과 구성
        final_results = []
        for i, doc_data in enumerate(sorted_docs):
            result = doc_data['result'].copy()
            result['score'] = doc_data['rrf_score']
            result['vector_score'] = doc_data['vector_score']
            result['bm25_score'] = doc_data['bm25_score']
            result['rank'] = i + 1
            final_results.append(result)
        
        return final_results
    
    def _weighted_combination(
        self,
        vector_results: List[Dict[str, Any]],
        bm25_results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        가중치 조합으로 결과 통합
        
        final_score = vector_weight * vector_score + bm25_weight * bm25_score
        
        Args:
            vector_results: 벡터 검색 결과
            bm25_results: BM25 검색 결과
            
        Returns:
            통합된 검색 결과
        """
        # 문서별 점수 계산
        doc_scores = {}
        
        # 벡터 검색 결과 처리
        for result in vector_results:
            doc_text = result['text']
            
            # FAISS는 L2 distance를 반환 (작을수록 유사)
            # 유사도로 변환: 1 / (1 + distance)
            vector_similarity = 1.0 / (1.0 + result['score'])
            
            if doc_text not in doc_scores:
                doc_scores[doc_text] = {
                    'result': result,
                    'vector_score': vector_similarity,
                    'bm25_score': 0.0
                }
            else:
                doc_scores[doc_text]['vector_score'] = max(
                    doc_scores[doc_text]['vector_score'],
                    vector_similarity
                )
        
        # BM25 검색 결과 처리
        for result in bm25_results:
            doc_text = result['text']
            
            if doc_text not in doc_scores:
                doc_scores[doc_text] = {
                    'result': result,
                    'vector_score': 0.0,
                    'bm25_score': result['score']
                }
            else:
                doc_scores[doc_text]['bm25_score'] = max(
                    doc_scores[doc_text]['bm25_score'],
                    result['score']
                )
        
        # 최종 점수 계산 및 정렬
        final_results = []
        for doc_text, doc_data in doc_scores.items():
            combined_score = (
                self.vector_weight * doc_data['vector_score'] +
                self.bm25_weight * doc_data['bm25_score']
            )
            
            result = doc_data['result'].copy()
            result['score'] = combined_score
            result['vector_score'] = doc_data['vector_score']
            result['bm25_score'] = doc_data['bm25_score']
            final_results.append(result)
        
        # 점수로 정렬
        final_results.sort(key=lambda x: x['score'], reverse=True)
        
        # rank 재할당
        for i, result in enumerate(final_results):
            result['rank'] = i + 1
        
        return final_results
    
    def search(
        self, 
        query: str, 
        top_k: int = 5,
        filter_codes: Dict[str, str] = None
    ) -> List[Dict[str, Any]]:
        """
        하이브리드 검색 (벡터 + BM25)
        
        Args:
            query: 검색 질문
            top_k: 반환할 결과 수
            filter_codes: 필터링할 코드 (예: {"재료코드": "A12345"})
            
        Returns:
            검색 결과 리스트
        """
        # 쿼리 확장 (도메인 특화 키워드 추가)
        expander = get_query_expander()
        expanded_query = expander.expand_query(query)
        
        # 쿼리가 확장되었으면 로그 출력
        if expanded_query != query:
            print(f"[쿼리 확장] 원본: {query}")
            print(f"[쿼리 확장] 확장: {expanded_query}")
        
        # 각 검색기에서 더 많은 후보를 가져옴
        # Reranker 사용 시 더 많은 후보 검색 (top_k * 4)
        search_k = top_k * 4 if self.use_reranker else top_k * 2
        
        # 1. FAISS 벡터 검색 (확장된 쿼리 사용)
        vector_results = self.faiss_retriever.search(
            query=expanded_query,
            top_k=search_k,
            filter_codes=filter_codes
        )
        
        # 2. BM25 키워드 검색 (확장된 쿼리 사용)
        bm25_results = self.bm25_retriever.search(
            query=expanded_query,
            top_k=search_k
        )
        
        # 필터링 적용 (BM25 결과에도)
        if filter_codes:
            filtered_bm25 = []
            for result in bm25_results:
                match = True
                for key, value in filter_codes.items():
                    if result['metadata'].get(key) != value:
                        match = False
                        break
                if match:
                    filtered_bm25.append(result)
            bm25_results = filtered_bm25
        
        # 3. 결과 통합
        if self.use_rrf:
            final_results = self._reciprocal_rank_fusion(vector_results, bm25_results)
        else:
            final_results = self._weighted_combination(vector_results, bm25_results)
        
        # 4. Reranking (선택적)
        if self.use_reranker and final_results:
            print(f"\n[Reranking] {len(final_results)}개 결과를 Cohere Rerank로 재정렬")
            final_results = self.reranker.rerank(query, final_results, top_k=top_k)
            return final_results
        
        # 5. top_k 개수만큼만 반환 (reranking 미사용 시)
        return final_results[:top_k]
    
    def search_by_codes(
        self,
        material_code: str = None,
        procedure_code: str = None,
        query: str = "",
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        재료코드/시술코드로 필터링하여 하이브리드 검색
        
        Args:
            material_code: 재료코드
            procedure_code: 시술코드
            query: 검색 질문 (선택사항)
            top_k: 반환할 결과 수
            
        Returns:
            검색 결과 리스트
        """
        # 필터 구성
        filter_codes = {}
        if material_code:
            filter_codes["재료코드"] = material_code
        if procedure_code:
            filter_codes["시술코드"] = procedure_code
        
        # 질문이 없으면 기본 질문 생성
        if not query:
            query = f"재료코드 {material_code} 시술코드 {procedure_code}의 보험 인정기준"
        
        # 검색 수행
        k = top_k if top_k else 5
        return self.search(query, k, filter_codes if filter_codes else None)


# 테스트용 메인 함수
if __name__ == "__main__":
    print("=" * 60)
    print("하이브리드 검색기 테스트")
    print("=" * 60)
    
    retriever = HybridRetriever(
        vector_weight=0.7,
        bm25_weight=0.3,
        use_rrf=False  # 가중치 조합 방식 사용
    )
    
    # 테스트 검색
    print("\n테스트: '10mm 이상의 비파열성 뇌동맥류'")
    results = retriever.search("10mm 이상의 비파열성 뇌동맥류", top_k=5)
    
    for i, result in enumerate(results, 1):
        print(f"\n[{i}] 종합 점수: {result['score']:.4f}")
        print(f"    벡터: {result.get('vector_score', 0):.4f}, BM25: {result.get('bm25_score', 0):.4f}")
        print(f"    타입: {result['metadata'].get('type', 'N/A')}")
        print(f"    내용: {result['text'][:100]}...")

