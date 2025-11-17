import { mdToText } from './mdToText'

/**
 * @description 답변 내용을 파싱하여 테이블과 일반 텍스트를 구분
 * @param {string} answer 답변 텍스트
 * @returns {Array} 파싱된 콘텐츠 배열 (type: 'text' | 'table')
 */
export function parseAnswer(answer) {
  if (!answer || typeof answer !== 'string') return []

  const sections = []
  const lines = answer.split('\n')
  let i = 0

  while (i < lines.length) {
    const line = lines[i]

    // 마크다운 테이블 감지 (| 로 시작하고 | 로 구분되는 형식)
    if (line.trim().startsWith('|') && line.trim().endsWith('|')) {
      const tableLines = []
      let j = i

      // 테이블 라인들을 모두 수집
      while (j < lines.length && lines[j].trim().startsWith('|') && lines[j].trim().endsWith('|')) {
        tableLines.push(lines[j])
        j++
      }

      // 테이블 파싱
      if (tableLines.length >= 2) { // 최소 헤더 + 구분선이 있어야 함
        const parsedTable = parseMarkdownTable(tableLines)
        if (parsedTable) {
          sections.push({
            type: 'table',
            content: parsedTable
          })
          i = j
          continue
        }
      }
    }

    // 고정폭 텍스트 테이블 감지 (연속된 라인이 비슷한 컬럼 구조를 가짐)
    const potentialTableLines = []
    let j = i
    
    // 비어있지 않은 연속된 라인 수집
    while (j < lines.length && lines[j].trim() && !lines[j].trim().startsWith('|')) {
      potentialTableLines.push(lines[j])
      j++
    }

    // 3줄 이상이고 테이블로 보이면 테이블로 파싱
    if (potentialTableLines.length >= 3) {
      const fixedWidthTable = detectFixedWidthTable(potentialTableLines)
      if (fixedWidthTable) {
        sections.push({
          type: 'table',
          content: fixedWidthTable
        })
        i = j
        continue
      }
    }

    // 일반 텍스트 수집
    const textLines = []
    while (i < lines.length && !(lines[i].trim().startsWith('|') && lines[i].trim().endsWith('|'))) {
      textLines.push(lines[i])
      i++
      
      // 다음이 테이블로 보이면 중단
      if (i < lines.length) {
        const nextLines = []
        let k = i
        while (k < lines.length && k < i + 5 && lines[k].trim()) {
          nextLines.push(lines[k])
          k++
        }
        if (nextLines.length >= 3 && detectFixedWidthTable(nextLines)) {
          break
        }
      }
    }

    if (textLines.length > 0) {
      const textContent = textLines.join('\n').trim()
      if (textContent) {
        sections.push({
          type: 'text',
          content: mdToText(textContent)
        })
      }
    }
  }

  return sections
}

/**
 * @description 마크다운 테이블을 파싱
 * @param {Array<string>} lines 테이블 라인 배열
 * @returns {Object|null} 파싱된 테이블 객체 { headers, rows }
 */
function parseMarkdownTable(lines) {
  if (lines.length < 2) return null

  // 헤더 파싱
  const headerLine = lines[0]
  const headers = headerLine
    .split('|')
    .map(cell => cell.trim())
    .filter(cell => cell !== '')

  if (headers.length === 0) return null

  // 구분선 확인 (두 번째 줄)
  const separatorLine = lines[1]
  const isSeparator = separatorLine.includes('---') || separatorLine.includes(':--') || separatorLine.includes('--:')
  
  // 구분선이 있으면 3번째 줄부터, 없으면 2번째 줄부터 데이터로 처리
  const startIndex = isSeparator ? 2 : 1

  // 데이터 행 파싱
  const rows = []
  for (let i = startIndex; i < lines.length; i++) {
    const cells = lines[i]
      .split('|')
      .map(cell => cell.trim())
      .filter((cell, index, arr) => {
        // 첫 번째와 마지막 빈 셀 제거 (| 시작/종료로 인한)
        if (index === 0 || index === arr.length - 1) return cell !== ''
        return true
      })

    if (cells.length > 0) {
      rows.push(cells)
    }
  }

  return { headers, rows }
}

