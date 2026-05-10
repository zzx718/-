<template>
  <div class="log-search">
    <div class="page-header">
      <div class="card-header">
        <h2>日志查询</h2>
      </div>
    </div>

    <div class="content-section">
      <div class="search-panel">
        <div class="search-row">
          <div class="form-group">
            <label>服务器</label>
            <select v-model="searchForm.server_id" class="form-select" @change="searchLogs">
              <option :value="null">-- 所有服务器 --</option>
              <option v-for="server in servers" :key="server.id" :value="server.id">
                {{ server.server_name }} ({{ server.ip_address }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>日志类型</label>
            <select v-model="searchForm.log_type" class="form-select" @change="searchLogs">
              <option value="">-- 全部 --</option>
              <option value="container">容器日志</option>
              <option value="application">应用日志</option>
              <option value="system">系统日志</option>
            </select>
          </div>

          <div class="form-group">
            <label>日志级别</label>
            <div class="level-checkboxes">
              <label v-for="level in ['debug', 'info', 'warning', 'error', 'critical']" :key="level">
                <input type="checkbox" v-model="searchForm.log_levels" :value="level" @change="searchLogs" />
                {{ level.toUpperCase() }}
              </label>
            </div>
          </div>
        </div>

        <div class="search-row">
          <div class="form-group">
            <label>关键词</label>
            <input type="text" v-model="searchForm.keyword" class="form-input" placeholder="搜索关键词..." @keyup.enter="searchLogs" />
          </div>

          <div class="form-group">
            <label>时间范围</label>
            <div class="time-range">
              <input type="datetime-local" v-model="searchForm.start_time" class="form-input" @change="searchLogs" />
              <span>-</span>
              <input type="datetime-local" v-model="searchForm.end_time" class="form-input" @change="searchLogs" />
            </div>
          </div>
        </div>

        <div class="search-actions">
          <button class="btn btn-primary" @click="searchLogs">搜索</button>
          <button class="btn" @click="resetSearch">重置</button>
          <button class="btn" @click="loadStats">刷新统计</button>
        </div>
      </div>

      <div v-if="stats.total > 0" class="stats-panel">
        <div class="stat-item">
          <span class="stat-label">总日志数</span>
          <span class="stat-value">{{ stats.total }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">ERROR</span>
          <span class="stat-value error">{{ stats.by_level?.ERROR || stats.by_level?.error || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">WARNING</span>
          <span class="stat-value warning">{{ stats.by_level?.WARNING || stats.by_level?.warning || 0 }}</span>
        </div>
        <div class="stat-item">
          <span class="stat-label">INFO</span>
          <span class="stat-value info">{{ stats.by_level?.INFO || stats.by_level?.info || 0 }}</span>
        </div>
      </div>

      <div class="logs-container">
        <div class="logs-header">
          <span>共 {{ logsTotal }} 条结果</span>
        </div>
        <div class="logs-list">
          <div v-for="log in logs" :key="log.id" class="log-item">
            <div class="log-meta">
              <span class="log-time">{{ formatDate(log['@timestamp']) }}</span>
              <span class="log-level" :class="log.log_level">{{ log.log_level?.toUpperCase() || 'INFO' }}</span>
              <span v-if="log.server_id" class="log-tag server-tag">{{ getServerName(log.server_id) }}</span>
              <span v-if="log.log_type" class="log-tag type-tag">{{ getLogTypeName(log.log_type) }}</span>
              <span v-if="log.container_name" class="log-tag">{{ log.container_name }}</span>
              <span v-if="log.service_name" class="log-tag">{{ log.service_name }}</span>
            </div>
            <div class="log-message">{{ log.message }}</div>
          </div>
          <div v-if="logs.length === 0" class="empty-text">暂无日志数据</div>
        </div>

        <div class="pagination" v-if="logsTotal > 0">
          <button class="btn btn-outline" :disabled="page <= 1" @click="changePage(-1)">上一页</button>
          <span class="page-info">第 {{ page }} 页 / 共 {{ Math.ceil(logsTotal / pageSize) }} 页</span>
          <button class="btn btn-outline" :disabled="logs.length < pageSize" @click="changePage(1)">下一页</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { logApi, serverApi } from '../api/index.js'

const servers = ref([])
const logs = ref([])
const logsTotal = ref(0)
const stats = ref({ total: 0, by_level: {}, by_hour: [] })
const page = ref(1)
const pageSize = ref(50)

const searchForm = ref({
  server_id: null,
  log_type: '',
  log_levels: [],
  keyword: '',
  start_time: '',
  end_time: ''
})

onMounted(() => {
  loadServers()
  loadStats()
  searchLogs()
})

const loadServers = async () => {
  try {
    const res = await serverApi.getServers()
    servers.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

const searchLogs = async () => {
  try {
    const params = {
      page: page.value,
      page_size: pageSize.value
    }
    
    if (searchForm.value.server_id) params.server_id = searchForm.value.server_id
    if (searchForm.value.log_type) params.log_type = searchForm.value.log_type
    if (searchForm.value.keyword) params.keyword = searchForm.value.keyword
    if (searchForm.value.start_time) params.start_time = searchForm.value.start_time
    if (searchForm.value.end_time) params.end_time = searchForm.value.end_time
    if (searchForm.value.log_levels?.length) params.log_levels = searchForm.value.log_levels
    
    const res = await logApi.searchLogs(params)
    logs.value = res.data?.logs || []
    logsTotal.value = res.data?.total || 0
  } catch (e) {
    console.error(e)
  }
}

const loadStats = async () => {
  try {
    const params = {}
    if (searchForm.value.server_id) params.server_id = searchForm.value.server_id
    const res = await logApi.getLogStats(params)
    stats.value = res.data || { total: 0, by_level: {}, by_hour: [] }
  } catch (e) {
    console.error(e)
  }
}

const resetSearch = () => {
  searchForm.value = {
    server_id: null,
    log_type: '',
    log_levels: [],
    keyword: '',
    start_time: '',
    end_time: ''
  }
  page.value = 1
  searchLogs()
}

const changePage = (delta) => {
  page.value += delta
  searchLogs()
}

const formatDate = (str) => {
  if (!str) return '-'
  return new Date(str).toLocaleString()
}

const getServerName = (serverId) => {
  const server = servers.value.find(s => s.id === serverId)
  return server ? `${server.server_name} (${server.ip_address})` : `服务器 ${serverId}`
}

const getLogTypeName = (type) => {
  const map = {
    'system': '系统日志',
    'container': '容器日志',
    'application': '应用日志'
  }
  return map[type] || type
}
</script>

<style scoped>
.log-search { padding: 20px; }
.page-header {
  background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.card-header h2 { margin: 0; color: #303133; }

.content-section {
  background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.search-panel {
  border-bottom: 1px solid #ebeef5; padding-bottom: 20px; margin-bottom: 20px;
}
.search-row {
  display: flex; gap: 20px; margin-bottom: 15px; flex-wrap: wrap;
}
.form-group { flex: 1; min-width: 200px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: 500; color: #606266; }
.form-select, .form-input { width: 100%; padding: 8px; border: 1px solid #dcdfe6; border-radius: 4px; }

.level-checkboxes { display: flex; gap: 15px; }
.level-checkboxes label { display: flex; align-items: center; gap: 5px; cursor: pointer; }

.time-range { display: flex; gap: 10px; align-items: center; }

.search-actions { display: flex; gap: 10px; margin-top: 10px; }

.btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; }
.btn-primary { background: #409eff; color: white; }

.stats-panel {
  display: flex; gap: 30px; padding: 15px; background: #f5f7fa; border-radius: 8px; margin-bottom: 20px;
}
.stat-item { text-align: center; }
.stat-label { display: block; font-size: 12px; color: #909399; }
.stat-value { display: block; font-size: 24px; font-weight: bold; color: #303133; }
.stat-value.error { color: #f56c6c; }
.stat-value.warning { color: #e6a23c; }
.stat-value.info { color: #409eff; }

.logs-container { margin-top: 20px; }
.logs-header {
  padding: 10px 0; border-bottom: 1px solid #ebeef5; color: #909399;
}

.logs-list { margin-top: 15px; }
.log-item {
  padding: 12px; border-bottom: 1px solid #f5f7fa; border-radius: 4px;
}
.log-item:hover { background: #f9fafc; }
.log-meta { display: flex; gap: 10px; margin-bottom: 5px; align-items: center;
}
.log-time { color: #909399; font-size: 12px; }
.log-level {
  padding: 2px 6px; border-radius: 3px; font-size: 11px; font-weight: bold;
}
.log-level.DEBUG { background: #f0f9ff; color: #409eff; }
.log-level.INFO { background: #e1f3d8; color: #67c23a; }
.log-level.WARNING { background: #fdf6ec; color: #e6a23c; }
.log-level.ERROR { background: #fef0f0; color: #f56c6c; }
.log-level.CRITICAL { background: #fee2e2; color: #dc2626; }
.log-tag {
  padding: 2px 6px; background: #f4f4f5; color: #909399; border-radius: 3px; font-size: 11px;
}
  .server-tag {
    background-color: #e3f2fd !important;
    color: #0d47a1 !important;
    border: 1px solid #bbdefb;
  }
  .type-tag {
    background-color: #e8f5e9 !important;
    color: #2e7d32 !important;
    border: 1px solid #c8e6c9;
  }
.empty-text { text-align: center; color: #909399; padding: 40px; }

.pagination {
  display: flex;
  justify-content: center;
  align-items: center;
  gap: 15px;
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #ebeef5;
}

.page-info {
  font-size: 14px;
  color: #606266;
}

.btn-outline {
  background: white;
  border: 1px solid #dcdfe6;
  color: #606266;
  padding: 6px 15px;
  border-radius: 4px;
  cursor: pointer;
  transition: all 0.2s;
}

.btn-outline:hover:not(:disabled) {
  color: #409eff;
  border-color: #c6e2ff;
  background-color: #ecf5ff;
}

.btn-outline:disabled {
  color: #c0c4cc;
  cursor: not-allowed;
  background-image: none;
}
</style>
