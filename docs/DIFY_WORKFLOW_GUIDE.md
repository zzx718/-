# Dify 工作流配置指南

## 📋 概述

本文档详细说明如何在 Dify 平台创建和配置**服务器智能告警决策工作流**，实现基于 AI 大模型的智能监控告警系统。

**适用版本**：Dify v0.6.0+  
**配置时间**：约 15-20 分钟  
**难度等级**：⭐⭐⭐ 中等

---

## 一、准备工作

### 1.1 前置条件

在开始配置之前，请确保满足以下条件：

- ✅ 已部署 Dify 平台（本地或云端）
- ✅ 拥有 Dify 账号并能够访问工作室
- ✅ 已配置至少一个 LLM 模型（如 OpenAI GPT-4、Claude、国产大模型等）
- ✅ 了解项目后端 API 的数据结构

### 1.2 访问 Dify 平台

**本项目使用的 Dify 地址**：`http://192.168.245.111`

使用您的账号登录后即可开始配置。

---

## 二、创建工作流

### 2.1 进入工作流创建页面

1. 登录 Dify 平台
2. 点击顶部导航栏 **「工作室」** 标签
3. 在左侧菜单中选择 **「工作流」**
4. 点击页面右上角的 **「+ 创建工作流」** 按钮

### 2.2 填写工作流基本信息

在弹出的创建对话框中，按照以下规范填写：

| 配置项 | 值 | 说明 |
|--------|------|------|
| **工作流名称** | `服务器智能告警决策` | 建议使用中文，便于团队理解 |
| **工作流描述** | `基于服务器监控指标、历史趋势和日志数据，利用AI大模型进行智能告警判断` | 可选，但建议填写以便后续维护 |
| **工作流类型** | `Workflow（工作流）` | ⚠️ 注意：不要选择 Chatflow |

填写完成后，点击 **「创建」** 按钮。

---

## 三、配置开始节点（输入变量）

### 3.1 理解输入变量的作用

工作流的**开始节点**用于接收后端 API 传递的数据。本项目需要接收 5 个 JSON 对象，包含服务器信息、监控指标、历史趋势、日志数据和上下文信息。

### 3.2 进入开始节点配置

创建工作流后，会自动进入编辑页面，此时画布上有一个 **「开始」** 节点。

1. 点击画布上的 **「开始」** 节点
2. 右侧会弹出配置面板，显示 **「输入变量」** 区域

### 3.3 添加输入变量（⚠️ 关键步骤）

#### 🎯 配置原则

每个变量都必须严格按照以下规范配置：

| 配置项 | 说明 | 注意事项 |
|--------|------|----------|
| **变量名 (Variable)** | 变量的唯一标识符 | 必须与后端代码中的键名**完全一致**（区分大小写） |
| **标签名 (Label)** | 在界面上显示的中文名称 | 可自定义，建议使用中文便于理解 |
| **字段类型 (Field Type)** | 数据类型 | ⚠️ **必须选择 `对象 (Object)`**，绝不能选择文本(String)或其他类型 |
| **必填 (Required)** | 是否必填 | ⚠️ **必须勾选**，确保后端传入完整数据 |

#### 📝 逐步添加 5 个变量

点击 **「+ 添加变量」** 按钮，按照以下配置逐一添加：

---

##### ① server_info - 服务器基本信息

```
变量名：server_info
标签名：服务器基本信息
字段类型：对象 (Object) ⚠️
必填：是 ✅
```

**包含字段**：
```json
{
  "id": 1,
  "name": "服务器A",
  "ip_address": "192.168.1.100",
  "server_name": "应用服务器",
  "importance": "medium",
  "description": "核心业务服务器"
}
```

---

##### ② current_metrics - 当前监控指标

```
变量名：current_metrics
标签名：当前监控指标
字段类型：对象 (Object) ⚠️
必填：是 ✅
```

**包含字段**：
```json
{
  "cpu": 85.5,
  "memory": 72.3,
  "disk": 65.8
}
```

---

##### ③ history_trend - 历史趋势数据

```
变量名：history_trend
标签名：历史趋势数据
字段类型：对象 (Object) ⚠️
必填：是 ✅
```

**包含字段**：
```json
{
  "cpu_5min_ago": 75.2,
  "cpu_10min_ago": 68.5,
  "cpu_trend": "rising",
  "cpu_change_rate": 13.7,
  "memory_trend": "stable",
  "is_sustained_alert": true,
  "sustained_minutes": 5,
  "recent_data_points": [...]
}
```

