"""
문서 로더 - PDF, Word, HWP 등 다양한 형식 지원
"""

import os
from typing import List, Dict, Any
import pdfplumber
import fitz  # PyMuPDF

from tools.semantic_chunker import SemanticChunker


class DocumentLoader:
    """다양한 문서 형식을 로드하고 텍스트를 추출하는 클래스"""
    
    def __init__(self):
        """초기화"""
        pass
    
    def extract_tables_from_pdf(self, pdf_path: str) -> List[Dict[str, Any]]:
        """
        PDF에서 모든 테이블을 추출하고 구조화
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            테이블 데이터 리스트 (각 행이 개별 딕셔너리)
        """
        structured_data = []
        
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page_num, page in enumerate(pdf.pages, 1):
                    tables = page.extract_tables()
                    
                    if not tables:
                        continue
                    
                    print(f"  [페이지 {page_num}] {len(tables)}개 테이블 발견")
                    
                    for table_idx, table in enumerate(tables):
                        if not table or len(table) < 2:
                            continue
                        
                        # 헤더 행 추출 및 정리
                        headers = [str(cell).strip() if cell else f"Column_{i}" for i, cell in enumerate(table[0])]
                        
                        # 빈 헤더 제거 확인
                        if not any(headers):
                            print(f"    → 테이블 {table_idx + 1}: 헤더 없음, 건너뜀")
                            continue
                        
                        print(f"    → 테이블 {table_idx + 1}: 컬럼 {len(headers)}개 - {', '.join(headers[:5])}")
                        
                        # 데이터 행 처리 (헤더 제외)
                        rows_added = 0
                        for row_idx, row in enumerate(table[1:], 1):
                            # 행 길이가 헤더보다 짧으면 패딩
                            if len(row) < len(headers):
                                row = row + [''] * (len(headers) - len(row))
                            
                            # 전체 행 데이터 저장
                            row_data = {}
                            has_content = False
                            
                            for col_idx, (header, cell) in enumerate(zip(headers, row)):
                                cell_value = str(cell).strip() if cell else ""
                                row_data[header] = cell_value
                                if cell_value:
                                    has_content = True
                            
                            # 완전히 빈 행은 건너뛰기
                            if not has_content:
                                continue
                            
                            # 구조화된 데이터 저장
                            structured_data.append({
                                'page_number': page_num,
                                'table_index': table_idx,
                                'row_index': row_idx,
                                'headers': headers,
                                'row_data': row_data
                            })
                            rows_added += 1
                        
                        if rows_added > 0:
                            print(f"       [OK] {rows_added}개 행 추출")
            
            if structured_data:
                print(f"  [OK] 총 {len(structured_data)}개 구조화된 테이블 행 추출")
            
        except Exception as e:
            print(f"  [WARNING] 테이블 추출 중 오류: {str(e)}")
        
        return structured_data
    
    def extract_pdf_title(self, pdf_path: str) -> str:
        """
        PDF에서 제목 추출
        
        우선순위:
        1. PDF 메타데이터의 title 필드 (PyMuPDF 사용)
        2. 첫 페이지 첫 줄 텍스트
        3. 파일명 (확장자 제거)
        
        Args:
            pdf_path: PDF 파일 경로
            
        Returns:
            추출된 제목
        """
        try:
            # 1. PyMuPDF로 메타데이터에서 title 추출
            doc = fitz.open(pdf_path)
            metadata = doc.metadata
            doc.close()
            
            if metadata and metadata.get('title'):
                title = metadata['title'].strip()
                if title and len(title) > 0:
                    return title
        except Exception as e:
            print(f"메타데이터 추출 실패: {e}")
        
        try:
            # 2. 첫 페이지 첫 줄에서 추출
            with pdfplumber.open(pdf_path) as pdf:
                if len(pdf.pages) > 0:
                    first_page_text = pdf.pages[0].extract_text()
                    if first_page_text:
                        # 첫 줄 추출 (줄바꿈 기준)
                        lines = [line.strip() for line in first_page_text.split('\n') if line.strip()]
                        if lines:
                            title = lines[0]
                            # 너무 길면 자르기 (100자 제한)
                            if len(title) > 100:
                                title = title[:100] + "..."
                            return title
        except Exception as e:
            print(f"첫 페이지 텍스트 추출 실패: {e}")
        
        # 3. 파일명 사용 (확장자 제거)
        filename = os.path.basename(pdf_path)
        title = os.path.splitext(filename)[0]
        return title
    
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
            
            # 제목 추출
            title = self.extract_pdf_title(pdf_path)
            print(f"추출된 제목: {title}")
            
            # 테이블 추출
            print("\n테이블 데이터 추출 중...")
            table_data = self.extract_tables_from_pdf(pdf_path)
            
            return {
                "filename": os.path.basename(pdf_path),
                "filepath": pdf_path,
                "title": title,
                "total_pages": len(pages_data),
                "full_text": full_text.strip(),
                "pages": pages_data,
                "file_type": "pdf",
                "table_data": table_data  # 테이블 데이터 추가
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
            
            # 제목 추출
            title = self.extract_pdf_title(pdf_path)
            print(f"추출된 제목: {title}")
            
            # 테이블 추출
            print("\n테이블 데이터 추출 중...")
            table_data = self.extract_tables_from_pdf(pdf_path)
            
            return {
                "filename": os.path.basename(pdf_path),
                "filepath": pdf_path,
                "title": title,
                "total_pages": len(pages_data),
                "full_text": full_text.strip(),
                "pages": pages_data,
                "file_type": "pdf",
                "table_data": table_data  # 테이블 데이터 추가
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
    
    def create_table_chunks(self, doc_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        테이블 데이터를 개별 청크로 변환
        각 테이블 행이 하나의 청크가 됨
        
        Args:
            doc_data: 문서 데이터 (table_data 포함)
            
        Returns:
            테이블 청크 리스트
        """
        table_data = doc_data.get("table_data", [])
        
        if not table_data:
            return []
        
        print(f"\n  [TABLE] 테이블 청크 생성 중: {len(table_data)}개 행")
        
        table_chunks = []
        
        for idx, row_info in enumerate(table_data):
            row_data = row_info.get('row_data', {})
            headers = row_info.get('headers', [])
            
            # 텍스트 생성: 각 컬럼의 데이터를 "[컬럼명] 값" 형식으로
            text_parts = []
            
            for header in headers:
                value = row_data.get(header, '').strip()
                if value:
                    text_parts.append(f"[{header}] {value}")
            
            chunk_text = "\n".join(text_parts)
            
            # 메타데이터 생성 (범용적 처리)
            chunk_metadata = {
                "filename": doc_data.get("filename", ""),
                "filepath": doc_data.get("filepath", ""),
                "file_type": doc_data.get("file_type", ""),
                "total_pages": doc_data.get("total_pages", 0),
                "source_type": "table",  # 테이블 출처 표시
                "page_number": row_info.get('page_number', 0),
                "table_index": row_info.get('table_index', 0),
                "row_index": row_info.get('row_index', 0),
                "chunk_index": idx,
                "table_columns": headers,  # 전체 컬럼 리스트
                "column_data": {k: v for k, v in row_data.items() if v}  # 모든 컬럼 데이터
            }
            
            # 파일명 기반 주요 필드 자동 감지 및 추가
            filename = doc_data.get("filename", "")
            primary_field_standard = None  # 표준화된 필드명
            primary_value = None
            target_keywords = []
            
            if "기준" in filename:
                primary_field_standard = "제목"
                target_keywords = ["제목"]
            elif "질의" in filename:
                primary_field_standard = "질의"  # 표준화된 값
                target_keywords = ["질의", "질 의", "질  의"]  # 공백 변형 포함
            
            # 테이블 컬럼에서 키워드와 매칭되는 컬럼 찾기
            if target_keywords:
                for keyword in target_keywords:
                    # 공백 제거하고 비교
                    for col_name in row_data.keys():
                        if keyword.replace(" ", "") == col_name.replace(" ", ""):
                            primary_value = row_data[col_name]  # 실제 값 추출
                            break
                    if primary_value:
                        break
            
            # 주요 필드가 발견되면 메타데이터에 추가
            if primary_field_standard and primary_value:
                chunk_metadata['primary_field'] = primary_field_standard  # 표준화된 필드명 저장
                chunk_metadata['primary_content'] = primary_value
                if idx < 3:  # 처음 3개만 로그 출력
                    print(f"    [자동감지] '{primary_field_standard}' → '{primary_value[:30]}...'")
            
            table_chunks.append({
                "chunk_id": idx,
                "text": chunk_text,
                "start_char": 0,
                "end_char": len(chunk_text),
                "metadata": chunk_metadata
            })
        
        print(f"  [OK] {len(table_chunks)}개 테이블 청크 생성 완료")
        return table_chunks
    
    def chunk_document(
        self, 
        doc_data: Dict[str, Any], 
        chunk_size: int = 1000,
        overlap: int = 100,
        use_semantic_chunking: bool = True
    ) -> List[Dict[str, Any]]:
        """
        문서를 청크로 분할
        
        Args:
            doc_data: 문서 데이터
            chunk_size: 청크 크기 (문자 수) - semantic chunking 시 target_size
            overlap: 오버랩 크기
            use_semantic_chunking: 의미 단위 청킹 사용 여부 (기본 True)
            
        Returns:
            청크 리스트
        """
        full_text = doc_data["full_text"]
        
        # Semantic Chunking 사용
        if use_semantic_chunking:
            print(f"  [SEMANTIC] 의미 단위 청킹 사용 (목표: {chunk_size}자, 오버랩: {overlap}자)")
            
            chunker = SemanticChunker(
                min_chunk_size=chunk_size // 2,
                max_chunk_size=chunk_size * 2,
                target_chunk_size=chunk_size,
                overlap=overlap
            )
            
            # 문서 메타데이터 준비
            base_metadata = {
                "filename": doc_data.get("filename", ""),
                "filepath": doc_data.get("filepath", ""),
                "file_type": doc_data.get("file_type", ""),
                "total_pages": doc_data.get("total_pages", 0)
            }
            
            # Semantic chunking 실행
            semantic_chunks = chunker.chunk_by_structure(full_text, base_metadata)
            
            # 청크 ID 추가
            for i, chunk in enumerate(semantic_chunks):
                chunk['chunk_id'] = i
                chunk['start_char'] = 0  # Semantic chunking에서는 정확한 위치 추적 어려움
                chunk['end_char'] = len(chunk['text'])
            
            print(f"  [OK] {len(semantic_chunks)}개 의미 단위 청크 생성 완료")
            
            # 테이블 청크 생성
            table_chunks = self.create_table_chunks(doc_data)
            
            # 청크 합치기
            all_chunks = semantic_chunks + table_chunks
            
            # 합쳐진 청크의 ID 재설정
            for i, chunk in enumerate(all_chunks):
                chunk['chunk_id'] = i
            
            if table_chunks:
                print(f"  [TOTAL] 총 {len(all_chunks)}개 청크 (의미 단위: {len(semantic_chunks)}, 테이블: {len(table_chunks)})")
            
            return all_chunks
        
        # 기존 고정 크기 청킹 (하위 호환성)
        print(f"  [FIXED] 고정 크기 청킹 사용 ({chunk_size}자, 오버랩: {overlap}자)")
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
        
        print(f"문서를 {len(chunks)}개 고정 크기 청크로 분할 완료")
        
        # 테이블 청크 생성
        table_chunks = self.create_table_chunks(doc_data)
        
        # 청크 합치기
        all_chunks = chunks + table_chunks
        
        # 합쳐진 청크의 ID 재설정
        for i, chunk in enumerate(all_chunks):
            chunk['chunk_id'] = i
        
        if table_chunks:
            print(f"  [TOTAL] 총 {len(all_chunks)}개 청크 (고정 크기: {len(chunks)}, 테이블: {len(table_chunks)})")
        
        return all_chunks


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

