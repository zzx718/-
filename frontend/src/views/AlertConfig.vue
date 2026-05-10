<template>
  <div class="alert-config">
    <div class="page-header">
      <div class="card-header">
        <h2>告警配置与历史</h2>
        <div class="tabs">
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'rules' }"
            @click="activeTab = 'rules'"
          >
            告警规则
          </button>
          <button 
            class="tab-btn" 
            :class="{ active: activeTab === 'history' }"
            @click="activeTab = 'history'"
          >
            告警历史
          </button>
        </div>
      </div>
    </div>

    <!-- 告警规则列表 -->
    <div v-if="activeTab === 'rules'" class="content-section">
      <div class="action-bar">
        <select v-model="filterServerId" class="filter-select" @change="loadRules">
          <option :value="null">-- 所有服务器 --</option>
          <option v-for="server in servers" :key="server.id" :value="server.id">
            {{ server.server_name }} ({{ server.ip_address }})
          </option>
        </select>
        <button class="btn btn-primary" @click="openAddDialog">添加规则</button>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>服务器</th>
              <th>指标类型</th>
              <th>触发阈值</th>
              <th>静默时间(分)</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="rule in rules" :key="rule.id">
              <td>{{ rule.server_name }}</td>
              <td>
                <span class="metric-tag" :class="rule.metric_type">{{ rule.metric_type.toUpperCase() }}</span>
              </td>
              <td>> {{ rule.threshold }}%</td>
              <td>{{ rule.silence_minutes }}</td>
              <td>
                <span class="status-tag" :class="rule.is_enabled ? 'enabled' : 'disabled'">
                  {{ rule.is_enabled ? '启用' : '禁用' }}
                </span>
              </td>
              <td>{{ formatDate(rule.created_at) }}</td>
              <td>
                <button class="btn btn-small" @click="editRule(rule)">编辑</button>
                <button class="btn btn-small btn-danger" @click="deleteRule(rule)">删除</button>
              </td>
            </tr>
            <tr v-if="rules.length === 0">
              <td colspan="7" class="empty-text">暂无告警规则，请添加</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <!-- 告警历史列表 -->
    <div v-if="activeTab === 'history'" class="content-section">
      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>时间</th>
              <th>服务器</th>
              <th>告警指标</th>
              <th>触发值 / 阈值</th>
              <th>状态</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in historyList" :key="item.id">
              <td>{{ formatDate(item.triggered_at) }}</td>
              <td>{{ item.server_name }}</td>
              <td>
                <span class="metric-tag" :class="item.metric_type">{{ item.metric_type.toUpperCase() }}</span>
              </td>
              <td>
                <span class="value-highlight">{{ item.current_value }}%</span>
                <span class="threshold-sub"> / {{ item.threshold_snapshot }}%</span>
              </td>
              <td>{{ item.status }}</td>
            </tr>
            <tr v-if="historyList.length === 0">
              <td colspan="5" class="empty-text">暂无告警记录</td>
            </tr>
          </tbody>
        </table>
      </div>
      <!-- 分页简易版 -->
      <div class="pagination" v-if="historyTotal > 0">
         <button :disabled="historyPage <= 1" @click="changeHistoryPage(-1)">上一页</button>
         <span>第 {{ historyPage }} 页</span>
         <button :disabled="historyList.length < 20" @click="changeHistoryPage(1)">下一页</button>
      </div>
    </div>

    <!-- 规则编辑弹窗 -->
    <div v-if="showDialog" class="dialog-overlay" @click="showDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>{{ editingRule ? '编辑规则' : '添加告警规则' }}</h3>
          <button class="close-btn" @click="showDialog = false">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-group" v-if="!editingRule">
            <label>服务器</label>
            <select v-model="ruleForm.server_id" class="form-select">
              <option v-for="server in servers" :key="server.id" :value="server.id">
                {{ server.server_name }} ({{ server.ip_address }})
              </option>
            </select>
          </div>
          
          <div class="form-group" v-if="!editingRule">
            <label>监控指标</label>
             <select v-model="ruleForm.metric_type" class="form-select">
              <option value="cpu">CPU使用率</option>
              <option value="memory">内存使用率</option>
              <option value="disk">磁盘使用率</option>
            </select>
          </div>

          <div class="form-group">
            <label>触发阈值 (%)</label>
            <input type="number" v-model="ruleForm.threshold" min="1" max="100" />
            <span class="hint">当指标持续超过此值时触发告警</span>
          </div>

          <div class="form-group">
            <label>静默时间 (分钟)</label>
            <input type="number" v-model="ruleForm.silence_minutes" min="1" />
            <span class="hint">告警发生后，在此时间内不再重复发送邮件</span>
          </div>

          <div class="form-group checkbox-group">
             <label>
               <input type="checkbox" v-model="ruleForm.is_enabled"> 启用此规则
             </label>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn" @click="showDialog = false">取消</button>
          <button class="btn btn-primary" @click="saveRule">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { alertApi, serverApi } from '../api/index.js'

const activeTab = ref('rules')
const rules = ref([])
const historyList = ref([])
const servers = ref([])
const filterServerId = ref(null)