---

##### ④ related_logs - 相关日志记录

```
变量名：related_logs
标签名：相关日志记录
字段类型：对象 (Object) ⚠️
必填：是 ✅
```

**包含字段**：
```json
{
  "error_count_last_10min": 5,
  "warning_count_last_10min": 12,
  "recent_errors": [
    "[ERROR] [Memory] OOM killer triggered on process java (pid 10243)"
  ],
  "keyword_hits": {}
}
```

---

##### ⑤ context - 上下文信息

```
变量名：context
标签名：上下文信息
字段类型：对象 (Object) ⚠️
必填：是 ✅
```

**包含字段**：
```json
{
  "hour_of_day": 10,
  "day_of_week": 1,
  "is_working_hours": true,
  "recent_alerts": [],
  "last_alert_time": null,
  "is_in_silent_period": false
}
```

---

### 3.4 验证配置

添加完成后，确认：
- ✅ 5 个变量都已添加
- ✅ 变量名拼写完全正确
- ✅ 字段类型都是 `对象 (Object)`
- ✅ 所有变量都勾选了 `必填`

---

## 四、添加「变量转换」代码节点（⚠️ 必须在 LLM 之前）

### 4.0 为什么需要这个节点

Dify 的 LLM 提示词编辑器**只支持 String / Number / Boolean / Array 类型**的变量直接插入。如果把 Object 类型变量插入提示词，会显示红色感叹号「**无效的变量**」，运行时实际内容为空。

**解决方案**：在开始节点和 LLM 节点之间，先用一个代码节点把 5 个 Object 变量序列化为 JSON 字符串，再传给 LLM。

**最终节点顺序**：
```
开始 → [代码节点: Object转String] → LLM节点 → [代码节点: 解析LLM输出] → 结束
```

### 4.1 添加代码节点（Object转String）

1. 点击「开始」节点右侧的 **「+」** 按钮
2. 选择 **「代码」** 节点
3. 连接「开始」→「代码节点」

### 4.2 配置代码节点

**输入变量**（点击「+ 添加输入变量」，共 5 个）：

| 变量名 | 来源 | 类型 |
|--------|------|------|
| `server_info` | `开始节点 / server_info` | Object |
| `current_metrics` | `开始节点 / current_metrics` | Object |
| `history_trend` | `开始节点 / history_trend` | Object |
| `related_logs` | `开始节点 / related_logs` | Object |
| `context` | `开始节点 / context` | Object |

**代码内容**（语言选 Python）：

```python
import json

def main(server_info: dict, current_metrics: dict, history_trend: dict, related_logs: dict, context: dict) -> dict:
    return {
        "server_info_str":      json.dumps(server_info,      ensure_ascii=False),
        "current_metrics_str":  json.dumps(current_metrics,  ensure_ascii=False),
        "history_trend_str":    json.dumps(history_trend,    ensure_ascii=False),
        "related_logs_str":     json.dumps(related_logs,     ensure_ascii=False),
        "context_str":          json.dumps(context,          ensure_ascii=False),
    }
```

**输出变量**（Dify 会根据 return 自动识别，类型均为 String）：

| 变量名 | 类型 |
|--------|------|
| `server_info_str` | String |
| `current_metrics_str` | String |
| `history_trend_str` | String |
| `related_logs_str` | String |
| `context_str` | String |

---

## 五、添加 LLM 节点

### 5.1 添加节点

1. 在工作流画布上点击「代码节点」右侧的 **「+」** 按钮
2. 选择 **「LLM」** 节点
3. 连接「代码节点（Object转String）」→「LLM节点」

### 5.2 配置 LLM 节点

点击 LLM 节点，在右侧面板配置：

#### 选择模型

| 配置项 | 值 | 说明 |
|--------|------|------|
| **模型提供商** | 根据实际情况选择 | 如 OpenAI、Anthropic、国产大模型等 |
| **模型** | GPT-4、qwen3.6-plus 等 | 建议使用推理能力强的模型 |
| **温度 (Temperature)** | `0.3` | 较低的温度使输出更稳定和确定 |
| **最大令牌数** | `2000` | 根据需要调整 |

#### 配置提示词（Prompt）

在 **「用户提示词」** 区域，输入以下 Prompt 模板。

> ✅ **此处引用的变量全部是 String 类型**（来自前一个代码节点的输出），在下拉框中可以正常选到，不会出现红色「无效的变量」提示。
>
> 插入变量方式：在提示词编辑器中输入 `/` 或 `{` 触发变量选择器，找到 `代码节点` 下的 `xxx_str` 变量点击插入。

