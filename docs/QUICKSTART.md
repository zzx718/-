# 快速开始指南

## 项目概述

基于云原生与Dify的分布式服务器智能管控平台。

## 技术栈

- **后端**: Flask, SQLAlchemy, Redis, Kafka
- **前端**: Vue3, Element Plus, ECharts
- **数据库**: MySQL, Redis, Elasticsearch
- **消息队列**: Kafka (KRaft模式)
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

## 一、环境架构说明（调试阶段）

本项目采用**混合架构**：

- **开发环境**: Windows本地电脑
  - 运行后端代码 (Flask)
  - 运行前端代码 (Vue3)
  - 代码编辑和调试

- **基础设施环境**: Linux虚拟机 (IP: 192.168.245.111, CentOS)
  - 运行Docker容器
  - 提供MySQL、Redis、Kafka、Elasticsearch等中间件服务

---

## 二、虚拟机环境准备 (CentOS)

### 2.1 登录到Linux虚拟机

通过SSH客户端连接：
```bash
# Windows使用SSH客户端连接
ssh root@192.168.245.111

# 输入密码登录
```

### 2.2 安装必要的软件 (CentOS)

```bash
# 更新系统
yum update -y

# 安装基础软件
yum install -y git curl wget

# 安装Docker
yum install -y docker

# 配置Docker国内镜像源（加速镜像拉取）
mkdir -p /etc/docker
cat > /etc/docker/daemon.json << EOF
{
  "registry-mirrors": [
    "https://docker.1ms.run",
    "https://docker.1panel.live/"
  ]
}
EOF

# 重启Docker服务
systemctl daemon-reload
systemctl restart docker

# 启动Docker服务
systemctl start docker
systemctl enable docker

# 验证安装
docker --version
docker compose --version

# 验证镜像源配置
docker info | grep Registry
```

### 2.3 复制Docker Compose文件

在Windows上：
```bash
# 将docker-compose.yml复制到虚拟机
scp docker-compose.yml root@192.168.245.111:/root/
```

### 2.4 启动基础设施服务

在虚拟机上：
```bash
# 进入目录
cd /root

# 启动所有服务
docker compose up -d

# 查看服务状态
docker compose ps

# 查看日志
docker compose logs -f
```

**服务列表**：
- MySQL (端口 3306)
- Redis (端口 6379)
- Kafka (端口 9092, KRaft模式)
- Elasticsearch (端口 9200)
- Kibana (端口 5601)

### 2.5 验证服务启动

在虚拟机上：
```bash
# 验证MySQL
docker exec -it monitor-mysql mysql -u root -ppassword -e "SELECT VERSION();"

# 验证Redis
docker exec -it monitor-redis redis-cli ping

# 验证Elasticsearch
curl http://localhost:9200

# 验证Kafka，列出当前 Kafka 集群中所有的 Topic（主题），输出为空则成功
docker exec -it monitor-kafka kafka-topics --list --bootstrap-server localhost:9092
```

---

## 三、本地开发环境配置 (Windows)

### 3.1 配置环境变量

```bash
# 复制环境变量示例
copy .env.example .env

# 编辑环境变量文件
# 使用文本编辑器打开 .env 文件
```

填写以下配置：

```env
# Flask配置
DEBUG=True
HOST=0.0.0.0
PORT=5000

# 数据库配置 - 指向虚拟机
DB_HOST=192.168.245.111
DB_USER=root
DB_PASS=password
DB_PORT=3306
DATABASE=monitor

# Redis配置 - 指向虚拟机
REDIS_HOST=192.168.245.111
REDIS_PORT=6379

# Kafka配置 - 指向虚拟机
KAFKA_BOOTSTRAP_SERVERS=192.168.245.111:9092

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

# Elasticsearch配置 - 指向虚拟机
ES_HOST=192.168.245.111
ES_PORT=9200
ES_USERNAME=
ES_PASSWORD=
ES_USE_SSL=False
```

### 3.2 安装Python依赖

```bash
# 创建虚拟环境
python -m venv .venv

# 激活虚拟环境
.venv\Scripts\activate

# 升级pip
python -m pip install --upgrade pip

# 安装依赖
pip install -r requirements.txt
```

### 3.3 初始化数据库

```bash
# 初始化数据库迁移
flask db init

# 生成迁移文件
flask db migrate -m "Initial migration"

# 执行数据库迁移
flask db upgrade
```

### 3.4 启动后端服务

```bash
# 启动后端（调试模式）
python app.py
```

后端将在 `http://localhost:5000` 启动

---

## 四、前端配置 (Windows)

### 4.1 安装Node.js依赖

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install
```

### 4.2 启动开发服务器

```bash
# 启动前端开发服务器（调试模式）
npm run dev
```

前端将在 `http://localhost:5173` 启动

