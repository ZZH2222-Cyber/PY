<template>
  <el-menu
    :default-active="activeIndex"
    class="main-sidebar"
    @select="handleSelect"
    :collapse="isCollapse"
  >
    <el-menu-item index="/">
      <el-icon><HomeFilled /></el-icon>
      <template #title>首页仪表盘</template>
    </el-menu-item>

    <el-menu-item index="/test-cases">
      <el-icon><Document /></el-icon>
      <template #title>测试用例</template>
    </el-menu-item>

    <el-menu-item index="/run-tests">
      <el-icon><VideoPlay /></el-icon>
      <template #title>运行测试</template>
    </el-menu-item>

    <el-menu-item index="/reports">
      <el-icon><DataLine /></el-icon>
      <template #title>测试报告</template>
    </el-menu-item>

    <el-sub-menu index="ai">
      <template #title>
        <el-icon><Cpu /></el-icon>
        <span>AI 智能测试</span>
      </template>
      <el-menu-item index="/ai-generation">AI 用例生成</el-menu-item>
      <el-menu-item index="/security-testing">安全测试</el-menu-item>
    </el-sub-menu>

    <el-menu-item index="/settings">
      <el-icon><Setting /></el-icon>
      <template #title>系统设置</template>
    </el-menu-item>
  </el-menu>
</template>

<script setup>
import { ref, computed, watch } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import {
  HomeFilled,
  Document,
  VideoPlay,
  DataLine,
  Cpu,
  Setting
} from '@element-plus/icons-vue'

const router = useRouter()
const route = useRoute()
const isCollapse = ref(false)

const activeIndex = computed(() => route.path)

const handleSelect = (index) => {
  router.push(index)
}

watch(() => route.path, () => {
})
</script>

<style scoped>
.main-sidebar {
  height: 100%;
  border-right: none;
  background: #f5f7fa;
}

.main-sidebar:not(.el-menu--collapse) {
  width: 220px;
}
</style>