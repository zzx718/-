# Dify 工作流配置指南

## 概述

本文档说明如何在Dify平台配置智能告警决策工作流。

---

## 一、创建工作流

### 1.1 登录Dify平台

访问 https://dify.ai 并登录

### 1.2 创建空白工作流

1. 点击「工作室」→「工作流」
2. 点击「创建空白工作流」
3. 填写工作流名称：`服务器智能告警决策`
4. 选择「从空白开始」

---

## 二、配置工作流开始节点

### 2.1 设置输入变量

工作流开始节点需要配置以下输入变量：

| 变量名 | 类型 | 说明 |
|--------|------|------|
| `server_info` | Object | 服务器基本信息 |
| `current_metrics` | Object | 当前监控指标 |
| `history_trend` | Object | 历史趋势数据 |
| `related_logs` | Object | 相关日志数据 |
| `context` | Object | 上下文信息 |

### 2.2 输入变量详细结构

```json
{
  "server_info": {
    "id": 1,
    "name": "服务器A",
    "ip_address": "192.168.1.100",
    "server_name": "应用服务器",
    "importance": "medium",
    "description": "核心业务服务器"
  },
  "current_metrics": {
    "cpu": 85.5,
    "memory": 72.3,
    "disk": 65.8
  },
  "history_trend": {
    "cpu_5min_ago": 75.2,
    "cpu_10min_ago": 68.5,
    "cpu_trend": "rising",
    "cpu_change_rate": 13.7,
    "memory_trend": "stable",
    "is_sustained_alert": true,
    "sustained_minutes": 5,
    "recent_data_points": [
      {
        "cpu": 75.2,
        "memory": 70.1,
        "disk": 65.0,
        "time": "10:00:00"
      },
      {
        "cpu": 80.3,
        "memory": 71.5,
        "disk": 65.2,
        "time": "10:00:30"
      }
    ]
  },
  "related_logs": {
    "error_count_last_10min": 5,
    "warning_count_last_10min": 12,
    "recent_errors": [],
    "keyword_hits": {}
  },
  "context": {
    "hour_of_day": 10,
    "day_of_week": 1,
    "is_working_hours": true,
    "recent_alerts": [],
    "last_alert_time": null,
    "is_in_silent_period": false
  }
}
```

---

## 三、添加LLM节点

### 3.1 选择模型

选择一个合适的LLM模型（如 GPT-4、Claude 等）

### 3.2 配置Prompt

使用以下Prompt模板：

```
你是一位专业的服务器运维专家。请根据以下服务器监控数据，判断是否需要告警，并给出处理建议。

## 服务器信息
服务器ID: {{start.server_info.id}}
服务器名称: {{start.server_info.name}}
IP地址: {{start.server_info.ip_address}}
重要性: {{start.server_info.importance}}
描述: {{start.server_info.description}}

## 当前监控指标
CPU使用率: {{start.current_metrics.cpu}}%
内存使用率: {{start.current_metrics.memory}}%
磁盘使用率: {{start.current_metrics.disk}}%

## 历史趋势
- CPU 5分钟前: {{start.history_trend.cpu_5min_ago}}%
- CPU 10分钟前: {{start.history_trend.cpu_10min_ago}}%
- CPU趋势: {{start.history_trend.cpu_trend}}
- CPU变化率: {{start.history_trend.cpu_change_rate}}%
- 是否持续告警: {{start.history_trend.is_sustained_alert}}
- 持续时间: {{start.history_trend.sustained_minutes}}分钟

## 相关日志
- 最近10分钟错误数: {{start.related_logs.error_count_last_10min}}
- 最近10分钟警告数: {{start.related_logs.warning_count_last_10min}}

## 上下文
- 当前时间: {{start.context.hour_of_day}}点
- 星期: {{start.context.day_of_week}}
- 是否工作时间: {{start.context.is_working_hours}}

---

## 任务

请根据以上信息，做出智能判断，并以JSON格式输出结果：

{
  "should_alert": boolean,           // 是否需要告警: true/false
  "alert_level": string,              // 告警级别: "info" | "warning" | "critical" | "emergency"
  "alert_reason": string,             // 告警原因详细说明
  "severity_score": number,           // 严重程度评分 0-100
  "priority": string,                 // 优先级: "low" | "medium" | "high" | "urgent"
  "recommendation": string,           // 处理建议
  "action_items": string[],           // 建议执行的操作列表
  "email": {                          // 邮件配置
    "subject": string,
    "content": string,
    "recipient": string
  },
  "silent_period": {                  // 静默期配置
    "enabled": boolean,
    "minutes": number
  }
}

要求：
1. 只有当指标持续超过阈值且趋势上升时才告警
2. 告警级别根据指标严重程度和持续时间判断
3. 处理建议要具体可行
4. 输出严格的JSON格式，不要有其他文字
```