const showDialog = ref(false)
const editingRule = ref(null)
const ruleForm = ref({
  server_id: null,
  metric_type: 'cpu',
  threshold: 80,
  silence_minutes: 60,
  is_enabled: true
})

const historyPage = ref(1)
const historyTotal = ref(0)

onMounted(() => {
  loadServers()
  loadRules()
})

// 监听Tab切换
watch(activeTab, (newTab) => {
  if (newTab === 'rules') {
    loadRules()
  } else {
    loadHistory()
  }
})

const loadServers = async () => {
  try {
    const res = await serverApi.getServers()
    servers.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

const loadRules = async () => {
  try {
    const params = {}
    if (filterServerId.value) params.server_id = filterServerId.value
    const res = await alertApi.getRules(params)
    rules.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

const loadHistory = async () => {
  try {
    const params = { page: historyPage.value, per_page: 20 }
    const res = await alertApi.getHistory(params)
    historyList.value = res.data.list || []
    historyTotal.value = res.data.total || 0
  } catch (e) {
    console.error(e)
  }
}

const changeHistoryPage = (delta) => {
  historyPage.value += delta
  loadHistory()
}

const openAddDialog = () => {
  editingRule.value = null
  ruleForm.value = {
    server_id: servers.value.length > 0 ? servers.value[0].id : null, 
    metric_type: 'cpu',
    threshold: 80,
    silence_minutes: 60,
    is_enabled: true
  }
  showDialog.value = true
}

const editRule = (rule) => {
  editingRule.value = rule
  ruleForm.value = { ...rule }
  showDialog.value = true
}

const saveRule = async () => {
  try {
    if (editingRule.value) {
      // Update
      await alertApi.updateRule(editingRule.value.id, ruleForm.value)
    } else {
      // Create
      await alertApi.createRule(ruleForm.value)
    }
    showDialog.value = false
    loadRules()
    alert('保存成功')
  } catch (error) {
    console.error(error)
    alert('保存失败')
  }
}

const deleteRule = async (rule) => {
  if(confirm('确定删除此规则吗？')) {
    try {
      await alertApi.deleteRule(rule.id)
      loadRules()
    } catch(e) {
      alert('删除失败')
    }
  }
}

const formatDate = (str) => {
  if(!str) return '-'
  return new Date(str).toLocaleString()
}
</script>

<style scoped>
.alert-config { padding: 20px; }
.page-header { 
  background: white; padding: 20px; border-radius: 8px; margin-bottom: 20px; 
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}
.card-header { display: flex; justify-content: space-between; align-items: center; }
.card-header h2 { margin: 0; color: #303133; }

.tabs { display: flex; gap: 10px; }
.tab-btn {
  padding: 8px 16px; border: 1px solid #dcdfe6; background: white;
  border-radius: 4px; cursor: pointer; transition: all 0.3s;
}
.tab-btn.active {
  background: #409eff; color: white; border-color: #409eff;
}

.content-section {
  background: white; padding: 20px; border-radius: 8px; box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.action-bar { margin-bottom: 20px; display: flex; gap: 10px; }
.filter-select { padding: 8px; border-radius: 4px; border: 1px solid #dcdfe6; }

.data-table { width: 100%; border-collapse: collapse; }
.data-table th, .data-table td { padding: 12px; text-align: left; border-bottom: 1px solid #ebeef5; }
.data-table th { background: #f5f7fa; color: #909399; font-weight: 500; }

.metric-tag {
  display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 12px; font-weight: bold;
}
.metric-tag.cpu { background: #e1f3d8; color: #67c23a; }
.metric-tag.memory { background: #fdf6ec; color: #e6a23c; }
.metric-tag.disk { background: #f4f4f5; color: #909399; }

.status-tag { display: inline-block; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
.status-tag.enabled { background: #f0f9ff; color: #409eff; }
.status-tag.disabled { background: #fef0f0; color: #f56c6c; }

.btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin-right: 5px; }
.btn-primary { background: #409eff; color: white; }
.btn-small { padding: 4px 8px; font-size: 12px; }
.btn-danger { background: #f56c6c; color: white; }

.dialog-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0; 
  background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 999;
}
.dialog { background: white; width: 500px; border-radius: 8px; overflow: hidden; }
.dialog-header { padding: 15px 20px; border-bottom: 1px solid #ebeef5; display: flex; justify-content: space-between; align-items: center; }
.close-btn { background: none; border: none; font-size: 20px; cursor: pointer; }
.dialog-body { padding: 20px; }
.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: 500; }
.form-select, .form-group input { width: 100%; padding: 8px; border: 1px solid #dcdfe6; border-radius: 4px; }
.hint { font-size: 12px; color: #909399; margin-top: 4px; display: block; }

.dialog-footer { padding: 15px 20px; border-top: 1px solid #ebeef5; text-align: right; }

.value-highlight { font-weight: bold; color: #f56c6c; }
.threshold-sub { color: #909399; font-size: 0.9em; }
.pagination { margin-top: 20px; display: flex; justify-content: flex-end; align-items: center; gap: 10px; }
.empty-text { text-align: center; color: #909399; padding: 20px; }
</style>