# 基于Dify低代码平台的服务器智能告警与辅助决策系统 - 设计文档

## 一、项目概述

### 1.1 项目背景
本项目基于现有的Flask+Vue3服务器监控系统，引入Dify低代码平台和ELK日志栈，将硬编码的告警逻辑改为可视化工作流编排，并结合日志分析实现更智能、更全面的服务器管控系统。

### 1.2 项目目标
- **保留现有功能**：完整保留原有的监控数据采集、存储、可视化功能
- **引入Dify智能决策**：将告警逻辑抽离到Dify工作流
- **实现决策可追溯**：完整记录每次Dify决策过程
- **支持人工反馈**：允许人工标记决策质量，持续优化
- **集成ELK日志栈**：实现日志采集、存储、检索、可视化
- **告警+日志关联分析**：Dify决策时自动查询相关日志，智能诊断问题

---

## 二、系统架构设计

### 2.1 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                      前端展示层 (Vue3 + ECharts + Kibana)        │
│  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ ┌─────────────┐ │
│  │  实时监控   │ │  告警历史   │ │  Dify决策   │ │  日志检索   │ │
│  └─────────────┘ └─────────────┘ └─────────────┘ └─────────────┘ │
└──────────────────────────────┬──────────────────────────────────┘
                               │
┌──────────────────────────────▼──────────────────────────────────┐
│                      业务逻辑层 (Flask)                          │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐  │
│  │  监控数据采集    │ │  数据持久化      │ │  Dify集成服务    │  │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘  │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐  │
│  │  告警执行模块    │ │  决策记录管理    │ │  日志查询服务    │  │
│  └──────────────────┘ └──────────────────┘ └──────────────────┘  │
└──────────────────────┬───────────────┬───────────────────┬───────┘
                       │               │                   │
        ┌──────────────▼──────────┐  ┌▼──────────────────┐ ┌▼───────────┐
        │        MySQL           │  │         Dify       │ │Elasticsearch│
        │  - monitor_data        │  │  - 智能告警工作流  │ │  - 日志数据 │
        │  - alert_history       │  │  - 辅助决策工作流  │ │  - 全文索引 │
        │  - dify_decisions      │  │  - 日志分析工作流  │ └────────────┘
        │  - servers/users       │  └────────────────────┘
        └─────────────────────────┘
                       │
        ┌──────────────▼──────────┐
        │        Redis            │
        │  - 实时缓存            │
        │  - 热点数据            │
        └─────────────────────────┘
```

### 2.2 日志采集与处理架构 (ELK Stack)

```
┌─────────────────────────────────────────────────────────────────┐
│                      日志采集层                                  │
│  ┌──────────────────┐ ┌──────────────────┐ ┌──────────────────┐ │
│  │  Filebeat        │ │  Docker日志API    │ │  应用日志文件    │ │
│  │  (系统/应用日志) │ │  (容器日志采集)   │ │  (Flask日志)     │ │
│  └────────┬─────────┘ └────────┬─────────┘ └────────┬─────────┘ │
└───────────┼─────────────────────┼─────────────────────┼───────────┘
            │                     │                     │
┌───────────▼─────────────────────▼─────────────────────▼───────────┐
│                      消息队列 (Kafka - 可选)                       │
│                    日志缓冲 + 削峰填谷                            │
└───────────┬─────────────────────┬─────────────────────┬───────────┘
            │                     │                     │
┌───────────▼─────────────────────▼─────────────────────▼───────────┐
│                      日志处理层 (Logstash - 可选)                   │
│                    日志清洗、格式化、解析                            │
└───────────┬─────────────────────┬─────────────────────┬───────────┘
            │                     │                     │
