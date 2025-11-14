"""
FAISS 벡터 검색 툴
질문을 임베딩으로 변환하고 유사한 문서를 검색
"""

import os
import pickle
from typing import List, Dict, Any
import numpy as np
import faiss
from dotenv import load_dotenv

from tools.embedder_tool import TitanEmbedder

# 환경 변수 로드
load_dotenv()


class FAISSRetriever:
    """FAISS 벡터 검색 클래스"""
    
    def __init__(self):
        """초기화 및 인덱스 로드"""
        self.embedder = TitanEmbedder()
        self.vector_store_path = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
        self.top_k = int(os.getenv("TOP_K_RESULTS", "5"))
        
        # FAISS 인덱스 로드
        self.index = None
        self.metadata = None
        self._load_index()
    
    def _load_index(self):
        """FAISS 인덱스 및 메타데이터 로드"""
        index_path = os.path.join(self.vector_store_path, "faiss_index.bin")
        metadata_path = os.path.join(self.vector_store_path, "metadata.pkl")
        
        try:
            # FAISS 인덱스 로드
            if os.path.exists(index_path):
                self.index = faiss.read_index(index_path)
                print(f"FAISS 인덱스 로드 완료: {self.index.ntotal}개 벡터")
            else:
                print(f"경고: FAISS 인덱스 파일이 없습니다: {index_path}")
                print("데이터 전처리 파이프라인을 먼저 실행해주세요.")
            
            # 메타데이터 로드
            if os.path.exists(metadata_path):
                with open(metadata_path, 'rb') as f:
                    self.metadata = pickle.load(f)
                print(f"메타데이터 로드 완료: {len(self.metadata)}개 항목")
            else:
                print(f"경고: 메타데이터 파일이 없습니다: {metadata_path}")
                
        except Exception as e:
            print(f"인덱스 로드 중 오류 발생: {str(e)}")
            raise
    
    def search(
        self, 
        query: str, 
        top_k: int = None,
        filter_codes: Dict[str, str] = None
    ) -> List[Dict[str, Any]]:
        """
        질문과 유사한 문서 검색
        
        Args:
            query: 검색 질문
            top_k: 반환할 결과 수 (None이면 기본값 사용)
            filter_codes: 필터링할 코드 (예: {"재료코드": "A12345"})
            
        Returns:
            검색 결과 리스트 (각 결과는 text, metadata, score 포함)
        """
        if self.index is None or self.metadata is None:
            return {
                "error": "FAISS 인덱스가 로드되지 않았습니다. 데이터 전처리를 먼저 실행해주세요.",
                "results": []
            }
        
        try:
            # 1. 질문을 임베딩으로 변환
            query_embedding = self.embedder.embed_text(query)
            query_vector = np.array([query_embedding], dtype='float32')
            
            # 2. FAISS 검색 (더 많은 후보 검색)
            k = top_k if top_k else self.top_k
            search_k = k * 3 if filter_codes else k  # 필터링이 있으면 더 많이 검색
            
            distances, indices = self.index.search(query_vector, search_k)
            
            # 3. 결과 구성
            results = []
            for i, (dist, idx) in enumerate(zip(distances[0], indices[0])):
                if idx >= 0 and idx < len(self.metadata):
                    result = {
                        "text": self.metadata[idx]['text'],
                        "metadata": self.metadata[idx]['metadata'],
                        "score": float(dist),  # L2 거리 (작을수록 유사)
                        "rank": i + 1
                    }
                    
                    # 4. 필터링 적용
                    if filter_codes:
                        match = True
                        for key, value in filter_codes.items():
                            if result['metadata'].get(key) != value:
                                match = False
                                break
                        if match:
                            results.append(result)
                    else:
                        results.append(result)
                    
                    # top_k 개수만큼만 반환
                    if len(results) >= k:
                        break
            
            return results
            
        except Exception as e:
            print(f"검색 중 오류 발생: {str(e)}")
            return {
                "error": str(e),
                "results": []
            }
    
    def search_by_codes(
        self,
        material_code: str = None,
        procedure_code: str = None,
        query: str = "",
        top_k: int = None
    ) -> List[Dict[str, Any]]:
        """
        재료코드/시술코드로 필터링하여 검색
        
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
        return self.search(query, top_k, filter_codes if filter_codes else None)


# Strands Agent Tool로 래핑
def create_retriever_tool():
    """
    Strands Agent에서 사용 가능한 검색 툴 생성
    
    Returns:
        검색 툴 딕셔너리
    """
    retriever = FAISSRetriever()
    
    def search_function(query: str, material_code: str = None, procedure_code: str = None) -> str:
        """검색 함수 (Strands Agent용)"""
        results = retriever.search_by_codes(
            material_code=material_code,
            procedure_code=procedure_code,
            query=query,
            top_k=3
        )
        
        # 결과를 문자열로 포맷팅
        if isinstance(results, dict) and "error" in results:
            return f"검색 오류: {results['error']}"
        
        if not results:
            return "관련 문서를 찾을 수 없습니다."
        
        output = "검색 결과:\n\n"
        for i, result in enumerate(results, 1):
            output += f"[{i}] {result['metadata']['type']}\n"
            output += f"{result['text']}\n"
            output += f"유사도 점수: {result['score']:.4f}\n"
            output += "-" * 60 + "\n"
        
        return output
    
    tool = {
        "name": "search_insurance_criteria",
        "description": "보험 인정기준 데이터베이스에서 관련 정보를 검색합니다. 재료코드, 시술코드, 질문을 입력하면 관련 인정기준, 제외사항, 심사기준 등을 반환합니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "query": {
                    "type": "string",
                    "description": "검색할 질문 (예: '삭감 여부', '인정기준', '제외사항')"
                },
                "material_code": {
                    "type": "string",
                    "description": "재료코드 (선택사항)"
                },
                "procedure_code": {
                    "type": "string",
                    "description": "시술코드 (선택사항)"
                }
            },
            "required": ["query"]
        },
        "function": search_function
    }
    
    return tool


# 테스트용 메인 함수
if __name__ == "__main__":
    # 검색기 초기화 및 테스트
    retriever = FAISSRetriever()
    
    # 테스트 질의
    print("\n" + "=" * 60)
    print("테스트 1: 일반 검색")
    print("=" * 60)
    results = retriever.search("고관절 전치환술 인정기준", top_k=3)
    for i, result in enumerate(results, 1):
        print(f"\n[{i}] {result['metadata']['재료명']} - {result['metadata']['type']}")
        print(f"점수: {result['score']:.4f}")
        print(result['text'][:200] + "...")
    
    print("\n" + "=" * 60)
    print("테스트 2: 코드별 검색")
    print("=" * 60)
    results = retriever.search_by_codes(
        material_code="A12345",
        procedure_code="N2095",
        query="삭감 여부"
    )
    for i, result in enumerate(results, 1):
        print(f"\n[{i}] {result['metadata']['type']}")
        print(result['text'][:200] + "...")

