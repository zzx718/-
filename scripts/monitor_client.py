"""
监控数据采集客户端
"""

import psutil
import requests
import time
import sys
import os
import socket
import hashlib

class MonitorClient:
    def __init__(self, api_url, app_id=None, secret_key=None, collect_interval=30, ip_address=None):
        self.api_url = api_url.rstrip('/')
        self.app_id = app_id
        self.secret_key = secret_key
        self.collect_interval = collect_interval
        self.ip_address = ip_address or self._get_local_ip()
        self.running = False

        print(f"服务器IP: {self.ip_address}")
        # self._test_connection()

    def _get_local_ip(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("8.8.8.8", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except:
            return "127.0.0.1"
    
    # 生成签名 Sign
    def _generate_sign(self, timestamp):
        """生成签名: sha256(appid + secret_key + timestamp)"""
        if not self.app_id or not self.secret_key:
            return ""
        
        # 拼接原始字符串
        raw_str = f"{self.app_id}{self.secret_key}{timestamp}"
        
        # 计算SHA256
        return hashlib.sha256(raw_str.encode('utf-8')).hexdigest()

    def _test_connection(self):
        try:
            # 简单的联通性测试，不带鉴权
            base_url = self.api_url.replace('/api', '')
            response = requests.get(f"{base_url}", timeout=5) # 访问根路径通常不需要鉴权
            if response.status_code == 200:
                print("API服务连通性检查：成功")
            else:
                print(f"API服务响应异常: {response.status_code}")
        except Exception as e:
            print(f"API服务连接失败: {e}")
            # sys.exit(1) # 不强制退出，允许重试

    def collect_cpu(self):
        try:
            return round(psutil.cpu_percent(interval=1), 2)
        except:
            return None

    def collect_memory(self):
        try:
            return round(psutil.virtual_memory().percent, 2)
        except:
            return None

    def collect_disk(self):
        try:
            path = 'C:\\' if os.name == 'nt' else '/'
            disk = psutil.disk_usage(path)
            return round((disk.used / disk.total) * 100, 2)
        except:
            return None

    def send_data(self, metrics):
        if not metrics:
            return False

        data = {
            "metrics": metrics,
            "ip_address": self.ip_address
        }

        try:
            timestamp = str(int(time.time()))
            sign = self._generate_sign(timestamp)
            
            headers = {
                'Content-Type': 'application/json',
                'X-App-ID': self.app_id,
                'X-Timestamp': timestamp,
                'X-Sign': sign
            }

            response = requests.post(
                f"{self.api_url}/monitor/data",
                json=data,
                headers=headers,
                timeout=10
            )

            if response.status_code == 200:
                result = response.json()
                if result.get('code') == 0:
                    print(f"数据发送成功: {list(metrics.keys())}")
                    return True
                else:
                    print(f"数据发送失败(1): {result.get('msg', result.get('message', '未知错误'))}")
                    return False
            else:
                print(f"数据发送失败(2): HTTP {response.status_code} - {response.text}")
                return False
        except Exception as e:
            print(f"数据发送异常: {e}")
            return False

    def collect_and_send(self):
        metrics = {}

        cpu_value = self.collect_cpu()
        if cpu_value is not None:
            metrics["cpu"] = cpu_value

        memory_value = self.collect_memory()
        if memory_value is not None:
            metrics["memory"] = memory_value

        disk_value = self.collect_disk()
        if disk_value is not None:
            metrics["disk"] = disk_value

        if metrics:
            self.send_data(metrics)

    def run(self):
        print(f"监控客户端启动 - 服务器IP: {self.ip_address}, 采集间隔: {self.collect_interval}秒")
        self.running = True

        try:
            while self.running:
                start_time = time.time()
                self.collect_and_send()

                elapsed_time = time.time() - start_time
                sleep_time = max(0, self.collect_interval - elapsed_time)

                if sleep_time > 0:
                    time.sleep(sleep_time)
                else:
                    print("采集耗时超过间隔时间，立即进行下次采集")

        except KeyboardInterrupt:
            print("收到停止信号，正在关闭监控客户端...")
            self.running = False
        except Exception as e:
            print(f"监控客户端运行异常: {e}")
            self.running = False


def main():
    API_URL = "http://127.0.0.1:5000/api"
    # 鉴权配置 (必须与服务端 api_auth.py 中的 API_CREDENTIALS 一致)
    APP_ID = "default_client" 
    SECRET_KEY = "sk_default_123456"
    COLLECT_INTERVAL = 30
    IP_ADDRESS = None

    # 支持命令行传参覆盖默认配置
    if len(sys.argv) > 1:
        API_URL = sys.argv[1]
    if len(sys.argv) > 2:
        APP_ID = sys.argv[2]
    if len(sys.argv) > 3:
        SECRET_KEY = sys.argv[3]

    print(f"启动监控客户端...")
    print(f"服务端地址: {API_URL}")
    print(f"AppID: {APP_ID}")

    client = MonitorClient(API_URL, APP_ID, SECRET_KEY, COLLECT_INTERVAL, IP_ADDRESS)
    client.run()


if __name__ == "__main__":
    main()
