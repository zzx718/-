# 开发设计文档

## 目录
1. [项目概述](#一项目概述)
2. [技术栈](#二技术栈)
3. [项目结构详解](#三项目结构详解)
4. [开发环境搭建](#四开发环境搭建)
5. [后端开发指南](#五后端开发指南)
6. [前端开发指南](#六前端开发指南)
7. [数据库设计](#七数据库设计)
8. [API接口规范](#八api接口规范)
9. [代码规范](#九代码规范)
10. [测试指南](#十测试指南)
11. [部署指南](#十一部署指南)

---

## 一、项目概述

### 1.1 项目简介
本项目是一个**基于云原生与Dify的分布式服务器智能管控平台**，采用Flask+Vue3技术栈，集成ELK日志栈和Dify低代码平台，实现智能告警与辅助决策。

### 1.2 核心功能模块

| 模块 | 说明 |
|------|------|
| **监控数据采集** | Agent采集CPU、内存、磁盘，30秒上报一次 |
| **数据存储** | MySQL存监控/告警数据，ES存日志，Redis做缓存 |
| **智能告警** | 持续告警判断 + Dify工作流决策 |
| **日志分析** | ELK日志栈，支持全文检索和可视化 |
| **前端展示** | Vue3 + ECharts，实时监控、日志检索、决策记录 |

### 1.3 开发原则

- **先设计后开发**：完善设计文档再编码
- **模块化设计**：高内聚低耦合
- **异常降级**：关键功能要有降级方案
- **可追溯性**：所有重要操作要有日志记录

---

## 二、技术栈

### 2.1 后端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Python | 3.8+ | 开发语言 |
| Flask | 2.3.3 | Web框架 |
| Flask-SQLAlchemy | 3.0.5 | ORM框架 |
| Flask-Migrate | 4.0.5 | 数据库迁移 |
| Flask-JWT-Extended | 4.5.2 | JWT认证 |
| Flask-CORS | 4.0.0 | 跨域处理 |
| SQLAlchemy | 2.0.21 | ORM核心 |
| PyMySQL | 1.1.0 | MySQL驱动 |
| Elasticsearch | 8.11.0 | 日志搜索引擎 |
| APScheduler | 3.10.4 | 定时任务 |
| Flask-Mail | 0.9.1 | 邮件发送 |
| Gunicorn | 21.2.0 | WSGI服务器 |

### 2.2 前端技术栈

| 技术 | 版本 | 用途 |
|------|------|------|
| Vue | 3.x | 前端框架 |
| Vite | - | 构建工具 |
| Vue Router | - | 路由管理 |
| Pinia | - | 状态管理 |
| ECharts | - | 图表可视化 |
| Axios | - | HTTP客户端 |

### 2.3 基础设施

| 技术 | 版本 | 用途 |
|------|------|------|
| MySQL | 8.0 | 关系型数据库 |
| Redis | - | 缓存/消息队列 |
| Elasticsearch | 8.11.0 | 全文搜索引擎 |
| Kibana | 8.11.0 | 日志可视化 |
| Docker | - | 容器化 |
| Docker Compose | - | 容器编排 |

---

## 三、项目结构详解

```
monitor_system-1/
├── app.py                          # Flask应用入口
├── config/
│   └── setting.py                  # 配置文件
├── model/                          # 数据模型层
│   ├── __init__.py
│   ├── base.py                     # 数据库基类
│   ├── user.py                     # 用户模型
│   ├── server.py                   # 服务器模型
│   ├── monitor.py                  # 监控数据/告警模型
│   ├── audit.py                    # 审计日志模型
│   └── associations.py             # 关联表
├── router/                         # API路由层
│   ├── __init__.py
│   ├── auth.py                     # 认证接口
│   ├── user.py                     # 用户管理接口
│   ├── server.py                   # 服务器管理接口
│   ├── monitor.py                  # 监控数据接口
│   ├── alert.py                    # 告警管理接口
│   ├── audit.py                    # 审计日志接口
│   └── logs.py                     # 日志查询接口（待开发）
├── services/                       # 业务服务层
│   ├── __init__.py
│   ├── dify_service.py             # Dify集成服务（待开发）
│   └── log_service.py              # 日志服务（已删除，设计阶段）
├── lib/                            # 工具库
│   ├── api_auth.py                 # API签名认证
│   ├── async_tasks.py              # 异步任务
│   ├── jwt_utils.py                # JWT工具
│   └── response.py                 # 统一响应格式
├── mail/                           # 邮件模块
│   └── alert.py                    # 告警邮件
├── migrations/                     # 数据库迁移
│   ├── versions/
│   └── alembic.ini
├── scripts/                        # 脚本工具
│   ├── monitor_client.py           # 监控Agent
│   ├── create_admin.py             # 创建管理员
│   └── cleanup_data.py             # 清理旧数据
├── frontend/                       # 前端项目
│   ├── src/
│   │   ├── views/                  # 页面组件
│   │   ├── api/                    # API调用
│   │   ├── stores/                 # 状态管理
│   │   └── router/                 # 路由配置
│   └── package.json
├── .env.example                    # 环境变量示例
├── requirements.txt                # Python依赖
├── docker-compose.yml              # Docker编排
├── Dockerfile                      # 后端Dockerfile
├── DESIGN.md                       # 系统设计文档
├── FUNCTION_FLOW.md                # 功能流转文档
└── DEVELOPMENT.md                  # 本文档
```

### 3.1 目录职责说明

| 目录 | 职责 |
|------|------|
| `model/` | 只负责数据库表定义和基础CRUD，不包含业务逻辑 |
| `router/` | API路由层，负责参数校验、调用service、返回响应 |
| `services/` | 业务逻辑层，核心业务逻辑在此 |
| `lib/` | 通用工具，可被任意模块调用 |
| `mail/` | 邮件相关功能 |
| `scripts/` | 运维脚本 |

---

## 四、开发环境搭建

### 4.1 环境要求

- Python 3.8+
- Node.js 16+
- Docker & Docker Compose (可选，用于容器化部署)
- MySQL 8.0+
- Redis (可选)
- Elasticsearch 8.11.0+ (可选，用于日志功能)

### 4.2 后端环境搭建

#### 步骤1：克隆项目
```bash
cd d:\MyProjects\毕设\monitor_system-1
```

#### 步骤2：创建虚拟环境（推荐）
```bash
python -m venv venv
venv\Scripts\activate
```

#### 步骤3：安装依赖
```bash
pip install -r requirements.txt
```

#### 步骤4：配置环境变量
```bash
copy .env.example .env
```

编辑 `.env` 文件，配置数据库连接等信息。

#### 步骤5：初始化数据库
```bash
flask db upgrade
```

#### 步骤6：创建管理员
```bash
python scripts/create_admin.py
```

#### 步骤7：启动后端服务
```bash
python app.py
```

后端服务将在 `http://localhost:5000` 启动。

### 4.3 前端环境搭建

#### 步骤1：进入前端目录
```bash
cd frontend
```

#### 步骤2：安装依赖
```bash
npm install
```

#### 步骤3：启动开发服务器
```bash
npm run dev
```

前端服务将在 `http://localhost:5173` 启动（Vite默认端口）。

### 4.4 Docker环境搭建（可选）

如果使用Docker Compose一键启动所有服务：

```bash
docker-compose up -d
```

这将启动：
- backend: Flask后端
- frontend: Vue3前端
- db: MySQL数据库
- elasticsearch: Elasticsearch
- kibana: Kibana

---

## 五、后端开发指南

### 5.1 新增API接口开发流程

#### 步骤1：定义数据模型（如需要）
在 `model/` 目录下创建或修改模型文件。

示例（model/example.py）：
```python
from .base import db
from datetime import datetime

class Example(db.Model):
    __tablename__ = 'examples'
    
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.now)
    
    @classmethod
    def create(cls, name):
        example = cls(name=name)
        db.session.add(example)
        db.session.commit()
        return example
```

#### 步骤2：创建数据库迁移
```bash
flask db migrate -m "add_examples_table"
flask db upgrade
```

#### 步骤3：创建Service层（如需要）
在 `services/` 目录下创建业务逻辑。

#### 步骤4：创建API路由
在 `router/` 目录下创建路由文件。

示例（router/example.py）：
```python
from flask import request
from flask_restful import Resource
from lib.response import response
from model import Example
from lib.jwt_utils import admin_required

class ExampleAPI(Resource):
    @admin_required
    def get(self):
        examples = Example.query.all()
        data = [{'id': e.id, 'name': e.name} for e in examples]
        return response(data=data)
    
    @admin_required
    def post(self):
        data = request.json
        name = data.get('name')
        example = Example.create(name)
        return response(data={'id': example.id})
```

#### 步骤5：注册路由
在 `router/__init__.py` 中注册新路由。

### 5.2 统一响应格式

所有API接口必须使用 `lib.response.response()` 函数返回统一格式：

```python
from lib.response import response

# 成功响应
return response(data={'key': 'value'}, message='操作成功')

# 失败响应
return response(code=400, message='参数错误')
```

响应格式：
```json
{
  "code": 0,
  "message": "成功",
  "data": {}
}
```

### 5.3 认证与授权

| 认证方式 | 用途 | 装饰器 |
|---------|------|--------|
| JWT | 管理后台用户 | `@admin_required` |
| API Key | Agent上报数据 | `@api_key_required` |

### 5.4 异步任务处理

使用 `lib.async_tasks.executor` 处理耗时任务：

```python
from lib.async_tasks import executor, async_process_monitor_data

executor.submit(
    async_process_monitor_data,
    app,
    server_ip,
    metrics
)
```

---

## 六、前端开发指南

### 6.1 新增页面开发流程

#### 步骤1：创建页面组件
在 `frontend/src/views/` 目录下创建Vue组件。

示例（frontend/src/views/ExampleView.vue）：
```vue
<template>
  <div class="example-view">
    <h1>示例页面</h1>
  </div>
</template>

<script setup>
</script>

<style scoped>
</style>
```

#### 步骤2：配置路由
在 `frontend/src/router/index.js` 中添加路由。

#### 步骤3：添加API调用（如需要）
在 `frontend/src/api/index.js` 中添加API函数。

### 6.2 API调用规范

使用封装好的API函数：

```javascript
import { getExamples, createExample } from '@/api'

// 获取列表
const fetchData = async () => {
  const res = await getExamples()
  if (res.code === 0) {
    console.log(res.data)
  }
}

// 创建
const handleCreate = async () => {
  const res = await createExample({ name: 'test' })
  if (res.code === 0) {
    alert('创建成功')
  }
}
```

### 6.3 状态管理

使用Pinia进行状态管理，在 `frontend/src/stores/` 中定义store。

---

## 七、数据库设计

### 7.1 核心表结构

#### users表（用户表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| username | VARCHAR | 用户名 |
| email | VARCHAR | 邮箱 |
| password_hash | VARCHAR | 密码哈希 |
| is_admin | BOOLEAN | 是否管理员 |
| created_at | DATETIME | 创建时间 |

#### servers表（服务器表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| server_name | VARCHAR | 服务器名称 |
| ip_address | VARCHAR | IP地址 |
| description | TEXT | 描述 |
| created_at | DATETIME | 创建时间 |

#### monitor_data表（监控数据表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| server_id | INT | 服务器ID（外键） |
| cpu_value | DECIMAL | CPU使用率 |
| memory_value | DECIMAL | 内存使用率 |
| disk_value | DECIMAL | 磁盘使用率 |
| recorded_at | DATETIME | 记录时间（索引） |

#### alert_rules表（告警规则表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| server_id | INT | 服务器ID（外键） |
| metric_type | ENUM | 指标类型（cpu/memory/disk） |
| threshold | DECIMAL | 阈值 |
| silence_minutes | INT | 静默时间（分钟） |
| is_enabled | BOOLEAN | 是否启用 |

#### alert_history表（告警历史表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| server_id | INT | 服务器ID（外键） |
| metric_type | VARCHAR | 告警指标 |
| current_value | DECIMAL | 当前值 |
| threshold_snapshot | DECIMAL | 阈值快照 |
| alert_content | TEXT | 告警内容 |
| status | ENUM | 状态（firing/resolved/ignored） |
| triggered_at | DATETIME | 触发时间 |
| resolved_at | DATETIME | 恢复时间 |

#### audit_logs表（审计日志表）
| 字段 | 类型 | 说明 |
|------|------|------|
| id | INT | 主键 |
| user_id | INT | 用户ID（外键） |
| action | VARCHAR | 操作类型 |
| resource_type | VARCHAR | 资源类型 |
| resource_id | INT | 资源ID |
| details | TEXT | 详情 |
| created_at | DATETIME | 创建时间 |

### 7.2 新增表（待开发）

#### dify_decisions表（Dify决策记录表）
详见 DESIGN.md 3.2节。

#### smart_alert_rules表（智能告警规则表）
详见 DESIGN.md 3.3节。

---

## 八、API接口规范

### 8.1 接口命名规范

- 使用RESTful风格
- 名词复数形式
- 小写，用连字符分隔

示例：
- `GET /api/servers` - 获取服务器列表
- `POST /api/servers` - 创建服务器
- `GET /api/servers/1` - 获取服务器详情
- `PUT /api/servers/1` - 更新服务器
- `DELETE /api/servers/1` - 删除服务器

### 8.2 HTTP状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

### 8.3 业务错误码

| code | 说明 |
|------|------|
| 0 | 成功 |
| 400 | 参数错误 |
| 401 | 未授权 |
| 403 | 禁止访问 |
| 404 | 不存在 |
| 500 | 服务器错误 |

### 8.4 现有接口列表

详见 router/ 目录下的各路由文件。

---

## 九、代码规范

### 9.1 Python代码规范

- 遵循PEP 8规范
- 使用4空格缩进
- 函数和变量使用蛇形命名（snake_case）
- 类名使用大驼峰命名（CamelCase）
- 常量使用全大写下划线分隔（UPPER_CASE）

### 9.2 Git提交规范

```
<type>(<scope>): <subject>

< body >

<footer>
```

type类型：
- feat: 新功能
- fix: 修复bug
- docs: 文档更新
- style: 代码格式调整
- refactor: 重构
- test: 测试相关
- chore: 构建/工具链相关

示例：
```
feat(alert): add Dify integration for smart alerting

- Add dify_service.py
- Update alert.py to support Dify workflow
- Add dify_decisions table

Closes #123
```

---

## 十、测试指南

### 10.1 单元测试（待添加）

使用pytest进行单元测试。

### 10.2 接口测试

使用Postman或curl测试API接口。

### 10.3 手动测试清单

- [ ] 用户登录/登出
- [ ] 服务器CRUD
- [ ] 监控数据上报
- [ ] 告警规则配置
- [ ] 告警触发
- [ ] 邮件发送
- [ ] 日志查询（待开发）
- [ ] Dify决策（待开发）

---

## 十一、部署指南

### 11.1 Docker Compose部署

```bash
# 构建并启动所有服务
docker-compose up -d

# 查看日志
docker-compose logs -f

# 停止服务
docker-compose down
```

### 11.2 环境变量配置

复制 `.env.example` 为 `.env` 并修改配置：

```env
FLASK_APP=app.py
FLASK_DEBUG=0
SQLALCHEMY_DATABASE_URI=mysql+pymysql://root:password@db:3306/monitor_system
ELASTICSEARCH_HOST=elasticsearch
ELASTICSEARCH_PORT=9200
DIFY_API_URL=https://api.dify.ai/v1
DIFY_API_KEY=your-dify-api-key
DIFY_WORKFLOW_ID=your-workflow-id
```

### 11.3 生产环境注意事项

- 关闭FLASK_DEBUG
- 使用Gunicorn替代Flask开发服务器
- 配置HTTPS
- 定期备份数据库
- 配置日志轮转
- 设置监控告警

---

## 附录

### A. 参考文档

- [Flask官方文档](https://flask.palletsprojects.com/)
- [Vue3官方文档](https://vuejs.org/)
- [Elasticsearch官方文档](https://www.elastic.co/guide/en/elasticsearch/reference/)
- [Dify官方文档](https://docs.dify.ai/)

### B. 常见问题

#### Q: 数据库迁移失败怎么办？
A: 检查数据库连接配置，确认数据库已启动。

#### Q: 如何重置数据库？
A: 删除migrations/versions/下的迁移文件，重新执行flask db init和flask db migrate。

#### Q: Elasticsearch连接失败？
A: 确认ES容器已启动，检查ELASTICSEARCH_HOST和ELASTICSEARCH_PORT配置。

---

**文档版本**: v1.0  
**最后更新**: 2026-03-22