┌───────────▼─────────────────────▼─────────────────────▼───────────┐
│                      日志存储层 (Elasticsearch)                     │
│  ┌──────────────────────────────────────────────────────────────┐ │
│  │  索引:                                                         │ │
│  │  - system-logs-YYYY.MM.DD      (系统日志)                    │ │
│  │  - application-logs-YYYY.MM.DD (应用日志)                    │ │
│  │  - container-logs-YYYY.MM.DD   (容器日志)                    │ │
│  │  - alert-logs-YYYY.MM.DD       (告警日志)                    │ │
│  └──────────────────────────────────────────────────────────────┘ │
└───────────────────────────────────────────────────────────────────┘
                              │
┌─────────────────────────────▼─────────────────────────────────────┐
│                      日志可视化 (Kibana)                           │
│  - 日志检索与过滤                                                  │
│  - 日志统计图表                                                    │
│  - 日志异常检测                                                    │
│  - 告警关联视图                                                    │
└───────────────────────────────────────────────────────────────────┘
```

### 2.3 核心数据流

#### 2.3.1 监控数据与告警流程

```
Agent采集数据
    ↓
Flask接收监控数据
    ↓
存入MySQL (monitor_data)
    ↓
触发告警检查
    ↓
┌────────────────────────────────────┐
│  准备Dify工作流输入:              │
│  - 当前指标                         │
│  - 历史趋势                         │
│  - 服务器信息                       │
│  - 上下文信息                       │
│  - 相关日志 (从ES查询)             │
└────────────────────────────────────┘
    ↓
调用Dify工作流API
    ↓
获取Dify决策结果
    ↓
┌────────────────────────────────────┐
│  执行决策:                          │
│  1. 记录Dify决策到MySQL            │
│  2. 根据决策发送告警邮件            │
│  3. 存入告警历史                    │
│  4. 关联查询相关日志                │
└────────────────────────────────────┘
    ↓
前端展示
```

#### 2.3.2 日志采集与处理流程

```
Filebeat/Docker API采集日志
    ↓
发送到Kafka (可选，用于缓冲)
    ↓
Logstash处理 (可选，清洗格式化)
    ↓
存入Elasticsearch
    ↓
建立索引，支持全文检索
    ↓
