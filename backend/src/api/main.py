"""
FastAPI 메인 애플리케이션
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

from .routes import router

# 환경 변수 로드
load_dotenv()

# FastAPI 앱 초기화
app = FastAPI(
    title="보험 인정기준 RAG API",
    description="보험재료코드 및 시술행위코드의 심평원 인정기준 삭감 여부 판단 시스템",
    version="1.0.0"
)

# CORS 설정
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # 프로덕션에서는 특정 도메인만 허용
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 라우터 등록
app.include_router(router, prefix="/api", tags=["insurance"])

# 루트 경로
@app.get("/")
async def root():
    """루트 경로"""
    return {
        "message": "보험 인정기준 RAG API 서버",
        "docs": "/docs",
        "api": "/api"
    }


if __name__ == "__main__":
    import uvicorn
    
    host = os.getenv("API_HOST", "0.0.0.0")
    port = int(os.getenv("API_PORT", "8000"))
    
    print(f"서버 시작: http://{host}:{port}")
    print(f"API 문서: http://{host}:{port}/docs")
    
    uvicorn.run(
        "main:app",
        host=host,
        port=port,
        reload=True
    )

