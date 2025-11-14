"""
AWS Bedrock Titan Embeddings 툴
텍스트를 벡터로 변환하는 임베딩 생성 기능
"""

import json
import os
from typing import List, Union
import boto3
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()


class TitanEmbedder:
    """AWS Bedrock Titan Embeddings를 사용한 임베딩 생성 클래스"""
    
    def __init__(self):
        """AWS Bedrock 클라이언트 초기화"""
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.embedding_model_id = os.getenv(
            "EMBEDDING_MODEL_ID", 
            "amazon.titan-embed-text-v2:0"
        )
        
        # Bedrock Runtime 클라이언트 생성
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.aws_region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
    
    def embed_text(self, text: str) -> List[float]:
        """
        단일 텍스트를 임베딩 벡터로 변환
        
        Args:
            text: 임베딩할 텍스트
            
        Returns:
            임베딩 벡터 (리스트)
        """
        try:
            # Titan Embeddings V2 API 호출
            body = json.dumps({
                "inputText": text,
                "dimensions": 1024,  # Titan V2는 최대 1024 차원
                "normalize": True     # 정규화된 벡터 반환
            })
            
            response = self.bedrock_runtime.invoke_model(
                modelId=self.embedding_model_id,
                body=body,
                contentType="application/json",
                accept="application/json"
            )
            
            # 응답 파싱
            response_body = json.loads(response["body"].read())
            embedding = response_body.get("embedding", [])
            
            return embedding
            
        except Exception as e:
            print(f"임베딩 생성 중 오류 발생: {str(e)}")
            raise
    
    def embed_texts(self, texts: List[str]) -> List[List[float]]:
        """
        여러 텍스트를 배치로 임베딩 벡터로 변환
        
        Args:
            texts: 임베딩할 텍스트 리스트
            
        Returns:
            임베딩 벡터 리스트
        """
        embeddings = []
        
        for i, text in enumerate(texts):
            try:
                embedding = self.embed_text(text)
                embeddings.append(embedding)
                
                if (i + 1) % 10 == 0:
                    print(f"임베딩 진행 중: {i + 1}/{len(texts)}")
                    
            except Exception as e:
                print(f"텍스트 {i} 임베딩 실패: {str(e)}")
                # 실패한 경우 None 추가
                embeddings.append(None)
        
        return embeddings


# Strands Agent Tool로 래핑
def create_embedder_tool():
    """
    Strands Agent에서 사용 가능한 임베딩 툴 생성
    
    Returns:
        임베딩 툴 딕셔너리
    """
    embedder = TitanEmbedder()
    
    tool = {
        "name": "embed_text",
        "description": "텍스트를 벡터 임베딩으로 변환합니다. 질의나 문서를 검색 가능한 형태로 만듭니다.",
        "parameters": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "임베딩으로 변환할 텍스트"
                }
            },
            "required": ["text"]
        },
        "function": lambda text: embedder.embed_text(text)
    }
    
    return tool


# 테스트용 메인 함수
if __name__ == "__main__":
    # 임베더 초기화 및 테스트
    embedder = TitanEmbedder()
    
    test_text = "고관절 전치환술의 보험 인정기준은 무엇인가요?"
    print(f"테스트 텍스트: {test_text}")
    
    embedding = embedder.embed_text(test_text)
    print(f"임베딩 차원: {len(embedding)}")
    print(f"임베딩 샘플 (처음 5개): {embedding[:5]}")

