# Flask 企业级服务器监控系统 (Monitor System)

基于 Flask + Vue 3 开发的现代化服务器监控平台，旨在为中小型企业提供轻量级、可扩展的 IT 基础设施监控解决方案。系统支持服务器资源实时监控、精细化告警策略、资产分组管理及操作审计。

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

### 5. 系统架构
- **后端**：Flask + SQLAlchemy + MySQL + Flask-Restful (RESTful API 规范)
- **前端**：Vue 3 + Vite + ECharts (可视化图表) + 原生 CSS (轻量化无外部 UI 库)
- **部署**：支持 Docker 容器化部署，包含 Dockerfile 与 docker-compose.yml。

## 📁 项目结构  

```
monitor_system/
├── app.py                    # Flask 应用入口
├── config/                   # 配置文件
├── model/                    # 数据模型层 (Refactored)
│   ├── base.py                   # 数据库实例
│   ├── user.py                   # 用户模型
│   ├── server.py                 # 服务器与分组模型
│   ├── monitor.py                # 监控数据与告警模型
│   ├── audit.py                  # 审计日志模型
│   └── associations.py           # 关联表
├── router/                   # API 路由层
│   ├── server.py                 # 服务器/分组管理接口
│   ├── monitor.py                # 监控数据接口
│   └── ...
├── lib/                      # 核心工具库
│   ├── async_tasks.py            # 异步任务队列
│   └── api_auth.py               # 签名认证
├── mail/                     # 邮件告警模块
├── frontend/                 # Vue 3 前端源码
├── scripts/                  # 运维脚本
│   ├── monitor_client.py         # 监控 Agent
│   ├── create_admin.py           # 创建管理员脚本
│   └── cleanup_data.py           # 数据清理脚本
├── docker-compose.yml        # 容器编排文件
└── requirements.txt          # Python 依赖
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



