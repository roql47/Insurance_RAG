"""
LangChain을 사용한 보험 인정기준 RAG 시스템
AWS Bedrock Claude 4.5 Haiku + 하이브리드 검색
LCEL (LangChain Expression Language) 사용
"""

import os
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

# LangChain 임포트 (최신 LCEL 방식)
from langchain_aws import ChatBedrock
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import StrOutputParser
from langchain_core.runnables import RunnablePassthrough

# 커스텀 검색기
from tools.langchain_retriever import HybridLangChainRetriever

# 환경 변수 로드
load_dotenv()


class InsuranceLangChainAgent:
    """LangChain 기반 보험 인정기준 답변 에이전트"""
    
    def __init__(self):
        """에이전트 초기화"""
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.model_id = os.getenv(
            "BEDROCK_MODEL_ID",
            "anthropic.claude-4-5-haiku-20251015-v1:0"
        )
        
        # Claude 모델 초기화
        self.llm = ChatBedrock(
            model_id=self.model_id,
            region_name=self.aws_region,
            model_kwargs={
                "temperature": 0.1,  # 일관된 답변
                "top_p": 0.9,
                "max_tokens": 2500
            }
        )
        
        # 하이브리드 검색기 초기화
        self.retriever = HybridLangChainRetriever()
        
        # 프롬프트 템플릿 정의
        self.system_prompt = """당신은 건강보험심사평가원의 보험 인정기준 전문가입니다.

역할:
- 의료기관의 보험재료 및 시술행위 코드에 대한 급여 인정 여부를 판단합니다.
- 수가 산정 방법, 청구 방법, 코드 조합 등을 안내합니다.
- 심평원의 인정기준 데이터베이스를 기반으로 정확한 근거를 제시합니다.
- 삭감 가능성이 있는 경우 명확한 이유와 관련 법령을 제시합니다.

답변 원칙:
1. 제공된 검색 결과를 꼼꼼히 읽고 분석합니다.
2. 각 문서에서 발견한 구체적인 예시, 규정, 기준을 명확히 확인합니다.
3. 구체적인 코드, 수가, 산정방법을 명시합니다.
4. 추측이 아닌, 문서에 명시된 내용만을 근거로 답변합니다.

답변 형식:

**📋 문서 분석**:
- 문서 1: [핵심 규정]
- 문서 2: [핵심 규정]
- 적용 규정: [관련 고시, 법령]

---

**수가 산정 방법** (해당 시):
1. 주 시술: 코드, 내역
2. 추가 시술: 코드, 내역
3. 재료대: 산정 방법

**청구 예시**:
| 코드 | 항목 | 수량 | 내역 |
|------|------|------|------|
| 코드 | 08 | 1 | 시술명 |

**참고사항**:
- 추가 설명

---

**판단** (삭감 질문 시): 인정됨/삭감 가능성 있음/삭감됨

**근거**:
- 인정기준이나 제외사항

**관련 법령**:
- 고시명 및 조항"""

        self.prompt_template = ChatPromptTemplate.from_messages([
            ("system", self.system_prompt),
            ("human", """검색된 관련 문서:

{context}

질문: {question}

위 문서를 분석하여 정확한 답변을 제공하세요.""")
        ])
        
        # 간단한 체인 생성
        self.chain = self.prompt_template | self.llm | StrOutputParser()
        
        print("✅ LangChain Agent 초기화 완료")
    
    def _format_docs(self, docs):
        """검색된 문서를 포맷팅"""
        if not docs:
            return "관련 문서를 찾을 수 없습니다."
        
        formatted = []
        for i, doc in enumerate(docs, 1):
            metadata = doc.metadata
            formatted.append(
                f"[문서 {i}] {metadata.get('filename', 'Unknown')} "
                f"(점수: {metadata.get('score', 0):.4f})\n"
                f"{doc.page_content}\n"
            )
        
        return "\n".join(formatted)
    
    def answer_query(
        self,
        question: str,
        material_code: Optional[str] = None,
        procedure_code: Optional[str] = None,
        conversation_history: Optional[List[Dict[str, str]]] = None
    ) -> Dict[str, Any]:
        """
        질의에 대한 답변 생성
        
        Args:
            question: 사용자 질문
            material_code: 재료코드 (선택사항)
            procedure_code: 시술코드 (선택사항)
            conversation_history: 이전 대화 내역
            
        Returns:
            답변 딕셔너리
        """
        try:
            # 질문에 코드 정보 추가
            full_question = question
            if material_code:
                full_question = f"재료코드: {material_code}\n{full_question}"
            if procedure_code:
                full_question = f"시술코드: {procedure_code}\n{full_question}"
            
            # 대화 히스토리 추가 (간단한 버전)
            if conversation_history and len(conversation_history) > 0:
                history_text = "\n이전 대화:\n"
                for msg in conversation_history[-2:]:  # 마지막 2개만
                    role = "사용자" if msg["role"] == "user" else "AI"
                    history_text += f"{role}: {msg['content'][:100]}...\n"
                full_question = history_text + "\n" + full_question
            
            # 1. 문서 검색
            docs = self.retriever._get_relevant_documents(full_question, k=5)
            
            if not docs:
                return {
                    "answer": "죄송합니다. 관련 문서를 찾을 수 없습니다. 질문을 다시 확인해주세요.",
                    "sources": [],
                    "material_code": material_code,
                    "procedure_code": procedure_code,
                    "question": question
                }
            
            # 2. 체인 실행
            context_text = self._format_docs(docs)
            answer = self.chain.invoke({
                "context": context_text,
                "question": full_question
            })
            
            # 3. 소스 문서 추출
            sources = []
            for doc in docs:
                metadata = doc.metadata
                sources.append({
                    "type": metadata.get("file_type", "document"),
                    "재료코드": metadata.get("재료코드"),
                    "재료명": metadata.get("재료명"),
                    "시술코드": metadata.get("시술코드"),
                    "시술명": metadata.get("시술명"),
                    "score": metadata.get("score", 0)
                })
            
            return {
                "answer": answer,
                "sources": sources,
                "material_code": material_code,
                "procedure_code": procedure_code,
                "question": question
            }
            
        except Exception as e:
            error_msg = f"LangChain Agent 실행 중 오류 발생: {str(e)}"
            print(error_msg)
            import traceback
            traceback.print_exc()
            
            return {
                "answer": error_msg,
                "sources": [],
                "material_code": material_code,
                "procedure_code": procedure_code,
                "question": question,
                "error": str(e)
            }


