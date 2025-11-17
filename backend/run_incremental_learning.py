"""
증분 학습 실행 스크립트
기존 학습 데이터를 유지하고 새로운 PDF만 추가로 학습합니다.
"""

import sys
import os

# src 디렉토리를 path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pipeline_pdf_incremental import IncrementalPDFPreprocessor


def main():
    print("=" * 60)
    print("증분 학습 (Incremental Learning)")
    print("기존 데이터 유지 + 새로운 PDF만 추가")
    print("=" * 60)
    
    # PDF 폴더 경로
    pdf_folder = "./data/raw"
    
    # 폴더 존재 확인
    if not os.path.exists(pdf_folder):
        print(f"❌ 오류: 폴더를 찾을 수 없습니다: {pdf_folder}")
        sys.exit(1)
    
    # 전처리기 초기화
    preprocessor = IncrementalPDFPreprocessor()
    
    # 증분 학습 실행
    try:
        preprocessor.process_new_pdfs(pdf_folder)
        print("\n✅ 성공! 새로운 PDF가 학습되었습니다.")
        print("이제 'python run_server.py'로 API 서버를 시작할 수 있습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(
        description="증분 학습: 새로운 PDF만 추가",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
사용 예시:
  # 새로운 PDF만 학습
  python run_incremental_learning.py
  
  # 이미 처리된 파일도 다시 학습
  python run_incremental_learning.py --force
  
  # 처리된 파일 목록 확인
  python run_incremental_learning.py --list
  
  # 처리된 파일 목록 초기화 (전체 재학습 시)
  python run_incremental_learning.py --reset
        """
    )
    parser.add_argument("--force", action="store_true", help="이미 처리된 파일도 다시 처리")
    parser.add_argument("--reset", action="store_true", help="처리된 파일 목록 초기화")
    parser.add_argument("--list", action="store_true", help="처리된 파일 목록 출력")
    
    args = parser.parse_args()
    
    # PDF 폴더
    pdf_folder = "./data/raw"
    
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
            print("다음에 실행하면 모든 파일을 다시 학습합니다.")
        sys.exit(0)
    
    # 폴더 확인
    if not os.path.exists(pdf_folder):
        print(f"❌ 오류: 폴더를 찾을 수 없습니다: {pdf_folder}")
        sys.exit(1)
    
    # 증분 학습 실행
    try:
        print("=" * 60)
        print("증분 학습 (Incremental Learning)")
        print("기존 데이터 유지 + 새로운 PDF만 추가")
        print("=" * 60)
        
        preprocessor.process_new_pdfs(pdf_folder, force_reprocess=args.force)
        print("\n✅ 성공! 새로운 PDF가 학습되었습니다.")
        print("이제 'python run_server.py'로 API 서버를 시작할 수 있습니다.")
    except Exception as e:
        print(f"\n❌ 오류 발생: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

