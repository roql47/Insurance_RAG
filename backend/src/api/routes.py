"""
API 라우트 정의
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
import sys
import os

# 부모 디렉토리를 path에 추가
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.answer_agent import answer_insurance_query
from pipeline import DataPreprocessor

router = APIRouter()


# 대화 메시지 모델
class ConversationMessage(BaseModel):
    """대화 메시지 모델"""
    role: str = Field(..., description="메시지 역할 (user/assistant)")
    content: str = Field(..., description="메시지 내용")


# 요청/응답 모델 정의
class QueryRequest(BaseModel):
    """질의 요청 모델"""
    material_code: Optional[str] = Field(None, description="재료코드 (예: A12345, 선택사항)")
    procedure_code: Optional[str] = Field(None, description="시술코드 (예: N2095, 선택사항)")
    question: str = Field(..., description="질문 내용")
    conversation_history: Optional[List[ConversationMessage]] = Field(
        None, 
        description="이전 대화 내역 (선택사항)"
    )
    excluded_sources: Optional[List[str]] = Field(
        None,
        description="제외할 문서 텍스트 목록 (재검색 시 노이즈 문서 제거용)"
    )


class Source(BaseModel):
    """참고 문서 모델"""
    type: str
    filename: Optional[str] = None
    pdf_title: Optional[str] = None
    재료코드: Optional[str] = None
    재료명: Optional[str] = None
    시술코드: Optional[str] = None
    시술명: Optional[str] = None
    score: float
    text: str  # 제외 기능을 위한 문서 텍스트


class QueryResponse(BaseModel):
    """질의 응답 모델"""
    answer: str = Field(..., description="답변 내용")
    sources: List[Source] = Field(..., description="참고한 문서 리스트")
    material_code: Optional[str] = None
    procedure_code: Optional[str] = None
    question: str


class PreprocessRequest(BaseModel):
    """전처리 요청 모델"""
    data_path: Optional[str] = Field(
        "./data/raw/sample_criteria.json",
        description="전처리할 데이터 파일 경로"
    )


@router.post("/query", response_model=QueryResponse)
async def query_insurance_criteria(request: QueryRequest):
    """
    보험 인정기준 질의
    
    재료코드와 시술코드를 기반으로 보험 인정 여부를 판단합니다.
    대화 히스토리를 통해 이전 대화 내용을 참고할 수 있습니다.
    """
    try:
        # 대화 히스토리를 딕셔너리 리스트로 변환
        conversation_history = None
        if request.conversation_history:
            conversation_history = [
                {"role": msg.role, "content": msg.content}
                for msg in request.conversation_history
            ]
        
        result = answer_insurance_query(
            material_code=request.material_code,
            procedure_code=request.procedure_code,
            question=request.question,
            conversation_history=conversation_history,
            excluded_sources=request.excluded_sources
        )
        
        return QueryResponse(**result)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"질의 처리 중 오류 발생: {str(e)}"
        )


@router.post("/preprocess")
async def preprocess_data(request: PreprocessRequest):
    """
    데이터 전처리 실행
    
    원본 데이터를 청크로 나누고 임베딩을 생성하여 FAISS 인덱스에 저장합니다.
    """
    try:
        preprocessor = DataPreprocessor()
        preprocessor.run_pipeline(request.data_path)
        
        return {
            "status": "success",
            "message": "데이터 전처리가 완료되었습니다.",
            "data_path": request.data_path
        }
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"전처리 중 오류 발생: {str(e)}"
        )


@router.get("/health")
async def health_check():
    """
    헬스 체크 엔드포인트
    """
    return {
        "status": "healthy",
        "service": "Insurance RAG API"
    }


@router.get("/")
async def root():
    """
    루트 엔드포인트
    """
    return {
        "message": "보험 인정기준 RAG API",
        "version": "1.0.0",
        "endpoints": {
            "POST /query": "보험 인정기준 질의",
            "POST /preprocess": "데이터 전처리",
            "GET /health": "헬스 체크"
        }
    }

