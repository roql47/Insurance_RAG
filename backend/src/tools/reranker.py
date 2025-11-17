"""
AWS Bedrock Cohere Rerank 3.5 API
검색 결과를 재정렬하여 정확도 향상
"""

import json
import os
from typing import List, Dict, Any
import boto3
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


class CohereReranker:
    """AWS Bedrock Cohere Rerank 3.5를 사용한 재정렬"""
    
    def __init__(self):
        """AWS Bedrock 클라이언트 초기화"""
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.model_id = os.getenv("RERANK_MODEL_ID", "cohere.rerank-v3-5:0")
        
        # Bedrock Runtime 클라이언트 생성
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.aws_region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        
        print(f"[OK] CohereReranker 초기화")
        print(f"    리전: {self.aws_region}")
        print(f"    모델: {self.model_id}")
    
    def rerank(
        self,
        query: str,
        documents: List[Dict[str, Any]],
        top_k: int = 5
    ) -> List[Dict[str, Any]]:
        """
        검색 결과를 Cohere Rerank로 재정렬
        
        Args:
            query: 검색 질문
            documents: 검색 결과 리스트 (각 문서는 'text'와 'metadata' 포함)
            top_k: 반환할 상위 결과 수
            
        Returns:
            재정렬된 검색 결과 리스트
        """
        if not documents:
            return []
        
        # 최대 100개까지만 rerank 가능 (Cohere 제한)
        if len(documents) > 100:
            print(f"⚠️  문서 수가 100개를 초과하여 상위 100개만 rerank합니다.")
            documents = documents[:100]
        
        try:
            # 1. 문서를 Cohere API 형식으로 변환
            doc_texts = [doc['text'] for doc in documents]
            
            # 2. Cohere Rerank API 호출 (AWS Bedrock 형식)
            body = json.dumps({
                "query": query,
                "documents": doc_texts,
                "top_n": min(top_k, len(documents)),
                "return_documents": False
            })
            
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType="application/json",
                accept="application/json"
            )
            
            # 3. 응답 파싱
            response_body = json.loads(response["body"].read())
            results = response_body.get("results", [])
            
            # 4. relevance_score로 재정렬된 결과 구성
            reranked_docs = []
            for result in results:
                index = result["index"]
                relevance_score = result["relevance_score"]
                
                # 원본 문서에 relevance_score 추가
                doc = documents[index].copy()
                doc['rerank_score'] = relevance_score
                doc['original_rank'] = index + 1
                
                # 기존 score를 original_score로 보존
                if 'score' in doc:
                    doc['original_score'] = doc['score']
                
                # rerank_score를 새로운 score로 설정
                doc['score'] = relevance_score
                
                reranked_docs.append(doc)
            
            print(f"✅ Reranking 완료: {len(documents)}개 → {len(reranked_docs)}개")
            
            # 상위 몇 개의 점수 출력 (디버깅용)
            for i, doc in enumerate(reranked_docs[:3], 1):
                print(f"   [{i}] Rerank: {doc['rerank_score']:.4f} "
                      f"(원본 순위: {doc['original_rank']}, "
                      f"원본 점수: {doc.get('original_score', 0):.4f})")
            
            return reranked_docs
            
        except Exception as e:
            error_msg = f"Reranking 중 오류 발생: {str(e)}"
            print(f"❌ {error_msg}")
            
            # 오류 시 원본 결과 반환
            print("   → 원본 검색 결과를 반환합니다.")
            return documents[:top_k]


# 싱글톤 인스턴스
_reranker = None


def get_reranker() -> CohereReranker:
    """Reranker 싱글톤 인스턴스 반환"""
    global _reranker
    if _reranker is None:
        _reranker = CohereReranker()
    return _reranker


# 테스트용 메인 함수
if __name__ == "__main__":
    reranker = CohereReranker()
    
    # 테스트 질의와 문서
    query = "9mm 뇌동맥 혈관에 스텐트 삽입 가능해?"
    
    test_docs = [
        {
            "text": "좌측 혈관(LM, LAD, LCx)과 우측 혈관(RCA)을 동시 실시한 경우 관상동맥 스텐트 삽입술 수가산정방법",
            "metadata": {"type": "관상동맥"},
            "score": 0.85
        },
        {
            "text": "직경 10mm이상의 비파열성 뇌동맥류 급여대상. 직경 10mm미만의 비파열성 뇌동맥류 중 아래의 경우 사례별로 인정",
            "metadata": {"type": "뇌동맥류"},
            "score": 0.65
        },
        {
            "text": "경피적 혈관성형술(PTC, atherectomy 등) 후 관상동맥 스텐트 혈관직경이 2.5mm 이상",
            "metadata": {"type": "관상동맥"},
            "score": 0.75
        }
    ]
    
    print(f"질의: {query}\n")
    print("원본 검색 결과:")
    for i, doc in enumerate(test_docs, 1):
        print(f"  [{i}] 점수: {doc['score']:.2f} - {doc['text'][:50]}...")
    
    print("\n" + "=" * 60)
    reranked = reranker.rerank(query, test_docs, top_k=3)
    
    print("\nReranked 결과:")
    for i, doc in enumerate(reranked, 1):
        print(f"  [{i}] Rerank: {doc['rerank_score']:.4f} "
              f"(원본: {doc['original_score']:.2f}, 순위: {doc['original_rank']}) "
              f"- {doc['text'][:50]}...")

