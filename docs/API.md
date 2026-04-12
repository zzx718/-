# API 接口文档

## 概述

所有API接口统一使用 `/api` 前缀，返回格式统一为：

```json
{
  "code": 0,
  "message": "success",
  "data": {}
}
```

- `code`: 0 表示成功，其他表示失败
- `message`: 提示信息
- `data`: 返回数据

---

## 认证说明

需要认证的接口需要在请求头中携带：

```
Authorization: Bearer <token>
```

---

## 一、Dify 智能决策 API

### 1.1 获取决策列表

**接口**: `GET /api/dify/decisions`

**认证**: 需要管理员权限

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `page` | int | 否 | 页码，默认1 |
| `page_size` | int | 否 | 每页数量，默认20 |
| `server_id` | int | 否 | 服务器ID筛选 |

**响应示例**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "items": [
      {
        "id": 1,
        "server_id": 1,
        "workflow_id": "abc123",
        "workflow_run_id": "def456",
        "current_metrics": {
          "cpu": 85.5,
          "memory": 72.3,
          "disk": 65.8
        },
        "should_alert": true,
        "alert_level": "warning",
        "alert_reason": "CPU使用率持续超过阈值",
        "executed": false,
        "human_feedback": null,
        "created_at": "2026-03-22T10:00:00"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 20
  }
}
```

---

### 1.2 获取决策详情

**接口**: `GET /api/dify/decisions/<decision_id>`

**认证**: 需要管理员权限

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `decision_id` | int | 是 | 决策ID |

**响应示例**:
```json
{
  "code": 0,
  "message": "success",
  "data": {
    "id": 1,
    "server_id": 1,
    "workflow_id": "abc123",
    "workflow_run_id": "def456",
    "input_data": {},
    "current_metrics": {},
    "history_trend": {},
    "should_alert": true,
    "alert_level": "warning",
    "alert_reason": "CPU使用率持续超过阈值",
    "decision_output": {},
    "recommendation": "建议检查进程...",
    "action_items": ["检查CPU使用最高的进程", "考虑扩容"],
    "executed": false,
    "execution_result": null,
    "human_feedback": null,
    "feedback_comment": null,
    "created_at": "2026-03-22T10:00:00",
    "executed_at": null,
    "feedback_at": null
  }
}
```

---

### 1.3 提交人工反馈

**接口**: `PUT /api/dify/decisions/<decision_id>`

**认证**: 需要管理员权限

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `decision_id` | int | 是 | 决策ID |

**请求体**:
```json
{
  "human_feedback": "correct",
  "feedback_comment": "决策正确"
}
```

**human_feedback 可选值**: `correct` | `wrong` | `neutral`

---

### 1.4 获取智能规则列表

**接口**: `GET /api/dify/smart-rules`

**认证**: 需要管理员权限

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `server_id` | int | 否 | 服务器ID筛选 |

**响应示例**:
```json
{
  "code": 0,
  "message": "success",
  "data": [
    {
      "id": 1,
      "server_id": 1,
      "rule_name": "高CPU告警",
      "rule_description": "当CPU超过80%时触发",
      "dify_workflow_id": "abc123",
      "trigger_condition": {},
      "is_enabled": true,
      "priority": 0,
      "silent_minutes": 30,
      "created_at": "2026-03-22T10:00:00",
      "updated_at": "2026-03-22T10:00:00"
    }
  ]
}
```

---

### 1.5 创建智能规则

**接口**: `POST /api/dify/smart-rules`

**认证**: 需要管理员权限

**请求体**:
```json
{
  "server_id": 1,
  "rule_name": "高CPU告警",
  "rule_description": "当CPU超过80%时触发",
  "dify_workflow_id": "abc123",
  "dify_api_key": "optional-key",
  "trigger_condition": {},
  "is_enabled": true,
  "priority": 0,
  "silent_minutes": 30
}
```

---

### 1.6 更新智能规则

**接口**: `PUT /api/dify/smart-rules/<rule_id>`

**认证**: 需要管理员权限

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `rule_id` | int | 是 | 规则ID |

**请求体**: 同创建接口

---

### 1.7 删除智能规则

**接口**: `DELETE /api/dify/smart-rules/<rule_id>`

**认证**: 需要管理员权限

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `rule_id` | int | 是 | 规则ID |

---

### 1.8 手动触发工作流

**接口**: `POST /api/dify/trigger/<server_id>`

**认证**: 需要管理员权限

**路径参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `server_id` | int | 是 | 服务器ID |

**响应示例**:
```json
{
  "code": 0,
  "message": "Workflow triggered",
  "data": {
    "success": true,
    "workflow_run_id": "def456",
    "data": {},
    "outputs": {}
  }
}
```

---

## 二、日志查询 API

### 2.1 搜索日志

**接口**: `POST /api/logs/search`

**认证**: 需要管理员权限

**请求体**:
```json
{
  "server_id": 1,
  "log_type": "container",
  "container_name": "nginx",
  "service_name": "web",
  "keyword": "error",
  "start_time": "2026-03-22T00:00:00",
  "end_time": "2026-03-22T23:59:59",
  "log_levels": ["error", "warning"],
  "page": 1,
  "page_size": 50
}
```

**响应示例**:
```json
{
  "code": 0,
  "message": "Search logs success",
  "data": {
    "logs": [
      {
        "id": "log-id-123",
        "@timestamp": "2026-03-22T10:00:00",
        "server_id": 1,
        "log_type": "container",
        "container_name": "nginx",
        "log_level": "error",
        "message": "Connection refused"
      }
    ],
    "total": 100,
    "page": 1,
    "page_size": 50
  }
}
```

---

### 2.2 获取日志统计

**接口**: `GET /api/logs/stats`

**认证**: 需要管理员权限

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `server_id` | int | 否 | 服务器ID筛选 |
| `hours` | int | 否 | 统计小时数，默认24 |

**响应示例**:
```json
{
  "code": 0,
  "message": "Get log stats success",
  "data": {
    "total": 1000,
    "by_level": {
      "error": 50,
      "warning": 200,
      "info": 750
    },
    "by_hour": [
      {
        "time": "2026-03-22T00:00:00",
        "count": 100
      }
    ]
  }
}
```

---

### 2.3 获取关联日志

**接口**: `GET /api/logs/related`

**认证**: 需要管理员权限

**查询参数**:
| 参数 | 类型 | 必填 | 说明 |
|------|------|------|------|
| `server_id` | int | 是 | 服务器ID |
| `alert_time` | string | 是 | 告警时间 (ISO格式) |
| `window_minutes` | int | 否 | 时间窗口，默认10 |

**响应示例**:
```json
{
  "code": 0,
  "message": "Get related logs success",
  "data": {
    "decision_id": 1,
    "related_logs": []
  }
}
```

---

## 三、其他 API（原有接口）

### 3.1 认证接口

**登录**: `POST /api/auth/login`

**请求体**:
```json
{
  "username": "admin",
  "password": "password"
}
```

---

### 3.2 服务器管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/servers` | GET | 获取服务器列表 |
| `/api/servers` | POST | 创建服务器 |
| `/api/servers/<id>` | GET | 获取服务器详情 |
| `/api/servers/<id>` | PUT | 更新服务器 |
| `/api/servers/<id>` | DELETE | 删除服务器 |

---

### 3.3 监控数据

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/monitor/data` | GET | 获取监控数据 |
| `/api/monitor/data` | POST | 提交监控数据 |
| `/api/monitor/stats` | GET | 获取监控统计 |

---

### 3.4 告警管理

| 接口 | 方法 | 说明 |
|------|------|------|
| `/api/alert-rules` | GET | 获取告警规则 |
| `/api/alert-rules` | POST | 创建告警规则 |
| `/api/alert-rules/<id>` | PUT | 更新告警规则 |
| `/api/alert-rules/<id>` | DELETE | 删除告警规则 |
| `/api/alert-history` | GET | 获取告警历史 |

---

## 四、错误码说明

| Code | 说明 |
|------|------|
| 0 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 无权限 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |
