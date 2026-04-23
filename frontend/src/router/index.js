import { createRouter, createWebHistory } from 'vue-router'
import Dashboard from '../views/Dashboard.vue'
import TestCases from '../views/TestCases.vue'
import RunTests from '../views/RunTests.vue'
import Reports from '../views/Reports.vue'
import AIGeneration from '../views/AIGeneration.vue'
import SecurityTesting from '../views/SecurityTesting.vue'
import Settings from '../views/Settings.vue'

const routes = [
  {
    path: '/',
    name: 'Dashboard',
    component: Dashboard
  },
  {
    path: '/test-cases',
    name: 'TestCases',
    component: TestCases
  },
  {
    path: '/run-tests',
    name: 'RunTests',
    component: RunTests
  },
  {
    path: '/reports',
    name: 'Reports',
    component: Reports
  },
  {
    path: '/ai-generation',
    name: 'AIGeneration',
    component: AIGeneration
  },
  {
    path: '/security-testing',
    name: 'SecurityTesting',
    component: SecurityTesting
  },
  {
    path: '/settings',
    name: 'Settings',
    component: Settings
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router