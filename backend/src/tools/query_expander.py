"""
쿼리 확장 도구
사용자 질의에 도메인 특화 키워드를 자동으로 추가하여 검색 정확도 향상
"""

class QueryExpander:
    """쿼리 확장기"""
    
    def __init__(self):
        """
        도메인 특화 키워드 매핑
        특정 의학 용어가 질의에 포함되면 관련 전문 용어를 추가
        """
        self.expansion_rules = {
            # 뇌혈관 관련
            "뇌동맥": ["뇌동맥류", "비파열성", "Flow-diverter", "색전술"],
            "뇌": ["뇌동맥", "뇌혈관", "뇌동맥류"],
            
            # 관상동맥 관련
            "관상동맥": ["LM", "LAD", "LCx", "RCA", "경피적"],
            "심장": ["관상동맥", "LM", "LAD"],
            "스텐트": ["삽입술", "경피적"],
            "병변": ["협착", "병변부위"],  # 병변 관련 키워드 추가
            
            # 시술 관련
            "확장술": ["혈관성형술", "PTC", "PTCA"],
            "죽상반": ["atherectomy", "죽상반절제술"],
            "cross-over": ["걸쳐서", "병변"],
            
            # 보험 관련
            "삭감": ["급여", "인정기준", "요양급여"],
            "청구": ["수가", "산정", "소정점수"],
            "수가산정": ["단일혈관", "추가혈관", "소정점수"],
        }
    
    def expand_query(self, query: str) -> str:
        """
        질의 확장
        
        Args:
            query: 원본 질의
            
        Returns:
            확장된 질의
        """
        expanded_terms = []
        
        # 질의에 포함된 키워드 확인
        for keyword, related_terms in self.expansion_rules.items():
            if keyword in query:
                # 관련 용어 중 질의에 없는 것만 추가
                for term in related_terms:
                    if term not in query:
                        expanded_terms.append(term)
        
        # 원본 질의 + 확장 용어
        if expanded_terms:
            expanded_query = f"{query} {' '.join(expanded_terms)}"
            return expanded_query
        
        return query
    
    def get_domain_context(self, query: str) -> str:
        """
        질의의 도메인 컨텍스트 파악
        
        Args:
            query: 질의
            
        Returns:
            도메인 ("brain", "coronary", "general")
        """
        # 뇌혈관 관련
        brain_keywords = ["뇌", "뇌동맥", "뇌혈관", "뇌동맥류"]
        if any(kw in query for kw in brain_keywords):
            return "brain"
        
        # 관상동맥 관련
        coronary_keywords = ["관상동맥", "심장", "LM", "LAD", "LCx", "RCA"]
        if any(kw in query for kw in coronary_keywords):
            return "coronary"
        
        return "general"


# 싱글톤 인스턴스
_expander = None

def get_query_expander() -> QueryExpander:
    """쿼리 확장기 싱글톤 인스턴스 반환"""
    global _expander
    if _expander is None:
        _expander = QueryExpander()
    return _expander