```
你是一位专业的服务器运维专家，负责分析服务器监控数据并做出告警决策。

## 📊 服务器信息
{{#代码节点.server_info_str#}}

---

## 📈 当前监控指标
{{#代码节点.current_metrics_str#}}

---

## 📉 历史趋势分析
{{#代码节点.history_trend_str#}}

---

## 📝 相关日志（过去10分钟真实ELK数据）
{{#代码节点.related_logs_str#}}

---

## ⏰ 上下文信息
{{#代码节点.context_str#}}

---

## 🎯 任务要求

请根据以上信息进行智能分析，判断是否需要发送告警，并给出详细的处理建议。

**分析要点**：

1. **综合评估**：不要仅看单个指标是否超标，要综合考虑趋势、持续时间、日志异常等多个维度
2. **智能判断**：
   - 瞬时波动（如CPU短暂升高后下降）不需要告警
   - 持续超标且趋势上升才需要告警
   - 结合日志中的错误信息判断严重程度
3. **分级告警**：
   - `info`：指标接近阈值，仅记录
   - `warning`：单个指标超标，需要关注
   - `critical`：多个指标超标或持续时间长，需要立即处理
   - `emergency`：严重超标且有大量错误日志，紧急处理
4. **优先级判断**：
   - `low`：不紧急，可以排期处理
   - `medium`：需要关注，今日处理
   - `high`：需要立即处理
   - `urgent`：最高优先级，立即响应

**输出格式**：

请以**严格的JSON格式**输出分析结果，不要包含任何其他文字或解释：

```json
{
  "should_alert": true,
  "alert_level": "critical",
  "alert_reason": "CPU使用率持续5分钟超过85%且呈上升趋势，同时检测到5条OOM相关错误日志，内存压力严重",
  "severity_score": 85,
  "priority": "high",
  "recommendation": "建议立即检查Java进程内存占用，考虑重启应用或扩容服务器内存",
  "action_items": [
    "使用 top 命令查看内存占用最高的进程",
    "检查 Java 应用的堆内存配置",
    "分析近期是否有流量突增",
    "如果问题持续，考虑重启应用或扩容"
  ],
  "email": {
    "subject": "【严重告警】服务器A CPU和内存严重超标",
    "content": "检测到服务器192.168.1.100出现严重性能问题，CPU使用率85.5%且持续上升，已触发OOM错误。建议立即处理。",
    "recipient": "ops@company.com"
  },
  "silent_period": {
    "enabled": true,
    "minutes": 30
  }
}
```

**字段说明**：

- `should_alert` (boolean)：是否发送告警，true 或 false
- `alert_level` (string)：告警级别，可选值：info / warning / critical / emergency
- `alert_reason` (string)：详细的告警原因分析
- `severity_score` (number)：严重程度评分，0-100
- `priority` (string)：优先级，可选值：low / medium / high / urgent
- `recommendation` (string)：处理建议概述
- `action_items` (array)：具体的操作步骤列表
- `email.subject` (string)：邮件主题
- `email.content` (string)：邮件正文
- `email.recipient` (string)：收件人邮箱
- `silent_period.enabled` (boolean)：是否启用静默期
- `silent_period.minutes` (number)：静默期时长（分钟）

请确保输出的是**纯JSON格式**，不要添加任何Markdown代码块标记或其他文字。
```

---

### 5.3 设置输出变量（你问的这里）

在当前版本 Dify 中，LLM 节点通常会自动提供以下输出变量：

- `text`（string）：模型生成的主内容
- `reasoning_content`（string）：推理内容（部分模型可用）
- `usage`（object）：token 用量信息

这里**不需要**在 LLM 节点里手动新建或改名为 `llm_output`。正确做法是：

1. 点击 LLM 节点，在右侧 `设置` 面板确认 `输出变量` 下存在 `text`。
2. 到下一个“解析输出”代码节点中，新增输入变量名 `llm_output`（名称可自定义）。
3. 将该输入变量的来源选择为：`LLM.text`。

补充说明（DeepSeek 常见情况）：

- 若看到“模型不支持，自动降级为提示注入”，属于模型/适配器能力差异，流程仍可正常运行。
- 建议关闭“结构化输出”开关（或接受降级），继续使用 `LLM.text + 代码节点 JSON 解析兜底`。

---

## 六、添加「解析输出」代码节点（推荐）

### 6.1 为什么需要代码节点

