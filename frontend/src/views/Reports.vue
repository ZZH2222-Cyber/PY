<template>
  <div class="reports">
    <el-row :gutter="20">
      <el-col :span="8">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-item">
            <div class="summary-icon" style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
              <el-icon :size="28"><Document /></el-icon>
            </div>
            <div class="summary-info">
              <div class="summary-value">{{ summary.total }}</div>
              <div class="summary-label">总测试数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-item">
            <div class="summary-icon" style="background: linear-gradient(135deg, #11998e 0%, #38ef7d 100%);">
              <el-icon :size="28"><SuccessFilled /></el-icon>
            </div>
            <div class="summary-info">
              <div class="summary-value">{{ summary.passed }}</div>
              <div class="summary-label">通过数</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :span="8">
        <el-card class="summary-card" shadow="hover">
          <div class="summary-item">
            <div class="summary-icon" style="background: linear-gradient(135deg, #eb3349 0%, #f45c43 100%);">
              <el-icon :size="28"><CircleCloseFilled /></el-icon>
            </div>
            <div class="summary-info">
              <div class="summary-value">{{ summary.failed }}</div>
              <div class="summary-label">失败数</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" style="margin-top: 20px;">
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>测试结果分布</span>
          </template>
          <div class="pie-chart">
            <el-progress type="circle" :percentage="summary.passRate" :color="passRateColor">
              <template #default>
                <span class="rate-text">{{ summary.passRate }}%</span>
                <span class="rate-label">通过率</span>
              </template>
            </el-progress>
          </div>
        </el-card>
      </el-col>
      <el-col :span="12">
        <el-card class="chart-card">
          <template #header>
            <span>测试趋势</span>
          </template>
          <div class="trend-list">
            <div v-for="(item, index) in trends" :key="index" class="trend-item">
              <span class="trend-date">{{ item.date }}</span>
              <el-progress :percentage="item.rate" :color="item.rate >= 90 ? '#67c23a' : item.rate >= 70 ? '#e6a23c' : '#f56c6c'" />
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-card class="table-card" style="margin-top: 20px;">
      <template #header>
        <div class="card-header">
          <span>历史报告</span>
          <div class="header-actions">
            <el-button type="primary" @click="handleGenerate">
              <el-icon><Refresh /></el-icon>生成报告
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="reports" stripe style="width: 100%">
        <el-table-column prop="id" label="报告ID" width="100" />
        <el-table-column prop="name" label="报告名称" min-width="150" />
        <el-table-column prop="env" label="环境" width="100" />
        <el-table-column prop="total" label="用例数" width="100" />
        <el-table-column prop="passed" label="通过" width="80">
          <template #default="{ row }">
            <span style="color: #67c23a;">{{ row.passed }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="failed" label="失败" width="80">
          <template #default="{ row }">
            <span style="color: #f56c6c;">{{ row.failed }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="passRate" label="通过率" width="100">
          <template #default="{ row }">
            <el-tag :type="row.passRate >= 90 ? 'success' : row.passRate >= 70 ? 'warning' : 'danger'">
              {{ row.passRate }}%
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="duration" label="耗时" width="100" />
        <el-table-column prop="createTime" label="生成时间" width="180" />
        <el-table-column label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleView(row)">查看</el-button>
            <el-button type="success" size="small" @click="handleDownload(row)">下载</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { ElMessage } from 'element-plus'
import {
  Document,
  SuccessFilled,
  CircleCloseFilled,
  Refresh
} from '@element-plus/icons-vue'

const summary = reactive({
  total: 126,
  passed: 118,
  failed: 8,
  get passRate() {
    return this.total > 0 ? Math.round((this.passed / this.total) * 100) : 0
  }
})

const passRateColor = computed(() => {
  if (summary.passRate >= 90) return '#67c23a'
  if (summary.passRate >= 70) return '#e6a23c'
  return '#f56c6c'
})

const trends = ref([
  { date: '2026-04-23', rate: 94 },
  { date: '2026-04-22', rate: 89 },
  { date: '2026-04-21', rate: 96 },
  { date: '2026-04-20', rate: 78 },
  { date: '2026-04-19', rate: 92 }
])

const reports = ref([
  {
    id: 'RPT001',
    name: '日常回归测试',
    env: '测试环境',
    total: 50,
    passed: 48,
    failed: 2,
    passRate: 96,
    duration: '5分32秒',
    createTime: '2026-04-23 21:50:00'
  },
  {
    id: 'RPT002',
    name: '登录模块测试',
    env: '测试环境',
    total: 15,
    passed: 15,
    failed: 0,
    passRate: 100,
    duration: '1分12秒',
    createTime: '2026-04-23 20:30:00'
  },
  {
    id: 'RPT003',
    name: '订单流程测试',
    env: '预发环境',
    total: 30,
    passed: 27,
    failed: 3,
    passRate: 90,
    duration: '3分45秒',
    createTime: '2026-04-23 18:00:00'
  }
])

function reactive(target) {
  return ref(target)
}

const handleGenerate = () => {
  ElMessage.success('报告生成中...')
}

const handleView = (row) => {
  ElMessage.info('查看报告功能开发中')
}

const handleDownload = (row) => {
  ElMessage.success('报告下载中...')
}
</script>

<style scoped>
.reports {
  padding: 20px;
}

.summary-card,
.chart-card,
.table-card {
  border-radius: 12px;
}

.summary-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.summary-icon {
  width: 56px;
  height: 56px;
  border-radius: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  color: white;
}

.summary-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.summary-label {
  font-size: 14px;
  color: #909399;
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

.pie-chart {
  display: flex;
  justify-content: center;
  align-items: center;
  height: 200px;
}

.rate-text {
  display: block;
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.rate-label {
  display: block;
  font-size: 14px;
  color: #909399;
}

.trend-list {
  display: flex;
  flex-direction: column;
  gap: 16px;
}

.trend-item {
  display: flex;
  align-items: center;
  gap: 16px;
}

.trend-date {
  width: 100px;
  font-size: 14px;
  color: #606266;
}
</style>