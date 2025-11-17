"""
LangChain용 하이브리드 검색기
기존 HybridRetriever를 LangChain BaseRetriever로 래핑
"""

from typing import List, Dict, Any, Optional
from langchain_core.retrievers import BaseRetriever
from langchain_core.documents import Document
from langchain_core.callbacks import CallbackManagerForRetrieverRun

from tools.hybrid_retriever import HybridRetriever


class HybridLangChainRetriever(BaseRetriever):
    """
    LangChain BaseRetriever를 상속받은 하이브리드 검색기
    FAISS (벡터 검색 70%) + BM25 (키워드 검색 30%)
    """
    
    # 클래스 속성으로 검색기 정의
    hybrid_retriever: HybridRetriever = None
    vector_weight: float = 0.7
    bm25_weight: float = 0.3
    top_k: int = 5
    
    def __init__(
        self, 
        vector_weight: float = 0.7,
        bm25_weight: float = 0.3,
        top_k: int = 5,
        **kwargs
    ):
        """
        초기화
        
        Args:
            vector_weight: 벡터 검색 가중치 (기본 0.7)
            bm25_weight: BM25 검색 가중치 (기본 0.3)
            top_k: 반환할 문서 수 (기본 5)
        """
        super().__init__(**kwargs)
        self.vector_weight = vector_weight
        self.bm25_weight = bm25_weight
        self.top_k = top_k
        
        # 하이브리드 검색기 초기화
        self.hybrid_retriever = HybridRetriever(
            vector_weight=vector_weight,
            bm25_weight=bm25_weight,
            use_rrf=False
        )
        
        print(f"✅ LangChain 하이브리드 검색기 초기화 (벡터: {vector_weight}, BM25: {bm25_weight})")
    
    def _get_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
        **kwargs
    ) -> List[Document]:
        """
        관련 문서 검색 (LangChain BaseRetriever 인터페이스)
        
        Args:
            query: 검색 질문
            run_manager: 콜백 매니저
            **kwargs: 추가 검색 옵션
            
        Returns:
            LangChain Document 리스트
        """
        try:
            # 필터 추출 (material_code, procedure_code 등)
            filter_codes = kwargs.get("filter", None)
            top_k = kwargs.get("k", self.top_k)
            
            # 하이브리드 검색 실행
            results = self.hybrid_retriever.search(
                query=query,
                top_k=top_k,
                filter_codes=filter_codes
            )
            
            # LangChain Document 형식으로 변환
            documents = []
            for result in results:
                # 메타데이터에 점수 추가
                metadata = result.get('metadata', {}).copy()
                metadata['score'] = result.get('score', 0)
                metadata['vector_score'] = result.get('vector_score', 0)
                metadata['bm25_score'] = result.get('bm25_score', 0)
                
                doc = Document(
                    page_content=result['text'],
                    metadata=metadata
                )
                documents.append(doc)
            
            return documents
            
        except Exception as e:
            print(f"검색 중 오류 발생: {str(e)}")
            import traceback
            traceback.print_exc()
            return []
    
    async def _aget_relevant_documents(
        self,
        query: str,
        *,
        run_manager: Optional[CallbackManagerForRetrieverRun] = None,
        **kwargs
    ) -> List[Document]:
        """
        비동기 검색 (현재는 동기 버전 호출)
        
        Args:
            query: 검색 질문
            run_manager: 콜백 매니저
            **kwargs: 추가 검색 옵션
            
        Returns:
            LangChain Document 리스트
        """
        # 현재는 동기 버전 호출
        # 필요 시 asyncio로 비동기 처리 구현 가능
        return self._get_relevant_documents(query, run_manager=run_manager, **kwargs)


# LangChain VectorStore 스타일 래퍼 (선택사항)
class HybridVectorStore:
    """
    VectorStore 인터페이스를 흉내낸 래퍼
    LangChain의 VectorStore를 기대하는 코드와의 호환성을 위해
    """
    
    def __init__(
        self,
        vector_weight: float = 0.7,
        bm25_weight: float = 0.3
    ):
        """초기화"""
        self.retriever_instance = HybridLangChainRetriever(
            vector_weight=vector_weight,
            bm25_weight=bm25_weight
        )
    
    def as_retriever(self, **kwargs) -> HybridLangChainRetriever:
        """
        Retriever로 반환
        
        Returns:
            HybridLangChainRetriever 인스턴스
        """
        # kwargs로 top_k 등을 조정 가능
        if "search_kwargs" in kwargs:
            k = kwargs["search_kwargs"].get("k", 5)
            self.retriever_instance.top_k = k
        
        return self.retriever_instance
    
    def similarity_search(
        self,
        query: str,
        k: int = 5,
        **kwargs
    ) -> List[Document]:
        """
        유사도 검색 (VectorStore 인터페이스)
        
        Args:
            query: 검색 질문
            k: 반환할 문서 수
            **kwargs: 추가 옵션
            
        Returns:
            Document 리스트
        """
        return self.retriever_instance._get_relevant_documents(
            query,
            k=k,
            **kwargs
        )
    
    def similarity_search_with_score(
        self,
        query: str,
        k: int = 5,
        **kwargs
    ) -> List[tuple[Document, float]]:
        """
        점수와 함께 유사도 검색
        
        Args:
            query: 검색 질문
            k: 반환할 문서 수
            **kwargs: 추가 옵션
            
        Returns:
            (Document, score) 튜플 리스트
        """
        docs = self.similarity_search(query, k=k, **kwargs)
        # 메타데이터에서 점수 추출
        return [(doc, doc.metadata.get("score", 0.0)) for doc in docs]


# 테스트용 메인 함수
if __name__ == "__main__":
    print("=" * 60)
    print("LangChain 하이브리드 검색기 테스트")
    print("=" * 60)
    
    # 검색기 생성
    retriever = HybridLangChainRetriever()
    
    # 테스트 검색
    test_query = "스텐트 삽입술 급여 인정기준"
    print(f"\n테스트 질문: {test_query}\n")
    
    documents = retriever._get_relevant_documents(test_query)
    
    print(f"검색 결과: {len(documents)}개 문서\n")
    for i, doc in enumerate(documents, 1):
        print(f"[{i}] 점수: {doc.metadata.get('score', 0):.4f}")
        print(f"    파일: {doc.metadata.get('filename', 'Unknown')}")
        print(f"    내용: {doc.page_content[:100]}...")
        print()
    
    # VectorStore 스타일 테스트
    print("\n" + "=" * 60)
    print("VectorStore 스타일 인터페이스 테스트")
    print("=" * 60)
    
    vector_store = HybridVectorStore()
    results = vector_store.similarity_search(test_query, k=3)
    
    print(f"\n검색 결과: {len(results)}개 문서\n")
    for i, doc in enumerate(results, 1):
        print(f"[{i}] {doc.metadata.get('filename', 'Unknown')}")
        print(f"    {doc.page_content[:100]}...")
        print()

