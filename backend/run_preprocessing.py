"""
데이터 전처리 실행 스크립트 (루트 디렉토리에서 실행)
"""

import sys
import os

# src 디렉토리를 path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pipeline import DataPreprocessor

if __name__ == "__main__":
    print("=" * 60)
    print("데이터 전처리 시작")
    print("=" * 60)
    
    # 전처리기 초기화
    preprocessor = DataPreprocessor()
    
    # 샘플 데이터 경로
    raw_data_path = "./data/raw/sample_criteria.json"
    
    # 파일 존재 확인
    if not os.path.exists(raw_data_path):
        print(f"오류: 데이터 파일을 찾을 수 없습니다: {raw_data_path}")
        sys.exit(1)
    
    # 전처리 실행
    try:
        preprocessor.run_pipeline(raw_data_path)
        print("\n✅ 전처리가 성공적으로 완료되었습니다!")
        print("이제 'python run_server.py'로 API 서버를 시작할 수 있습니다.")
    except Exception as e:
        print(f"\n❌ 전처리 중 오류 발생: {str(e)}")
        sys.exit(1)