/**
 * @description 고정폭 텍스트 테이블 감지 및 파싱
 * @param {Array<string>|string} input 텍스트 또는 라인 배열
 * @returns {Object|null} 파싱된 테이블 또는 null
 */
export function detectFixedWidthTable(input) {
  const lines = Array.isArray(input) 
    ? input.filter(line => line.trim())
    : input.split('\n').filter(line => line.trim())
  
  // 최소 4줄 이상이어야 테이블로 인식 (헤더 + 3개 이상의 데이터 행)
  if (lines.length < 4) return null

  // 첫 줄을 헤더로 간주
  const firstLine = lines[0].trim()
  
  // 불릿 리스트로 시작하면 테이블이 아님
  if (/^[-*•]\s/.test(firstLine)) return null
  
  // 대부분의 줄이 불릿 리스트면 테이블이 아님
  const bulletListLines = lines.filter(line => /^[-*•]\s/.test(line.trim()))
  if (bulletListLines.length > lines.length * 0.5) return null
  
  // 마크다운 문법(**, -, :, 등)이 많으면 테이블이 아님
  const markdownSymbolCount = (firstLine.match(/[*:\-_#]/g) || []).length
  if (markdownSymbolCount > 2) return null
  
  // 괄호가 헤더에 있으면 테이블이 아닐 가능성 높음
  if (firstLine.includes('(') || firstLine.includes(')')) return null
  
  // 탭 문자가 있는 경우 테이블로 간주하지 않음 (잘못된 포맷일 가능성)
  if (lines.some(line => line.includes('\t'))) return null
  
  // 여러 방법으로 컬럼 구분 시도
  let potentialHeaders = null
  let columnPattern = null

  // 방법 1: 2개 이상의 공백으로 구분
  potentialHeaders = firstLine.split(/\s{2,}/)
  if (potentialHeaders.length >= 3) { // 최소 3개 컬럼
    columnPattern = /\s{2,}/
  }

  // 방법 2: 단일 공백으로 구분 (최소 4개 이상의 컬럼이 있어야 함)
  if (!columnPattern || potentialHeaders.length < 3) {
    const singleSpaceSplit = firstLine.split(/\s+/)
    if (singleSpaceSplit.length >= 4) {
      potentialHeaders = singleSpaceSplit
      columnPattern = /\s+/
    }
  }

  if (!potentialHeaders || potentialHeaders.length < 3) return null

  // 헤더가 너무 길면 테이블이 아님
  const hasLongHeader = potentialHeaders.some(header => header.length > 20)
  if (hasLongHeader) return null
  
  // 헤더에 의미있는 텍스트가 있어야 함 (최소 2글자 이상 단어)
  const headerHasText = potentialHeaders.filter(header => 
    /[가-힣a-zA-Z]{2,}/.test(header)
  ).length >= 2
  if (!headerHasText) return null

  // 모든 라인을 같은 패턴으로 파싱
  const allRows = lines.map(line => {
    const trimmed = line.trim()
    const cells = trimmed.split(columnPattern)
    
    // 괄호로 묶인 마지막 설명 처리 (예: "(RCA 스텐트삽입술 - 단일혈관)")
    if (cells.length > potentialHeaders.length) {
      // 마지막 여러 셀을 하나로 합침
      const lastCells = cells.slice(potentialHeaders.length - 1)
      const mergedLast = lastCells.join(' ')
      return [...cells.slice(0, potentialHeaders.length - 1), mergedLast]
    }
    
    return cells
  })

  const columnCount = potentialHeaders.length
  
  // 데이터 행 검증 - 모든 행이 헤더와 비슷한 열 수를 가져야 함
  const dataRows = allRows.slice(1)
  const validRows = dataRows.filter(row => {
    const diff = Math.abs(row.length - columnCount)
    return diff <= 1 || (row.length >= columnCount && row[columnCount - 1].includes('('))
  })
  
  // 최소 70% 이상이 유효한 행이어야 함
  if (validRows.length < dataRows.length * 0.7) return null

  return {
    headers: potentialHeaders,
    rows: dataRows.map(row => {
      // 행의 셀 수를 헤더에 맞춤
      while (row.length < columnCount) {
        row.push('')
      }
      return row.slice(0, columnCount)
    })
  }
}

