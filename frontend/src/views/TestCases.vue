<template>
  <div class="test-cases">
    <el-card class="filter-card">
      <el-form :inline="true" :model="filterForm">
        <el-form-item label="用例名称">
          <el-input v-model="filterForm.name" placeholder="请输入用例名称" clearable />
        </el-form-item>
        <el-form-item label="模块">
          <el-select v-model="filterForm.module" placeholder="请选择模块" clearable>
            <el-option label="登录模块" value="login" />
            <el-option label="用户模块" value="user" />
            <el-option label="订单模块" value="order" />
            <el-option label="支付模块" value="payment" />
          </el-select>
        </el-form-item>
        <el-form-item label="优先级">
          <el-select v-model="filterForm.priority" placeholder="请选择优先级" clearable>
            <el-option label="高" value="high" />
            <el-option label="中" value="medium" />
            <el-option label="低" value="low" />
          </el-select>
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleSearch">搜索</el-button>
          <el-button @click="handleReset">重置</el-button>
        </el-form-item>
      </el-form>
    </el-card>

    <el-card class="table-card">
      <template #header>
        <div class="card-header">
          <span>测试用例列表</span>
          <div class="header-actions">
            <el-button type="success" @click="handleImport">
              <el-icon><Upload /></el-icon>导入
            </el-button>
            <el-button type="warning" @click="handleExport">
              <el-icon><Download /></el-icon>导出
            </el-button>
            <el-button type="primary" @click="handleAdd">
              <el-icon><Plus /></el-icon>新增用例
            </el-button>
          </div>
        </div>
      </template>

      <el-table :data="testCases" stripe style="width: 100%">
        <el-table-column prop="id" label="用例ID" width="100" />
        <el-table-column prop="name" label="用例名称" min-width="150" />
        <el-table-column prop="module" label="模块" width="100">
          <template #default="{ row }">
            <el-tag>{{ getModuleName(row.module) }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="method" label="请求方法" width="100">
          <template #default="{ row }">
            <el-tag :type="getMethodType(row.method)">{{ row.method }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="path" label="接口路径" min-width="150" />
        <el-table-column prop="priority" label="优先级" width="80">
          <template #default="{ row }">
            <el-tag :type="getPriorityType(row.priority)">{{ row.priority }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="enabled" label="状态" width="80">
          <template #default="{ row }">
            <el-switch v-model="row.enabled" @change="handleToggle(row)" />
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" size="small" @click="handleEdit(row)">编辑</el-button>
            <el-button type="danger" size="small" @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>

      <el-pagination
        v-model:current-page="pagination.page"
        v-model:page-size="pagination.size"
        :total="pagination.total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        style="margin-top: 20px; justify-content: flex-end;"
      />
    </el-card>

    <el-dialog
      v-model="dialogVisible"
      :title="dialogTitle"
      width="700px"
      :close-on-click-modal="false"
    >
      <el-form :model="caseForm" :rules="caseRules" ref="caseFormRef" label-width="100px">
        <el-form-item label="用例名称" prop="name">
          <el-input v-model="caseForm.name" placeholder="请输入用例名称" />
        </el-form-item>
        <el-form-item label="所属模块" prop="module">
          <el-select v-model="caseForm.module" placeholder="请选择模块">
            <el-option label="登录模块" value="login" />
            <el-option label="用户模块" value="user" />
            <el-option label="订单模块" value="order" />
            <el-option label="支付模块" value="payment" />
          </el-select>
        </el-form-item>
        <el-form-item label="请求方法" prop="method">
          <el-select v-model="caseForm.method" placeholder="请选择请求方法">
            <el-option label="GET" value="GET" />
            <el-option label="POST" value="POST" />
            <el-option label="PUT" value="PUT" />
            <el-option label="DELETE" value="DELETE" />
          </el-select>
        </el-form-item>
        <el-form-item label="接口路径" prop="path">
          <el-input v-model="caseForm.path" placeholder="请输入接口路径，如 /api/login" />
        </el-form-item>
        <el-form-item label="请求参数" prop="params">
          <el-input
            v-model="caseForm.params"
            type="textarea"
            :rows="3"
            placeholder="请输入请求参数（JSON格式）"
          />
        </el-form-item>
        <el-form-item label="请求头" prop="headers">
          <el-input
            v-model="caseForm.headers"
            type="textarea"
            :rows="2"
            placeholder="请输入请求头（JSON格式）"
          />
        </el-form-item>
        <el-form-item label="优先级" prop="priority">
          <el-radio-group v-model="caseForm.priority">
            <el-radio label="high">高</el-radio>
            <el-radio label="medium">中</el-radio>
            <el-radio label="low">低</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="预期状态码" prop="expectedStatus">
          <el-input-number v-model="caseForm.expectedStatus" :min="100" :max="599" />
        </el-form-item>
        <el-form-item label="断言字段" prop="assertField">
          <el-input v-model="caseForm.assertField" placeholder="请输入断言字段" />
        </el-form-item>
        <el-form-item label="预期值" prop="assertValue">
          <el-input v-model="caseForm.assertValue" placeholder="请输入预期值" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Plus, Upload, Download } from '@element-plus/icons-vue'

const filterForm = reactive({
  name: '',
  module: '',
  priority: ''
})

const pagination = reactive({
  page: 1,
  size: 10,
  total: 0
})

const testCases = ref([
  {
    id: 'TC001',
    name: '用户登录-正常登录',
    module: 'login',
    method: 'POST',
    path: '/api/login',
    params: '{"username":"admin","password":"123456"}',
    headers: '{}',
    priority: 'high',
    expectedStatus: 200,
    assertField: 'code',
    assertValue: '0',
    enabled: true
  },
  {
    id: 'TC002',
    name: '获取用户列表',
    module: 'user',
    method: 'GET',
    path: '/api/users',
    params: '{"page":1,"size":10}',
    headers: '{"Authorization":"Bearer ${token}"}',
    priority: 'medium',
    expectedStatus: 200,
    assertField: 'data',
    assertValue: '[]',
    enabled: true
  },
  {
    id: 'TC003',
    name: '创建订单',
    module: 'order',
    method: 'POST',
    path: '/api/orders',
    params: '{"product_id":1,"quantity":2}',
    headers: '{}',
    priority: 'high',
    expectedStatus: 201,
    assertField: 'order_id',
    assertValue: '',
    enabled: true
  }
])

pagination.total = testCases.value.length

const dialogVisible = ref(false)
const dialogTitle = ref('新增用例')
const caseFormRef = ref(null)

const caseForm = reactive({
  id: '',
  name: '',
  module: '',
  method: 'GET',
  path: '',
  params: '',
  headers: '',
  priority: 'medium',
  expectedStatus: 200,
  assertField: '',
  assertValue: ''
})

const caseRules = {
  name: [{ required: true, message: '请输入用例名称', trigger: 'blur' }],
  module: [{ required: true, message: '请选择模块', trigger: 'change' }],
  method: [{ required: true, message: '请选择请求方法', trigger: 'change' }],
  path: [{ required: true, message: '请输入接口路径', trigger: 'blur' }]
}

const getModuleName = (module) => {
  const map = { login: '登录', user: '用户', order: '订单', payment: '支付' }
  return map[module] || module
}

const getMethodType = (method) => {
  const map = { GET: 'success', POST: 'warning', PUT: 'primary', DELETE: 'danger' }
  return map[method] || 'info'
}

const getPriorityType = (priority) => {
  const map = { high: 'danger', medium: 'warning', low: 'info' }
  return map[priority] || 'info'
}

const handleSearch = () => {
  ElMessage.success('搜索功能已触发')
}

const handleReset = () => {
  filterForm.name = ''
  filterForm.module = ''
  filterForm.priority = ''
  ElMessage.info('已重置筛选条件')
}

const handleAdd = () => {
  dialogTitle.value = '新增用例'
  Object.keys(caseForm).forEach(key => {
    if (key !== 'method' && key !== 'priority' && key !== 'expectedStatus') {
      caseForm[key] = ''
    }
  })
  dialogVisible.value = true
}

const handleEdit = (row) => {
  dialogTitle.value = '编辑用例'
  Object.assign(caseForm, row)
  dialogVisible.value = true
}

const handleDelete = async (row) => {
  try {
    await ElMessageBox.confirm('确定要删除该用例吗？', '提示', {
      type: 'warning'
    })
    ElMessage.success('删除成功')
  } catch {
    ElMessage.info('已取消删除')
  }
}

const handleSave = async () => {
  if (!caseFormRef.value) return
  await caseFormRef.value.validate((valid) => {
    if (valid) {
      ElMessage.success(dialogTitle.value === '新增用例' ? '添加成功' : '保存成功')
      dialogVisible.value = false
    }
  })
}

const handleToggle = (row) => {
  ElMessage.success(`用例 "${row.name}" 已${row.enabled ? '启用' : '禁用'}`)
}

const handleImport = () => {
  ElMessage.info('导入功能开发中')
}

const handleExport = () => {
  ElMessage.info('导出功能开发中')
}
</script>

<style scoped>
.test-cases {
  padding: 20px;
}

.filter-card {
  margin-bottom: 20px;
}

.table-card {
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
</style>