虽然 LLM 通常能输出正确的 JSON 格式，但为了提高系统的健壮性，建议添加一个代码节点来：

- ✅ 验证 JSON 格式是否正确
- ✅ 补充缺失的默认值
- ✅ 处理异常情况，避免工作流失败

### 6.2 添加代码节点

1. 在工作流画布上点击 **「+」** 按钮
2. 选择 **「代码」** 节点
3. 放置在 LLM 节点后方
4. 连接 LLM 节点的输出到代码节点的输入

### 6.3 配置代码节点

点击代码节点，在右侧配置：

#### 输入变量

| 变量名 | 来源 | 类型 |
|--------|------|------|
| `llm_output` | `llm.text` | String |

#### 代码内容

在代码编辑器中输入以下 Python 代码：

```python
import json

def main(llm_output: str) -> dict:
    """
    解析和验证 LLM 输出的 JSON 数据
    """
    try:
        # 尝试解析 JSON
        result = json.loads(llm_output)
        
        # 定义默认值
        defaults = {
            "should_alert": False,
            "alert_level": "info",
            "alert_reason": "未检测到异常",
            "severity_score": 0,
            "priority": "low",
            "recommendation": "继续监控",
            "action_items": [],
            "email": {
                "subject": "",
                "content": "",
                "recipient": "ops@company.com"
            },
            "silent_period": {
                "enabled": False,
                "minutes": 30
            }
        }
        
        # 补充缺失的字段
        for key, default_value in defaults.items():
            if key not in result:
                result[key] = default_value
            elif key in ["email", "silent_period"] and isinstance(result[key], dict):
                # 补充嵌套字段的默认值
                for sub_key, sub_default in default_value.items():
                    if sub_key not in result[key]:
                        result[key][sub_key] = sub_default
        
        # 验证关键字段类型
        if not isinstance(result.get("should_alert"), bool):
            result["should_alert"] = False
        
        if result.get("alert_level") not in ["info", "warning", "critical", "emergency"]:
            result["alert_level"] = "info"
        
        if not isinstance(result.get("severity_score"), (int, float)):
            result["severity_score"] = 0
        else:
            # 确保分数在 0-100 范围内
            result["severity_score"] = max(0, min(100, result["severity_score"]))
        
        # 直接返回扁平字段，便于在 Dify 输出节点中逐个选择
        return result
        
    except json.JSONDecodeError as e:
        # JSON 解析失败
        return {
          "should_alert": False,
          "alert_level": "info",
          "alert_reason": f"LLM输出解析失败: {str(e)}",
          "severity_score": 0,
          "priority": "low",
          "recommendation": "请检查LLM配置和提示词",
          "action_items": ["检查工作流配置", "查看LLM日志"],
          "email": {
            "subject": "工作流配置错误",
            "content": "无法解析AI决策结果",
            "recipient": "ops@company.com"
          },
          "silent_period": {
            "enabled": False,
            "minutes": 30
          }
        }
    except Exception as e:
        # 其他异常
        return {
          "should_alert": False,
          "alert_level": "info",
          "alert_reason": f"处理异常: {str(e)}",
          "severity_score": 0,
          "priority": "low",
          "recommendation": "请联系管理员",
          "action_items": [],
          "email": {
            "subject": "",
            "content": "",
            "recipient": "ops@company.com"
          },
          "silent_period": {
            "enabled": False,
            "minutes": 30
          }
        }
```

#### 输出变量

⚠️ **这一步必须手动配置**（与你截图一致）：

1. 在代码节点底部 `输出变量` 区域，先删除默认的 `result`（如果存在）。
2. 点击 `+` 新增 9 个输出变量，名称必须与 `return` 字典的键一致。
3. 每个变量类型按下表设置。

如果这里仍只保留一个 `result`，后续输出节点就只能看到 `code.result`，无法逐个选择 `code.should_alert` 等字段。

| 变量名 | 类型 | 说明 |
|--------|------|------|
| `should_alert` | Boolean | 是否触发告警 |
| `alert_level` | String | 告警级别 |
| `alert_reason` | String | 告警原因 |
| `severity_score` | Number | 严重程度评分 |
| `priority` | String | 优先级 |
| `recommendation` | String | 处理建议 |
| `action_items` | Array[String] | 操作步骤列表 |
| `email` | Object | 邮件配置对象 |
| `silent_period` | Object | 静默期配置 |

---

## 七、配置输出节点（即结束节点）

### 7.1 进入输出节点配置