┌────────────────────────────────────┐
│  使用场景:                          │
│  1. Kibana可视化展示                │
│  2. Flask API提供日志查询           │
│  3. Dify告警时关联查询相关日志       │
│  4. 日志异常模式分析                │
└────────────────────────────────────┘
```

---

## 三、数据模型设计

### 3.1 Elasticsearch索引设计

**简化方案：只创建4个大类索引，用字段区分具体来源，而不是每个容器/服务一个索引**

#### 3.1.1 统一索引结构模板

```json
{
  "index_patterns": ["*-logs-*"],
  "mappings": {
    "properties": {
      "@timestamp": {"type": "date"},
      "server_id": {"type": "integer"},
      "server_name": {"type": "keyword"},
      "log_type": {"type": "keyword"},
      "log_level": {"type": "keyword"},
      "message": {"type": "text"},
      
      "container_id": {"type": "keyword"},
      "container_name": {"type": "keyword"},
      "image": {"type": "keyword"},
      
      "service_name": {"type": "keyword"},
      "request_id": {"type": "keyword"},
      "user_id": {"type": "integer"},
      "endpoint": {"type": "keyword"},
      "response_time": {"type": "float"},
      
      "source": {"type": "keyword"},
      "host": {"type": "keyword"},
      "process_id": {"type": "integer"}
    }
  }
}
```

#### 3.1.2 实际使用的索引（仅4个，按日期轮转）

| 索引名 | 用途 | 区分字段 |
|--------|------|---------|
| `system-logs-YYYY.MM.DD` | 系统日志 | `host`、`server_id` |
| `application-logs-YYYY.MM.DD` | 应用日志 | `service_name`、`server_id` |
| `container-logs-YYYY.MM.DD` | 所有容器日志 | `container_name`、`container_id` |
| `alert-logs-YYYY.MM.DD` | 告警日志 | `alert_id`、`server_id` |

**优点**：
- 只需要管理4个索引模板，不需要为每个容器创建索引
- 用字段查询过滤，灵活性更高
- 日期轮转自动管理，维护简单

### 3.2 新增表：Dify决策记录表 (dify_decisions)

```python
class DifyDecision(db.Model):
    """Dify决策记录表 - 记录每次Dify工作流的决策"""
    __tablename__ = 'dify_decisions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False, comment='关联服务器ID')
    
    # ========== 决策上下文 ==========
    workflow_id = db.Column(db.String(100), comment='Dify工作流ID')
    workflow_run_id = db.Column(db.String(100), comment='Dify工作流运行ID')
    
    # 输入数据快照
    input_data = db.Column(db.JSON, comment='发送给Dify的完整输入数据')
    current_metrics = db.Column(db.JSON, comment='当前指标快照')
    history_trend = db.Column(db.JSON, comment='历史趋势数据')
    
    # ========== 决策结果 ==========
    should_alert = db.Column(db.Boolean, default=False, comment='是否需要告警')
    alert_level = db.Column(db.Enum('info', 'warning', 'critical', 'emergency'), comment='告警级别')
    alert_reason = db.Column(db.Text, comment='告警原因说明')
    
    # 完整决策结果
    decision_output = db.Column(db.JSON, comment='Dify返回的完整决策结果')
    
    # 处理建议
    recommendation = db.Column(db.Text, comment='处理建议')
    action_items = db.Column(db.JSON, comment='建议执行的操作列表')
    
    # ========== 执行与反馈 ==========
    executed = db.Column(db.Boolean, default=False, comment='是否已执行')
    execution_result = db.Column(db.Text, comment='执行结果')
    
    # 人工反馈
    human_feedback = db.Column(db.Enum('correct', 'wrong', 'neutral'), comment='人工反馈: 正确/错误/中性')
    feedback_comment = db.Column(db.Text, comment='反馈备注')
    
    # ========== 时间字段 ==========
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间', index=True)
    executed_at = db.Column(db.DateTime, comment='执行时间')
    feedback_at = db.Column(db.DateTime, comment='反馈时间')
    
    @classmethod
    def create(cls, server_id, workflow_id, input_data, decision_output):
        """创建决策记录"""
        decision = cls(
            server_id=server_id,
            workflow_id=workflow_id,
            input_data=input_data,
            current_metrics=input_data.get('current_metrics'),
            history_trend=input_data.get('history_trend'),
            decision_output=decision_output,
            should_alert=decision_output.get('should_alert', False),
            alert_level=decision_output.get('alert_level'),
            alert_reason=decision_output.get('alert_reason'),
            recommendation=decision_output.get('recommendation'),
            action_items=decision_output.get('action_items')
        )
        db.session.add(decision)
        db.session.commit()
        return decision
    
    @classmethod
    def get_by_server(cls, server_id, limit=50):
        """获取服务器的决策记录"""
        return cls.query.filter_by(server_id=server_id).order_by(cls.created_at.desc()).limit(limit).all()
    
    @classmethod
    def get_pending(cls, limit=20):
        """获取待执行的决策"""
        return cls.query.filter_by(executed=False).order_by(cls.created_at.desc()).limit(limit).all()
