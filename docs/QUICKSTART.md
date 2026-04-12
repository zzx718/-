# 快速开始指南

## 项目概述

基于云原生与Dify的分布式服务器智能管控平台。

## 技术栈

- **后端**: Flask, SQLAlchemy, Redis, Kafka
- **前端**: Vue3, Element Plus, ECharts
- **数据库**: MySQL, Redis, Elasticsearch
- **消息队列**: Kafka
- **AI/低代码**: Dify

---

## 目录结构

```
monitor_system-1/
├── app.py                 # 后端主入口
├── config/                # 配置文件
├── model/                 # 数据模型
├── router/                # API路由
├── services/              # 业务服务
├── migrations/            # 数据库迁移
├── frontend/              # 前端项目
├── docker-compose.yml     # Docker编排
├── requirements.txt       # Python依赖
└── .env.example           # 环境变量示例
```

---

## 一、环境准备

### 1.1 安装Docker Desktop

- Windows: https://www.docker.com/products/docker-desktop/
- Linux: 安装Docker Engine和Docker Compose

### 1.2 验证Docker

```bash
docker --version
docker-compose --version
```

---

## 二、启动基础设施

### 2.1 启动所有服务

```bash
docker-compose up -d
```

这会启动：
- MySQL (端口 3306)
- Redis (端口 6379)
- Kafka (端口 9092)
- ZooKeeper
- Elasticsearch (端口 9200)
- Kibana (端口 5601)

### 2.2 查看服务状态

```bash
docker-compose ps
```

### 2.3 查看日志

```bash
docker-compose logs -f
```

---

## 三、后端配置

### 3.1 配置环境变量

```bash
# 复制环境变量示例
cp .env.example .env
```

编辑 `.env` 文件，填写以下配置：

```env
# Flask配置
DEBUG=True
HOST=0.0.0.0
PORT=5000

# 数据库配置
DB_HOST=127.0.0.1
DB_USER=root
DB_PASS=password
DB_PORT=3306
DATABASE=monitor

# 安全配置
SECRET_KEY=your-secret-key
JWT_SECRET_KEY=your-jwt-secret-key

# 邮件配置
SMTP_HOST=smtp.example.com
SMTP_PORT=465
SMTP_USER=user@example.com
SMTP_PASS=password
SMTP_SENDER=user@example.com

# Dify配置
DIFY_API_URL=https://api.dify.ai/v1
DIFY_API_KEY=your-dify-api-key
DIFY_WORKFLOW_ID=your-dify-workflow-id

# Elasticsearch配置
ES_HOST=localhost
ES_PORT=9200
ES_USERNAME=
ES_PASSWORD=
ES_USE_SSL=False
```

### 3.2 安装Python依赖

```bash
# 推荐使用虚拟环境
python -m venv venv

# Windows激活虚拟环境
venv\Scripts\activate

# Linux/Mac激活虚拟环境
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

### 3.3 初始化数据库

```bash
# 创建数据库表
flask db upgrade
```

### 3.4 启动后端服务

```bash
python app.py
```

后端将在 `http://localhost:5000` 启动

---

## 四、前端配置

### 4.1 安装Node.js依赖

```bash
cd frontend
npm install
```

### 4.2 启动开发服务器

```bash
npm run dev
```

前端将在 `http://localhost:5173` 启动

### 4.3 构建生产版本

```bash
npm run build
```

---

## 五、Dify配置

### 5.1 注册Dify账号

访问 https://dify.ai 注册账号

### 5.2 创建工作流

1. 登录Dify平台
2. 进入「工作室」→「工作流」
3. 点击「创建空白工作流」
4. 按照 `DIFY_WORKFLOW_GUIDE.md` 配置工作流

### 5.3 获取API Key

1. 进入工作流详情页
2. 点击「API访问」
3. 复制API Key和Workflow ID

### 5.4 配置到.env

将获取的API Key和Workflow ID填写到 `.env` 文件：

```env
DIFY_API_KEY=your-api-key
DIFY_WORKFLOW_ID=your-workflow-id
```

---

## 六、使用说明

### 6.1 访问系统

- 前端: http://localhost:5173
- 后端API: http://localhost:5000
- Kibana: http://localhost:5601

### 6.2 默认账号

系统首次启动需要注册用户，或在数据库中手动添加。

### 6.3 监控客户端

在需要监控的服务器上运行监控客户端：

```bash
python scripts/monitor_client.py
```

---

## 七、常见问题

### 7.1 Docker服务启动失败

```bash
# 查看详细日志
docker-compose logs <service-name>
```

### 7.2 数据库连接失败

检查 `.env` 中的数据库配置是否正确，确认MySQL容器是否正常运行。

### 7.3 前端无法访问后端

检查前端 `vite.config.js` 中的代理配置是否正确。

---

## 八、下一步

- 阅读 `DEVELOPMENT.md` 了解开发规范
- 阅读 `DIFY_WORKFLOW_GUIDE.md` 配置Dify工作流
- 阅读 `API.md` 了解API接口
