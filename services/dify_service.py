import requests
import os
from datetime import datetime, timedelta
from model import db, MonitorData, Server

class DifyService:
    def __init__(self):
        self.api_url = os.getenv('DIFY_API_URL', 'https://api.dify.ai/v1')
        self.api_key = os.getenv('DIFY_API_KEY', '')
        self.workflow_id = os.getenv('DIFY_WORKFLOW_ID', '')
    
    def is_configured(self):
        return bool(self.api_key and self.workflow_id)
    
    def _prepare_input_data(self, server_id, current_metrics):
        server = Server.get_by_id(server_id)
        if not server:
            return None
        
        end_time = datetime.now()
        start_time = end_time - timedelta(minutes=30)
        
        history_data = MonitorData.query.filter(
            MonitorData.server_id == server_id,
            MonitorData.recorded_at >= start_time
        ).order_by(MonitorData.recorded_at.asc()).all()
        
        recent_points = []
        for data in history_data[-5:]:
            recent_points.append({
                'cpu': float(data.cpu_value),
                'memory': float(data.memory_value),
                'disk': float(data.disk_value),
                'time': data.recorded_at.strftime('%H:%M:%S')
            })
        
        cpu_5min_ago = None
        cpu_10min_ago = None
        if len(history_data) >= 2:
            cpu_5min_ago = float(history_data[-2].cpu_value)
        if len(history_data) >= 4:
            cpu_10min_ago = float(history_data[-4].cpu_value)
        
        cpu_trend = 'stable'
        cpu_change_rate = 0
        if cpu_5min_ago and current_metrics.get('cpu'):
            cpu_change_rate = ((current_metrics['cpu'] - cpu_5min_ago) / max(cpu_5min_ago, 1)) * 100
            if cpu_change_rate > 10:
                cpu_trend = 'rising'
            elif cpu_change_rate < -10:
                cpu_trend = 'falling'
        
        input_data = {
            'server_info': {
                'id': server.id,
                'name': server.server_name,
                'ip_address': server.ip_address,
                'server_name': server.server_name,
                'importance': 'medium',
                'description': server.description or ''
            },
            'current_metrics': {
                'cpu': current_metrics.get('cpu', 0),
                'memory': current_metrics.get('memory', 0),
                'disk': current_metrics.get('disk', 0)
            },
            'history_trend': {
                'cpu_5min_ago': cpu_5min_ago,
                'cpu_10min_ago': cpu_10min_ago,
                'cpu_trend': cpu_trend,
                'cpu_change_rate': round(cpu_change_rate, 2),
                'memory_trend': 'stable',
                'is_sustained_alert': len(recent_points) >= 3,
                'sustained_minutes': len(recent_points),
                'recent_data_points': recent_points
            },
            'related_logs': {
                'error_count_last_10min': 0,
                'warning_count_last_10min': 0,
                'recent_errors': [],
                'keyword_hits': {}
            },
            'context': {
                'hour_of_day': datetime.now().hour,
                'day_of_week': datetime.now().weekday(),
                'is_working_hours': 9 <= datetime.now().hour <= 18,
                'recent_alerts': [],
                'last_alert_time': None,
                'is_in_silent_period': False
            }
        }
        
        return input_data
    
    def trigger_workflow(self, server_id, current_metrics):
        if not self.is_configured():
            return {
                'success': False,
                'error': 'Dify not configured',
                'fallback': True
            }
        
        input_data = self._prepare_input_data(server_id, current_metrics)
        if not input_data:
            return {
                'success': False,
                'error': 'Server not found',
                'fallback': True
            }
        
        url = f'{self.api_url}/workflows/run'
        headers = {
            'Authorization': f'Bearer {self.api_key}',
            'Content-Type': 'application/json'
        }
        
        payload = {
            'inputs': input_data,
            'response_mode': 'blocking',
            'user': f'server_{server_id}'
        }
        
        try:
            response = requests.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            return {
                'success': True,
                'workflow_run_id': result.get('workflow_run_id'),
                'data': result.get('data', {}),
                'outputs': result.get('data', {}).get('outputs', {})
            }
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'fallback': True
            }
    
    def parse_decision(self, dify_result):
        if not dify_result.get('success'):
            return None
        
        outputs = dify_result.get('outputs', {})
        
        return {
            'should_alert': outputs.get('should_alert', False),
            'alert_level': outputs.get('alert_level', 'info'),
            'alert_reason': outputs.get('alert_reason', ''),
            'severity_score': outputs.get('severity_score', 0),
            'priority': outputs.get('priority', 'medium'),
            'recommendation': outputs.get('recommendation', ''),
            'action_items': outputs.get('action_items', []),
            'email': outputs.get('email', {}),
            'silent_period': outputs.get('silent_period', {})
        }


dify_service = DifyService()