> ⚠️ 在你当前版本的 Dify 中，文档常说的“结束节点”在界面里显示为 **「输出」** 节点（橙色图标）。

1. 在画布上点击 **「输出」** 节点（它就是流程的结束节点）
2. 若画布中还没有该节点：
  - 点击上一个节点右侧 **「+」**
  - 在节点列表中选择 **「输出」**
  - 将上一个节点连线到 **「输出」**
3. 在右侧面板中配置输出变量

### 7.2 添加输出变量（⚠️ 极其重要）

**🚨 关键提示**：输出变量名称必须与后端代码 `services/dify_service.py` 中的解析逻辑**完全一致**！

**变量来源说明**：下方示例里的 `code.xxx` 指向“解析输出代码节点”的返回结果。如果你的代码节点名称不是 `code`，请在下拉中选择你自己的节点名，不要手输。

**界面操作说明**：在你当前版本的 Dify 里，输出节点通常只有两列需要配置：

- 左侧：`变量名`
- 右侧：`设置变量值`

这里**不需要手动再选一次类型**，类型会跟随你右侧选择的变量值自动确定。

> ⚠️ 如果你在变量选择器里只能看到 `code.result`，通常有两种原因：
> 1) 代码里仍是 `return {"result": ...}` 嵌套返回；
> 2) 代码节点的 `输出变量` 区域只配置了 `result`。
>
> 处理方式：改为“扁平 return”并在代码节点里手动新增 9 个输出变量，然后**先保存代码节点**，再重新打开输出节点。

点击 **「+ 添加变量」** 按钮，逐一添加以下 9 个输出变量：

---

#### ① should_alert（必填）

```
变量名：should_alert
值：code.should_alert
```

**说明**：是否触发告警的决策结果

---

#### ② alert_level（必填）

```
变量名：alert_level
值：code.alert_level
```

**说明**：告警级别 (info/warning/critical/emergency)

---

#### ③ alert_reason（必填）

```
变量名：alert_reason
值：code.alert_reason
```

**说明**：AI 分析的告警原因

---

#### ④ severity_score

```
变量名：severity_score
值：code.severity_score
```

**说明**：严重程度评分 (0-100)

---

#### ⑤ priority

```
变量名：priority
值：code.priority
```

**说明**：优先级 (low/medium/high/urgent)

---

#### ⑥ recommendation

```
变量名：recommendation
值：code.recommendation
```

**说明**：处理建议

---

#### ⑦ action_items

```
变量名：action_items
值：code.action_items
```

**说明**：具体操作步骤列表

---

#### ⑧ email

```
变量名：email
值：code.email
```

**说明**：邮件配置对象

---

#### ⑨ silent_period

```
变量名：silent_period
值：code.silent_period
```

**说明**：静默期配置

---

### 7.3 验证输出配置

确认：
- ✅ 9 个输出变量都已添加
- ✅ 变量名拼写完全正确（特别是前3个必填项）
- ✅ 右侧变量值都是从下拉中选择的 `code.xxx`
- ✅ 没有把多个变量都错误地指向同一个 `code.result`

---

## 八、发布和测试工作流

### 8.1 保存工作流

1. 点击右上角 **「保存」** 按钮
2. 确认工作流所有节点连接正确
3. 没有错误提示

### 8.2 在 Dify 平台内测试

#### 使用调试功能

1. 点击右上角 **「运行」** 或 **「调试」** 按钮
2. 在弹出的输入面板中，您会看到 5 个独立的输入框。请分别填入对应的测试数据：

**① server_info (服务器基本信息)**：
```json
{
  "id": 1,
  "name": "测试服务器",
  "ip_address": "192.168.1.100",
  "server_name": "应用服务器",
  "importance": "high",
  "description": "核心业务服务器"
}
```

**② current_metrics (当前监控指标)**：
```json
{
  "cpu": 88.5,
  "memory": 75.3,
  "disk": 65.8
}
```

**③ history_trend (历史趋势数据)**：
```json
{
  "cpu_5min_ago": 80.2,
  "cpu_10min_ago": 72.5,
  "cpu_trend": "rising",
  "cpu_change_rate": 16.0,
  "memory_trend": "rising",
  "is_sustained_alert": true,
  "sustained_minutes": 8
}
```

**④ related_logs (相关日志记录)**：
```json
{
  "error_count_last_10min": 8,
  "warning_count_last_10min": 15,
  "recent_errors": [
    "[ERROR] [Memory] OOM killer triggered",
    "[ERROR] Database connection timeout"
  ]
}
```

