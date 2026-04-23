<template>
  <div class="security-testing">
    <el-row :gutter="20">
      <el-col :span="12">
        <el-card class="test-card">
          <template #header>
            <div class="card-header">
              <span>SQL 注入测试</span>
              <el-icon color="#f56c6c" :size="24"><WarnTriangleFilled /></el-icon>
            </div>
          </template>

          <el-form :model="sqlForm" label-width="100px">
            <el-form-item label="目标URL">
              <el-input v-model="sqlForm.url" placeholder="请输入测试URL" />
            </el-form-item>
            <el-form-item label="测试参数">
              <el-input
                v-model="sqlForm.params"
                type="textarea"
                :rows="3"
                placeholder="请输入参数字段，多个用逗号分隔"
              />
            </el-form-item>
            <el-form-item label="测试级别">
              <el-radio-group v-model="sqlForm.level">
                <el-radio label="low">低</el-radio>
                <el-radio label="medium">中</el-radio>
                <el-radio label="high">高</el-radio>
              </el-radio-group>
            </el-form-item>
            <el-form-item>
              <el-button type="danger" @click="handleSQLTest" :loading="sqlTesting">
                <el-icon v-if="!sqlTesting"><Search /></el-icon>
                {{ sqlTesting ? '测试中...' : '开始测试' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>

      <el-col :span="12">
        <el-card class="test-card">
          <template #header>
            <div class="card-header">
              <span>XSS 跨站脚本测试</span>
              <el-icon color="#e6a23c" :size="24"><WarnTriangleFilled /></el-icon>
            </div>
          </template>

          <el-form :model="xssForm" label-width="100px">
            <el-form-item label="目标URL">
              <el-input v-model="xssForm.url" placeholder="请输入测试URL" />
            </el-form-item>
            <el-form-item label="测试参数">
              <el-input
                v-model="xssForm.params"
                type="textarea"
                :rows="3"
                placeholder="请输入参数字段，多个用逗号分隔"
              />
            </el-form-item>
            <el-form-item label="测试类型">
              <el-checkbox-group v-model="xssForm.types">
                <el-checkbox label="reflected">反射型</el-checkbox>
                <el-checkbox label="stored">存储型</el-checkbox>
                <el-checkbox label="dom">DOM型</el-checkbox>
              </el-checkbox-group>
            </el-form-item>
            <el-form-item>
              <el-button type="warning" @click="handleXSSTest" :loading="xssTesting">
                <el-icon v-if="!xssTesting"><Search /></el-icon>
                {{ xssTesting ? '测试中...' : '开始测试' }}
              </el-button>
            </el-form-item>
          </el-form>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="results-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>安全测试报告</span>
          <div class="header-actions">
            <el-button type="primary" size="small" @click="handleExport">
              <el-icon><Download /></el-icon>导出报告
            </el-button>
            <el-button type="danger" size="small" @click="handleClearResults">
              清空结果
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="securityResults" stripe style="width: 100%">
        <el-table-column type="index" label="序号" width="60" />
        <el-table-column prop="type" label="漏洞类型" width="120">
          <template #default="{ row }">
            <el-tag :type="row.type === 'SQL注入' ? 'danger' : 'warning'">
              {{ row.type }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="url" label="测试URL" min-width="200" show-overflow-tooltip />
        <el-table-column prop="param" label="参数" width="100" />
        <el-table-column prop="payload" label="Payload" min-width="200" show-overflow-tooltip />
        <el-table-column prop="severity" label="严重程度" width="100">
          <template #default="{ row }">
            <el-tag :type="getSeverityType(row.severity)">{{ row.severity }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="status" label="状态" width="100">
          <template #default="{ row }">
            <el-tag :type="row.status === '存在' ? 'danger' : 'success'">
              {{ row.status }}
            </el-tag>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <el-card class="summary-card" style="margin-top: 20px;">
      <template #header>
        <span>测试统计</span>
      </template>
      <el-row :gutter="20">
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-value">{{ summary.total }}</div>
            <div class="summary-label">测试用例</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-value" style="color: #f56c6c;">{{ summary.vulnerabilities }}</div>
            <div class="summary-label">发现漏洞</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-value" style="color: #67c23a;">{{ summary.safe }}</div>
            <div class="summary-label">安全</div>
          </div>
        </el-col>
        <el-col :span="6">
          <div class="summary-item">
            <div class="summary-value">{{ summary.duration }}</div>
            <div class="summary-label">测试耗时</div>
          </div>
        </el-col>
      </el-row>
    </el-card>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { WarnTriangleFilled, Search, Download } from '@element-plus/icons-vue'

const sqlTesting = ref(false)
const xssTesting = ref(false)

const sqlForm = reactive({
  url: '',
  params: '',
  level: 'medium'
})

const xssForm = reactive({
  url: '',
  params: '',
  types: ['reflected']
})

const securityResults = ref([
  {
    type: 'SQL注入',
    url: 'https://httpbin.org/get',
    param: 'id',
    payload: "1' OR '1'='1",
    severity: '高危',
    status: '不存在'
  },
  {
    type: 'XSS',
    url: 'https://httpbin.org/post',
    param: 'name',
    payload: '<script>alert("XSS")</' + 'script>',
    severity: '中危',
    status: '不存在'
  }
])

const summary = reactive({
  total: 45,
  vulnerabilities: 0,
  safe: 45,
  duration: '3分12秒'
})

const getSeverityType = (severity) => {
  const map = { '高危': 'danger', '中危': 'warning', '低危': 'info' }
  return map[severity] || 'info'
}

const handleSQLTest = async () => {
  if (!sqlForm.url) {
    ElMessage.warning('请输入目标URL')
    return
  }

  sqlTesting.value = true
  await new Promise(resolve => setTimeout(resolve, 2000))

  securityResults.value.push({
    type: 'SQL注入',
    url: sqlForm.url,
    param: 'id',
    payload: "1' UNION SELECT * FROM users--",
    severity: '高危',
    status: Math.random() > 0.7 ? '存在' : '不存在'
  })

  sqlTesting.value = false
  ElMessage.success('SQL注入测试完成')
}

const handleXSSTest = async () => {
  if (!xssForm.url) {
    ElMessage.warning('请输入目标URL')
    return
  }

  xssTesting.value = true
  await new Promise(resolve => setTimeout(resolve, 2000))

  securityResults.value.push({
    type: 'XSS',
    url: xssForm.url,
    param: 'name',
    payload: '<img src=x onerror=alert(1)>',
    severity: '中危',
    status: Math.random() > 0.8 ? '存在' : '不存在'
  })

  xssTesting.value = false
  ElMessage.success('XSS测试完成')
}

const handleExport = () => {
  ElMessage.success('安全报告导出中...')
}

const handleClearResults = () => {
  securityResults.value = []
  ElMessage.info('结果已清空')
}
</script>

<style scoped>
.security-testing {
  padding: 20px;
}

.test-card,
.results-card,
.summary-card {
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

.summary-item {
  text-align: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 12px;
}

.summary-value {
  font-size: 32px;
  font-weight: bold;
  color: #303133;
}

.summary-label {
  font-size: 14px;
  color: #909399;
  margin-top: 8px;
}
</style>