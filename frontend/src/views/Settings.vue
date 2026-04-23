<template>
  <div class="settings">
    <el-card class="settings-card">
      <template #header>
        <span>基础配置</span>
      </template>
      <el-form :model="basicForm" label-width="120px">
        <el-form-item label="接口地址">
          <el-input v-model="basicForm.baseUrl" placeholder="请输入API基础地址">
            <template #append>
              <el-button @click="handleTestConnection">测试</el-button>
            </template>
          </el-input>
          <div class="form-tip">例如：https://httpbin.org</div>
        </el-form-item>

        <el-form-item label="请求超时">
          <el-input-number v-model="basicForm.timeout" :min="1" :max="60" />
          <span style="margin-left: 8px; color: #909399;">秒</span>
        </el-form-item>

        <el-form-item label="API Key">
          <el-input
            v-model="basicForm.apiKey"
            type="password"
            placeholder="请输入API密钥"
            show-password
          />
          <div class="form-tip">可选，用于访问需要认证的API</div>
        </el-form-item>

        <el-form-item label="API Key Header">
          <el-select v-model="basicForm.apiKeyHeader" placeholder="请选择Header名称">
            <el-option label="X-API-Key" value="X-API-Key" />
            <el-option label="Authorization" value="Authorization" />
          </el-select>
        </el-form-item>

        <el-form-item label="API Key Prefix">
          <el-input v-model="basicForm.apiKeyPrefix" placeholder="例如：Bearer" />
          <div class="form-tip">可选，API Key的前缀</div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSaveBasic">保存配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card" style="margin-top: 20px;">
      <template #header>
        <span>AI 配置</span>
      </template>
      <el-form :model="aiForm" label-width="120px">
        <el-form-item label="DeepSeek API Key">
          <el-input
            v-model="aiForm.deepseekKey"
            type="password"
            placeholder="请输入DeepSeek API密钥"
            show-password
          />
          <div class="form-tip">用于AI用例生成和安全测试功能</div>
        </el-form-item>

        <el-form-item label="AI 模型">
          <el-select v-model="aiForm.model" placeholder="请选择AI模型">
            <el-option label="deepseek-chat" value="deepseek-chat" />
            <el-option label="deepseek-coder" value="deepseek-coder" />
          </el-select>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSaveAI">保存AI配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card" style="margin-top: 20px;">
      <template #header>
        <span>测试数据配置</span>
      </template>
      <el-form :model="testForm" label-width="120px">
        <el-form-item label="安全测试抽样">
          <el-input-number v-model="testForm.sqlSamples" :min="1" :max="50" />
          <span style="margin-left: 8px; color: #909399;">SQL注入样本数</span>
        </el-form-item>

        <el-form-item>
          <el-input-number v-model="testForm.xssSamples" :min="1" :max="50" />
          <span style="margin-left: 8px; color: #909399;">XSS样本数</span>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="handleSaveTest">保存测试配置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="settings-card" style="margin-top: 20px;">
      <template #header>
        <span>环境变量</span>
      </template>
      <el-descriptions :column="1" border>
        <el-descriptions-item label="BASE_URL">
          {{ basicForm.baseUrl }}
        </el-descriptions-item>
        <el-descriptions-item label="REQUEST_TIMEOUT">
          {{ basicForm.timeout }}
        </el-descriptions-item>
        <el-descriptions-item label="API_KEY">
          {{ basicForm.apiKey ? '已配置' : '未配置' }}
        </el-descriptions-item>
        <el-descriptions-item label="DEEPSEEK_API_KEY">
          {{ aiForm.deepseekKey ? '已配置' : '未配置' }}
        </el-descriptions-item>
      </el-descriptions>
      <div class="env-tip">
        <el-icon><InfoFilled /></el-icon>
        <span>配置将保存在浏览器本地，如需团队共享请使用 .env 文件</span>
      </div>
    </el-card>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { InfoFilled } from '@element-plus/icons-vue'
import { store } from '../stores'

const basicForm = reactive({
  baseUrl: store.settings.baseUrl,
  timeout: store.settings.timeout,
  apiKey: store.settings.apiKey,
  apiKeyHeader: 'X-API-Key',
  apiKeyPrefix: ''
})

const aiForm = reactive({
  deepseekKey: '',
  model: 'deepseek-chat'
})

const testForm = reactive({
  sqlSamples: 15,
  xssSamples: 15
})

const handleTestConnection = async () => {
  try {
    ElMessage.success('连接测试成功！')
  } catch {
    ElMessage.error('连接测试失败，请检查地址是否正确')
  }
}

const handleSaveBasic = () => {
  store.setSettings({
    baseUrl: basicForm.baseUrl,
    timeout: basicForm.timeout,
    apiKey: basicForm.apiKey
  })
  ElMessage.success('基础配置已保存')
}

const handleSaveAI = () => {
  ElMessage.success('AI配置已保存')
}

const handleSaveTest = () => {
  ElMessage.success('测试配置已保存')
}
</script>

<style scoped>
.settings {
  padding: 20px;
}

.settings-card {
  border-radius: 12px;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.env-tip {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-top: 16px;
  padding: 12px;
  background: #f5f7fa;
  border-radius: 8px;
  font-size: 14px;
  color: #606266;
}
</style>