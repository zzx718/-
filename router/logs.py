from flask import request
from flask_restful import Resource
from lib.response import response
from lib.jwt_utils import admin_required

try:
    from services.log_service import log_service
    HAS_LOG_SERVICE = True
except ImportError:
    HAS_LOG_SERVICE = False


class LogSearchAPI(Resource):
    @admin_required
    def post(self):
        if not HAS_LOG_SERVICE:
            return response(code=501, message='Log service not available')
        
        try:
            data = request.json or {}
            
            server_id = data.get('server_id', type=int)
            log_type = data.get('log_type')
            container_name = data.get('container_name')
            service_name = data.get('service_name')
            keyword = data.get('keyword')
            start_time = data.get('start_time')
            end_time = data.get('end_time')
            log_levels = data.get('log_levels')
            page = data.get('page', 1)
            page_size = data.get('page_size', 50)
            
            result = log_service.search_logs(
                server_id=server_id,
                log_type=log_type,
                container_name=container_name,
                service_name=service_name,
                keyword=keyword,
                start_time=start_time,
                end_time=end_time,
                log_levels=log_levels,
                page=page,
                page_size=page_size
            )
            
            return response(data=result, message='Search logs success')
        except Exception as e:
            return response(code=500, message=f'Search logs failed: {str(e)}')


class LogStatsAPI(Resource):
    @admin_required
    def get(self):
        if not HAS_LOG_SERVICE:
            return response(code=501, message='Log service not available')
        
        try:
            server_id = request.args.get('server_id', type=int)
            hours = request.args.get('hours', 24, type=int)
            
            stats = log_service.get_log_stats(
                server_id=server_id,
                hours=hours
            )
            
            return response(data=stats, message='Get log stats success')
        except Exception as e:
            return response(code=500, message=f'Get log stats failed: {str(e)}')


class RelatedLogsAPI(Resource):
    @admin_required
    def get(self):
        if not HAS_LOG_SERVICE:
            return response(code=501, message='Log service not available')
        
        try:
            decision_id = request.args.get('decision_id', type=int)
            server_id = request.args.get('server_id', type=int)
            alert_time = request.args.get('alert_time')
            window_minutes = request.args.get('window_minutes', 10, type=int)
            
            if not server_id or not alert_time:
                return response(code=400, message='server_id and alert_time required')
            
            result = log_service.get_related_logs(
                server_id=server_id,
                alert_time=alert_time,
                window_minutes=window_minutes
            )
            
            return response(data={
                'decision_id': decision_id,
                'related_logs': result.get('logs', [])
            }, message='Get related logs success')
        except Exception as e:
            return response(code=500, message=f'Get related logs failed: {str(e)}')
