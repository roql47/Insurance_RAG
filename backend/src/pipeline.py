"""
데이터 전처리 파이프라인
원본 데이터를 청크로 분할하고 임베딩을 생성하여 FAISS 인덱스에 저장
"""

import json
import os
import pickle
from typing import List, Dict, Any
import numpy as np
import faiss
from dotenv import load_dotenv

from tools.embedder_tool import TitanEmbedder

# 환경 변수 로드
load_dotenv()


class DataPreprocessor:
    """데이터 전처리 및 벡터 스토어 생성 클래스"""
    
    def __init__(self):
        """초기화"""
        self.embedder = TitanEmbedder()
        self.vector_store_path = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
        
        # 디렉토리 생성
        os.makedirs(self.vector_store_path, exist_ok=True)
    
    def load_raw_data(self, file_path: str) -> List[Dict[str, Any]]:
        """
        원본 JSON 데이터 로드
        
        Args:
            file_path: JSON 파일 경로
            
        Returns:
            데이터 리스트
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"원본 데이터 로드 완료: {len(data)}개 항목")
        return data
    
    def create_chunks(self, data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        데이터를 의미 있는 청크로 분할
        각 보험 인정기준 항목을 여러 청크로 나눔
        
        Args:
            data: 원본 데이터 리스트
            
        Returns:
            청크 리스트 (각 청크는 텍스트와 메타데이터 포함)
        """
        chunks = []
        
        for item in data:
            # 청크 1: 기본 정보 + 인정기준
            chunk_1 = {
                "text": f"""재료코드: {item['재료코드']}
재료명: {item['재료명']}
시술코드: {item['시술코드']}
시술명: {item['시술명']}

인정기준:
{item['인정기준']}""",
                "metadata": {
                    "chunk_id": f"{item['id']}_basic",
                    "재료코드": item['재료코드'],
                    "재료명": item['재료명'],
                    "시술코드": item['시술코드'],
                    "시술명": item['시술명'],
                    "type": "인정기준"
                }
            }
            chunks.append(chunk_1)
            
            # 청크 2: 제외사항
            chunk_2 = {
                "text": f"""재료코드: {item['재료코드']} ({item['재료명']})
시술코드: {item['시술코드']} ({item['시술명']})

제외사항 (인정되지 않는 경우):
{item['제외사항']}""",
                "metadata": {
                    "chunk_id": f"{item['id']}_exclusion",
                    "재료코드": item['재료코드'],
                    "재료명": item['재료명'],
                    "시술코드": item['시술코드'],
                    "시술명": item['시술명'],
                    "type": "제외사항"
                }
            }
            chunks.append(chunk_2)
            
            # 청크 3: 심사기준 + 근거법령
            chunk_3 = {
                "text": f"""재료코드: {item['재료코드']} ({item['재료명']})
시술코드: {item['시술코드']} ({item['시술명']})

심사기준:
{item['심사기준']}

근거법령:
{item['근거법령']}""",
                "metadata": {
                    "chunk_id": f"{item['id']}_criteria",
                    "재료코드": item['재료코드'],
                    "재료명": item['재료명'],
                    "시술코드": item['시술코드'],
                    "시술명": item['시술명'],
                    "type": "심사기준"
                }
            }
            chunks.append(chunk_3)
            
            # 청크 4: 참고사항 (있는 경우)
            if '참고사항' in item and item['참고사항']:
                chunk_4 = {
                    "text": f"""재료코드: {item['재료코드']} ({item['재료명']})
시술코드: {item['시술코드']} ({item['시술명']})

참고사항:
{item['참고사항']}""",
                    "metadata": {
                        "chunk_id": f"{item['id']}_reference",
                        "재료코드": item['재료코드'],
                        "재료명": item['재료명'],
                        "시술코드": item['시술코드'],
                        "시술명": item['시술명'],
                        "type": "참고사항"
                    }
                }
                chunks.append(chunk_4)
        
        print(f"청크 생성 완료: {len(chunks)}개 청크")
        return chunks
    
    def create_embeddings(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        청크에 임베딩 추가
        
        Args:
            chunks: 청크 리스트
            
        Returns:
            임베딩이 추가된 청크 리스트
        """
        print("임베딩 생성 시작...")
        
        texts = [chunk['text'] for chunk in chunks]
        embeddings = self.embedder.embed_texts(texts)
        
        # 임베딩을 각 청크에 추가
        for i, chunk in enumerate(chunks):
            chunk['embedding'] = embeddings[i]
        
        print("임베딩 생성 완료")
        return chunks
    
    def save_to_faiss(self, chunks: List[Dict[str, Any]]):
        """
        FAISS 인덱스에 저장
        
        Args:
            chunks: 임베딩이 포함된 청크 리스트
        """
        print("FAISS 인덱스 생성 중...")
        
        # 임베딩 추출 (None이 아닌 것만)
        valid_chunks = [c for c in chunks if c['embedding'] is not None]
        embeddings = np.array([c['embedding'] for c in valid_chunks], dtype='float32')
        
        # FAISS 인덱스 생성 (L2 거리 사용)
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        
        # 정규화된 벡터를 사용하면 내적 = 코사인 유사도
        # Titan은 이미 정규화된 벡터를 반환하므로 그대로 사용
        index.add(embeddings)
        
        # 인덱스 저장
        index_path = os.path.join(self.vector_store_path, "faiss_index.bin")
        faiss.write_index(index, index_path)
        print(f"FAISS 인덱스 저장 완료: {index_path}")
        
        # 메타데이터 저장 (임베딩 제외)
        metadata_list = []
        for chunk in valid_chunks:
            metadata = {
                "text": chunk['text'],
                "metadata": chunk['metadata']
            }
            metadata_list.append(metadata)
        
        metadata_path = os.path.join(self.vector_store_path, "metadata.pkl")
        with open(metadata_path, 'wb') as f:
            pickle.dump(metadata_list, f)
        print(f"메타데이터 저장 완료: {metadata_path}")
        
        print(f"총 {len(valid_chunks)}개 벡터가 인덱스에 추가되었습니다.")
    
    def run_pipeline(self, raw_data_path: str):
        """
        전체 파이프라인 실행
        
        Args:
            raw_data_path: 원본 데이터 파일 경로
        """
        print("=" * 60)
        print("데이터 전처리 파이프라인 시작")
        print("=" * 60)
        
        # 1. 원본 데이터 로드
        data = self.load_raw_data(raw_data_path)
        
        # 2. 청크 생성
        chunks = self.create_chunks(data)
        
        # 3. 임베딩 생성
        chunks_with_embeddings = self.create_embeddings(chunks)
        
        # 4. FAISS에 저장
        self.save_to_faiss(chunks_with_embeddings)
        
        print("=" * 60)
        print("데이터 전처리 파이프라인 완료")
        print("=" * 60)


# 메인 실행
if __name__ == "__main__":
    # 전처리기 초기화
    preprocessor = DataPreprocessor()
    
    # 샘플 데이터로 파이프라인 실행
    raw_data_path = "./data/raw/sample_criteria.json"
    preprocessor.run_pipeline(raw_data_path)

