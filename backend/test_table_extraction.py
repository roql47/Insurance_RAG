"""
테이블 추출 기능 테스트 스크립트
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from tools.document_loader import DocumentLoader


def test_table_extraction(pdf_path):
    """
    PDF에서 테이블 추출 테스트
    
    Args:
        pdf_path: 테스트할 PDF 파일 경로
    """
    print("=" * 60)
    print("테이블 추출 기능 테스트")
    print("=" * 60)
    
    loader = DocumentLoader()
    
    # 1. PDF 로드 (테이블 데이터 포함)
    print(f"\n1. PDF 로드 중: {pdf_path}")
    doc_data = loader.load_pdf(pdf_path, method="pdfplumber")
    
    # 2. 테이블 데이터 확인
    table_data = doc_data.get('table_data', [])
    print(f"\n2. 테이블 데이터 확인")
    print(f"   - 추출된 테이블 행 수: {len(table_data)}개")
    
    if table_data:
        print("\n   [테이블 행 샘플]")
        for i, row in enumerate(table_data[:3], 1):  # 처음 3개만 출력
            print(f"\n   행 {i}:")
            print(f"     - 제목: {row.get('title', 'N/A')}")
            print(f"     - 질의: {row.get('query', 'N/A')[:50]}...")
            print(f"     - 페이지: {row.get('page_number')}")
            print(f"     - 전체 컬럼: {list(row.get('full_row_data', {}).keys())}")
    else:
        print("   ⚠️  테이블 데이터가 없습니다. (또는 '제목'/'질의' 컬럼이 없음)")
    
    # 3. 청크 생성
    print(f"\n3. 청크 생성 중...")
    chunks = loader.chunk_document(
        doc_data,
        chunk_size=1500,
        overlap=200,
        use_semantic_chunking=True
    )
    
    # 4. 청크 분석
    print(f"\n4. 청크 분석")
    print(f"   - 총 청크 수: {len(chunks)}개")
    
    # 청크 타입별 카운트
    pdf_chunks = [c for c in chunks if c.get('metadata', {}).get('source_type') == 'pdf']
    table_chunks = [c for c in chunks if c.get('metadata', {}).get('source_type') == 'table']
    
    print(f"   - PDF 청크: {len(pdf_chunks)}개")
    print(f"   - 테이블 청크: {len(table_chunks)}개")
    
    # 5. 테이블 청크 샘플 출력
    if table_chunks:
        print(f"\n5. 테이블 청크 샘플")
        for i, chunk in enumerate(table_chunks[:2], 1):  # 처음 2개만 출력
            metadata = chunk.get('metadata', {})
            text = chunk.get('text', '')
            print(f"\n   [테이블 청크 {i}]")
            print(f"   - 제목: {metadata.get('table_title', 'N/A')}")
            print(f"   - 질의: {metadata.get('table_query', 'N/A')[:50]}...")
            print(f"   - 페이지: {metadata.get('page_number')}")
            print(f"   - 청크 텍스트 미리보기:")
            print(f"     {text[:200]}...")
    else:
        print("\n5. 테이블 청크 없음")
    
    print("\n" + "=" * 60)
    print("테스트 완료!")
    print("=" * 60)
    
    return {
        'total_chunks': len(chunks),
        'pdf_chunks': len(pdf_chunks),
        'table_chunks': len(table_chunks),
        'table_rows': len(table_data)
    }


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("사용법: python test_table_extraction.py <PDF_파일_경로>")
        print("\n예시:")
        print("  python test_table_extraction.py data/raw/test.pdf")
        sys.exit(1)
    
    pdf_path = sys.argv[1]
    
    if not os.path.exists(pdf_path):
        print(f"오류: 파일을 찾을 수 없습니다: {pdf_path}")
        sys.exit(1)
    
    try:
        result = test_table_extraction(pdf_path)
        
        print("\n[결과 요약]")
        print(f"  - 테이블 행: {result['table_rows']}개")
        print(f"  - 총 청크: {result['total_chunks']}개")
        print(f"    ├─ PDF: {result['pdf_chunks']}개")
        print(f"    └─ 테이블: {result['table_chunks']}개")
        
    except Exception as e:
        print(f"\n오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

