"""
여러 PDF 문서를 한 번에 전처리하는 배치 파이프라인
"""

import json
import os
import pickle
import glob
from typing import List, Dict, Any
import numpy as np
import faiss
from dotenv import load_dotenv

from tools.embedder_tool import TitanEmbedder
from tools.document_loader import DocumentLoader

# 환경 변수 로드
load_dotenv()


class BatchPDFPreprocessor:
    """여러 PDF 문서를 한 번에 전처리하는 클래스"""
    
    def __init__(self):
        """초기화"""
        self.embedder = TitanEmbedder()
        self.loader = DocumentLoader()
        self.vector_store_path = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
        
        # 디렉토리 생성
        os.makedirs(self.vector_store_path, exist_ok=True)
    
    def process_all_pdfs(self, pdf_folder: str):
        """
        폴더 내의 모든 PDF 파일 처리
        
        Args:
            pdf_folder: PDF 파일들이 있는 폴더 경로
        """
        print("=" * 60)
        print("배치 PDF 문서 전처리 파이프라인 시작")
        print("=" * 60)
        
        # PDF 파일 목록 가져오기
        pdf_pattern = os.path.join(pdf_folder, "*.pdf")
        pdf_files = glob.glob(pdf_pattern)
        
        if not pdf_files:
            print(f"오류: {pdf_folder}에 PDF 파일이 없습니다.")
            return
        
        print(f"\n발견된 PDF 파일: {len(pdf_files)}개")
        for i, pdf_file in enumerate(pdf_files, 1):
            print(f"  [{i}] {os.path.basename(pdf_file)}")
        print()
        
        # 모든 청크를 모으기
        all_chunks = []
        
        # 각 PDF 파일 처리
        for i, pdf_path in enumerate(pdf_files, 1):
            print(f"\n[{i}/{len(pdf_files)}] 처리 중: {os.path.basename(pdf_path)}")
            print("-" * 60)
            
            try:
                # PDF 로드
                doc_data = self.loader.load_pdf(pdf_path, method="pdfplumber")
                
                # 청크 생성
                chunks = self.loader.chunk_document(
                    doc_data,
                    chunk_size=1000,
                    overlap=100
                )
                
                # 메타데이터 강화
                for chunk in chunks:
                    chunk['metadata']['document_title'] = doc_data.get('filename', 'Unknown')
                    chunk['metadata']['source_type'] = 'pdf'
                    chunk['metadata']['source_file'] = os.path.basename(pdf_path)
                
                all_chunks.extend(chunks)
                print(f"[OK] 완료: {len(chunks)}개 청크 추가 (총 {len(all_chunks)}개)")
                
            except Exception as e:
                print(f"[ERROR] 오류 발생: {str(e)}")
                print(f"  파일 건너뛰기: {os.path.basename(pdf_path)}")
                continue
        
        if not all_chunks:
            print("\n오류: 처리된 청크가 없습니다.")
            return
        
        print(f"\n" + "=" * 60)
        print(f"총 {len(all_chunks)}개 청크 생성 완료")
        print("=" * 60)
        
        # 임베딩 생성
        print("\n임베딩 생성 시작...")
        texts = [chunk['text'] for chunk in all_chunks]
        embeddings = self.embedder.embed_texts(texts)
        
        for i, chunk in enumerate(all_chunks):
            chunk['embedding'] = embeddings[i]
        
        print("임베딩 생성 완료")
        
        # FAISS에 저장
        self.save_to_faiss(all_chunks)
        
        print("\n" + "=" * 60)
        print("배치 PDF 문서 전처리 파이프라인 완료")
        print("=" * 60)
        print(f"\n[SUCCESS] 총 {len(pdf_files)}개 PDF 파일, {len(all_chunks)}개 청크 학습 완료!")
    
    def save_to_faiss(self, chunks: List[Dict[str, Any]]):
        """
        FAISS 인덱스에 저장
        
        Args:
            chunks: 임베딩이 포함된 청크 리스트
        """
        print("\nFAISS 인덱스 생성 중...")
        
        # 임베딩 추출 (None이 아닌 것만)
        valid_chunks = [c for c in chunks if c['embedding'] is not None]
        embeddings = np.array([c['embedding'] for c in valid_chunks], dtype='float32')
        
        # FAISS 인덱스 생성
        dimension = embeddings.shape[1]
        index = faiss.IndexFlatL2(dimension)
        index.add(embeddings)
        
        # 인덱스 저장
        index_path = os.path.join(self.vector_store_path, "faiss_index.bin")
        faiss.write_index(index, index_path)
        print(f"FAISS 인덱스 저장 완료: {index_path}")
        
        # 메타데이터 저장
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


# 메인 실행
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("사용법: python pipeline_pdf_batch.py <PDF_폴더_경로>")
        print("예시: python pipeline_pdf_batch.py ../data/raw")
        sys.exit(1)
    
    pdf_folder = sys.argv[1]
    
    if not os.path.exists(pdf_folder):
        print(f"오류: 폴더를 찾을 수 없습니다: {pdf_folder}")
        sys.exit(1)
    
    # 전처리기 초기화
    preprocessor = BatchPDFPreprocessor()
    
    # 배치 파이프라인 실행
    try:
        preprocessor.process_all_pdfs(pdf_folder)
        print("\n[SUCCESS] 성공! 이제 'python run_server.py'로 API 서버를 시작할 수 있습니다.")
    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