---

## 四、添加代码节点（可选）

用于格式化和验证LLM输出，确保JSON格式正确。

```python
import json

def main(llm_output):
    try:
        result = json.loads(llm_output)
        
        # 设置默认值
        defaults = {
            "should_alert": False,
            "alert_level": "info",
            "alert_reason": "",
            "severity_score": 0,
            "priority": "medium",
            "recommendation": "",
            "action_items": [],
            "email": {
                "subject": "",
                "content": "",
                "recipient": ""
            },
            "silent_period": {
                "enabled": False,
                "minutes": 30
            }
        }
        
        for key, value in defaults.items():
            if key not in result:
                result[key] = value
        
        return result
    except Exception as e:
        return {
            "should_alert": False,
            "alert_level": "info",
            "alert_reason": f"解析失败: {str(e)}",
            "severity_score": 0,
            "priority": "low",
            "recommendation": "请检查LLM输出格式",
            "action_items": [],
            "email": {"subject": "", "content": "", "recipient": ""},
            "silent_period": {"enabled": False, "minutes": 30}
        }
```

---

## 五、配置工作流结束节点

### 5.1 设置输出变量

将LLM节点（或代码节点）的输出设置为工作流输出：

| 输出变量 | 来源 |
|----------|------|
| `should_alert` | llm.should_alert |
| `alert_level` | llm.alert_level |
| `alert_reason` | llm.alert_reason |
| `severity_score` | llm.severity_score |
| `priority` | llm.priority |
| `recommendation` | llm.recommendation |
| `action_items` | llm.action_items |
| `email` | llm.email |
| `silent_period` | llm.silent_period |

---

## 六、获取API凭证

### 6.1 获取API Key

1. 进入工作流详情页
2. 点击右上角「API访问」
3. 点击「创建密钥」
4. 复制生成的API Key

### 6.2 获取Workflow ID

在工作流URL中可以找到，例如：
```
https://cloud.dify.ai/workflow/abc123def456
                                ^^^^^^^^^^^^^^
                                这就是 Workflow ID
```

---

## 七、配置到项目

将获取的API Key和Workflow ID填写到 `.env` 文件：

```env
DIFY_API_URL=https://api.dify.ai/v1
DIFY_API_KEY=your-api-key-here
DIFY_WORKFLOW_ID=your-workflow-id-here
```

---

## 八、测试工作流

### 8.1 在Dify平台测试

1. 进入工作流编辑页
2. 点击「调试与预览」
3. 填入测试数据
4. 点击「运行」查看结果

### 8.2 通过API测试

使用项目提供的API手动触发：

```
POST /api/dify/trigger/<server_id>
```

---

## 九、工作流优化建议

### 9.1 多维度判断

- 不仅看单一指标，还要结合趋势和持续时间
- 考虑业务高峰期（如早晚高峰可以适当放宽阈值）

### 9.2 分级告警

| 级别 | 触发条件 | 响应方式 |
|------|----------|----------|
| Info | 指标接近阈值 | 记录日志 |
| Warning | 单指标超过阈值 | 邮件通知 |
| Critical | 多指标超标+持续 | 邮件+短信 |
| Emergency | 所有指标严重超标 | 邮件+短信+电话 |

### 9.3 静默期策略

- 同一服务器同一问题在30分钟内不重复告警
- 但严重程度升级时可以再次告警

---

## 十、故障排查

### 10.1 工作流执行失败

- 检查输入变量格式是否正确
- 查看Dify平台的工作流日志
- 确认API Key和Workflow ID正确

### 10.2 JSON解析失败

- 确保LLM输出严格的JSON格式
- 添加代码节点进行格式化和容错处理
