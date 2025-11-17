"""
의미 단위 청킹 시스템
문서 구조를 인식하여 의미 있는 단위로 청킹
"""

import re
from typing import List, Dict, Any, Tuple


class SemanticChunker:
    """문서 구조 기반 의미 단위 청킹"""
    
    def __init__(
        self,
        min_chunk_size: int = 500,
        max_chunk_size: int = 2500,
        target_chunk_size: int = 1500,
        overlap: int = 200
    ):
        """
        초기화
        
        Args:
            min_chunk_size: 최소 청크 크기
            max_chunk_size: 최대 청크 크기
            target_chunk_size: 목표 청크 크기
            overlap: 청크 간 오버랩 크기
        """
        self.min_chunk_size = min_chunk_size
        self.max_chunk_size = max_chunk_size
        self.target_chunk_size = target_chunk_size
        self.overlap = overlap
    
    def chunk_by_structure(
        self,
        text: str,
        metadata: Dict[str, Any] = None
    ) -> List[Dict[str, Any]]:
        """
        문서 구조를 인식하여 의미 단위로 청킹
        
        Args:
            text: 청킹할 텍스트
            metadata: 문서 메타데이터
            
        Returns:
            청크 리스트 (각 청크는 text와 metadata 포함)
        """
        if not text or not text.strip():
            return []
        
        metadata = metadata or {}
        
        # 1. 문서를 섹션으로 분할
        sections = self._split_into_sections(text)
        
        # 2. 각 섹션을 의미 단위로 청킹
        chunks = []
        for section_idx, section in enumerate(sections):
            section_chunks = self._chunk_section(section, section_idx, metadata)
            chunks.extend(section_chunks)
        
        # 3. 오버랩 추가
        chunks = self._add_overlap(chunks)
        
        return chunks
    
    def _split_into_sections(self, text: str) -> List[Dict[str, Any]]:
        """
        텍스트를 섹션으로 분할
        제목, 번호, 구분선 등을 기준으로 분할
        """
        sections = []
        current_section = {
            'title': None,
            'content': '',
            'level': 0
        }
        
        lines = text.split('\n')
        
        for line in lines:
            # 섹션 제목 감지 패턴
            # 1. 로마숫자/한글 번호 (Ⅰ, Ⅱ, 가., 나., 1), 2))
            # 2. 큰 글자 제목 (-, =로 구분)
            # 3. [페이지 N] 패턴
            
            is_title = False
            title_level = 0
            
            # 페이지 구분
            if re.match(r'\[페이지\s+\d+\]', line.strip()):
                if current_section['content'].strip():
                    sections.append(current_section.copy())
                current_section = {
                    'title': line.strip(),
                    'content': '',
                    'level': 1
                }
                is_title = True
                title_level = 1
            
            # 로마숫자 제목 (Ⅰ., Ⅱ., Ⅲ.)
            elif re.match(r'^[ⅠⅡⅢⅣⅤⅥⅦⅧⅨⅩ]\.?\s+', line.strip()):
                if current_section['content'].strip():
                    sections.append(current_section.copy())
                current_section = {
                    'title': line.strip(),
                    'content': '',
                    'level': 2
                }
                is_title = True
                title_level = 2
            
            # 번호 제목 (1., 2., 가., 나.)
            elif re.match(r'^[0-9가-힣]{1,2}\.?\s+', line.strip()) and len(line.strip()) < 100:
                # 짧은 줄만 제목으로 간주
                if current_section['content'].strip():
                    sections.append(current_section.copy())
                current_section = {
                    'title': line.strip(),
                    'content': '',
                    'level': 3
                }
                is_title = True
                title_level = 3
            
            # 구분선 (-, =)
            elif re.match(r'^[-=]{3,}$', line.strip()):
                if current_section['content'].strip():
                    sections.append(current_section.copy())
                current_section = {
                    'title': None,
                    'content': '',
                    'level': 2
                }
                is_title = True
                title_level = 2
            
            # 일반 내용
            if not is_title:
                current_section['content'] += line + '\n'
        
        # 마지막 섹션 추가
        if current_section['content'].strip():
            sections.append(current_section)
        
        return sections
    
    def _chunk_section(
        self,
        section: Dict[str, Any],
        section_idx: int,
        base_metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        섹션을 청크로 분할
        """
        content = section['content']
        title = section['title']
        
        if not content.strip():
            return []
        
        # 섹션이 목표 크기 이하면 그대로 반환
        if len(content) <= self.target_chunk_size:
            chunk_metadata = base_metadata.copy()
            chunk_metadata['section_title'] = title
            chunk_metadata['section_idx'] = section_idx
            chunk_metadata['chunk_idx'] = 0
            
            return [{
                'text': content.strip(),
                'metadata': chunk_metadata
            }]
        
        # 섹션이 크면 문단으로 분할
        paragraphs = self._split_into_paragraphs(content)
        
        chunks = []
        current_chunk = ''
        chunk_idx = 0
        
        for para in paragraphs:
            # 현재 청크에 문단을 추가했을 때 크기 확인
            potential_chunk = current_chunk + '\n\n' + para if current_chunk else para
            
            if len(potential_chunk) <= self.max_chunk_size:
                # 목표 크기를 넘었지만 최대 크기는 안 넘음
                if len(potential_chunk) >= self.target_chunk_size:
                    chunk_metadata = base_metadata.copy()
                    chunk_metadata['section_title'] = title
                    chunk_metadata['section_idx'] = section_idx
                    chunk_metadata['chunk_idx'] = chunk_idx
                    
                    chunks.append({
                        'text': potential_chunk.strip(),
                        'metadata': chunk_metadata
                    })
                    current_chunk = ''
                    chunk_idx += 1
                else:
                    current_chunk = potential_chunk
            else:
                # 최대 크기 초과
                if current_chunk:
                    chunk_metadata = base_metadata.copy()
                    chunk_metadata['section_title'] = title
                    chunk_metadata['section_idx'] = section_idx
                    chunk_metadata['chunk_idx'] = chunk_idx
                    
                    chunks.append({
                        'text': current_chunk.strip(),
                        'metadata': chunk_metadata
                    })
                    chunk_idx += 1
                
                # 문단 자체가 너무 크면 강제 분할
                if len(para) > self.max_chunk_size:
                    para_chunks = self._force_split(para, title, section_idx, chunk_idx, base_metadata)
                    chunks.extend(para_chunks)
                    chunk_idx += len(para_chunks)
                    current_chunk = ''
                else:
                    current_chunk = para
        
        # 마지막 청크 추가
        if current_chunk and len(current_chunk.strip()) >= self.min_chunk_size:
            chunk_metadata = base_metadata.copy()
            chunk_metadata['section_title'] = title
            chunk_metadata['section_idx'] = section_idx
            chunk_metadata['chunk_idx'] = chunk_idx
            
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': chunk_metadata
            })
        
        return chunks
    
    def _split_into_paragraphs(self, text: str) -> List[str]:
        """
        텍스트를 문단으로 분할
        """
        # 빈 줄로 구분
        paragraphs = re.split(r'\n\s*\n', text)
        
        # 빈 문단 제거
        paragraphs = [p.strip() for p in paragraphs if p.strip()]
        
        return paragraphs
    
    def _force_split(
        self,
        text: str,
        title: str,
        section_idx: int,
        start_chunk_idx: int,
        base_metadata: Dict[str, Any]
    ) -> List[Dict[str, Any]]:
        """
        너무 큰 텍스트를 강제로 분할
        """
        chunks = []
        words = text.split()
        current_chunk = ''
        chunk_idx = start_chunk_idx
        
        for word in words:
            potential_chunk = current_chunk + ' ' + word if current_chunk else word
            
            if len(potential_chunk) >= self.target_chunk_size:
                chunk_metadata = base_metadata.copy()
                chunk_metadata['section_title'] = title
                chunk_metadata['section_idx'] = section_idx
                chunk_metadata['chunk_idx'] = chunk_idx
                chunk_metadata['force_split'] = True
                
                chunks.append({
                    'text': current_chunk.strip(),
                    'metadata': chunk_metadata
                })
                current_chunk = word
                chunk_idx += 1
            else:
                current_chunk = potential_chunk
        
        # 마지막 청크
        if current_chunk:
            chunk_metadata = base_metadata.copy()
            chunk_metadata['section_title'] = title
            chunk_metadata['section_idx'] = section_idx
            chunk_metadata['chunk_idx'] = chunk_idx
            chunk_metadata['force_split'] = True
            
            chunks.append({
                'text': current_chunk.strip(),
                'metadata': chunk_metadata
            })
        
        return chunks
    
    def _add_overlap(self, chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        청크 간 오버랩 추가
        """
        if len(chunks) <= 1:
            return chunks
        
        overlapped_chunks = []
        
        for i, chunk in enumerate(chunks):
            text = chunk['text']
            
            # 이전 청크의 마지막 부분 추가
            if i > 0:
                prev_text = chunks[i - 1]['text']
                overlap_text = prev_text[-self.overlap:] if len(prev_text) > self.overlap else prev_text
                text = overlap_text + '\n...\n' + text
            
            overlapped_chunks.append({
                'text': text,
                'metadata': chunk['metadata']
            })
        
        return overlapped_chunks


# 테스트용 메인 함수
if __name__ == "__main__":
    chunker = SemanticChunker()
    
    test_text = """
[페이지 1]
Ⅰ. 치료재료
제5장 중재적 시술료

Flow-diverter를 이용한 뇌동맥류 색전술 시 사용하는 색전 기구(Embolization Device)는 다음의 경우에 요양급여를 인정함

- 다 음 -

가. 급여대상
1) 직경 10mm이상의 비파열성 뇌동맥류
2) 직경 10mm미만의 비파열성 뇌동맥류 중 아래의 경우 사례별로 인정

나. 급여개수 : 1개
다만, 환자의 상태나 동맥류의 해부학적 특성 등으로 불가피하게 급여개수를 초과하여 사용하는 경우에는 의사소견서 및 진료기록부 등 관련 자료를 첨부하여야 하며 제출된 관련 자료를 참조하여 요양급여를 인정함

[페이지 2]
Ⅱ. 관상동맥 스텐트

자656 경피적 관상동맥 스텐트 삽입술은 증상, 예후, 심장 기능의 개선 또는 사망률의 감소와 같은 임상적 유용성이 있는 경우에 시행함을 원칙으로 함.
"""
    
    chunks = chunker.chunk_by_structure(test_text, {'source': 'test.pdf'})
    
    print(f"총 {len(chunks)}개 청크 생성\n")
    for i, chunk in enumerate(chunks, 1):
        print(f"[청크 {i}]")
        print(f"제목: {chunk['metadata'].get('section_title', 'N/A')}")
        print(f"길이: {len(chunk['text'])}자")
        print(f"내용 미리보기:\n{chunk['text'][:200]}...\n")

