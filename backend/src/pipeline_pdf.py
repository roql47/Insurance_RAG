"""
PDF 문서 전처리 파이프라인
PDF 파일을 청크로 분할하고 임베딩을 생성하여 FAISS 인덱스에 저장
"""

import json
import os
import pickle
from typing import List, Dict, Any
import numpy as np
import faiss
from dotenv import load_dotenv

from tools.embedder_tool import TitanEmbedder
from tools.document_loader import DocumentLoader

# 환경 변수 로드
load_dotenv()


class PDFPreprocessor:
    """PDF 문서 전처리 및 벡터 스토어 생성 클래스"""
    
    def __init__(self):
        """초기화"""
        self.embedder = TitanEmbedder()
        self.loader = DocumentLoader()
        self.vector_store_path = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
        
        # 디렉토리 생성
        os.makedirs(self.vector_store_path, exist_ok=True)
    
    def load_pdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        PDF 파일 로드
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            문서 데이터
        """
        print(f"PDF 로드 중: {pdf_path}")
        doc_data = self.loader.load_pdf(pdf_path, method="pdfplumber")
        return doc_data
    
    def create_chunks(self, doc_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        문서를 청크로 분할
        
        Args:
            doc_data: 문서 데이터
            
        Returns:
            청크 리스트
        """
        print("문서 청크 분할 중...")
        
        # 문서 로더의 청크 분할 사용
        chunks = self.loader.chunk_document(
            doc_data,
            chunk_size=1000,  # 1000자씩
            overlap=100       # 100자 오버랩
        )
        
        # 메타데이터 강화
        for chunk in chunks:
            chunk['metadata']['document_title'] = doc_data.get('filename', 'Unknown')
            chunk['metadata']['source_type'] = 'pdf'
        
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
    
    def run_pipeline(self, pdf_path: str):
        """
        전체 파이프라인 실행
        
        Args:
            pdf_path: PDF 파일 경로
        """
        print("=" * 60)
        print("PDF 문서 전처리 파이프라인 시작")
        print("=" * 60)
        
        # 1. PDF 로드
        doc_data = self.load_pdf(pdf_path)
        
        # 2. 청크 생성
        chunks = self.create_chunks(doc_data)
        
        # 3. 임베딩 생성
        chunks_with_embeddings = self.create_embeddings(chunks)
        
        # 4. FAISS에 저장
        self.save_to_faiss(chunks_with_embeddings)
        
        print("=" * 60)
        print("PDF 문서 전처리 파이프라인 완료")
        print("=" * 60)


# 메인 실행
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("사용법: python pipeline_pdf.py <PDF_파일_경로>")
        print("예시: python pipeline_pdf.py ../data/raw/test.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # 전처리기 초기화
    preprocessor = PDFPreprocessor()
    
    # 파이프라인 실행
    try:
        preprocessor.run_pipeline(pdf_path)
        print("\n✅ 성공! 이제 'python run_server.py'로 API 서버를 시작할 수 있습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        sys.exit(1)