**⑤ context (上下文信息)**：
```json
{
  "hour_of_day": 14,
  "day_of_week": 3,
  "is_working_hours": true,
  "recent_alerts": [],
  "last_alert_time": null,
  "is_in_silent_period": false
}
```

3. 点击 **「运行」** 按钮
4. 查看每个节点的执行结果
5. 检查最终输出是否符合预期

### 8.3 发布工作流

测试通过后：

1. 点击右上角 **「发布」** 按钮
2. 在弹出对话框中确认发布
3. 工作流将变为可用状态

---

## 九、获取 API 凭证

### 9.1 获取 API 密钥

> **💡 提示**：您当前页面的 URL 是 `.../develop`，左侧菜单栏通常包含「**访问 API**」选项。

1. 在 Dify 平台当前页面的**左侧导航栏**（或页面右上角），找到并点击 **「访问 API」** (API Access)。
2. 在打开的 API 管理页面右上角，点击 **「API 密钥」** 按钮。
3. 点击 **「+ 创建密钥」**。
4. 为密钥命名（如：`monitor_system_key`），点击 **「确认」**。
5. **⚠️ 重要**：复制生成的 API Key 并妥善保存（它通常以 `app-` 开头，且只显示一次）。

**示例**：
```
app-Lx2PWw4eLStQVbgCH9XzFbvC
```

### 9.2 获取 Workflow ID

工作流的 ID 可以直接从您浏览器的 URL 地址栏中提取。

**您的真实 URL**：
```text
http://192.168.245.111/app/adb7a673-44cd-4531-a2ae-e8a25b657344/develop
```

**解析说明**：
在 `/app/` 和 `/develop` 之间的这一串长字符，就是您的 Workflow ID：
```text
adb7a673-44cd-4531-a2ae-e8a25b657344
```

将这个值复制备用即可。

---

## 十、配置到项目

### 10.1 创建或修改 .env 文件

在项目根目录下，编辑 `.env` 文件（如果不存在则创建），确保包含以下真实配置：

```env
# Dify 工作流配置
DIFY_API_URL=http://192.168.245.111/v1
DIFY_API_KEY=app-Lx2PWw4eLStQVbgCH9XzFbvC
DIFY_WORKFLOW_ID=adb7a673-44cd-4531-a2ae-e8a25b657344
```

### 10.2 验证配置

确保：
- ✅ `DIFY_API_URL` 指向正确的 Dify 实例
- ✅ `DIFY_API_KEY` 是刚才复制的完整密钥
- ✅ `DIFY_WORKFLOW_ID` 是工作流的正确 ID

### 10.3 重启应用

修改 `.env` 后，需要重启后端服务使配置生效：

```bash
# 如果使用 Docker
docker-compose restart backend

# 如果直接运行
# 停止当前进程，然后重新启动
python app.py
```

---

## 十一、测试与运行

### 11.1 启动真实监控客户端（日常运行）

在生产环境中，我们需要运行监控客户端脚本事实采集服务器数据（比如每 30 秒采集一次 CPU、内存传给后端）。

> **前置条件**：请先在网页端「进入**服务器管理** -> 点击**新增服务器**」，并记下自动生成的 Server ID（通常您的第一台服务器 ID 为 1）。

在您的服务器（或本机 PowerShell 终端）上执行以下命令：
```bash
# 激活环境
.\.venv\Scripts\Activate.ps1

# 启动普通客户端（如果此时电脑负载很高且持续 2 分钟，会自动触发下文的告警流）
python scripts/monitor_client.py

# 如果您的 Server ID 不是 1（而是其他 ID），请带上参数运行：
# python scripts/monitor_client.py --server-id 2
```


> **💡 生产自动化触发 vs 本地一键测试**
>
> 按照上面的 `monitor_client.py` 启动后，一旦它发去的数据连续超时（比如持续两分钟 CPU 达到 85%），系统就会在后台**自动**调用 Dify 触发智能告警决策，这就是“自动化”。
> 
> 但是，您可能不想仅仅为了测试一下 Dify 有没有配通，就去故意制造一次电脑死机（高负载）。所以，本系统专门提供了一个用来**无视负载指标，马上强制要求 Dify 发一次警报决策**的专门测试通道，下面就教您如何使用。

### 11.2 强制手动触发测试（调试用）

由于测试接口 `/api/dify/trigger/1` 启用了 JWT (JSON Web Token) 安全认证，您必须先获取您本人的登录 Token 才能发出强制测试请求。

