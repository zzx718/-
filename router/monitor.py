"""
监控数据API接口
支持批量数据提交和IP地址匹配
"""

from flask import request, current_app
from flask_restful import Resource
from lib.response import response
from model import MonitorData, Server
from model import db
from lib.jwt_utils import admin_required
from lib.api_auth import api_key_required
from mail.alert import check_and_send_alert_by_ip
from lib.async_tasks import executor, async_process_monitor_data

#监控数据API资源类
class MonitorDataAPI(Resource):
    #提交监控数据（需要API密钥）
    @api_key_required
    def post(self):
        try:
            data = request.json
            server_id = data.get('server_id')
            ip_address = data.get('ip_address')
            metrics = data.get('metrics')  # 改为批量提交

            # 验证必需字段
            if not metrics:
                return response(message="监控数据不能为空", code=400)

            # 获取服务器
            server = None
            if server_id:
                # 优先使用server_id查找
                server = Server.get_by_id(server_id)
            elif ip_address:
                # 根据IP地址查找服务器
                server = Server.get_by_ip(ip_address)
            else:
                return response(message="请提供server_id或ip_address", code=400)

            if not server:
                return response(message="服务器不存在", code=400)

            # 异步处理：将数据入库和告警检查放入后台线程池
            # 注意：需要传递当前的app对象，以便在线程中创建上下文
            # 使用 _get_current_object() 获取真实的 app 对象
            executor.submit(
                async_process_monitor_data, 
                current_app._get_current_object(), 
                server.ip_address, 
                metrics
            )

            # 立即返回成功，不再等待数据库和邮件
            return response(message="监控数据已接收，正在后台处理")

        except Exception as e:
            return response(message="提交监控数据失败", code=500)

    @admin_required
    def get(self):
        """获取监控数据（仅管理员）"""
        try:
            # 获取查询参数
            server_id = request.args.get('server_id', type=int)
            metric_type = request.args.get('metric_type')
            hours = request.args.get('hours', 24, type=float) # 改为 float，支持 0.16小时 (10分钟) 等短时间
            mode = request.args.get('mode', 'latest')  # 新增mode参数

            if mode == 'history':
                # 获取指定服务器的历史趋势数据
                if not server_id:
                    return response(message="必须提供 server_id 以获取历史数据", code=400)
                data = MonitorData.get_history_by_server_id(server_id, hours)
            elif server_id:
                # 获取指定服务器的数据
                data = MonitorData.get_latest_by_server(server_id)
                if data:
                    data = [data]  # 转换为列表格式
                else:
                    data = []
            else:
                # 获取所有最新数据

                data = []
                servers = Server.get_all()
                for server in servers:
                    latest = MonitorData.get_latest_by_server(server.id)
                    if latest:
                        data.append(latest)

            # 转换为字典格式，处理Decimal类型
            data_list = []
            for item in data:
                item_dict = dict(item)
                # 将Decimal类型转换为float
                for field in ['cpu_value', 'memory_value', 'disk_value']:
                    if field in item_dict and item_dict[field] is not None:
                        item_dict[field] = float(item_dict[field])
                data_list.append(item_dict)

            return response(data=data_list, message="获取监控数据成功")

        except Exception as e:
            return response(message="获取监控数据失败", code=500)

#监控统计API资源类
class MonitorStats(Resource):
    #获取监控统计信息
    @admin_required
    def get(self):
        try:
            # 获取查询参数
            server_id = request.args.get('server_id', type=int)
            hours = request.args.get('hours', 24, type=int)

            if server_id:
                servers = [Server.get_by_id(server_id)]
            else:
                servers = Server.get_all()

            stats = []
            for server in servers:
                server_stats = {
                    'server_id': server.id,
                    'server_name': server.server_name,
                    'ip_address': server.ip_address,
                    # status字段已删除
                    'users': [dict(user) for user in server.users],  # 多用户关联信息
                    'metrics': {}
                }

                # 获取最新监控数据
                latest_data = MonitorData.get_latest_by_server(server.id)
                if latest_data:
                    from config.setting import DEFAULT_THRESHOLDS
                    server_stats['metrics'] = {
                        'cpu': {
                            'value': float(latest_data.cpu_value),
                            'threshold_warning': DEFAULT_THRESHOLDS['cpu']['warning'],
                            'threshold_critical': DEFAULT_THRESHOLDS['cpu']['critical'],
                            'threshold_emergency': DEFAULT_THRESHOLDS['cpu']['emergency'],
                            'recorded_at': str(latest_data.recorded_at)
                        },
                        'memory': {
                            'value': float(latest_data.memory_value),
                            'threshold_warning': DEFAULT_THRESHOLDS['memory']['warning'],
                            'threshold_critical': DEFAULT_THRESHOLDS['memory']['critical'],
                            'threshold_emergency': DEFAULT_THRESHOLDS['memory']['emergency'],
                            'recorded_at': str(latest_data.recorded_at)
                        },
                        'disk': {
                            'value': float(latest_data.disk_value),
                            'threshold_warning': DEFAULT_THRESHOLDS['disk']['warning'],
                            'threshold_critical': DEFAULT_THRESHOLDS['disk']['critical'],
                            'threshold_emergency': DEFAULT_THRESHOLDS['disk']['emergency'],
                            'recorded_at': str(latest_data.recorded_at)
                        }
                    }

                stats.append(server_stats)

            return response(data=stats, message="获取监控统计成功")

        except Exception as e:
            return response(message="获取监控统计失败", code=500)


