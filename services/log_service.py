import os
from datetime import datetime, timedelta
from elasticsearch import Elasticsearch
from config.setting import ES_HOST, ES_PORT, ES_USERNAME, ES_PASSWORD, ES_USE_SSL

class LogService:
    def __init__(self):
        self.index_prefix = 'server-logs'
        self.es_client = None
        self._connect()
    
    def _connect(self):
        try:
            if ES_USERNAME and ES_PASSWORD:
                self.es_client = Elasticsearch(
                    hosts=[{'host': ES_HOST, 'port': ES_PORT}],
                    basic_auth=(ES_USERNAME, ES_PASSWORD),
                    use_ssl=ES_USE_SSL,
                    verify_certs=False
                )
            else:
                self.es_client = Elasticsearch(
                    hosts=[{'host': ES_HOST, 'port': ES_PORT}],
                    use_ssl=ES_USE_SSL,
                    verify_certs=False
                )
            if not self.es_client.ping():
                self.es_client = None
        except Exception:
            self.es_client = None
    
    def is_available(self):
        return self.es_client is not None
    
    def get_index_name(self, server_id=None):
        today = datetime.now().strftime('%Y.%m.%d')
        if server_id:
            return f'{self.index_prefix}-{server_id}-{today}'
        return f'{self.index_prefix}-{today}'
    
    def index_log(self, server_id, log_data):
        if not self.is_available():
            return False
        
        try:
            index_name = self.get_index_name(server_id)
            log_data['server_id'] = server_id
            log_data['@timestamp'] = datetime.now().isoformat()
            
            if not self.es_client.indices.exists(index=index_name):
                self._create_index(index_name)
            
            self.es_client.index(index=index_name, document=log_data)
            return True
        except Exception:
            return False
    
    def _create_index(self, index_name):
        mapping = {
            'mappings': {
                'properties': {
                    '@timestamp': {'type': 'date'},
                    'server_id': {'type': 'integer'},
                    'log_type': {'type': 'keyword'},
                    'container_name': {'type': 'keyword'},
                    'service_name': {'type': 'keyword'},
                    'log_level': {'type': 'keyword'},
                    'message': {'type': 'text'},
                    'source': {'type': 'keyword'}
                }
            }
        }
        self.es_client.indices.create(index=index_name, body=mapping)
    
    def search_logs(self, server_id=None, log_type=None, container_name=None, service_name=None,
                    keyword=None, start_time=None, end_time=None, log_levels=None, page=1, page_size=50):
        if not self.is_available():
            return {'logs': [], 'total': 0, 'page': page, 'page_size': page_size}
        
        try:
            query = {'bool': {'must': []}}
            
            if server_id:
                query['bool']['must'].append({'term': {'server_id': server_id}})
            if log_type:
                query['bool']['must'].append({'term': {'log_type': log_type}})
            if container_name:
                query['bool']['must'].append({'term': {'container_name': container_name}})
            if service_name:
                query['bool']['must'].append({'term': {'service_name': service_name}})
            if log_levels and isinstance(log_levels, list):
                query['bool']['must'].append({'terms': {'log_level': log_levels}})
            if keyword:
                query['bool']['must'].append({'match': {'message': keyword}})
            
            time_range = {}
            if start_time:
                time_range['gte'] = start_time
            if end_time:
                time_range['lte'] = end_time
            if time_range:
                query['bool']['must'].append({'range': {'@timestamp': time_range}})
            
            from_ = (page - 1) * page_size
            
            result = self.es_client.search(
                index=f'{self.index_prefix}-*',
                query=query,
                from_=from_,
                size=page_size,
                sort=[{'@timestamp': {'order': 'desc'}}]
            )
            
            logs = []
            for hit in result['hits']['hits']:
                log = hit['_source']
                log['id'] = hit['_id']
                logs.append(log)
            
            return {
                'logs': logs,
                'total': result['hits']['total']['value'] if isinstance(result['hits']['total'], dict) else result['hits']['total'],
                'page': page,
                'page_size': page_size
            }
        except Exception:
            return {'logs': [], 'total': 0, 'page': page, 'page_size': page_size}
    
    def get_log_stats(self, server_id=None, hours=24):
        if not self.is_available():
            return {'total': 0, 'by_level': {}, 'by_hour': []}
        
        try:
            end_time = datetime.now()
            start_time = end_time - timedelta(hours=hours)
            
            query = {'bool': {'must': [
                {'range': {'@timestamp': {'gte': start_time.isoformat(), 'lte': end_time.isoformat()}}}
            ]}}
            
            if server_id:
                query['bool']['must'].append({'term': {'server_id': server_id}})
            
            result = self.es_client.search(
                index=f'{self.index_prefix}-*',
                query=query,
                size=0,
                aggs={
                    'by_level': {'terms': {'field': 'log_level'}},
                    'by_hour': {
                        'date_histogram': {
                            'field': '@timestamp',
                            'fixed_interval': '1h'
                        }
                    }
                }
            )
            
            by_level = {}
            for bucket in result['aggregations']['by_level']['buckets']:
                by_level[bucket['key']] = bucket['doc_count']
            
            by_hour = []
            for bucket in result['aggregations']['by_hour']['buckets']:
                by_hour.append({
                    'time': bucket['key_as_string'],
                    'count': bucket['doc_count']
                })
            
            return {
                'total': result['hits']['total']['value'] if isinstance(result['hits']['total'], dict) else result['hits']['total'],
                'by_level': by_level,
                'by_hour': by_hour
            }
        except Exception:
            return {'total': 0, 'by_level': {}, 'by_hour': []}
    
    def get_related_logs(self, server_id, alert_time, window_minutes=10):
        if not self.is_available():
            return {'logs': []}
        
        try:
            if isinstance(alert_time, str):
                alert_time = datetime.fromisoformat(alert_time.replace('Z', '+00:00'))
            
            start_time = alert_time - timedelta(minutes=window_minutes)
            end_time = alert_time + timedelta(minutes=window_minutes)
            
            return self.search_logs(
                server_id=server_id,
                start_time=start_time.isoformat(),
                end_time=end_time.isoformat(),
                page_size=100
            )
        except Exception:
            return {'logs': []}


log_service = LogService()