```

### 3.2 新增表：智能告警规则表 (smart_alert_rules)

```python
class SmartAlertRule(db.Model):
    """智能告警规则表 - 管理Dify工作流绑定"""
    __tablename__ = 'smart_alert_rules'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    server_id = db.Column(db.Integer, db.ForeignKey('servers.id'), nullable=False, comment='关联服务器ID')
    
    rule_name = db.Column(db.String(100), nullable=False, comment='规则名称')
    rule_description = db.Column(db.Text, comment='规则描述')
    
    # Dify工作流配置
    dify_workflow_id = db.Column(db.String(100), comment='绑定的Dify工作流ID')
    dify_api_key = db.Column(db.String(200), comment='Dify API Key (可选，单独配置)')
    
    # 触发条件（简单前置过滤，减少Dify调用次数）
    trigger_condition = db.Column(db.JSON, comment='前置触发条件')
    
    # 状态管理
    is_enabled = db.Column(db.Boolean, default=True, comment='是否启用')
    priority = db.Column(db.Integer, default=0, comment='优先级，数字越大优先级越高')
    
    # 静默期配置
    silent_minutes = db.Column(db.Integer, default=30, comment='告警静默期(分钟)')
    
    created_at = db.Column(db.DateTime, default=datetime.now, comment='创建时间')
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now, comment='更新时间')
    
    @classmethod
    def get_by_server(cls, server_id):
        """获取服务器的启用规则"""
        return cls.query.filter_by(server_id=server_id, is_enabled=True).order_by(cls.priority.desc()).all()
    
    @classmethod
    def get_all_enabled(cls):
        """获取所有启用的规则"""
        return cls.query.filter_by(is_enabled=True).all()
```

---

## 四、Dify工作流设计

### 4.1 工作流输入数据结构（含日志）

```json
{
  "server_info": {
    "id": 1,
    "name": "核心数据库服务器",
    "ip_address": "192.168.1.100",
    "server_name": "数据库主服务器",
    "importance": "high",
    "description": "生产环境核心数据库"
  },
  
  "current_metrics": {
    "cpu": 85.5,
    "memory": 72.3,
    "disk": 65.8
  },
  
  "history_trend": {
    "cpu_5min_ago": 55.2,
    "cpu_10min_ago": 48.1,
    "cpu_trend": "rising",
    "cpu_change_rate": 5.1,
    "memory_trend": "stable",
    
    "is_sustained_alert": true,
    "sustained_minutes": 5,
    
    "recent_data_points": [
      {"cpu": 55.2, "memory": 68.0, "disk": 65.5, "time": "5分钟前"},
      {"cpu": 62.3, "memory": 69.5, "disk": 65.6, "time": "4分钟前"},
      {"cpu": 70.1, "memory": 70.2, "disk": 65.7, "time": "3分钟前"},
      {"cpu": 78.5, "memory": 71.0, "disk": 65.8, "time": "2分钟前"},
      {"cpu": 85.5, "memory": 72.3, "disk": 65.8, "time": "当前"}
    ]
  },
  
  "related_logs": {
    "error_count_last_10min": 15,
    "warning_count_last_10min": 28,
    
    "recent_errors": [
      {
        "timestamp": "2024-01-01 14:58:30",
        "log_level": "ERROR",
        "message": "MySQL connection timeout after 30s",
        "source": "application"
      },
      {
        "timestamp": "2024-01-01 14:57:45",
        "log_level": "ERROR",
        "message": "Slow query detected: SELECT * FROM orders took 12s",
        "source": "database"
      }
    ],
    
    "keyword_hits": {
      "timeout": 8,
      "error": 15,
      "slow query": 3,
      "connection refused": 2
    }
  },
  
  "context": {
    "hour_of_day": 15,
    "day_of_week": 3,
    "is_working_hours": true,
    
    "recent_alerts": [
      {
        "metric_type": "cpu",
        "level": "warning",
        "triggered_at": "2024-01-01 14:55:00"
      }
    ],
    
    "last_alert_time": "2024-01-01 14:55:00",
    "is_in_silent_period": false
  }
}
```

### 4.2 工作流输出数据结构

```json
{
  "should_alert": true,
  "alert_level": "critical",
  "alert_reason": "CPU从55%快速上升到85%，持续5分钟且仍在上升",
  
  "severity_score": 85,
  "priority": "high",
  
  "recommendation": "建议立即检查：1) 数据库慢查询 2) 异常进程 3) 考虑临时扩容",
  
  "action_items": [
    "send_email",
    "record_alert_history",
    "notify_admin"
  ],
  
  "email": {
    "should_send": true,
    "subject": "【严重告警】核心数据库服务器CPU异常",
    "content": "服务器【核心数据库服务器】(192.168.1.100)发生严重告警：\n\nCPU使用率：85.5%\n内存使用率：72.3%\n磁盘使用率：65.8%\n\n告警原因：CPU从55%快速上升到85%，持续5分钟\n\n处理建议：建议立即检查数据库慢查询或异常进程\n\n-- 智能监控系统"
  },
  
  "silent_period": {
    "enabled": true,
    "duration_minutes": 30
  },
  
  "next_steps": [
    "wait_30_minutes",
    "recheck_metrics"
  ]
}
```

### 4.3 工作流节点设计

#### 工作流1：基础智能告警工作流

```
1. 开始节点
   ↓
