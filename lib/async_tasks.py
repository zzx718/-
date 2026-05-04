from concurrent.futures import ThreadPoolExecutor
from flask import current_app
import logging
from model import db, MonitorData, Server
from mail.alert import check_and_send_alert_by_ip

# 创建全局线程池用于数据入库
# max_workers=10 表示最多同时有10个线程在后台处理任务
executor = ThreadPoolExecutor(max_workers=10)

# 创建独立的全局线程池，专用于耗时的 Dify 调用和邮件发送，防止阻塞数据入库
dify_executor = ThreadPoolExecutor(max_workers=5)

def async_process_monitor_data(app, server_ip, metrics):
    """
    异步处理监控数据：入库 + 告警
    注意：由于是异步线程，需要手动创建应用上下文
    """
    with app.app_context():
        try:
            # 1. 数据入库
            # 支持两种字段名格式
            cpu_value = metrics.get('cpu_value', metrics.get('cpu', 0.0))
            memory_value = metrics.get('memory_value', metrics.get('memory', 0.0))
            disk_value = metrics.get('disk_value', metrics.get('disk', 0.0))

            MonitorData.create_by_ip(
                server_ip,
                cpu_value,
                memory_value,
                disk_value
            )
            
            # 2. 告警检查 - 将每个指标的告警判定投递到专门的 dify_executor 中执行
            alert_metrics = {
                'cpu': cpu_value,
                'memory': memory_value,
                'disk': disk_value
            }
            # 启动另外的线程去执行告警判定（因为其中可能有同步阻塞的 API 请求）
            for metric_type, value in alert_metrics.items():
                dify_executor.submit(
                    async_check_alert_task, 
                    app, server_ip, metric_type, float(value), alert_metrics
                )
                
        except Exception as e:
            logging.error(f"异步处理监控数据入库失败: {str(e)}")

def async_check_alert_task(app, server_ip, metric_type, value, current_metrics):
    """
    完全异步的告警检测与 Dify 触发任务
    """
    with app.app_context():
        try:
            check_and_send_alert_by_ip(server_ip, metric_type, value, current_metrics)
        except Exception as e:
            logging.error(f"异步检查告警任务失败: {str(e)}")
