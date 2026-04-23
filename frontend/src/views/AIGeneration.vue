<template>
  <div class="ai-generation">
    <el-row :gutter="20">
      <el-col :span="16">
        <el-card class="input-card">
          <template #header>
            <div class="card-header">
              <span>AI 用例生成</span>
              <el-tag type="success">DeepSeek API</el-tag>
            </div>
          </template>

          <el-form :model="genForm" label-width="120px">
            <el-form-item label="接口描述">
              <el-input
                v-model="genForm.description"
                type="textarea"
                :rows="4"
                placeholder="请描述接口功能，例如：用户登录接口，支持用户名密码登录，返回token"
              />
            </el-form-item>

            <el-form-item label="请求方法">
              <el-checkbox-group v-model="genForm.methods">
                <el-checkbox label="GET" />
                <el-checkbox label="POST" />
                <el-checkbox label="PUT" />
                <el-checkbox label="DELETE" />
              </el-checkbox-group>
            </el-form-item>

            <el-form-item label="生成用例数量">
              <el-slider v-model="genForm.count" :min="1" :max="20" show-input />
            </el-form-item>

            <el-form-item label="包含场景">
              <el-checkbox-group v-model="genForm.scenarios">
                <el-checkbox label="normal">正常场景</el-checkbox>
                <el-checkbox label="boundary">边界值</el-checkbox>
                <el-checkbox label="error">异常场景</el-checkbox>
                <el-checkbox label="security">安全测试</el-checkbox>
              </el-checkbox-group>
            </el-form-item>

            <el-form-item>
              <el-button type="primary" @click="handleGenerate" :loading="generating">
                <el-icon v-if="!generating"><Operation /></el-icon>
                {{ generating ? '生成中...' : '生成测试用例' }}
              </el-button>
              <el-button @click="handleClear">清空</el-button>
            </el-form-item>
          </el-form>
        </el-card>

        <el-card class="results-card" style="margin-top: 20px;" v-if="generatedCases.length > 0">
          <template #header>
            <div class="card-header">
              <span>生成的测试用例</span>
              <div class="header-actions">
                <el-button type="success" size="small" @click="handleAddAll">
                  批量添加
                </el-button>
              </div>
            </div>
          </template>

          <el-table :data="generatedCases" stripe style="width: 100%">
            <el-table-column type="index" label="序号" width="60" />
            <el-table-column prop="name" label="用例名称" min-width="150" />
            <el-table-column prop="method" label="方法" width="80">
              <template #default="{ row }">
                <el-tag :type="getMethodType(row.method)">{{ row.method }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="path" label="路径" min-width="120" />
            <el-table-column prop="scenario" label="场景" width="100">
              <template #default="{ row }">
                <el-tag>{{ getScenarioName(row.scenario) }}</el-tag>
              </template>
            </el-table-column>
            <el-table-column label="操作" width="180" fixed="right">
              <template #default="{ row, $index }">
                <el-button type="primary" size="small" @click="handleViewDetail(row)">详情</el-button>
                <el-button type="success" size="small" @click="handleAdd(row, $index)">添加</el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="tips-card">
          <template #header>
            <span>使用提示</span>
          </template>
          <div class="tips-list">
            <div class="tip-item">
              <el-icon color="#409eff"><QuestionFilled /></el-icon>
              <span>描述越详细，生成的用例越精准</span>
            </div>
            <div class="tip-item">
              <el-icon color="#67c23a"><QuestionFilled /></el-icon>
              <span>支持生成正常、边界、异常等多种场景</span>
            </div>
            <div class="tip-item">
              <el-icon color="#e6a23c"><QuestionFilled /></el-icon>
              <span>生成后可编辑后再添加到用例库</span>
            </div>
            <div class="tip-item">
              <el-icon color="#f56c6c"><QuestionFilled /></el-icon>
              <span>需要配置 DeepSeek API Key</span>
            </div>
          </div>
        </el-card>

        <el-card class="history-card" style="margin-top: 20px;">
          <template #header>
            <span>历史生成记录</span>
          </template>
          <el-timeline>
            <el-timeline-item
              v-for="(item, index) in history"
              :key="index"
              :timestamp="item.time"
              placement="top"
            >
              <el-card>
                <p>{{ item.description }}</p>
                <el-tag size="small">{{ item.count }} 个用例</el-tag>
              </el-card>
            </el-timeline-item>
          </el-timeline>
        </el-card>
      </el-col>
    </el-row>

    <el-dialog v-model="detailVisible" title="用例详情" width="600px">
      <el-descriptions :column="1" border v-if="currentCase">
        <el-descriptions-item label="用例名称">{{ currentCase.name }}</el-descriptions-item>
        <el-descriptions-item label="请求方法">{{ currentCase.method }}</el-descriptions-item>
        <el-descriptions-item label="接口路径">{{ currentCase.path }}</el-descriptions-item>
        <el-descriptions-item label="测试场景">{{ getScenarioName(currentCase.scenario) }}</el-descriptions-item>
        <el-descriptions-item label="请求参数">
          <pre class="code-block">{{ currentCase.params }}</pre>
        </el-descriptions-item>
        <el-descriptions-item label="预期结果">
          <pre class="code-block">{{ currentCase.expected }}</pre>
        </el-descriptions-item>
      </el-descriptions>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { Operation, QuestionFilled } from '@element-plus/icons-vue'

const generating = ref(false)
const detailVisible = ref(false)
const currentCase = ref(null)

const genForm = reactive({
  description: '',
  methods: ['GET', 'POST'],
  count: 5,
  scenarios: ['normal', 'boundary']
})

const generatedCases = ref([])

const history = ref([
  { time: '2026-04-23 18:30', description: '用户登录接口测试用例生成', count: 8 },
  { time: '2026-04-22 15:20', description: '订单创建接口测试用例生成', count: 12 },
  { time: '2026-04-21 10:00', description: '商品查询接口测试用例生成', count: 6 }
])

const getMethodType = (method) => {
  const map = { GET: 'success', POST: 'warning', PUT: 'primary', DELETE: 'danger' }
  return map[method] || 'info'
}

const getScenarioName = (scenario) => {
  const map = { normal: '正常', boundary: '边界', error: '异常', security: '安全' }
  return map[scenario] || scenario
}

const handleGenerate = async () => {
  if (!genForm.description) {
    ElMessage.warning('请输入接口描述')
    return
  }

  generating.value = true

  await new Promise(resolve => setTimeout(resolve, 2000))

  const methods = genForm.methods.length > 0 ? genForm.methods : ['GET', 'POST']
  const scenarios = genForm.scenarios.length > 0 ? genForm.scenarios : ['normal']

  generatedCases.value = []
  for (let i = 0; i < genForm.count; i++) {
    const method = methods[i % methods.length]
    const scenario = scenarios[i % scenarios.length]
    generatedCases.value.push({
      name: `AI生成-${method}-${getScenarioName(scenario)}-${i + 1}`,
      method,
      path: '/api/' + genForm.description.substring(0, 10).replace(/\s/g, '_'),
      scenario,
      params: JSON.stringify({ id: i + 1, name: 'test' }, null, 2),
      expected: JSON.stringify({ code: 0, message: 'success' }, null, 2)
    })
  }

  generating.value = false
  ElMessage.success(`成功生成 ${generatedCases.value.length} 个测试用例`)
}

const handleClear = () => {
  genForm.description = ''
  genForm.methods = ['GET', 'POST']
  genForm.count = 5
  genForm.scenarios = ['normal']
  generatedCases.value = []
}

const handleViewDetail = (row) => {
  currentCase.value = row
  detailVisible.value = true
}

const handleAdd = (row, index) => {
  generatedCases.value.splice(index, 1)
  ElMessage.success(`用例 "${row.name}" 已添加到用例库`)
}

const handleAddAll = () => {
  const count = generatedCases.value.length
  generatedCases.value = []
  ElMessage.success(`成功添加 ${count} 个用例到用例库`)
}
</script>

<style scoped>
.ai-generation {
  padding: 20px;
}

.input-card,
.results-card,
.tips-card,
.history-card {
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

.tips-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.tip-item {
  display: flex;
  align-items: center;
  gap: 12px;
  font-size: 14px;
  color: #606266;
}

.code-block {
  background: #f5f7fa;
  padding: 12px;
  border-radius: 8px;
  overflow-x: auto;
  font-size: 12px;
  line-height: 1.6;
  margin: 0;
}
</style>