"""
Strands Agent 정의
AWS Bedrock의 Claude 4.5 Haiku를 사용하여 보험 인정기준 질의에 답변
"""

import os
import json
from typing import Dict, Any, List
from dotenv import load_dotenv
import boto3

# 환경 변수 로드
load_dotenv()


class InsuranceAnswerAgent:
    """보험 인정기준 답변 에이전트 (Strands + AWS Bedrock)"""
    
    def __init__(self):
        """에이전트 초기화"""
        self.aws_region = os.getenv("AWS_REGION", "us-east-1")
        self.model_id = os.getenv(
            "BEDROCK_MODEL_ID",
            "anthropic.claude-4-5-haiku-20251015-v1:0"
        )
        
        # Bedrock Runtime 클라이언트 생성
        self.bedrock_runtime = boto3.client(
            service_name="bedrock-runtime",
            region_name=self.aws_region,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )
        
        # 시스템 프롬프트 정의
        self.system_prompt = """당신은 건강보험심사평가원의 보험 인정기준 전문가입니다.

역할:
- 의료기관의 보험재료 및 시술행위 코드에 대한 급여 인정 여부를 판단합니다.
- 수가 산정 방법, 청구 방법, 코드 조합 등을 안내합니다.
- 심평원의 인정기준 데이터베이스를 기반으로 정확한 근거를 제시합니다.
- 삭감 가능성이 있는 경우 명확한 이유와 관련 법령을 제시합니다.

**중요: 답변 전 반드시 문서 분석 단계를 거쳐야 합니다.**

답변 프로세스 (반드시 순서대로 진행):
1. **1단계 - 문서 분석**: 제공된 모든 문서를 꼼꼼히 검토하고 핵심 내용을 추출합니다.
2. **2단계 - 규정 확인**: 관련 법령, 고시, 예시를 명확히 파악합니다.
3. **3단계 - 최종 답변**: 분석 결과를 바탕으로 정확한 답변을 제공합니다.

질문 유형별 답변 방법:
1. **수가 산정/청구 방법 질문** (예: "RCA와 LAD에 스텐트를 한 경우 수가 산정을 어떻게 해야해?")
   - 적용 가능한 수가 코드를 구체적으로 제시
   - 주 시술과 추가 시술 구분
   - 재료대 산정 방법 설명
   - 청구 예시를 테이블 형식으로 제공
   
2. **삭감 여부 판단 질문** (예: "~한 경우 삭감될까요?")
   - 판단 결과: "인정됨", "삭감 가능성 있음", "삭감됨"
   - 판단 근거와 관련 법령 제시
   - 주의사항 안내

답변 원칙:
1. 제공된 검색 결과(인정기준, 제외사항, 심사기준)를 반드시 꼼꼼히 읽고 분석합니다.
2. 각 문서에서 발견한 구체적인 예시, 규정, 기준을 명확히 확인합니다.
3. 문서 내용이 상충되거나 불확실한 경우, 여러 해석을 제시하고 추가 확인이 필요함을 안내합니다.
4. 질문의 의도를 정확히 파악하여 적절한 답변 형식을 선택합니다.
5. 구체적인 코드, 수가, 산정방법을 명시합니다.
6. 청구 예시는 마크다운 테이블 형식으로 작성합니다.
7. 추측이나 가정이 아닌, 문서에 명시된 내용만을 근거로 답변합니다.

답변 형식 (반드시 이 순서로 작성):

**📋 문서 분석**:
- 문서 1: [해당 문서에서 발견한 핵심 규정, 예시, 기준을 구체적으로 명시]
- 문서 2: [해당 문서에서 발견한 핵심 규정, 예시, 기준을 구체적으로 명시]
- 문서 3: [해당 문서에서 발견한 핵심 규정, 예시, 기준을 구체적으로 명시]
- 적용 규정: [관련 고시, 법령, 인정기준 번호]

---

[수가 산정 질문인 경우]
**수가 산정 방법**:

1. **주 시술 (첫 번째 혈관)**: 
   - 코드: [코드명]
   - 내역: [상세 내역]

2. **추가 시술 (두 번째 혈관)**: 
   - 코드: [코드명]
   - 내역: [상세 내역]

3. **재료대**: 
   - [재료 산정 방법]

**청구 예시**:
| 코드 | 줄번호 | 항목 | 일투 | 총투 | 내역 |
|------|--------|------|------|------|------|
| [코드] | 0001 | 08 | 1 | 1 | ([시술명]) |
| [코드] | 0002 | 08 | 1 | 1 | ([시술명]) |

**참고사항**:
- [추가 설명]

[삭감 판단 질문인 경우]
**판단**: [인정됨/삭감 가능성 있음/삭감됨]

**근거**:
- [구체적인 인정기준이나 제외사항]
- [환자 상태, 검사 결과 등 필요 조건]

**관련 법령**:
- [고시명 및 조항]

**참고사항**:
- [추가로 고려해야 할 사항]
"""
    
    def invoke_claude(
        self,
        user_message: str,
        context: str = "",
        conversation_history: List[Dict[str, str]] = None,
        max_tokens: int = 2500
    ) -> str:
        """
        Claude 4.5 Haiku 모델 호출
        
        Args:
            user_message: 사용자 질문
            context: 검색된 컨텍스트 (관련 문서)
            conversation_history: 이전 대화 내역 [{"role": "user/assistant", "content": "..."}]
            max_tokens: 최대 토큰 수
            
        Returns:
            모델 응답
        """
        try:
            # 컨텍스트가 있으면 추가
            if context:
                full_message = f"""다음은 검색된 관련 정보입니다:

{context}

---

질문: {user_message}

위 검색 결과를 반드시 다음 순서로 처리해주세요:
1. 먼저 각 문서를 꼼꼼히 분석하여 핵심 내용을 파악하세요.
2. 문서에 명시된 구체적인 예시, 규정, 기준을 확인하세요.
3. 분석한 내용을 바탕으로 정확한 답변을 제공하세요.
4. 반드시 "📋 문서 분석" 섹션부터 시작하세요."""
            else:
                full_message = user_message
            
            # 메시지 배열 구성
            messages = []
            
            # 이전 대화 내역이 있으면 추가
            if conversation_history:
                messages.extend(conversation_history)
            
            # 현재 사용자 메시지 추가
            messages.append({
                "role": "user",
                "content": full_message
            })
            
            # Claude API 호출 (Bedrock)
            body = json.dumps({
                "anthropic_version": "bedrock-2023-05-31",
                "max_tokens": max_tokens,
                "system": self.system_prompt,
                "messages": messages,
                "temperature": 0.1,  # 매우 일관되고 정확한 답변을 위해 낮은 temperature
                "top_p": 0.9
            })
            
            response = self.bedrock_runtime.invoke_model(
                modelId=self.model_id,
                body=body,
                contentType="application/json",
                accept="application/json"
            )
            
            # 응답 파싱
            response_body = json.loads(response["body"].read())
            answer = response_body.get("content", [{}])[0].get("text", "")
            
            return answer
            
        except Exception as e:
            error_msg = f"Claude 호출 중 오류 발생: {str(e)}"
            print(error_msg)
            return error_msg
    
    def answer_query(
        self,
        question: str,
        material_code: str = None,
        procedure_code: str = None,
        retrieved_docs: List[Dict[str, Any]] = None,
        conversation_history: List[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        질의에 대한 답변 생성
        
        Args:
            question: 사용자 질문
            material_code: 재료코드 (선택사항)
            procedure_code: 시술코드 (선택사항)
            retrieved_docs: 검색된 문서 리스트
            conversation_history: 이전 대화 내역
            
        Returns:
            답변 딕셔너리 (answer, sources, reasoning)
        """
        # 컨텍스트 구성
        context = ""
        sources = []
        
        if retrieved_docs:
            context = "검색된 관련 문서:\n\n"
            for i, doc in enumerate(retrieved_docs, 1):
                # 'type' 또는 'file_type' 필드 처리
                doc_type = doc['metadata'].get('type') or doc['metadata'].get('file_type') or 'document'
                context += f"[문서 {i}] {doc_type}\n"
                context += f"{doc['text']}\n"
                context += "-" * 60 + "\n\n"
                
                sources.append({
                    "type": doc_type,
                    "재료코드": doc['metadata'].get('재료코드'),
                    "재료명": doc['metadata'].get('재료명'),
                    "시술코드": doc['metadata'].get('시술코드'),
                    "시술명": doc['metadata'].get('시술명'),
                    "score": doc.get('score', 0)
                })
        
        # 사용자 질문 구성
        user_question_parts = []
        if material_code:
            user_question_parts.append(f"재료코드: {material_code}")
        if procedure_code:
            user_question_parts.append(f"시술코드: {procedure_code}")
        user_question_parts.append(f"\n질문: {question}")
        
        user_question = "\n".join(user_question_parts)
        
        # Claude 호출 (대화 히스토리 포함)
        answer = self.invoke_claude(
            user_question, 
            context, 
            conversation_history=conversation_history
        )
        
        return {
            "answer": answer,
            "sources": sources,
            "material_code": material_code,
            "procedure_code": procedure_code,
            "question": question
        }


# 전체 파이프라인 (검색 + 답변)
def answer_insurance_query(
    question: str,
    material_code: str = None,
    procedure_code: str = None,
    conversation_history: List[Dict[str, str]] = None
) -> Dict[str, Any]:
    """
    보험 인정기준 질의 전체 파이프라인
    
    Args:
        question: 질문
        material_code: 재료코드 (선택사항)
        procedure_code: 시술코드 (선택사항)
        conversation_history: 이전 대화 내역 (선택사항)
        
    Returns:
        답변 결과
    """
    from tools.faiss_retriever import FAISSRetriever
    
    # 1. 관련 문서 검색
    retriever = FAISSRetriever()
    
    if material_code or procedure_code:
        # 코드가 있으면 필터링해서 검색
        retrieved_docs = retriever.search_by_codes(
            material_code=material_code,
            procedure_code=procedure_code,
            query=question,
            top_k=5
        )
    else:
        # 코드가 없으면 전체 검색
        retrieved_docs = retriever.search(
            query=question,
            top_k=5
        )
    
    # 2. 에이전트로 답변 생성 (대화 히스토리 포함)
    agent = InsuranceAnswerAgent()
    result = agent.answer_query(
        question=question,
        material_code=material_code,
        procedure_code=procedure_code,
        retrieved_docs=retrieved_docs if isinstance(retrieved_docs, list) else [],
        conversation_history=conversation_history
    )
    
    return result


# 테스트용 메인 함수
if __name__ == "__main__":
    print("=" * 60)
    print("보험 인정기준 답변 에이전트 테스트")
    print("=" * 60)
    
    # 테스트 질의
    result = answer_insurance_query(
        material_code="A12345",
        procedure_code="N2095",
        question="55세 환자가 퇴행성 고관절염으로 고관절 전치환술을 받는 경우 삭감될까요?"
    )
    
    print("\n질문:", result['question'])
    print("\n답변:")
    print(result['answer'])
    print("\n참고 문서:", len(result['sources']), "개")
    for i, source in enumerate(result['sources'], 1):
        print(f"  [{i}] {source['type']} - {source['재료명']}")