### 4.3 构建生产版本

```bash
# 构建生产版本
npm run build

# 构建结果在 dist 目录
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

编辑 `.env` 文件，填写Dify配置：

```env
DIFY_API_KEY=your-api-key
DIFY_WORKFLOW_ID=your-workflow-id
```

---

## 六、服务访问地址

| 服务 | 地址 | 说明 |
|------|------|------|
| 前端页面 | http://localhost:5173 | Windows本地访问 |
| 后端API | http://localhost:5000 | Windows本地访问 |
| Kibana | http://192.168.245.111:5601 | 虚拟机访问 |
| Elasticsearch | http://192.168.245.111:9200 | 虚拟机访问 |
| MySQL | 192.168.245.111:3306 | 虚拟机访问 |
| Redis | 192.168.245.111:6379 | 虚拟机访问 |
| Kafka | 192.168.245.111:9092 | 虚拟机访问 |

---

## 七、默认账号

系统首次启动时，会自动创建默认管理员账号：

- **用户名**: admin
- **密码**: 123456

---

## 八、监控客户端

在需要监控的服务器上运行监控客户端：

```bash
# 在目标服务器上运行
python scripts/monitor_client.py
```

---

## 九、常见问题及解决方案

### 9.1 Docker服务启动失败

**问题**：Docker服务未运行
**解决方案**（在虚拟机上）：
```bash
# 启动Docker服务
systemctl start docker

# 查看Docker状态
systemctl status docker
```

### 9.2 数据库连接失败

**问题**：后端无法连接到MySQL
**解决方案**：
1. 检查虚拟机上的MySQL容器是否运行：`docker compose ps | grep mysql`
2. 检查 `.env` 文件中的数据库配置是否正确（IP地址是否为192.168.245.111）
3. 检查网络连接：在Windows上执行 `ping 192.168.245.111`
4. 检查虚拟机防火墙是否允许3306端口：`firewall-cmd --list-ports`

### 9.3 前端无法访问后端

**问题**：前端请求后端API失败
**解决方案**：
1. 检查后端服务是否运行：`http://localhost:5000/api/health`
2. 检查前端 `vite.config.js` 中的代理配置
3. 检查CORS配置是否正确

### 9.4 Kafka连接失败

**问题**：后端无法连接到Kafka
**解决方案**：
1. 检查Kafka容器是否运行：`docker compose ps | grep kafka`
2. 检查Kafka日志：`docker compose logs kafka`
3. 验证Kafka端口：在Windows上执行 `telnet 192.168.245.111 9092`

### 9.5 Elasticsearch连接失败

**问题**：后端无法连接到Elasticsearch
**解决方案**：
1. 检查ES容器是否运行：`docker compose ps | grep elasticsearch`
2. 检查ES状态：`curl http://192.168.245.111:9200`
3. 检查ES日志：`docker compose logs elasticsearch`

---

## 十、调试技巧

### 10.1 后端调试

- 后端启动时会显示调试器PIN码，可用于远程调试
- 查看后端控制台输出获取详细错误信息
- 使用 `curl` 测试API接口：
  ```bash
  curl http://localhost:5000/api/servers
  ```

### 10.2 前端调试

- 使用浏览器开发者工具查看网络请求
- 查看控制台日志获取错误信息
- 使用Vue DevTools进行Vue组件调试

### 10.3 虚拟机服务调试

- 查看容器日志：`docker compose logs <service-name>`
- 进入容器内部：`docker exec -it <container-id> bash`
- 检查容器网络：`docker network inspect monitor-net`

---

## 十一、服务管理

### 11.1 启动所有服务

**虚拟机上**：
```bash
# 启动Docker服务
docker compose up -d
```

**Windows上**：
```bash
# 启动后端服务
.venv\Scripts\activate
python app.py

# 启动前端服务（新终端）
cd frontend
npm run dev
```

### 11.2 停止所有服务

**虚拟机上**：
```bash
# 停止Docker服务
docker compose down
```

**Windows上**：
- 按 Ctrl+C 停止后端和前端服务

### 11.3 重启服务

**虚拟机上**：
```bash
# 重启Docker服务
docker compose restart
```

**Windows上**：
- 重启后端和前端服务

---

## 十二、下一步

- 阅读 `DEVELOPMENT.md` 了解开发规范
- 阅读 `DIFY_WORKFLOW_GUIDE.md` 配置Dify工作流
- 阅读 `API.md` 了解API接口
- 阅读 `DEPLOYMENT.md` 了解部署方案

---

## 十三、技术支持

如果遇到问题，请参考以下资源：

1. 查看项目文档
2. 检查服务日志
3. 确认网络连接
4. 验证配置文件

---

**🎉 系统搭建完成！开始使用你的分布式服务器智能管控平台吧！**