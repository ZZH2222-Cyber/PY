<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
              <el-icon :size="32"><Document /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalCases }}</div>
              <div class="stat-label">测试用例</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #36d1dc 0%, #5b86e5 100%);">
              <el-icon :size="32"><VideoPlay /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.totalRuns }}</div>
              <div class="stat-label">运行次数</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
              <el-icon :size="32"><SuccessFilled /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.passRate }}%</div>
              <div class="stat-label">通过率</div>
            </div>
          </div>
        </el-card>
      </el-col>

      <el-col :span="6">
        <el-card class="stat-card" shadow="hover">
          <div class="stat-content">
            <div class="stat-icon" style="background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);">
              <el-icon :size="32"><Clock /></el-icon>
            </div>
            <div class="stat-info">
              <div class="stat-value">{{ stats.avgDuration }}s</div>
              <div class="stat-label">平均耗时</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="16">
        <el-card class="chart-card">
          <template #header>
            <div class="card-header">
              <span>最近测试记录</span>
              <el-button type="primary" size="small" @click="$router.push('/run-tests')">
                立即运行
              </el-button>
            </div>
          </template>
          <el-table :data="recentTests" style="width: 100%">
            <el-table-column prop="name" label="用例名称" />
            <el-table-column prop="status" label="状态" width="100">
              <template #default="{ row }">
                <el-tag :type="row.status === '通过' ? 'success' : 'danger'">
                  {{ row.status }}
                </el-tag>
              </template>
            </el-table-column>
            <el-table-column prop="duration" label="耗时" width="100" />
            <el-table-column prop="time" label="执行时间" />
          </el-table>
        </el-card>
      </el-col>

      <el-col :span="8">
        <el-card class="chart-card">
          <template #header>
            <span>快速入口</span>
          </template>
          <div class="quick-entry">
            <div class="quick-item" @click="$router.push('/test-cases')">
              <el-icon :size="32" color="#667eea"><FolderAdd /></el-icon>
              <span>管理用例</span>
            </div>
            <div class="quick-item" @click="$router.push('/ai-generation')">
              <el-icon :size="32" color="#36d1dc"><Operation /></el-icon>
              <span>AI 生成</span>
            </div>
            <div class="quick-item" @click="$router.push('/security-testing')">
              <el-icon :size="32" color="#eb3349"><Lock /></el-icon>
              <span>安全检测</span>
            </div>
            <div class="quick-item" @click="$router.push('/reports')">
              <el-icon :size="32" color="#11998e"><DataLine /></el-icon>
              <span>查看报告</span>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="24">
        <el-card class="chart-card">
          <template #header>
            <span>环境配置</span>
          </template>
          <el-descriptions :column="3" border>
            <el-descriptions-item label="接口地址">
              {{ store.settings.baseUrl }}
            </el-descriptions-item>
            <el-descriptions-item label="超时时间">
              {{ store.settings.timeout }} 秒
            </el-descriptions-item>
            <el-descriptions-item label="API Key">
              {{ store.settings.apiKey ? '已配置' : '未配置' }}
            </el-descriptions-item>
          </el-descriptions>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import {
  Document,
  VideoPlay,
  SuccessFilled,
  Clock,
  FolderAdd,
  Operation as Magic,
  Lock,
  DataLine
} from '@element-plus/icons-vue'
import { store } from '../stores'

const stats = reactive({
  totalCases: 126,
  totalRuns: 458,
  passRate: 94.2,
  avgDuration: 1.2
})

const recentTests = ref([
  { name: '用户登录测试', status: '通过', duration: '0.8s', time: '2026-04-23 21:50' },
  { name: '获取用户列表', status: '通过', duration: '1.2s', time: '2026-04-23 21:48' },
  { name: '创建订单接口', status: '通过', duration: '0.5s', time: '2026-04-23 21:45' },
  { name: '支付接口测试', status: '失败', duration: '2.1s', time: '2026-04-23 21:40' },
  { name: '商品查询接口', status: '通过', duration: '0.9s', time: '2026-04-23 21:35' }
])
</script>

<style scoped>
.dashboard {
  padding: 20px;
}

.stat-card {
  border-radius: 12px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 16px;
}

.stat-icon {
  width: 64px;
  height: 64px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.chart-card {
  border-radius: 12px;
}

.quick-entry {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 16px;
}

.quick-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
  padding: 20px;
  border-radius: 12px;
  background: #f5f7fa;
  cursor: pointer;
  transition: all 0.3s;
}

.quick-item:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.quick-item span {
  font-size: 14px;
  color: #606266;
}
</style>