<template>
  <div class="audit-log">
    <div class="page-header">
      <div class="card-header">
        <h2>审计日志</h2>
        <el-button @click="fetchLogs(1)" :icon="Refresh">刷新</el-button>
      </div>
    </div>

    <div class="card">
      <el-table 
        v-loading="loading" 
        :data="logs" 
        style="width: 100%" 
        border
        stripe
      >
        <el-table-column prop="created_at" label="操作时间" width="180" />
        
        <el-table-column label="操作人" width="150">
          <template #default="scope">
            <el-tag v-if="scope.row.username_snapshot === 'SYSTEM'" type="info">系统</el-tag>
            <span v-else>{{ scope.row.username_snapshot }}</span>
          </template>
        </el-table-column>
        
        <el-table-column prop="client_ip" label="来源IP" width="140" />
        
        <el-table-column prop="action" label="动作类型" width="180">
          <template #default="scope">
            <el-tag :type="getActionType(scope.row.action)">
              {{ scope.row.action }}
            </el-tag>
          </template>
        </el-table-column>
        
        <el-table-column prop="target" label="操作对象" width="200" show-overflow-tooltip />
        <el-table-column prop="details" label="详细信息" show-overflow-tooltip />
      </el-table>

      <div class="pagination-container">
        <el-pagination
          v-if="total > 0"
          background
          layout="total, prev, pager, next"
          :current-page="currentPage"
          :page-size="pageSize"
          :total="total"
          @current-change="handlePageChange"
        />
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage } from 'element-plus'
import { Refresh } from '@element-plus/icons-vue'
import { useAuthStore } from '../stores/auth.js'
import axios from 'axios'

const authStore = useAuthStore()
const loading = ref(false)
const logs = ref([])
const total = ref(0)
const currentPage = ref(1)
const pageSize = ref(20)

// 获取动作对应的标签颜色
const getActionType = (action) => {
  if (action.includes('DELETE')) return 'danger'
  if (action.includes('UPDATE') || action.includes('EDIT')) return 'warning'
  if (action.includes('CREATE') || action.includes('ADD')) return 'success'
  return '' // default
}

const fetchLogs = async (page = 1) => {
  loading.value = true
  try {
    // 这里直接用axios调用新增的接口，也可以封装在api/index.js里
    const res = await axios.get('/api/audit-logs', {
      params: { page, per_page: pageSize.value },
      headers: { Authorization: `Bearer ${authStore.token}` }
    })
    
    if (res.data.code === 0) {
      logs.value = res.data.data.list
      total.value = res.data.data.total
      currentPage.value = res.data.data.current_page
    } else {
      ElMessage.error(res.data.msg || '获取日志失败')
    }
  } catch (error) {
    console.error('Fetch logs error:', error)
    ElMessage.error('无法连接到服务器')
  } finally {
    loading.value = false
  }
}

const handlePageChange = (page) => {
  fetchLogs(page)
}

onMounted(() => {
  fetchLogs()
})
</script>

<style scoped>
.audit-log {
  width: 100%;
}

.page-header {
  margin-bottom: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  font-size: 24px;
  color: #333;
}

.card {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 12px 0 rgba(0, 0, 0, 0.1);
  padding: 20px;
  overflow: hidden;
}

.pagination-container {
  margin-top: 20px;
  display: flex;
  justify-content: flex-end;
}
</style>