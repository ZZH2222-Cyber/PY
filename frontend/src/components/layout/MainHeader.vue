<template>
  <div class="main-header">
    <div class="header-left">
      <el-icon class="logo-icon" :size="24"><Monitor /></el-icon>
      <h1 class="title">API 自动化测试平台</h1>
    </div>
    <div class="header-right">
      <el-badge :value="notificationCount" :hidden="notificationCount === 0" class="notification-badge">
        <el-icon :size="20"><Bell /></el-icon>
      </el-badge>
      <el-dropdown @command="handleCommand">
        <span class="user-info">
          <el-avatar :size="32" icon="UserFilled" />
          <span class="username">{{ username }}</span>
        </span>
        <template #dropdown>
          <el-dropdown-menu>
            <el-dropdown-item command="settings">
              <el-icon><Setting /></el-icon>设置
            </el-dropdown-item>
            <el-dropdown-item command="logout" divided>
              <el-icon><SwitchButton /></el-icon>退出登录
            </el-dropdown-item>
          </el-dropdown-menu>
        </template>
      </el-dropdown>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { Monitor, Bell, Setting, SwitchButton } from '@element-plus/icons-vue'
import { store } from '../../stores'

const router = useRouter()
const notificationCount = ref(0)
const username = computed(() => store.user?.username || 'Admin')

const handleCommand = (command) => {
  if (command === 'logout') {
    store.clearStore()
    router.push('/login')
  } else if (command === 'settings') {
    router.push('/settings')
  }
}
</script>

<style scoped>
.main-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  height: 60px;
  padding: 0 24px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.header-left {
  display: flex;
  align-items: center;
  gap: 12px;
}

.logo-icon {
  color: white;
}

.title {
  font-size: 20px;
  font-weight: 600;
  margin: 0;
}

.header-right {
  display: flex;
  align-items: center;
  gap: 20px;
}

.notification-badge {
  cursor: pointer;
}

.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 8px;
  transition: background 0.3s;
}

.user-info:hover {
  background: rgba(255, 255, 255, 0.2);
}

.username {
  font-size: 14px;
}
</style>