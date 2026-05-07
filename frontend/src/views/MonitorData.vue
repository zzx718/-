<template>
  <div class="monitor-data">
    <div class="page-header">
      <div class="card-header">
        <h2>监控数据</h2>
        <div class="header-actions">
          <select v-model="selectedServerId" class="server-select">
            <option value="">所有服务器</option>
            <option
              v-for="server in servers"
              :key="server.id"
              :value="server.id"
            >
              {{ server.server_name }} ({{ server.ip_address }})
            </option>
          </select>
          <button class="btn btn-primary" @click="refreshData" :disabled="loading">
            {{ loading ? '刷新中...' : '刷新' }}
          </button>
        </div>
      </div>
    </div>

    <!-- 历史趋势图表 -->
    <div v-if="selectedServerId" class="chart-section card" style="background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);">
      <div class="card-header" style="margin-bottom: 10px;">
        <h3 style="margin: 0; color: #303133;">历史趋势分析</h3>
        <div style="display: flex; gap: 10px; align-items: center;">
          <select v-model="historyHours" class="server-select" style="min-width: 120px;" @change="loadHistoryData">
            <option :value="0.16">最近 10 分钟</option>
            <option :value="1">最近 1 小时</option>
            <option :value="24">最近 24 小时</option>
          </select>
          <div v-if="historyLoading" style="font-size: 14px; color: #999;">加载中...</div>
        </div>
      </div>
      <div class="chart-container-wrapper">
        <div class="chart-container" ref="chartRef" style="height: 300px; width: 100%;"></div>
      </div>
    </div>

    <!-- 监控数据列表 -->
    <div class="monitor-list">
      <div v-if="loading" class="loading">加载中...</div>
      <div v-else-if="monitorData.length === 0" class="empty">暂无监控数据</div>
      <div v-else class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>服务器</th>
              <th>IP地址</th>
              <th>CPU使用率</th>
              <th>内存使用率</th>
              <th>磁盘使用率</th>
              <th>记录时间</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in monitorData" :key="item.id">
              <td>{{ item.server_name }}</td>
              <td>{{ item.ip_address }}</td>
              <td>
                <span :class="getCpuClass(item.cpu_value)">
                  {{ formatValue(item.cpu_value) }}%
                </span>
              </td>
              <td>
                <span :class="getMemoryClass(item.memory_value)">
                  {{ formatValue(item.memory_value) }}%
                </span>
              </td>
              <td>
                <span :class="getDiskClass(item.disk_value)">
                  {{ formatValue(item.disk_value) }}%
                </span>
              </td>
              <td>{{ formatDate(item.recorded_at) }}</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 告警阈值说明 -->
    <div class="threshold-info">
      <h3>告警阈值说明</h3>
      <div class="threshold-grid">
        <div class="threshold-item">
          <span class="threshold-label normal">正常</span>
          <span class="threshold-desc">CPU &lt; 70%, 内存 &lt; 80%, 磁盘 &lt; 85%</span>
        </div>
        <div class="threshold-item">
          <span class="threshold-label warning">警告</span>
          <span class="threshold-desc">CPU 70-85%, 内存 80-90%, 磁盘 85-95%</span>
        </div>
        <div class="threshold-item">
          <span class="threshold-label critical">严重</span>
          <span class="threshold-desc">CPU &gt; 85%, 内存 &gt; 90%, 磁盘 &gt; 95%</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch, nextTick, onUnmounted } from 'vue'
import * as echarts from 'echarts'
// 移除Element Plus依赖，使用原生JavaScript
import { monitorApi, serverApi } from '@/api'

// 响应式数据
const loading = ref(false)
const monitorData = ref([])
const servers = ref([])
const selectedServerId = ref('')
const historyHours = ref(0.16) // 默认改成展示最近10分钟
const chartRef = ref(null)
const historyLoading = ref(false)
let chartInstance = null
let autoRefreshTimer = null

// 计算属性
const filteredData = computed(() => {
  if (!selectedServerId.value) {
    return monitorData.value
  }
  return monitorData.value.filter(item => item.server_id === parseInt(selectedServerId.value))
})

// 监听器
watch(selectedServerId, async (val) => {
  loadMonitorData()
  if (val) {
    // 等待DOM更新（因为v-if）
    await nextTick()
    loadHistoryData()
  } else {
    if (chartInstance) {
      chartInstance.dispose()
      chartInstance = null
    }
  }
})

// 生命周期
onMounted(() => {
  loadServers()
  loadMonitorData()
  window.addEventListener('resize', handleResize)
  // 添加自动刷新(5秒1次) 解决图表不同步的问题
  autoRefreshTimer = setInterval(() => {
    refreshData()
  }, 5000)
})

onUnmounted(() => {
  if (chartInstance) {
    chartInstance.dispose()
  }
  if (autoRefreshTimer) {
    clearInterval(autoRefreshTimer)
  }
  window.removeEventListener('resize', handleResize)
})

const handleResize = () => {
  chartInstance && chartInstance.resize()
}

// 方法
const loadServers = async () => {
  try {
    const response = await serverApi.getServers()
    if (response.code === 0) {
      servers.value = response.data || []
    }
  } catch (error) {
    console.error('加载服务器列表失败:', error)
  }
}

