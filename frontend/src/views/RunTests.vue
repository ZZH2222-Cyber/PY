<template>
  <div class="run-tests">
    <el-card class="config-card">
      <template #header>
        <span>测试配置</span>
      </template>
      <el-form :inline="true" :model="configForm">
        <el-form-item label="选择用例">
          <el-select v-model="configForm.cases" multiple placeholder="请选择测试用例" style="width: 400px;">
            <el-option label="用户登录测试" value="TC001" />
            <el-option label="获取用户列表" value="TC002" />
            <el-option label="创建订单" value="TC003" />
            <el-option label="支付接口" value="TC004" />
            <el-option label="商品查询" value="TC005" />
          </el-select>
        </el-form-item>
        <el-form-item label="运行环境">
          <el-select v-model="configForm.env" placeholder="请选择环境">
            <el-option label="测试环境" value="test" />
            <el-option label="预发环境" value="pre" />
            <el-option label="生产环境" value="prod" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleRunAll" :loading="running">
            <el-icon v-if="!running"><VideoPlay /></el-icon>
            {{ running ? '运行中...' : '运行全部' }}
          </el-button>
          <el-button @click="handleRunSelected" :disabled="configForm.cases.length === 0">
            运行选中
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="progress-card" v-if="running || testResults.length > 0">
      <template #header>
        <div class="card-header">
          <span>执行进度</span>
          <el-progress :percentage="progress" :status="progressStatus" style="width: 200px;" />
        </div>
      </template>
      <el-steps :active="currentStep" finish-status="success" align-center>
        <el-step title="准备测试" />
        <el-step title="执行用例" />
        <el-step title="数据校验" />
        <el-step title="生成报告" />
      </el-steps>
    </el-card>

    <el-card class="results-card">
      <template #header>
        <div class="card-header">
          <span>测试结果</span>
          <div class="header-actions">
            <el-button size="small" @click="handleClear">清空结果</el-button>
            <el-button type="primary" size="small" @click="handleViewReport">
              查看报告
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="testResults" stripe style="width: 100%" v-loading="running">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="caseName" label="用例名称" min-width="150" />
        <el-table-column prop="method" label="方法" width="80">
          <template #default="{ row }">
            <el-tag :type="getMethodType(row.method)">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="接口路径" min-width="150" />
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '通过' ? 'success' : row.status === '失败' ? 'danger' : 'info'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="100" />
        <el-table-column prop="code" label="响应码" width="100" />
        <el-table-column label="操作" width="120" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleViewDetail(row)">
              详情
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-dialog v-model="detailVisible" title="测试详情" width="800px">
      <el-descriptions :column="2" border v-if="currentDetail">
        <el-descriptions-item label="用例名称">{{ currentDetail.caseName }}</el-descriptions-item>
        <el-descriptions-item label="请求方法">{{ currentDetail.method }}</el-descriptions-item>
        <el-descriptions-item label="接口路径">{{ currentDetail.path }}</el-descriptions-item>
        <el-descriptions-item label="响应状态">{{ currentDetail.status }}</el-descriptions-item>
        <el-descriptions-item label="响应码">{{ currentDetail.code }}</el-descriptions-item>
        <el-descriptions-item label="耗时">{{ currentDetail.duration }}</el-descriptions-item>
      </el-descriptions>

      <el-tabs style="margin-top: 20px;">
        <el-tab-pane label="请求信息">
          <pre class="code-block">{{ currentDetail?.request || '{}' }}</pre>
        </el-tab-pane>
        <el-tab-pane label="响应信息">
          <pre class="code-block">{{ currentDetail?.response || '{}' }}</pre>
        </el-tab-pane>
        <el-tab-pane label="断言结果">
          <pre class="code-block">{{ currentDetail?.assertions || '{}' }}</pre>
        </el-tab-pane>
      </el-tabs>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage } from 'element-plus'
import { VideoPlay } from '@element-plus/icons-vue'

const router = useRouter()
const running = ref(false)
const progress = ref(0)
const currentStep = ref(0)
const detailVisible = ref(false)
const currentDetail = ref(null)

const configForm = reactive({
  cases: [],
  env: 'test'
})

const testResults = ref([])

const progressStatus = computed(() => {
  if (progress.value === 100) return 'success'
  if (progress.value < 30) return 'exception'
  return ''
})

const getMethodType = (method) => {
  const map = { GET: 'success', POST: 'warning', PUT: 'primary', DELETE: 'danger' }
  return map[method] || 'info'
}

const handleRunAll = async () => {
  running.value = true
  progress.value = 0
  currentStep.value = 0
  testResults.value = []

  const allCases = [
    { caseName: '用户登录测试', method: 'POST', path: '/api/login' },
    { caseName: '获取用户列表', method: 'GET', path: '/api/users' },
    { caseName: '创建订单', method: 'POST', path: '/api/orders' },
    { caseName: '支付接口', method: 'POST', path: '/api/pay' },
    { caseName: '商品查询', method: 'GET', path: '/api/products' }
  ]

  for (let i = 0; i < allCases.length; i++) {
    await new Promise(resolve => setTimeout(resolve, 800))
    currentStep.value = 1
    progress.value = Math.floor(((i + 1) / allCases.length) * 100)

    const result = {
      ...allCases[i],
      status: Math.random() > 0.2 ? '通过' : '失败',
      code: Math.random() > 0.2 ? 200 : 500,
      duration: (Math.random() * 2 + 0.5).toFixed(2) + 's',
      request: JSON.stringify({ method: allCases[i].method, path: allCases[i].path }, null, 2),
      response: JSON.stringify({ code: Math.random() > 0.2 ? 0 : 500, data: {}, message: 'success' }, null, 2),
      assertions: JSON.stringify([{ field: 'code', expected: 0, actual: Math.random() > 0.2 ? 0 : 500, passed: Math.random() > 0.2 }], null, 2)
    }

    testResults.value.push(result)
  }

  currentStep.value = 4
  progress.value = 100
  running.value = false
  ElMessage.success('测试执行完成')
}

const handleRunSelected = () => {
  if (configForm.cases.length === 0) {
    ElMessage.warning('请先选择要运行的用例')
    return
  }
  ElMessage.info('运行选中用例功能开发中')
}

const handleClear = () => {
  testResults.value = []
  progress.value = 0
  currentStep.value = 0
}

const handleViewReport = () => {
  router.push('/reports')
}

const handleViewDetail = (row) => {
  currentDetail.value = row
  detailVisible.value = true
}
</script>

<style scoped>
.run-tests {
  padding: 20px;
}

.config-card,
.progress-card,
.results-card {
  margin-bottom: 20px;
  border-radius: 12px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.header-actions {
  display: flex;
  gap: 8px;
}

.code-block {
  background: #f5f7fa;
  padding: 16px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 12px;
  line-height: 1.6;
}
</style>