2. 数据校验节点
   - 检查必填字段
   - 数据格式校验
   ↓
3. 趋势分析节点
   - 计算CPU变化率
   - 判断上升/下降/稳定
   - 检查是否持续告警
   ↓
4. 条件判断节点1 - 快速上升判断
   if CPU变化率 > 30% and CPU > 80%
       → 严重告警分支
   else
       → 继续判断
   ↓
5. 条件判断节点2 - 双指标判断
   if CPU > 80% and 内存 > 75%
       → 紧急告警分支
   else if CPU > 90% or 内存 > 90%
       → 严重告警分支
   else if CPU > 70% or 内存 > 70%
       → 普通告警分支
   else
       → 不告警分支
   ↓
6. 告警级别确定
   - 根据分支设置alert_level
   - 生成告警原因描述
   ↓
7. 静默期检查
   - 查询最近告警记录
   - 判断是否在静默期
   ↓
8. 处理建议生成
   - 根据告警级别生成建议
   - 建议具体操作步骤
   ↓
9. 邮件内容生成
   - 生成邮件主题
   - 生成邮件正文
   ↓
10. 结束节点
    - 输出完整决策结果
```

---

## 五、核心API设计

### 5.1 Dify相关API

#### 1. 触发Dify告警决策
```
POST /api/dify/trigger-alert
Request:
{
  "server_id": 1,
  "metrics": {
    "cpu": 85.5,
    "memory": 72.3,
    "disk": 65.8
  }
}

Response:
{
  "code": 0,
  "message": "决策触发成功",
  "data": {
    "decision_id": 123,
    "should_alert": true,
    "alert_level": "critical"
  }
}
```

#### 2. 获取决策记录列表
```
GET /api/dify/decisions?server_id=1&limit=50

Response:
{
  "code": 0,
  "data": [
    {
      "id": 123,
      "server_id": 1,
      "should_alert": true,
      "alert_level": "critical",
      "created_at": "2024-01-01 15:00:00"
    }
  ]
}
```

#### 3. 获取决策详情
```
GET /api/dify/decisions/123

Response:
{
  "code": 0,
  "data": {
    "id": 123,
    "server_id": 1,
    "input_data": {...},
    "decision_output": {...},
    "recommendation": "...",
    "executed": true,
    "human_feedback": "correct"
  }
}
```

#### 4. 提交人工反馈
```
POST /api/dify/decisions/123/feedback
Request:
{
  "feedback": "correct",
  "comment": "决策准确，确实是慢查询导致"
}

Response:
{
  "code": 0,
  "message": "反馈提交成功"
}
```

#### 5. 智能告警规则管理
```
GET    /api/smart-alert-rules          # 获取规则列表
POST   /api/smart-alert-rules          # 创建规则
GET    /api/smart-alert-rules/1        # 获取规则详情
PUT    /api/smart-alert-rules/1        # 更新规则
DELETE /api/smart-alert-rules/1        # 删除规则
```

### 5.2 日志查询API

#### 1. 搜索日志
```
POST /api/logs/search
Request:
{
  "server_id": 1,
  "log_type": "system",
  "keyword": "error",
  "start_time": "2024-01-01T00:00:00",
  "end_time": "2024-01-01T23:59:59",
  "log_level": ["ERROR", "WARNING"],
  "page": 1,
  "page_size": 50
}

