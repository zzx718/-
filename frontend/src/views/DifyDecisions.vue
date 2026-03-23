<template>
  <div class="dify-decisions">
    <div class="page-header">
      <div class="card-header">
        <h2>Dify智能决策</h2>
        <div class="tabs">
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'decisions' }"
            @click="activeTab = 'decisions'"
          >
            决策历史
          </button>
          <button
            class="tab-btn"
            :class="{ active: activeTab === 'rules' }"
            @click="activeTab = 'rules'"
          >
            智能规则
          </button>
        </div>
      </div>
    </div>

    <div v-if="activeTab === 'decisions'" class="content-section">
      <div class="action-bar">
        <select v-model="filterServerId" class="filter-select" @change="loadDecisions">
          <option :value="null">-- 所有服务器 --</option>
          <option v-for="server in servers" :key="server.id" :value="server.id">
            {{ server.server_name }} ({{ server.ip_address }})
          </option>
        </select>
        <select v-model="filterAlertLevel" class="filter-select" @change="loadDecisions">
          <option :value="null">-- 所有级别 --</option>
          <option value="info">Info</option>
          <option value="warning">Warning</option>
          <option value="critical">Critical</option>
          <option value="emergency">Emergency</option>
        </select>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>服务器</th>
              <th>时间</th>
              <th>当前指标</th>
              <th>告警级别</th>
              <th>是否告警</th>
              <th>执行状态</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="decision in decisions" :key="decision.id">
              <td>{{ decision.id }}</td>
              <td>{{ getServerName(decision.server_id) }}</td>
              <td>{{ formatDate(decision.created_at) }}</td>
              <td>
                <div v-if="decision.current_metrics">
                  CPU: {{ decision.current_metrics.cpu }}%<br>
                  内存: {{ decision.current_metrics.memory }}%<br>
                  磁盘: {{ decision.current_metrics.disk }}%
                </div>
              </td>
              <td>
                <span class="level-tag" :class="decision.alert_level">
                  {{ decision.alert_level?.toUpperCase() || '-' }}
                </span>
              </td>
              <td>
                <span class="status-tag" :class="decision.should_alert ? 'alert' : 'no-alert'">
                  {{ decision.should_alert ? '是' : '否' }}
                </span>
              </td>
              <td>
                <span class="status-tag" :class="decision.executed ? 'executed' : 'pending'">
                  {{ decision.executed ? '已执行' : '待执行' }}
                </span>
                <span v-if="decision.human_feedback" class="feedback-tag" :class="decision.human_feedback">
                  {{ getFeedbackText(decision.human_feedback) }}
                </span>
              </td>
              <td>
                <button class="btn btn-small" @click="showDecisionDetail(decision)">详情</button>
              </td>
            </tr>
            <tr v-if="decisions.length === 0">
              <td colspan="8" class="empty-text">暂无决策记录</td>
            </tr>
          </tbody>
        </table>
      </div>

      <div class="pagination" v-if="total > 0">
        <button :disabled="page <= 1" @click="changePage(-1)">上一页</button>
        <span>第 {{ page }} 页</span>
        <button :disabled="decisions.length < pageSize" @click="changePage(1)">下一页</button>
      </div>
    </div>

    <div v-if="activeTab === 'rules'" class="content-section">
      <div class="action-bar">
        <select v-model="filterRuleServerId" class="filter-select" @change="loadRules">
          <option :value="null">-- 所有服务器 --</option>
          <option v-for="server in servers" :key="server.id" :value="server.id">
            {{ server.server_name }} ({{ server.ip_address }})
          </option>
        </select>
        <button class="btn btn-primary" @click="openAddRuleDialog">添加规则</button>
      </div>

      <div class="table-container">
        <table class="data-table">
          <thead>
            <tr>
              <th>规则名称</th>
              <th>服务器</th>
              <th>Dify工作流ID</th>
              <th>优先级</th>
              <th>静默时间(分)</th>
              <th>状态</th>
              <th>创建时间</th>
              <th>操作</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="rule in rules" :key="rule.id">
              <td>{{ rule.rule_name }}</td>
              <td>{{ getServerName(rule.server_id) }}</td>
              <td><code>{{ rule.dify_workflow_id || '-' }}</code></td>
              <td>{{ rule.priority }}</td>
              <td>{{ rule.silent_minutes }}</td>
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
              <td colspan="8" class="empty-text">暂无智能规则</td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showDetailDialog" class="dialog-overlay" @click="showDetailDialog = false">
      <div class="dialog detail-dialog" @click.stop>
        <div class="dialog-header">
          <h3>决策详情</h3>
          <button class="close-btn" @click="showDetailDialog = false">&times;</button>
        </div>
        <div class="dialog-body" v-if="selectedDecision">
          <div class="detail-section">
            <h4>基本信息</h4>
            <p><strong>决策ID:</strong> {{ selectedDecision.id }}</p>
            <p><strong>服务器:</strong> {{ getServerName(selectedDecision.server_id) }}</p>
            <p><strong>创建时间:</strong> {{ formatDate(selectedDecision.created_at) }}</p>
            <p><strong>工作流ID:</strong> {{ selectedDecision.workflow_id || '-' }}</p>
            <p><strong>运行ID:</strong> {{ selectedDecision.workflow_run_id || '-' }}</p>
          </div>

          <div class="detail-section">
            <h4>当前指标</h4>
            <pre>{{ JSON.stringify(selectedDecision.current_metrics, null, 2) }}</pre>
          </div>

          <div class="detail-section">
            <h4>告警原因</h4>
            <p>{{ selectedDecision.alert_reason || '-' }}</p>
          </div>

          <div class="detail-section">
            <h4>处理建议</h4>
            <p>{{ selectedDecision.recommendation || '-' }}</p>
          </div>

          <div class="detail-section" v-if="selectedDecision.action_items?.length">
            <h4>建议操作</h4>
            <ul>
              <li v-for="(item, i) in selectedDecision.action_items" :key="i">{{ item }}</li>
            </ul>
          </div>

          <div class="detail-section">
            <h4>人工反馈</h4>
            <div class="feedback-buttons">
              <button
                v-for="f in ['correct', 'wrong', 'neutral']"
                :key="f"
                class="feedback-btn"
                :class="{ active: selectedDecision.human_feedback === f }"
                @click="submitFeedback(f)"
              >
                {{ getFeedbackText(f) }}
              </button>
            </div>
            <input
              v-model="feedbackComment"
              type="text"
              placeholder="备注信息"
              class="form-input"
            />
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn" @click="showDetailDialog = false">关闭</button>
        </div>
      </div>
    </div>

    <div v-if="showRuleDialog" class="dialog-overlay" @click="showRuleDialog = false">
      <div class="dialog" @click.stop>
        <div class="dialog-header">
          <h3>{{ editingRule ? '编辑规则' : '添加智能规则' }}</h3>
          <button class="close-btn" @click="showRuleDialog = false">&times;</button>
        </div>
        <div class="dialog-body">
          <div class="form-group">
            <label>服务器</label>
            <select v-model="ruleForm.server_id" class="form-select">
              <option v-for="server in servers" :key="server.id" :value="server.id">
                {{ server.server_name }} ({{ server.ip_address }})
              </option>
            </select>
          </div>

          <div class="form-group">
            <label>规则名称</label>
            <input type="text" v-model="ruleForm.rule_name" class="form-input" />
          </div>

          <div class="form-group">
            <label>规则描述</label>
            <textarea v-model="ruleForm.rule_description" class="form-input" rows="3"></textarea>
          </div>

          <div class="form-group">
            <label>Dify工作流ID</label>
            <input type="text" v-model="ruleForm.dify_workflow_id" class="form-input" />
          </div>

          <div class="form-group">
            <label>优先级</label>
            <input type="number" v-model="ruleForm.priority" class="form-input" min="0" />
          </div>

          <div class="form-group">
            <label>静默时间 (分钟)</label>
            <input type="number" v-model="ruleForm.silent_minutes" class="form-input" min="1" />
          </div>

          <div class="form-group checkbox-group">
            <label>
              <input type="checkbox" v-model="ruleForm.is_enabled" /> 启用此规则
            </label>
          </div>
        </div>
        <div class="dialog-footer">
          <button class="btn" @click="showRuleDialog = false">取消</button>
          <button class="btn btn-primary" @click="saveRule">保存</button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, watch } from 'vue'
