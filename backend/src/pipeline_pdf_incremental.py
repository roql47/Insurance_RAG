"""
증분 학습: 기존 학습 데이터를 유지하고 새로운 PDF만 추가로 학습
"""

import json
import os
import pickle
import glob
from typing import List, Dict, Any, Set
import numpy as np
import faiss
from dotenv import load_dotenv
from datetime import datetime

from tools.embedder_tool import TitanEmbedder
from tools.document_loader import DocumentLoader

# 환경 변수 로드
load_dotenv()


class IncrementalPDFPreprocessor:
    """증분 학습을 지원하는 PDF 전처리 클래스"""
    
    def __init__(self):
        """초기화"""
        self.embedder = TitanEmbedder()
        self.loader = DocumentLoader()
        self.vector_store_path = os.getenv("VECTOR_STORE_PATH", "./data/vector_store")
        self.processed_files_path = os.path.join(self.vector_store_path, "processed_files.json")
        
        # 디렉토리 생성
        os.makedirs(self.vector_store_path, exist_ok=True)
        
        # 기존 인덱스 로드
        self.index = None
        self.metadata = []
        self.processed_files = set()
        self._load_existing_data()
    
    def _load_existing_data(self):
        """기존 FAISS 인덱스, 메타데이터, 처리된 파일 목록 로드"""
        index_path = os.path.join(self.vector_store_path, "faiss_index.bin")
        metadata_path = os.path.join(self.vector_store_path, "metadata.pkl")
        
        # FAISS 인덱스 로드
        if os.path.exists(index_path):
            self.index = faiss.read_index(index_path)
            print(f"[OK] 기존 FAISS 인덱스 로드: {self.index.ntotal}개 벡터")
        else:
            print("[INFO] 기존 FAISS 인덱스 없음 (새로 생성)")
        
        # 메타데이터 로드
        if os.path.exists(metadata_path):
            with open(metadata_path, 'rb') as f:
                self.metadata = pickle.load(f)
            print(f"[OK] 기존 메타데이터 로드: {len(self.metadata)}개 항목")
        else:
            print("[INFO] 기존 메타데이터 없음 (새로 생성)")
        
        # 처리된 파일 목록 로드
        if os.path.exists(self.processed_files_path):
            with open(self.processed_files_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.processed_files = set(data.get('files', []))
            print(f"[OK] 처리된 파일 목록 로드: {len(self.processed_files)}개 파일")
            for filename in self.processed_files:
                print(f"   - {filename}")
        else:
            print("[INFO] 처리된 파일 목록 없음")
    
    def _save_processed_files(self):
        """처리된 파일 목록 저장"""
        data = {
            'files': list(self.processed_files),
            'last_updated': datetime.now().isoformat()
        }
        with open(self.processed_files_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def process_new_pdfs(self, pdf_folder: str, force_reprocess: bool = False):
        """
        새로운 PDF 파일만 처리하여 기존 인덱스에 추가
        
        Args:
            pdf_folder: PDF 파일들이 있는 폴더 경로
            force_reprocess: True면 이미 처리된 파일도 다시 처리
        """
        print("=" * 60)
        print("증분 학습: 새로운 PDF만 추가")
        print("=" * 60)
        
        # PDF 파일 목록 가져오기
        pdf_pattern = os.path.join(pdf_folder, "*.pdf")
        all_pdf_files = glob.glob(pdf_pattern)
        
        if not all_pdf_files:
            print(f"[ERROR] 오류: {pdf_folder}에 PDF 파일이 없습니다.")
            return
        
        print(f"\n전체 PDF 파일: {len(all_pdf_files)}개")
        
        # 새로운 파일만 필터링
        if force_reprocess:
            new_pdf_files = all_pdf_files
            print("[WARNING] 강제 재처리 모드: 모든 파일을 처리합니다.")
        else:
            new_pdf_files = [
                pdf for pdf in all_pdf_files 
                if os.path.basename(pdf) not in self.processed_files
            ]
        
        if not new_pdf_files:
            print("\n[OK] 처리할 새로운 PDF 파일이 없습니다. 모든 파일이 이미 학습되었습니다.")
            return
        
        print(f"\n[NEW] 새로 처리할 파일: {len(new_pdf_files)}개")
        for i, pdf_file in enumerate(new_pdf_files, 1):
            print(f"  [{i}] {os.path.basename(pdf_file)}")
        print()
        
        # 새로운 청크 수집
        new_chunks = []
        successfully_processed = []
        
        # 각 새 PDF 파일 처리
        for i, pdf_path in enumerate(new_pdf_files, 1):
            filename = os.path.basename(pdf_path)
            print(f"\n[{i}/{len(new_pdf_files)}] 처리 중: {filename}")
            print("-" * 60)
            
            try:
                # PDF 로드
                doc_data = self.loader.load_pdf(pdf_path, method="pdfplumber")
                
                # 청크 생성 (의미 단위 청킹 사용)
                chunks = self.loader.chunk_document(
                    doc_data,
                    chunk_size=1500,  # 목표 청크 크기 증가
                    overlap=200,       # 오버랩 증가
                    use_semantic_chunking=True  # 의미 단위 청킹 활성화
                )
                
                # 메타데이터 강화
                for chunk in chunks:
                    chunk['metadata']['document_title'] = doc_data.get('title', filename)
                    # 테이블 청크가 아닌 경우만 source_type을 'pdf'로 설정
                    if 'source_type' not in chunk['metadata']:
                        chunk['metadata']['source_type'] = 'pdf'
                    chunk['metadata']['source_file'] = filename
                    chunk['metadata']['pdf_title'] = doc_data.get('title', filename)  # 명시적 제목 필드
                    chunk['metadata']['processed_date'] = datetime.now().isoformat()
                
                new_chunks.extend(chunks)
                successfully_processed.append(filename)
                print(f"[OK] 완료: {len(chunks)}개 청크 생성")
                
            except Exception as e:
                print(f"[ERROR] 오류 발생: {str(e)}")
                print(f"  파일 건너뛰기: {filename}")
                continue
        
        if not new_chunks:
            print("\n[ERROR] 처리된 청크가 없습니다.")
            return
        
        print(f"\n" + "=" * 60)
        print(f"새로 생성된 청크: {len(new_chunks)}개")
        print("=" * 60)
        
        # 임베딩 생성
        print("\n임베딩 생성 시작...")
        texts = [chunk['text'] for chunk in new_chunks]
        embeddings = self.embedder.embed_texts(texts)
        
        for i, chunk in enumerate(new_chunks):
            chunk['embedding'] = embeddings[i]
        
        print("[OK] 임베딩 생성 완료")
        
        # 기존 인덱스에 추가
        self.add_to_faiss(new_chunks)
        
        # 처리된 파일 목록 업데이트
        self.processed_files.update(successfully_processed)
        self._save_processed_files()
        
        print("\n" + "=" * 60)
        print("증분 학습 완료")
        print("=" * 60)
        print(f"\n[SUCCESS] {len(successfully_processed)}개 PDF 파일, {len(new_chunks)}개 청크 추가 완료!")
        print(f"총 벡터 수: {self.index.ntotal}개")
    
    def add_to_faiss(self, new_chunks: List[Dict[str, Any]]):
        """
        기존 FAISS 인덱스에 새로운 청크 추가
        
        Args:
            new_chunks: 임베딩이 포함된 새 청크 리스트
        """
        print("\nFAISS 인덱스에 추가 중...")
        
        # 임베딩 추출
        valid_chunks = [c for c in new_chunks if c['embedding'] is not None]
        new_embeddings = np.array([c['embedding'] for c in valid_chunks], dtype='float32')
        
        # 기존 인덱스가 없으면 새로 생성
        if self.index is None:
            dimension = new_embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dimension)
            print(f"새 FAISS 인덱스 생성 (차원: {dimension})")
        
        # 벡터 추가
        self.index.add(new_embeddings)
        print(f"[OK] {len(valid_chunks)}개 벡터 추가됨 (총 {self.index.ntotal}개)")
        
        # 메타데이터 추가
        for chunk in valid_chunks:
            metadata = {
                "text": chunk['text'],
                "metadata": chunk['metadata']
            }
            self.metadata.append(metadata)
        
        # 저장
        self._save_index_and_metadata()
    
    def _save_index_and_metadata(self):
        """FAISS 인덱스, 메타데이터, BM25 인덱스 저장"""
        # FAISS 인덱스 저장
        index_path = os.path.join(self.vector_store_path, "faiss_index.bin")
        faiss.write_index(self.index, index_path)
        print(f"[OK] FAISS 인덱스 저장: {index_path}")
        
        # 메타데이터 저장
        metadata_path = os.path.join(self.vector_store_path, "metadata.pkl")
        with open(metadata_path, 'wb') as f:
            pickle.dump(self.metadata, f)
        print(f"[OK] 메타데이터 저장: {metadata_path}")
        
        # BM25 인덱스 재생성 및 저장
        print("BM25 인덱스 업데이트 중...")
        try:
            from tools.bm25_retriever import BM25Retriever
            
            # 문서와 메타데이터 추출
            documents = [item['text'] for item in self.metadata]
            metadata_only = [item['metadata'] for item in self.metadata]
            
            # BM25 인덱스 생성 및 저장
            bm25_retriever = BM25Retriever()
            bm25_retriever.build_index(documents, metadata_only)
            bm25_retriever.save_index()
            
            print(f"[OK] BM25 인덱스 저장 완료")
        except Exception as e:
            print(f"[WARNING] BM25 인덱스 업데이트 실패: {str(e)}")
            print("   (FAISS 검색은 정상 작동합니다)")
    
    def reset_processed_files(self):
        """처리된 파일 목록 초기화 (전체 재학습용)"""
        if os.path.exists(self.processed_files_path):
            os.remove(self.processed_files_path)
        self.processed_files = set()
        print("[OK] 처리된 파일 목록 초기화됨")
    
    def list_processed_files(self):
        """처리된 파일 목록 출력"""
        if not self.processed_files:
            print("처리된 파일이 없습니다.")
            return
        
        print(f"\n처리된 파일 목록 ({len(self.processed_files)}개):")
        for i, filename in enumerate(sorted(self.processed_files), 1):
            print(f"  [{i}] {filename}")


# 메인 실행
if __name__ == "__main__":
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(description="증분 학습: 새로운 PDF만 추가")
    parser.add_argument("pdf_folder", help="PDF 파일들이 있는 폴더 경로")
    parser.add_argument("--force", action="store_true", help="이미 처리된 파일도 다시 처리")
    parser.add_argument("--reset", action="store_true", help="처리된 파일 목록 초기화")
    parser.add_argument("--list", action="store_true", help="처리된 파일 목록 출력")
    
    args = parser.parse_args()
    
    # 전처리기 초기화
    preprocessor = IncrementalPDFPreprocessor()
    
    # 처리된 파일 목록 출력
    if args.list:
        preprocessor.list_processed_files()
        sys.exit(0)
    
    # 처리된 파일 목록 초기화
    if args.reset:
        confirm = input("[WARNING] 처리된 파일 목록을 초기화하시겠습니까? (y/N): ")
        if confirm.lower() == 'y':
            preprocessor.reset_processed_files()
        sys.exit(0)
    
    # PDF 폴더 확인
    if not os.path.exists(args.pdf_folder):
        print(f"[ERROR] 오류: 폴더를 찾을 수 없습니다: {args.pdf_folder}")
        sys.exit(1)
    
    # 증분 학습 실행
    try:
        preprocessor.process_new_pdfs(args.pdf_folder, force_reprocess=args.force)
        print("\n[OK] 성공! 이제 'python run_server.py'로 API 서버를 시작할 수 있습니다.")
    except Exception as e:
        print(f"\n[ERROR] 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