const loadMonitorData = async () => {
  try {
    loading.value = true
    const params = selectedServerId.value ? { server_id: parseInt(selectedServerId.value) } : undefined
    const response = await monitorApi.getMonitorData(params)
    if (response.code === 0) {
      monitorData.value = response.data || []
    } else {
      alert('加载监控数据失败: ' + (response.msg || ''))
    }
  } catch (error) {
    console.error('加载监控数据失败:', error)
    alert('加载监控数据失败')
  } finally {
    loading.value = false
  }
}

const refreshData = () => {
  loadMonitorData()
  if (selectedServerId.value) {
    loadHistoryData()
  }
}

const formatValue = (value) => {
  if (value === null || value === undefined) return '--'
  return parseFloat(value).toFixed(1)
}

const formatDate = (dateStr) => {
  if (!dateStr) return ''
  return new Date(dateStr).toLocaleString()
}

const getCpuClass = (value) => {
  const num = parseFloat(value)
  if (num >= 85) return 'critical'
  if (num >= 70) return 'warning'
  return 'normal'
}

const getMemoryClass = (value) => {
  const num = parseFloat(value)
  if (num >= 90) return 'critical'
  if (num >= 80) return 'warning'
  return 'normal'
}

const getDiskClass = (value) => {
  const num = parseFloat(value)
  if (num >= 95) return 'critical'
  if (num >= 85) return 'warning'
  return 'normal'
}

// 历史趋势图表相关方法
const loadHistoryData = async () => {
  if (!selectedServerId.value) return 

  try {
    historyLoading.value = true
    // 请求历史数据
    const res = await monitorApi.getMonitorData({ 
        server_id: parseInt(selectedServerId.value),
        mode: 'history',
        hours: historyHours.value 
    })
    
    if (res.code === 0) {
      if (res.data && res.data.length > 0) {
          initChart(res.data)
      }
    }
  } catch (err) {
    console.error('获取历史趋势失败', err)
  } finally {
    historyLoading.value = false
  }
}

const initChart = (data) => {
    if (!chartRef.value) return

    if (!chartInstance) {
        chartInstance = echarts.init(chartRef.value)
    }
    
    // 数据处理
    const times = data.map(item => new Date(item.recorded_at).toLocaleTimeString())
    const cpuData = data.map(item => item.cpu_value)
    const memData = data.map(item => item.memory_value)
    const diskData = data.map(item => item.disk_value)

    const option = {
        title: { text: '' },
        tooltip: { trigger: 'axis' },
        legend: { data: ['CPU', '内存', '磁盘'], bottom: 0 },
        grid: { left: '3%', right: '4%', bottom: '10%', top: '3%', containLabel: true },
        xAxis: { type: 'category', boundaryGap: false, data: times },
        yAxis: { type: 'value', max: 100 },
        series: [
            { name: 'CPU', type: 'line', data: cpuData, showSymbol: false, smooth: true, itemStyle: { color: '#ff4d4f' } },
            { name: '内存', type: 'line', data: memData, showSymbol: false, smooth: true, itemStyle: { color: '#1890ff' } },
            { name: '磁盘', type: 'line', data: diskData, showSymbol: false, smooth: true, itemStyle: { color: '#52c41a' } }
        ]
    }
    
    chartInstance.setOption(option)
}
</script>

<style scoped>
.monitor-data {
  padding: 20px;
}

.page-header {
  background: white;
  padding: 20px;
  border-radius: 8px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-header h2 {
  margin: 0;
  color: #303133;
}

.header-actions {
  display: flex;
  align-items: center;
  gap: 10px;
}

.server-select {
  padding: 8px 12px;
  border: 1px solid #dcdfe6;
  border-radius: 4px;
  font-size: 14px;
  min-width: 200px;
}

.monitor-list {
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
  overflow: hidden;
  margin-bottom: 20px;
}

.loading, .empty {
  padding: 40px;
  text-align: center;
  color: #909399;
}

.table-container {
  overflow-x: auto;
}

.data-table {
  width: 100%;
  border-collapse: collapse;
}

.data-table th,
.data-table td {
  padding: 12px;
  text-align: left;
  border-bottom: 1px solid #ebeef5;
}

.data-table th {
  background: #f5f7fa;
  font-weight: 500;
  color: #909399;
}

.data-table tr:hover {
  background: #f5f7fa;
}

.normal {
  color: #67c23a;
  font-weight: 500;
}

.warning {
  color: #e6a23c;
  font-weight: 500;
}

.critical {
  color: #f56c6c;
  font-weight: 500;
}

.btn {
  padding: 8px 16px;
  border: none;
  border-radius: 4px;
  cursor: pointer;
  font-size: 14px;
  transition: all 0.3s;
}

.btn-primary {
  background: #409eff;
  color: white;
}

.btn-primary:hover:not(:disabled) {
  background: #66b1ff;
}

.btn-primary:disabled {
  background: #c0c4cc;
  cursor: not-allowed;
}

.threshold-info {
  background: white;
  padding: 20px;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.threshold-info h3 {
  margin: 0 0 15px 0;
  color: #606266;
}

.threshold-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 15px;
}

.threshold-item {
  display: flex;
  align-items: center;
  gap: 10px;
}

.threshold-label {
  padding: 4px 8px;
  border-radius: 4px;
  font-size: 12px;
  font-weight: 500;
  min-width: 50px;
  text-align: center;
}

.threshold-label.normal {
  background: #f0f9ff;
  color: #67c23a;
}

.threshold-label.warning {
  background: #fdf6ec;
  color: #e6a23c;
}

.threshold-label.critical {
  background: #fef0f0;
  color: #f56c6c;
}

.threshold-desc {
  color: #606266;
  font-size: 14px;
}
</style>