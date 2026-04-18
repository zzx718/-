# 基于云原生与Dify的分布式服务器智能管控平台

基于 Flask + Vue 3 开发的现代化服务器监控平台，集成 Dify 低代码平台实现智能决策，使用 Elasticsearch 进行日志管理，为企业提供智能化的 IT 基础设施监控解决方案。系统支持服务器资源实时监控、智能告警决策、资产分组管理及操作审计。

## 🚀 核心功能

### 1. 资产管理 (CMDB Lite)
- **服务器管理**：支持服务器的增删改查（CRUD），维护 IP、端口、描述等信息。
- **分组管理**：【新增】支持服务器按业务线或环境分组，便于批量管理。
- **多用户关联**：支持多对多权限分配，用户仅可查看被授权的服务器。

### 2. 监控与数据采集
- **Agent 上报**：提供 Python 编写的轻量级 Agent (`scripts/monitor_client.py`)，自动采集 CPU、内存、磁盘使用率。
- **高并发处理**：后端采用**异步线程池** (`ThreadPoolExecutor`) 处理监控数据上报，解耦入库与告警逻辑，提升接口吞吐量。
- **实时看板**：前端实时展示服务器资源水位。
- **趋势可视化**：【新增】集成 ECharts 图表库，提供服务器 CPU、内存、磁盘利用率的 24 小时历史趋势折线图，辅助运维人员精确定位故障时间点。

### 3. 企业级告警系统
- **动态阈值配置**：【新增】不再使用全局硬编码阈值，支持为每台服务器单独配置告警规则（CPU/内存/磁盘阈值、静默时间）。
- **告警记录**：【新增】完整记录历史告警信息 (`AlertHistory`)，便于故障复盘和 SLA 统计。
- **邮件通知**：触发阈值时自动发送邮件给关联负责人。

### 4. 安全与审计
- **操作审计**：【新增】关键操作（如删除服务器、修改规则）自动记录审计日志 (`AuditLog`)，满足合规要求。
- **API 安全**：
    - 管理后台：集成 JWT (JSON Web Token) 认证。
    - Agent 上报：支持 API Key 签名认证，防止恶意数据注入。

### 5. 智能决策系统
- **Dify集成**：集成 Dify 低代码平台，实现基于 LLM 的智能告警决策
- **多维度判断**：结合 CPU、内存、磁盘指标，以及历史趋势和相关日志进行综合判断
- **决策历史**：完整记录决策过程和结果，支持人工反馈优化
- **智能规则管理**：支持基于 Dify 工作流的智能规则配置

### 6. 日志管理系统
- **Elasticsearch集成**：使用 Elasticsearch 存储和检索日志
- **日志查询**：支持按服务器、日志类型、时间范围等多维度查询
- **日志统计**：提供日志级别分布和时间趋势统计
- **关联分析**：将日志与告警关联，辅助故障定位

### 7. 系统架构
- **后端**：Flask + SQLAlchemy + MySQL + Kafka + Redis + Flask-Restful (RESTful API 规范)
- **前端**：Vue 3 + Vite + Element Plus + ECharts (可视化图表)
- **存储**：MySQL (元数据) + Redis (实时数据) + Elasticsearch (日志数据)
- **消息队列**：Kafka (数据传输)
- **AI/低代码**：Dify (智能决策)
- **部署**：支持 Docker 容器化部署，包含 Dockerfile 与 docker-compose.yml。

## 📁 项目结构  

```
monitor_system/
├── app.py                    # Flask 应用入口
├── config/                   # 配置文件
│   └── setting.py                # 系统配置
├── model/                    # 数据模型层
│   ├── base.py                   # 数据库实例
│   ├── user.py                   # 用户模型
│   ├── server.py                 # 服务器与分组模型
│   ├── monitor.py                # 监控数据与告警模型（包含Dify决策模型）
│   ├── audit.py                  # 审计日志模型
│   └── associations.py           # 关联表
├── router/                   # API 路由层
│   ├── server.py                 # 服务器/分组管理接口
│   ├── monitor.py                # 监控数据接口
│   ├── alert.py                  # 告警管理接口
│   ├── user.py                   # 用户管理接口
│   ├── audit.py                  # 审计日志接口
│   ├── dify.py                   # Dify决策接口
│   ├── logs.py                   # 日志查询接口
│   └── __init__.py               # 路由注册
├── lib/                      # 核心工具库
│   ├── async_tasks.py            # 异步任务队列
│   ├── api_auth.py               # 签名认证
│   ├── jwt_utils.py              # JWT工具
│   └── response.py               # 响应工具
├── mail/                     # 邮件告警模块
│   └── alert.py                  # 告警邮件
├── services/                 # 业务服务
│   ├── dify_service.py           # Dify集成服务
│   └── log_service.py            # 日志服务
├── frontend/                 # Vue 3 前端源码
│   ├── src/                      # 源代码
│   │   ├── api/                  # API 调用
│   │   ├── views/                # 页面组件
│   │   │   ├── DifyDecisions.vue # Dify决策管理页面
│   │   │   └── LogSearch.vue     # 日志查询页面
│   │   └── router/               # 路由配置
│   └── package.json              # 前端依赖
├── scripts/                  # 运维脚本
│   ├── monitor_client.py         # 监控 Agent
│   ├── create_admin.py           # 创建管理员脚本
│   └── cleanup_data.py           # 数据清理脚本
├── migrations/               # 数据库迁移
├── docker-compose.yml        # 容器编排文件
├── requirements.txt          # Python 依赖
├── .env                      # 环境变量
└── docs/                     # 文档
```

## 🛠️ 快速开始

### 1. 环境准备
- Python 3.8+
- MySQL 5.7+ / 8.0
- Node.js 16+ (用于前端开发)

### 2. 后端部署
```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 配置环境变量
cp .env.example .env
# 修改 .env 中的数据库连接信息 (DB_HOST, DB_USER, DB_PASS...)

# 3. 初始化数据库
flask db upgrade

# 4. 创建管理员账号
python scripts/create_admin.py

# 5. 启动服务
python app.py
```

### 3. 前端启动
```bash
cd frontend
npm install
npm run dev
```

### 4. 启动监控 Agent
在目标服务器上运行：
```bash
# 修改脚本中的 API_URL 指向后端地址
python scripts/monitor_client.py
```

## 📝 开发计划

- [x] 服务器分组管理：后端支持分组API，前端Vue3实现了分组查询与创建。
- [x] 动态告警规则：后端逻辑支基于单台服务器的阈值判定。
- [x] 操作审计日志：核心操作（增删改）已集成 `AuditLog` 记录。
- [x] 历史趋势图表可视化：前端集成 `ECharts`，实现 CPU/内存/磁盘 24小时数据折线图。
- [x] 告警历史记录：告警触发后自动写入数据库，支持故障回溯。
- [x] 告警规则前端配置页面：支持规则增删改查及告警历史查询。