# 전체 파이프라인 (LangChain 사용)
def answer_insurance_query_langchain(
    question: str,
    material_code: Optional[str] = None,
    procedure_code: Optional[str] = None,
    conversation_history: Optional[List[Dict[str, str]]] = None
) -> Dict[str, Any]:
    """
    보험 인정기준 질의 파이프라인 (LangChain)
    
    Args:
        question: 질문
        material_code: 재료코드 (선택사항)
        procedure_code: 시술코드 (선택사항)
        conversation_history: 이전 대화 내역 (선택사항)
        
    Returns:
        답변 결과
    """
    agent = InsuranceLangChainAgent()
    return agent.answer_query(
        question=question,
        material_code=material_code,
        procedure_code=procedure_code,
        conversation_history=conversation_history
    )


# 테스트용 메인 함수
if __name__ == "__main__":
    print("=" * 60)
    print("LangChain 보험 인정기준 답변 에이전트 테스트")
    print("=" * 60)
    
    # 테스트 질의
    result = answer_insurance_query_langchain(
        question="RCA와 LAD에 스텐트를 삽입한 경우 수가 산정은 어떻게 하나요?"
    )
    
    print("\n질문:", result['question'])
    print("\n답변:")
    print(result['answer'])
    print("\n참고 문서:", len(result['sources']), "개")
    for i, source in enumerate(result['sources'], 1):
        print(f"  [{i}] {source['type']} (점수: {source.get('score', 0):.4f})")
