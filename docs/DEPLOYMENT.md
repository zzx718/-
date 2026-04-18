# 部署指南

## 概述

本文档说明如何将项目部署到生产环境。

---

## 目录

- [环境要求](#环境要求)
- [Docker部署](#docker部署)
- [手动部署](#手动部署)
- [生产环境优化](#生产环境优化)
- [监控与运维](#监控与运维)

---

## 环境要求

### 服务器配置

| 配置项 | 最低配置 | 推荐配置 |
|--------|----------|----------|
| CPU | 2核 | 4核+ |
| 内存 | 4GB | 8GB+ |
| 磁盘 | 40GB | 100GB+ |
| 操作系统 | Linux (Ubuntu/CentOS) | Linux (Ubuntu 22.04) |

### 软件要求

- Docker 20.10+
- Docker Compose 2.0+
- (可选) Nginx 1.20+

---

## Docker部署

### 1. 克隆代码

```bash
git clone https://github.com/your-username/your-repo.git
cd monitor_system-1
```

### 2. 配置环境变量

```bash
# 复制环境变量模板
cp .env.example .env

# 编辑环境变量
vim .env
```

**重要配置项**:

```env
# 生产环境必须关闭DEBUG
DEBUG=False

# 使用强密钥
SECRET_KEY=your-strong-secret-key-here
JWT_SECRET_KEY=your-strong-jwt-key-here

# 数据库配置（使用Docker内部网络）
DB_HOST=mysql
DB_USER=root
DB_PASS=your-strong-mysql-password

# Dify配置
DIFY_API_KEY=your-dify-api-key
DIFY_WORKFLOW_ID=your-dify-workflow-id

# Elasticsearch配置
ES_HOST=elasticsearch
ES_PORT=9200
```

### 3. 修改docker-compose.yml（生产环境）

创建 `docker-compose.prod.yml`:

```yaml
version: '3.8'

services:
  mysql:
    image: mysql:8.0
    restart: always
    environment:
      MYSQL_ROOT_PASSWORD: ${DB_PASS}
      MYSQL_DATABASE: ${DATABASE}
    volumes:
      - mysql_data:/var/lib/mysql
    networks:
      - monitor-net

  redis:
    image: redis:7-alpine
    restart: always
    volumes:
      - redis_data:/data
    networks:
      - monitor-net

  kafka:
    image: confluentinc/cp-kafka:7.5.0
    restart: always
    environment:
      KAFKA_PROCESS_ROLES: broker,controller
      KAFKA_CONTROLLER_QUORUM_VOTERS: 1@kafka:9093
      KAFKA_LISTENERS: PLAINTEXT://0.0.0.0:9092,CONTROLLER://0.0.0.0:9093,PLAINTEXT_HOST://0.0.0.0:29092
      KAFKA_ADVERTISED_LISTENERS: PLAINTEXT://kafka:9092,PLAINTEXT_HOST://localhost:29092
      KAFKA_LISTENER_SECURITY_PROTOCOL_MAP: PLAINTEXT:PLAINTEXT,CONTROLLER:PLAINTEXT,PLAINTEXT_HOST:PLAINTEXT
      KAFKA_INTER_BROKER_LISTENER_NAME: PLAINTEXT
      KAFKA_OFFSETS_TOPIC_REPLICATION_FACTOR: 1
      KAFKA_TRANSACTION_STATE_LOG_MIN_ISR: 1
      KAFKA_TRANSACTION_STATE_LOG_REPLICATION_FACTOR: 1
      KAFKA_AUTO_CREATE_TOPICS_ENABLE: "true"
    volumes:
      - kafka_data:/var/lib/kafka/data
    networks:
      - monitor-net

  elasticsearch:
    image: docker.elastic.co/elasticsearch/elasticsearch:8.11.0
    restart: always
    environment:
      - discovery.type=single-node
      - xpack.security.enabled=false
      - "ES_JAVA_OPTS=-Xms1g -Xmx1g"
    volumes:
      - es_data:/usr/share/elasticsearch/data
    networks:
      - monitor-net

  kibana:
    image: docker.elastic.co/kibana/kibana:8.11.0
    restart: always
    depends_on:
      - elasticsearch
    environment:
      - ELASTICSEARCH_HOSTS=http://elasticsearch:9200
    networks:
      - monitor-net

  backend:
    build:
      context: .
      dockerfile: Dockerfile.backend
    restart: always
    depends_on:
      - mysql
      - redis
      - kafka
      - elasticsearch
    environment:
      - DB_HOST=mysql
      - REDIS_HOST=redis
      - KAFKA_BOOTSTRAP_SERVERS=kafka:9092
      - ES_HOST=elasticsearch
    env_file:
      - .env
    ports:
      - "5000:5000"
    networks:
      - monitor-net

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    restart: always
    depends_on:
      - backend
    ports:
      - "80:80"
    networks:
      - monitor-net

volumes:
  mysql_data:
  redis_data:
  kafka_data:
  es_data:

networks:
  monitor-net:
    driver: bridge
```

### 4. 创建后端Dockerfile

创建 `Dockerfile.backend`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y \
    gcc \
    default-libmysqlclient-dev \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# 复制依赖文件
COPY requirements.txt .

# 安装Python依赖
RUN pip install --no-cache-dir -r requirements.txt

# 复制应用代码
COPY . .

# 暴露端口
EXPOSE 5000

# 启动命令
CMD ["sh", "-c", "flask db upgrade && python app.py"]
```

### 5. 启动所有服务

```bash
# 使用生产环境配置启动
docker-compose -f docker-compose.prod.yml up -d

# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f
```

---

## 手动部署

### 1. 后端部署

#### 1.1 安装Python依赖

```bash
# 创建虚拟环境
python -m venv venv
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt
```

#### 1.2 配置环境变量

```bash
cp .env.example .env
# 编辑 .env 文件
```

#### 1.3 初始化数据库

```bash
flask db upgrade
```

#### 1.4 使用Gunicorn部署

```bash
# 安装Gunicorn
pip install gunicorn

# 启动服务
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

#### 1.5 使用Systemd管理服务

创建 `/etc/systemd/system/monitor-backend.service`:

```ini
[Unit]
Description=Monitor Backend Service
After=network.target

[Service]
Type=notify
User=www-data
WorkingDirectory=/path/to/monitor_system-1
Environment="PATH=/path/to/venv/bin"
ExecStart=/path/to/venv/bin/gunicorn -w 4 -b 0.0.0.0:5000 app:app
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务:

```bash
systemctl daemon-reload
systemctl enable monitor-backend
systemctl start monitor-backend
systemctl status monitor-backend
```

---

### 2. 前端部署

#### 2.1 构建前端

```bash
cd frontend
npm install
npm run build
```

#### 2.2 使用Nginx部署

创建Nginx配置 `/etc/nginx/sites-available/monitor`:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    location / {
        root /path/to/monitor_system-1/frontend/dist;
        try_files $uri $uri/ /index.html;
    }

    # 后端API代理
    location /api {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    client_max_body_size 10M;
}
```

启用配置:

```bash
ln -s /etc/nginx/sites-available/monitor /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx
```

---

## 生产环境优化

### 1. 数据库优化

#### MySQL配置

在 `docker-compose.prod.yml` 中添加:

```yaml
mysql:
  command:
    - --innodb-buffer-pool-size=1G
    - --max-connections=200
    - --slow-query-log=1
    - --slow-query-log-file=/var/lib/mysql/slow.log
```

#### Redis配置

```yaml
redis:
  command: redis-server --maxmemory 1gb --maxmemory-policy allkeys-lru
```

### 2. 日志管理

配置日志轮转 `/etc/logrotate.d/monitor`:

```
/path/to/monitor_system-1/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0640 www-data www-data
}
```

### 3. 安全加固

#### HTTPS配置

使用Let's Encrypt:

```bash
apt-get install certbot python3-certbot-nginx
certbot --nginx -d your-domain.com
```

#### 防火墙配置

```bash
# 只开放必要端口
ufw allow 22/tcp
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

### 4. 备份策略

#### 数据库备份脚本

创建 `scripts/backup.sh`:

```bash
#!/bin/bash
BACKUP_DIR=/data/backups
DATE=$(date +%Y%m%d_%H%M%S)

mkdir -p $BACKUP_DIR

# 备份MySQL
docker exec monitor-system-1-mysql-1 mysqldump -u root -p${DB_PASS} ${DATABASE} > $BACKUP_DIR/db_$DATE.sql

# 备份Redis
docker exec monitor-system-1-redis-1 redis-cli BGSAVE

# 保留最近7天的备份
find $BACKUP_DIR -name "db_*.sql" -mtime +7 -delete
```

添加到crontab:

```bash
crontab -e
# 每天凌晨2点备份
0 2 * * * /path/to/scripts/backup.sh
```

---

## 监控与运维

### 1. 健康检查

#### 后端健康检查

```bash
curl http://localhost:5000/api/monitor/stats
```

#### Docker健康检查

在 `docker-compose.prod.yml` 中添加:

```yaml
backend:
  healthcheck:
    test: ["CMD", "curl", "-f", "http://localhost:5000/api/monitor/stats"]
    interval: 30s
    timeout: 10s
    retries: 3
```

### 2. 常用运维命令

```bash
# 查看服务状态
docker-compose -f docker-compose.prod.yml ps

# 查看日志
docker-compose -f docker-compose.prod.yml logs -f backend

# 重启服务
docker-compose -f docker-compose.prod.yml restart backend

# 进入容器
docker-compose -f docker-compose.prod.yml exec backend bash

# 数据库迁移
docker-compose -f docker-compose.prod.yml exec backend flask db upgrade
```

### 3. 性能监控

使用Prometheus + Grafana监控:

1. 部署Prometheus和Grafana
2. 配置MySQL Exporter、Redis Exporter
3. 配置监控面板

---

## 故障排查

### 服务无法启动

```bash
# 查看详细日志
docker-compose -f docker-compose.prod.yml logs <service-name>

# 检查端口占用
netstat -tlnp | grep <port>
```

### 数据库连接失败

```bash
# 检查MySQL容器状态
docker-compose -f docker-compose.prod.yml ps mysql

# 进入MySQL容器
docker-compose -f docker-compose.prod.yml exec mysql bash
mysql -u root -p
```

### 前端无法访问后端

检查:
1. Nginx配置是否正确
2. 后端服务是否正常运行
3. 防火墙是否开放端口
4. 浏览器控制台是否有CORS错误

---

## 更新与回滚

### 更新部署

```bash
# 拉取最新代码
git pull origin main

# 重新构建并启动
docker-compose -f docker-compose.prod.yml up -d --build
```

### 回滚

```bash
# 回滚到上一个版本
git checkout HEAD~1

# 重新部署
docker-compose -f docker-compose.prod.yml up -d --build

# 恢复数据库备份
docker exec -i monitor-system-1-mysql-1 mysql -u root -p${DB_PASS} ${DATABASE} < /path/to/backup.sql
```