在您的 PowerShell 里，请**依序执行以下两步**：

**第 1 步：获取管理员 Token 并自动记录**
```powershell
$loginResponse = Invoke-RestMethod -Uri "http://localhost:5000/api/auth/login" -Method Post -Headers @{ "Content-Type" = "application/json" } -Body '{"username":"admin", "password":"123456"}'
$token = $loginResponse.data.token
Write-Host "成功获取Token，准备就绪！" -ForegroundColor Green
```

**第 2 步：拿着 Token 发起测试指控**
*(末尾的 `/1` 代表我们要用 1 号服务器的名义来向大模型发送请求)*
```powershell
Invoke-RestMethod -Uri "http://localhost:5000/api/dify/trigger/1" -Method Post -Headers @{ "Content-Type" = "application/json"; "Authorization" = "Bearer $token" }
```

> **💡 进阶方案 (直接使用您的网页端按钮)**：  
> 您也可以直接在项目网页 UI 里，点击具体的测试按钮，它会自动帮您拼装发送这部分带有 Token 的请求，同样可以立即调用 Dify。

### 11.3 查看执行结果

如果看到控制台刷出结果了，不要忘了验证：
1. 刚才的 PowerShell 窗口有没有返回正确的判断内容
2. 您的 Flask 黑窗里有没有报错
3. 登录来到您的 Dify 平台内，点击那个工作流内部的“执行日志”看看它具体说的话
4. 您的目标邮箱里收到最终的应急信没

---

## 十二、工作流优化建议

### 12.1 告警策略优化

#### 多维度判断

不要仅依赖单一指标，应综合考虑：

- ✅ **指标值**：当前 CPU、内存、磁盘使用率
- ✅ **趋势**：是上升、下降还是稳定
- ✅ **持续时间**：瞬时波动 vs 持续超标
- ✅ **日志异常**：是否有错误日志
- ✅ **业务时间**：工作时间 vs 非工作时间

#### 分级告警策略

| 级别 | 触发条件 | 响应方式 | 建议静默期 |
|------|----------|----------|-----------|
| **Info** | 指标接近阈值（如 CPU > 70%） | 仅记录日志 | 60分钟 |
| **Warning** | 单指标超过阈值但无日志异常 | 邮件通知 | 30分钟 |
| **Critical** | 多指标超标或有错误日志 | 邮件+即时通知 | 15分钟 |
| **Emergency** | 所有指标严重超标+大量错误日志 | 邮件+短信+电话 | 不静默 |

### 12.2 业务场景适配

#### 高峰期容忍度

在提示词中添加业务高峰期的判断逻辑：

```
- 如果是工作日的早高峰（8-10点）或晚高峰（18-20点），CPU/内存阈值可以适当放宽 10-15%
- 如果是凌晨（0-6点），即使指标略高也可能是正常的定时任务
```

#### 服务器重要性

根据 `server_info.importance` 调整告警敏感度：

- **high（高）**：更敏感，轻微异常就告警
- **medium（中）**：标准策略
- **low（低）**：更宽松，严重问题才告警

### 12.3 静默期策略

合理设置静默期，避免告警疲劳：

- ✅ 同一服务器同一问题在静默期内不重复发送
- ✅ 但如果严重程度升级（如从 warning 升至 critical），应立即告警
- ✅ 紧急级别（emergency）可以不设静默期

---

## 十三、故障排查

### 13.1 工作流执行失败

#### 症状

- API 调用返回错误
- Dify 平台显示执行失败

#### 排查步骤

1. **检查输入数据格式**
   ```bash
   # 查看后端日志中发送给 Dify 的数据
   tail -f logs/app.log | grep -i dify
   ```

2. **查看 Dify 工作流日志**
   - 登录 Dify 平台
   - 进入工作流
   - 点击「日志」或「执行历史」
   - 查看失败的执行记录

3. **验证变量类型**
   - 确认所有输入变量类型都是 `对象 (Object)`
   - 确认变量名拼写正确

4. **检查 API 凭证**
   - 验证 API Key 是否正确
   - 验证 Workflow ID 是否正确
   - 确认 API URL 可访问

### 13.2 JSON 解析失败

#### 症状

- LLM 输出无法解析为 JSON
- 代码节点捕获到解析错误

#### 解决方案

1. **优化 LLM 提示词**
   - 强调"输出纯 JSON，不要有其他文字"
   - 在提示词末尾再次强调格式要求

2. **降低模型温度**
   - 将 Temperature 设置为 0.1-0.3
   - 使输出更确定、更规范

