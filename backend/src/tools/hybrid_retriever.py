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
from tools.bm25_reranker import get_bm25_reranker

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
    
    def get_all_chunks_by_doc_code(
        self,
        doc_code: str,
        max_chunks: int = 100
    ) -> List[Dict[str, Any]]:
        """
        문서 코드로 해당 문서의 모든 청크 반환
        
        Args:
            doc_code: 문서 코드 (예: "자656", "제2022-264호")
            max_chunks: 최대 반환 청크 수 (토큰 제한 방지)
            
        Returns:
            해당 문서의 모든 청크 리스트
        """
        if not self.faiss_retriever.metadata:
            print("[WARNING] 메타데이터가 로드되지 않았습니다.")
            return []
        
        print(f"\n[문서 검색] 문서 코드: '{doc_code}'")
        
        # 메타데이터에서 doc_code가 일치하는 청크 찾기
        matching_chunks = []
        
        for item in self.faiss_retriever.metadata:
            metadata = item.get('metadata', {})
            item_doc_code = metadata.get('doc_code', '')
            
            # 문서 코드 매칭
            if item_doc_code == doc_code:
                chunk = {
                    "text": item['text'],
                    "metadata": metadata,
                    "score": 1.0,  # 필터링된 결과는 모두 관련성 높음
                    "rank": len(matching_chunks) + 1
                }
                matching_chunks.append(chunk)
                
                # 최대 개수 제한
                if len(matching_chunks) >= max_chunks:
                    break
        
        if matching_chunks:
            print(f"[OK] {len(matching_chunks)}개 청크 발견")
        else:
            print(f"[WARNING] 문서 코드 '{doc_code}'에 해당하는 청크를 찾을 수 없습니다.")
        
        return matching_chunks
    
    def get_all_chunks_by_pdf_title(
        self,
        pdf_title_keyword: str,
        max_chunks: int = 100
    ) -> List[Dict[str, Any]]:
        """
        PDF 제목 키워드로 해당 문서의 모든 청크 반환
        
        Args:
            pdf_title_keyword: PDF 제목에 포함된 키워드
            max_chunks: 최대 반환 청크 수
            
        Returns:
            해당 문서의 모든 청크 리스트
        """
        if not self.faiss_retriever.metadata:
            print("[WARNING] 메타데이터가 로드되지 않았습니다.")
            return []
        
        print(f"\n[문서 검색] PDF 제목 키워드: '{pdf_title_keyword}'")
        
        # 메타데이터에서 pdf_title이 키워드를 포함하는 청크 찾기
        matching_chunks = []
        
        for item in self.faiss_retriever.metadata:
            metadata = item.get('metadata', {})
            pdf_title = metadata.get('pdf_title', '')
            
            # PDF 제목에 키워드가 포함되어 있는지 확인
            if pdf_title_keyword.lower() in pdf_title.lower():
                chunk = {
                    "text": item['text'],
                    "metadata": metadata,
                    "score": 1.0,
                    "rank": len(matching_chunks) + 1
                }
                matching_chunks.append(chunk)
                
                # 최대 개수 제한
                if len(matching_chunks) >= max_chunks:
                    break
        
        if matching_chunks:
            print(f"[OK] {len(matching_chunks)}개 청크 발견")
        else:
            print(f"[WARNING] 제목에 '{pdf_title_keyword}'가 포함된 문서를 찾을 수 없습니다.")
        
        return matching_chunks
    
    def search_with_fallback(
        self,
        query: str,
        top_k: int = 5,
        filter_codes: Dict[str, str] = None,
        use_local_rerank: bool = True
    ) -> List[Dict[str, Any]]:
        """
        하이브리드 검색 + BM25 리랭크 + Fallback (primary_field 없는 문서 전체 검색)
        
        Args:
            query: 검색 질문
            top_k: 반환할 결과 수
            filter_codes: 필터링할 코드
            use_local_rerank: BM25 로컬 리랭크 사용 여부
            
        Returns:
            검색 결과 리스트
        """
        # 1. 일반 하이브리드 검색
        results = self.search(query, top_k, filter_codes)
        
        # 2. 결과가 있는지 확인
        if not results:
            print("[INFO] 검색 결과가 없습니다.")
            return []
        
        # 3. primary_field가 없는 문서 감지
        docs_without_primary = set()
        
        for result in results:
            metadata = result.get('metadata', {})
            
            # primary_field가 없고, doc_code가 있는 경우
            if not metadata.get('primary_field') and metadata.get('doc_code'):
                doc_code = metadata['doc_code']
                docs_without_primary.add(doc_code)
        
        # 4. primary_field 없는 문서의 전체 청크 추가
        additional_chunks = []
        if docs_without_primary:
            print(f"\n[Fallback] primary_field 없는 문서 {len(docs_without_primary)}개 발견")
            for doc_code in docs_without_primary:
                print(f"  → {doc_code} 문서 전체 청크 추가")
                doc_chunks = self.get_all_chunks_by_doc_code(doc_code, max_chunks=50)
                additional_chunks.extend(doc_chunks)
        
        # 5. 기존 결과와 추가 청크 합치기
        all_results = results + additional_chunks
        
        # 6. BM25 로컬 리랭크 적용
        if use_local_rerank and len(all_results) > top_k:
            print(f"\n[Local Rerank] BM25로 {len(all_results)}개 청크 재정렬")
            local_reranker = get_bm25_reranker()
            all_results = local_reranker.rerank(query, all_results, top_k=top_k * 2)
        
        # 7. 최종 결과 반환
        return all_results[:top_k * 2]  # top_k의 2배 반환 (충분한 컨텍스트)


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

