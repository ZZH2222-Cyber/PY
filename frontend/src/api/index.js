import axios from 'axios'
import { ElMessage } from 'element-plus'

const api = axios.create({
  baseURL: 'http://localhost:5173',
  timeout: 30000
})

api.interceptors.request.use(
  config => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  error => {
    return Promise.reject(error)
  }
)

api.interceptors.response.use(
  response => {
    return response.data
  },
  error => {
    ElMessage.error(error.message || '请求失败')
    return Promise.reject(error)
  }
)

export const testAPI = {
  runTest: (testPath) => api.post('/api/run-test', { testPath }),
  getTestStatus: (taskId) => api.get(`/api/test-status/${taskId}`),
  getTestLogs: (taskId) => api.get(`/api/test-logs/${taskId}`)
}

export const caseAPI = {
  getCases: () => api.get('/api/cases'),
  getCase: (id) => api.get(`/api/cases/${id}`),
  createCase: (data) => api.post('/api/cases', data),
  updateCase: (id, data) => api.put(`/api/cases/${id}`, data),
  deleteCase: (id) => api.delete(`/api/cases/${id}`)
}

export const reportAPI = {
  getReports: () => api.get('/api/reports'),
  getReport: (id) => api.get(`/api/reports/${id}`),
  generateReport: () => api.post('/api/reports/generate')
}

export const aiAPI = {
  generateCases: (description) => api.post('/api/ai/generate', { description }),
  generateTestData: (schema) => api.post('/api/ai/generate-data', { schema })
}

export const securityAPI = {
  sqlInjectionTest: (url, params) => api.post('/api/security/sql-injection', { url, params }),
  xssTest: (url, params) => api.post('/api/security/xss', { url, params }),
  getSecurityReport: () => api.get('/api/security/report')
}

export default api