Response:
{
  "code": 0,
  "data": {
    "total": 150,
    "logs": [
      {
        "id": "log_123456",
        "@timestamp": "2024-01-01T14:58:30.000Z",
        "server_id": 1,
        "log_level": "ERROR",
        "message": "MySQL connection timeout after 30s",
        "source": "application"
      }
    ]
  }
}
```

#### 2. 获取日志统计
```
GET /api/logs/stats?server_id=1&hours=24

Response:
{
  "code": 0,
  "data": {
    "total_logs": 12500,
    "error_count": 150,
    "warning_count": 450,
    "info_count": 11900,
    "hourly_stats": [
      {"hour": 0, "count": 500, "errors": 5},
      {"hour": 1, "count": 450, "errors": 3}
    ]
  }
}
```

#### 3. 获取告警相关日志
```
GET /api/logs/related?decision_id=123

Response:
{
  "code": 0,
  "data": {
    "decision_id": 123,
    "related_logs": [
      {
        "timestamp": "2024-01-01T14:58:30.000Z",
        "log_level": "ERROR",
        "message": "MySQL connection timeout",
        "relevance_score": 0.95
      }
    ]
  }
}
```

---

## 六、实现步骤

### Phase 1: 基础框架（1-2天）
- [ ] 创建数据模型 (DifyDecision, SmartAlertRule)
- [ ] 创建数据库迁移文件
- [ ] 创建Dify集成服务 (dify_service.py)
- [ ] 配置Dify API密钥

### Phase 2: ELK日志栈（2-3天）
- [ ] 更新docker-compose.yml，添加ES、Kibana
- [ ] 更新requirements.txt，添加elasticsearch依赖
- [ ] 创建日志服务 (log_service.py)
- [ ] 配置ES连接和索引管理
- [ ] 实现日志查询API

### Phase 3: 核心功能（2-3天）
- [ ] 实现Dify工作流调用
- [ ] 实现输入数据准备（历史趋势、上下文、相关日志）
- [ ] 实现决策结果解析和存储
- [ ] 改造告警逻辑，集成Dify
- [ ] 实现告警与日志关联查询

### Phase 4: API与前端（2-3天）
- [ ] 创建Dify相关API路由
- [ ] 创建智能告警规则API
- [ ] 创建日志查询API
- [ ] 前端决策记录页面
- [ ] 前端规则管理页面
- [ ] 前端日志检索页面

### Phase 5: 完善与测试（1-2天）
- [ ] 人工反馈功能
- [ ] 静默期管理
- [ ] 完整流程测试
- [ ] 文档完善

---

## 七、Dify工作流导入模板

### 基础告警工作流JSON（可直接导入Dify）

（此处预留，实际实现时提供完整的Dify工作流导出文件）

---

## 八、注意事项

1. **Dify API限流**: 注意Dify API调用频率限制，避免频繁调用
2. **错误处理**: Dify调用失败时，应有降级方案（回退到原有的硬编码告警）
3. **数据安全**: Dify API密钥要安全存储，不要提交到代码仓库
4. **性能优化**: 可以在前置条件过滤掉明显不需要告警的情况，减少Dify调用
5. **日志记录**: 完整记录Dify调用的输入输出，便于调试和分析

---

## 九、扩展方向（可选）

1. **多工作流支持**: 不同服务器绑定不同的Dify工作流
2. **A/B测试**: 同时运行两个工作流，对比效果
3. **工作流版本管理**: 记录工作流变更历史
4. **决策效果分析**: 统计决策准确率，优化工作流
5. **自动优化**: 根据人工反馈自动调整工作流参数