3. **添加输出格式示例**
   - 在提示词中给出完整的 JSON 输出示例
   - 使用 few-shot 提示方法

4. **使用 JSON 模式（如果模型支持）**
   - 某些模型（如 GPT-4）支持 JSON mode
   - 在 API 调用时设置 `response_format: { type: "json_object" }`

### 13.3 告警未发送

#### 症状

- 工作流执行成功
- 但没有收到告警邮件

#### 排查步骤

1. **检查决策结果**
   - 查看工作流输出的 `should_alert` 是否为 `true`
   - 确认 `alert_level` 达到了发送邮件的阈值

2. **检查邮件配置**
   - 验证项目的邮件服务配置是否正确
   - 查看后端日志中的邮件发送记录

3. **检查静默期**
   - 确认该服务器当前不在静默期内
   - 查看 `context.is_in_silent_period` 的值

---

## 十四、高级配置

### 14.1 添加条件分支

如果需要根据告警级别执行不同的后续操作，可以在工作流中添加**条件节点**：

1. 在代码节点后添加「条件」节点
2. 设置条件：`code.alert_level == "emergency"`
3. 分别连接不同的后续节点（如不同的通知渠道）

### 14.2 集成其他通知渠道

可以在工作流中添加 HTTP 请求节点，调用：

- 企业微信机器人
- 钉钉机器人
- Slack webhook
- PagerDuty API
- 短信接口

### 14.3 记录决策历史

添加 HTTP 请求节点，将 AI 的决策结果回传到后端数据库，便于：

- 分析 AI 决策的准确性
- 优化告警策略
- 生成决策报告

---

## 十五、最佳实践总结

### ✅ 配置规范

- 变量名必须与后端代码严格一致
- 所有输入变量使用 `对象 (Object)` 类型
- 所有输入变量设置为必填
- 输出变量名称不能拼写错误

### ✅ 提示词设计

- 提供清晰的角色定位（运维专家）
- 给出明确的分析维度和判断标准
- 强调输出格式要求（纯 JSON）
- 提供完整的 JSON 输出示例

### ✅ 健壮性设计

- 添加代码节点进行 JSON 验证
- 设置默认值和异常处理
- 限制数值范围（如 severity_score 0-100）
- 验证关键字段类型

### ✅ 测试流程

- 先在 Dify 平台内测试
- 再通过 API 集成测试
- 模拟各种边界情况
- 验证异常处理逻辑

---

## 十六、附录

### 附录A：完整的数据结构示例

请参考原文档第 2.2 节的详细 JSON 结构。

### 附录B：后端集成代码示例

```python
# services/dify_service.py 中的关键代码片段

async def call_dify_workflow(server_data: dict) -> dict:
    """调用 Dify 工作流"""
    response = await http_client.post(
        f"{DIFY_API_URL}/workflows/run",
        headers={
            "Authorization": f"Bearer {DIFY_API_KEY}",
            "Content-Type": "application/json"
        },
        json={
            "inputs": {
                "server_info": server_data["server_info"],
                "current_metrics": server_data["current_metrics"],
                "history_trend": server_data["history_trend"],
                "related_logs": server_data["related_logs"],
                "context": server_data["context"]
            },
            "response_mode": "blocking"
        }
    )
    
    result = response.json()
    return result["data"]["outputs"]
```

### 附录C：常见问题 FAQ

**Q1：为什么必须使用 Object 类型而不是 String？**

A：因为后端传递的是 Python 字典（dict），对应 JSON 的对象类型。如果使用 String，Dify 会将整个字典序列化为字符串，导致无法在提示词中访问内部字段。

**Q2：如何修改提示词而不影响已发布的工作流？**

A：修改后点击「保存」，然后重新「发布」。API 调用会自动使用最新发布的版本。

**Q3：可以使用免费的 LLM 模型吗？**

A：可以，但建议使用推理能力较强的模型（如 GPT-3.5 以上、Claude 2 以上、或国产的文心一言、通义千问等）以确保决策质量。

**Q4：工作流执行需要多长时间？**

A：通常在 2-10 秒之间，取决于 LLM 模型的响应速度和网络状况。

---

## 结语

通过本指南，您应该能够成功配置 Dify 工作流，实现基于 AI 大模型的智能告警决策。

如有问题，请查看：
- Dify 官方文档：https://docs.dify.ai/
- 项目 GitHub Issues
- 或联系技术支持

祝配置顺利！ 🎉
