"""
서버 실행 스크립트 (루트 디렉토리에서 실행)
"""

import sys
import os

# src 디렉토리를 path에 추가
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

import uvicorn
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

if __name__ == "__main__":
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print("=" * 60)
    print("보험 인정기준 RAG API 서버 시작")
    print("=" * 60)
    print(f"서버 주소: http://{host}:{port}")
    print(f"API 문서: http://{host}:{port}/docs")
    print(f"API 엔드포인트: http://{host}:{port}/api")
    print("=" * 60)
    print("종료하려면 Ctrl+C를 누르세요.")
    print("=" * 60)
    
    uvicorn.run(
        "api.main:app",
        host=host,
        port=port,
        reload=False  # 간단하게 reload 비활성화
    )

