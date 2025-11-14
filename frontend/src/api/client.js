import axios from 'axios'

// API 기본 URL 설정
const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000/api'

// axios 인스턴스 생성
const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 60000, // 60초 타임아웃 (AI 응답 대기)
})

// 요청 인터셉터
apiClient.interceptors.request.use(
  (config) => {
    console.log('API 요청:', config.method.toUpperCase(), config.url)
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 응답 인터셉터
apiClient.interceptors.response.use(
  (response) => {
    console.log('API 응답:', response.status, response.data)
    return response
  },
  (error) => {
    console.error('API 오류:', error.response?.data || error.message)
    return Promise.reject(error)
  }
)

/**
 * 보험 인정기준 질의 API
 */
export const queryInsuranceCriteria = async (materialCode, procedureCode, question, conversationHistory = null) => {
  try {
    const requestBody = {
      question: question
    }
    
    // 코드가 있을 때만 추가
    if (materialCode) {
      requestBody.material_code = materialCode
    }
    if (procedureCode) {
      requestBody.procedure_code = procedureCode
    }
    
    // 대화 히스토리가 있을 때만 추가
    if (conversationHistory && conversationHistory.length > 0) {
      requestBody.conversation_history = conversationHistory
    }
    
    const response = await apiClient.post('/query', requestBody)
    return response.data
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || 
      error.message || 
      '서버와의 통신 중 오류가 발생했습니다.'
    )
  }
}

/**
 * 데이터 전처리 API
 */
export const preprocessData = async (dataPath = './data/raw/sample_criteria.json') => {
  try {
    const response = await apiClient.post('/preprocess', {
      data_path: dataPath,
    })
    return response.data
  } catch (error) {
    throw new Error(
      error.response?.data?.detail || 
      error.message || 
      '데이터 전처리 중 오류가 발생했습니다.'
    )
  }
}

/**
 * 헬스 체크 API
 */
export const healthCheck = async () => {
  try {
    const response = await apiClient.get('/health')
    return response.data
  } catch (error) {
    throw new Error('서버가 응답하지 않습니다.')
  }
}

export default apiClient

