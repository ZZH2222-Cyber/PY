import { reactive } from 'vue'

export const store = reactive({
  user: null,
  token: localStorage.getItem('token') || '',
  settings: {
    baseUrl: localStorage.getItem('baseUrl') || 'https://httpbin.org',
    timeout: parseInt(localStorage.getItem('timeout') || '10'),
    apiKey: localStorage.getItem('apiKey') || ''
  },
  testResults: [],
  testCases: [],
  reports: [],

  setToken(token) {
    this.token = token
    localStorage.setItem('token', token)
  },

  setSettings(settings) {
    this.settings = { ...this.settings, ...settings }
    localStorage.setItem('baseUrl', this.settings.baseUrl)
    localStorage.setItem('timeout', this.settings.timeout.toString())
    localStorage.setItem('apiKey', this.settings.apiKey)
  },

  clearStore() {
    this.token = ''
    this.user = null
    localStorage.clear()
  }
})