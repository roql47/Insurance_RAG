"""
문서 로더 - PDF, Word, HWP 등 다양한 형식 지원
"""

import os
from typing import List, Dict, Any
import pdfplumber
import fitz  # PyMuPDF


class DocumentLoader:
    """다양한 문서 형식을 로드하고 텍스트를 추출하는 클래스"""
    
    def __init__(self):
        """초기화"""
        pass
    
    def load_pdf_with_pdfplumber(self, pdf_path: str) -> Dict[str, Any]:
        """
        pdfplumber를 사용하여 PDF에서 텍스트 추출
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            문서 정보 딕셔너리
        """
        print(f"PDF 파일 로드 중: {pdf_path}")
        
        full_text = ""
        pages_data = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                total_pages = len(pdf.pages)
                print(f"총 페이지 수: {total_pages}")
                
                for i, page in enumerate(pdf.pages, 1):
                    page_text = page.extract_text()
                    if page_text:
                        full_text += f"\n\n[페이지 {i}]\n{page_text}"
                        pages_data.append({
                            "page_number": i,
                            "text": page_text
                        })
                    
                    if i % 10 == 0:
                        print(f"진행 중: {i}/{total_pages} 페이지 처리 완료")
            
            print(f"PDF 로드 완료: 총 {len(pages_data)}페이지, {len(full_text)}자")
            
            return {
                "filename": os.path.basename(pdf_path),
                "filepath": pdf_path,
                "total_pages": len(pages_data),
                "full_text": full_text.strip(),
                "pages": pages_data,
                "file_type": "pdf"
            }
            
        except Exception as e:
            print(f"PDF 로드 중 오류 발생: {str(e)}")
            raise
    
    def load_pdf_with_pymupdf(self, pdf_path: str) -> Dict[str, Any]:
        """
        PyMuPDF를 사용하여 PDF에서 텍스트 추출 (대안)
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            문서 정보 딕셔너리
        """
        print(f"PDF 파일 로드 중 (PyMuPDF): {pdf_path}")
        
        full_text = ""
        pages_data = []
        
        try:
            doc = fitz.open(pdf_path)
            total_pages = len(doc)
            print(f"총 페이지 수: {total_pages}")
            
            for i, page in enumerate(doc, 1):
                page_text = page.get_text()
                if page_text:
                    full_text += f"\n\n[페이지 {i}]\n{page_text}"
                    pages_data.append({
                        "page_number": i,
                        "text": page_text
                    })
                
                if i % 10 == 0:
                    print(f"진행 중: {i}/{total_pages} 페이지 처리 완료")
            
            doc.close()
            
            print(f"PDF 로드 완료: 총 {len(pages_data)}페이지, {len(full_text)}자")
            
            return {
                "filename": os.path.basename(pdf_path),
                "filepath": pdf_path,
                "total_pages": len(pages_data),
                "full_text": full_text.strip(),
                "pages": pages_data,
                "file_type": "pdf"
            }
            
        except Exception as e:
            print(f"PDF 로드 중 오류 발생: {str(e)}")
            raise
    
    def load_pdf(self, pdf_path: str, method: str = "pdfplumber") -> Dict[str, Any]:
        """
        PDF 파일 로드 (메소드 선택 가능)
        
        Args:
            pdf_path: PDF 파일 경로
            method: 사용할 라이브러리 ("pdfplumber" 또는 "pymupdf")
            
        Returns:
            문서 정보 딕셔너리
        """
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"파일을 찾을 수 없습니다: {pdf_path}")
        
        if method == "pdfplumber":
            return self.load_pdf_with_pdfplumber(pdf_path)
        elif method == "pymupdf":
            return self.load_pdf_with_pymupdf(pdf_path)
        else:
            raise ValueError(f"지원하지 않는 메소드: {method}")
    
    def chunk_document(
        self, 
        doc_data: Dict[str, Any], 
        chunk_size: int = 1000,
        overlap: int = 100
    ) -> List[Dict[str, Any]]:
        """
        문서를 청크로 분할
        
        Args:
            doc_data: 문서 데이터
            chunk_size: 청크 크기 (문자 수)
            overlap: 오버랩 크기
            
        Returns:
            청크 리스트
        """
        full_text = doc_data["full_text"]
        chunks = []
        
        # 간단한 청크 분할 (문자 기반)
        start = 0
        chunk_id = 0
        
        while start < len(full_text):
            end = start + chunk_size
            chunk_text = full_text[start:end]
            
            # 마지막 청크가 아니면 문장 단위로 자르기
            if end < len(full_text):
                # 마지막 마침표나 줄바꿈 찾기
                last_period = chunk_text.rfind('.')
                last_newline = chunk_text.rfind('\n')
                split_point = max(last_period, last_newline)
                
                if split_point > chunk_size * 0.5:  # 최소 50% 이상은 유지
                    chunk_text = chunk_text[:split_point + 1]
                    end = start + len(chunk_text)
            
            chunks.append({
                "chunk_id": chunk_id,
                "text": chunk_text.strip(),
                "start_char": start,
                "end_char": end,
                "metadata": {
                    "filename": doc_data["filename"],
                    "file_type": doc_data["file_type"],
                    "chunk_index": chunk_id,
                    "total_pages": doc_data.get("total_pages", 0)
                }
            })
            
            chunk_id += 1
            start = end - overlap
        
        print(f"문서를 {len(chunks)}개 청크로 분할 완료")
        return chunks


# 테스트용 메인 함수
if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("사용법: python document_loader.py <PDF_파일_경로>")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    # 로더 초기화
    loader = DocumentLoader()
    
    # PDF 로드
    doc_data = loader.load_pdf(pdf_path)
    
    print("\n" + "=" * 60)
    print("문서 정보:")
    print("=" * 60)
    print(f"파일명: {doc_data['filename']}")
    print(f"총 페이지: {doc_data['total_pages']}")
    print(f"총 텍스트 길이: {len(doc_data['full_text'])}자")
    
    # 청크 분할
    chunks = loader.chunk_document(doc_data, chunk_size=500, overlap=50)
    
    print("\n첫 번째 청크 미리보기:")
    print("-" * 60)
    print(chunks[0]["text"][:300] + "...")

