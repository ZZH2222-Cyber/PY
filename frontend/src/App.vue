<script setup>
import MainHeader from './components/layout/MainHeader.vue'
import MainSidebar from './components/layout/MainSidebar.vue'
</script>

<template>
  <el-config-provider>
    <div class="app-container">
      <MainHeader />
      <div class="main-content">
        <MainSidebar class="sidebar" />
        <div class="content-wrapper">
          <router-view />
        </div>
      </div>
    </div>
  </el-config-provider>
</template>

<style>
* {
  margin: 0;
  padding: 0;
  box-sizing: border-box;
}

html, body, #app {
  height: 100%;
  font-family: 'Helvetica Neue', Helvetica, 'PingFang SC', 'Hiragino Sans GB', 'Microsoft YaHei', Arial, sans-serif;
}

.app-container {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.main-content {
  flex: 1;
  display: flex;
  overflow: hidden;
}

.sidebar {
  width: 220px;
  flex-shrink: 0;
  background: #f5f7fa;
  overflow-y: auto;
}

.content-wrapper {
  flex: 1;
  overflow-y: auto;
  background: #f0f2f5;
}
</style>