import { difyApi, serverApi } from '@/api'

const activeTab = ref('decisions')
const decisions = ref([])
const rules = ref([])
const servers = ref([])
const filterServerId = ref(null)
const filterRuleServerId = ref(null)
const filterAlertLevel = ref(null)
const page = ref(1)
const pageSize = ref(20)
const total = ref(0)

const showDetailDialog = ref(false)
const showRuleDialog = ref(false)
const selectedDecision = ref(null)
const feedbackComment = ref('')
const editingRule = ref(null)
const ruleForm = ref({
  server_id: null,
  rule_name: '',
  rule_description: '',
  dify_workflow_id: '',
  priority: 0,
  silent_minutes: 30,
  is_enabled: true
})

onMounted(() => {
  loadServers()
  loadDecisions()
})

watch(activeTab, (newTab) => {
  if (newTab === 'decisions') {
    loadDecisions()
  } else {
    loadRules()
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

const loadDecisions = async () => {
  try {
    const params = { page: page.value, page_size: pageSize.value }
    if (filterServerId.value) params.server_id = filterServerId.value
    const res = await difyApi.getDecisions(params)
    decisions.value = res.data?.items || []
    total.value = res.data?.total || 0
  } catch (e) {
    console.error(e)
  }
}

const loadRules = async () => {
  try {
    const params = {}
    if (filterRuleServerId.value) params.server_id = filterRuleServerId.value
    const res = await difyApi.getSmartRules(params)
    rules.value = res.data || []
  } catch (e) {
    console.error(e)
  }
}

const getServerName = (serverId) => {
  const server = servers.value.find(s => s.id === serverId)
  return server ? `${server.server_name} (${server.ip_address})` : serverId
}

const getFeedbackText = (feedback) => {
  const map = { correct: '正确', wrong: '错误', neutral: '中性' }
  return map[feedback] || feedback
}

const showDecisionDetail = (decision) => {
  selectedDecision.value = decision
  feedbackComment.value = decision.feedback_comment || ''
  showDetailDialog.value = true
}

const submitFeedback = async (feedback) => {
  try {
    await difyApi.submitFeedback(selectedDecision.value.id, {
      human_feedback: feedback,
      feedback_comment: feedbackComment.value
    })
    selectedDecision.value.human_feedback = feedback
    selectedDecision.value.feedback_comment = feedbackComment.value
    alert('反馈提交成功')
  } catch (e) {
    console.error(e)
    alert('反馈提交失败')
  }
}

const openAddRuleDialog = () => {
  editingRule.value = null
  ruleForm.value = {
    server_id: servers.value.length > 0 ? servers.value[0].id : null,
    rule_name: '',
    rule_description: '',
    dify_workflow_id: '',
    priority: 0,
    silent_minutes: 30,
    is_enabled: true
  }
  showRuleDialog.value = true
}

const editRule = (rule) => {
  editingRule.value = rule
  ruleForm.value = { ...rule }
  showRuleDialog.value = true
}

const saveRule = async () => {
  try {
    if (editingRule.value) {
      await difyApi.updateSmartRule(editingRule.value.id, ruleForm.value)
    } else {
      await difyApi.createSmartRule(ruleForm.value)
    }
    showRuleDialog.value = false
    loadRules()
    alert('保存成功')
  } catch (e) {
    console.error(e)
    alert('保存失败')
  }
}

const deleteRule = async (rule) => {
  if (confirm('确定删除此规则吗？')) {
    try {
      await difyApi.deleteSmartRule(rule.id)
      loadRules()
    } catch (e) {
      console.error(e)
      alert('删除失败')
    }
  }
}

const changePage = (delta) => {
  page.value += delta
  loadDecisions()
}

const formatDate = (str) => {
  if (!str) return '-'
  return new Date(str).toLocaleString()
}
</script>

<style scoped>
.dify-decisions { padding: 20px; }
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

.level-tag {
  display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; font-weight: bold;
}
.level-tag.info { background: #f0f9ff; color: #409eff; }
.level-tag.warning { background: #fdf6ec; color: #e6a23c; }
.level-tag.critical { background: #fef0f0; color: #f56c6c; }
.level-tag.emergency { background: #fee2e2; color: #dc2626; }

.status-tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; margin-right: 5px; }
.status-tag.alert { background: #fef0f0; color: #f56c6c; }
.status-tag.no-alert { background: #f0f9ff; color: #409eff; }
.status-tag.executed { background: #f0f9ff; color: #409eff; }
.status-tag.pending { background: #fef0f0; color: #f56c6c; }
.status-tag.enabled { background: #f0f9ff; color: #409eff; }
.status-tag.disabled { background: #fef0f0; color: #f56c6c; }

.feedback-tag { display: inline-block; padding: 2px 8px; border-radius: 4px; font-size: 12px; }
.feedback-tag.correct { background: #e1f3d8; color: #67c23a; }
.feedback-tag.wrong { background: #fef0f0; color: #f56c6c; }
.feedback-tag.neutral { background: #f4f4f5; color: #909399; }

.btn { padding: 8px 16px; border: none; border-radius: 4px; cursor: pointer; margin-right: 5px; }
.btn-primary { background: #409eff; color: white; }
.btn-small { padding: 4px 8px; font-size: 12px; }
.btn-danger { background: #f56c6c; color: white; }

.dialog-overlay {
  position: fixed; top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.5); display: flex; justify-content: center; align-items: center; z-index: 999;
}
.dialog { background: white; width: 500px; border-radius: 8px; overflow: hidden; }
.detail-dialog { width: 700px; max-height: 90vh; overflow-y: auto; }
.dialog-header { padding: 15px 20px; border-bottom: 1px solid #ebeef5; display: flex; justify-content: space-between; align-items: center; }
.close-btn { background: none; border: none; font-size: 20px; cursor: pointer; }
.dialog-body { padding: 20px; }
.form-group { margin-bottom: 15px; }
.form-group label { display: block; margin-bottom: 5px; font-weight: 500; }
.form-select, .form-input { width: 100%; padding: 8px; border: 1px solid #dcdfe6; border-radius: 4px; }
.dialog-footer { padding: 15px 20px; border-top: 1px solid #ebeef5; text-align: right; }

.detail-section { margin-bottom: 20px; }
.detail-section h4 { margin: 0 0 10px 0; color: #303133; border-bottom: 1px solid #ebeef5; padding-bottom: 5px; }
.detail-section p { margin: 5px 0; }
.detail-section pre { background: #f5f7fa; padding: 10px; border-radius: 4px; overflow-x: auto; font-size: 12px; }
.detail-section ul { padding-left: 20px; margin: 5px 0; }

.feedback-buttons { display: flex; gap: 10px; margin-bottom: 10px; }
.feedback-btn {
  padding: 8px 16px; border: 1px solid #dcdfe6; background: white; border-radius: 4px; cursor: pointer;
}
.feedback-btn.active { background: #409eff; color: white; border-color: #409eff; }

.pagination { margin-top: 20px; display: flex; justify-content: flex-end; align-items: center; gap: 10px; }
.empty-text { text-align: center; color: #909399; padding: 20px; }
code { background: #f5f7fa; padding: 2px 6px; border-radius: 4px; font-size: 12px; }
</style>
