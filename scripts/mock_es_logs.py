"""
用于毕设演示：模拟探针采集日志并写入 Elasticsearch
运行此脚本可以向 ES 注入各种常见的服务器报警、中间件报错日志，用于在“日志查询”页面展示。
"""

import sys
import os
import random
import time
from datetime import datetime, timedelta

# 将项目根目录加入到sys.path中，以便能够引入 config 和 services
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from services.log_service import LogService
from model.server import Server
from model import db
from flask import Flask
from config import setting

def create_app():
    app = Flask(__name__)
    app.config.from_object(setting)
    db.init_app(app)
    return app

def generate_mock_logs(server_id):
    log_service = LogService()
    if not log_service.is_available():
        print("❌ Elasticsearch连接失败！请确保 docker-compose 中的 elasticsearch 正在运行。")
        return
        
    print(f"正在向服务器(ID:{server_id})注入模拟测试日志...")
    
    # 定义常见的模拟日志模板格式
    mock_log_templates = [
        # SSH 认证日志
        {"type": "system", "container": "host", "service": "sshd", "level": "WARNING", "msg": "Failed password for root from 192.168.1.100 port 46210 ssh2"},
        {"type": "system", "container": "host", "service": "sshd", "level": "ERROR", "msg": "Received disconnect from 192.168.1.100 port 46210: 11: Bye Bye [preauth]"},
        
        # 内核与物理资源
        {"type": "system", "container": "host", "service": "kernel", "level": "ERROR", "msg": "Out of memory: Killed process 3125 (mysql) total-vm:409600kB, anon-vm:819200kB"},
        {"type": "system", "container": "host", "service": "kernel", "level": "WARNING", "msg": "TCP: request_sock_TCP: Possible SYN flooding on port 80. Sending cookies."},
        
        # Nginx 日志
        {"type": "container", "container": "nginx-server", "service": "nginx", "level": "ERROR", "msg": "2026/05/01 10:14:22 [error] 23#23: *11 upstream timed out (110: Connection timed out) while reading response header from upstream"},
        {"type": "container", "container": "nginx-server", "service": "nginx", "level": "WARNING", "msg": "403 Forbidden: Limiting rate of requests from client 10.0.0.1"},
        
        # MySQL 日志
        {"type": "container", "container": "mysql-db", "service": "mysql", "level": "WARNING", "msg": "[Warning] Aborted connection 15612 to db: 'monitor' user: 'root' (Got an error reading communication packets)"},
        {"type": "container", "container": "mysql-db", "service": "mysql", "level": "ERROR", "msg": "InnoDB: Unable to lock ./ibdata1 error: 11"},
        
        # Redis 日志
        {"type": "container", "container": "redis-cache", "service": "redis", "level": "WARNING", "msg": "OOM command not allowed when used memory > 'maxmemory'"},
        
        # 业务应用日志
        {"type": "application", "container": "monitor-backend", "service": "java-app", "level": "ERROR", "msg": "java.lang.NullPointerException: Cannot invoke \"String.length()\" because \"name\" is null"},
    ]
    
    # 模拟过去 2 小时的时间范围
    end_time = datetime.now()
    start_time = end_time - timedelta(hours=2)
    
    insert_count = 0
    # 随机生成30到50条日志
    total_logs_to_generate = random.randint(30, 50)
    
    for _ in range(total_logs_to_generate):
        template = random.choice(mock_log_templates)
        
        # 随机时间点
        random_seconds = random.randint(0, int((end_time - start_time).total_seconds()))
        log_time = start_time + timedelta(seconds=random_seconds)
        
        log_data = {
            'log_type': template['type'],
            'container_name': template['container'],
            'service_name': template['service'],
            'log_level': template['level'],
            'message': template['msg'],
            'source': '/var/log/' + template['service'] + '.log',
            '@timestamp': log_time.isoformat()
        }
        
        # 将日志通过 LogService 写入 ES
        success = log_service.index_log(server_id=server_id, log_data=log_data)
        if success:
            insert_count += 1
            print(f"[{log_time.strftime('%Y-%m-%d %H:%M:%S')}] {template['level']} - {template['service']} 写入成功")
            
    print(f"\n✅ 模拟日志写入完毕！成功写入了 {insert_count} 条相关日志数据。前端可以直接看效果了。")

if __name__ == '__main__':
    app = create_app()
    with app.app_context():
        # 这里获取所有的服务器
        servers = Server.query.all()
        if not servers:
            print("⚠️ 数据库中还没有监控服务器。请先在前端页面添加一个服务器或执行 create_admin.py 添加服务器。")
            sys.exit(1)
            
        print(f"找到 {len(servers)} 台服务器，准备写入模拟日志...")
        for server in servers:
            generate_mock_logs(server.id)
