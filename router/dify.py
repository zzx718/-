from flask import request
from flask_restful import Resource
from lib.response import response
from lib.jwt_utils import admin_required
from model import db, MonitorData
from model.monitor import DifyDecision, SmartAlertRule
from services.dify_service import dify_service


class DifyDecisionAPI(Resource):
    @admin_required
    def get(self):
        try:
            page = request.args.get('page', 1, type=int)
            page_size = request.args.get('page_size', 20, type=int)
            server_id = request.args.get('server_id', type=int)
            
            query = DifyDecision.query
            if server_id:
                query = query.filter_by(server_id=server_id)
            
            paginated = query.order_by(DifyDecision.created_at.desc()).paginate(
                page=page, per_page=page_size, error_out=False
            )
            
            decisions = []
            for d in paginated.items:
                decisions.append({
                    'id': d.id,
                    'server_id': d.server_id,
                    'workflow_id': d.workflow_id,
                    'workflow_run_id': d.workflow_run_id,
                    'current_metrics': d.current_metrics,
                    'should_alert': d.should_alert,
                    'alert_level': d.alert_level,
                    'alert_reason': d.alert_reason,
                    'recommendation': d.recommendation,
                    'executed': d.executed,
                    'human_feedback': d.human_feedback,
                    'created_at': d.created_at.isoformat() if d.created_at else None
                })
            
            return response(data={
                'items': decisions,
                'total': paginated.total,
                'page': page,
                'page_size': page_size
            })
        except Exception as e:
            return response(code=500, message=f'Failed to get decisions: {str(e)}')


class DifyDecisionDetailAPI(Resource):
    @admin_required
    def get(self, decision_id):
        try:
            decision = DifyDecision.query.get(decision_id)
            if not decision:
                return response(code=404, message='Decision not found')
            
            return response(data={
                'id': decision.id,
                'server_id': decision.server_id,
                'workflow_id': decision.workflow_id,
                'workflow_run_id': decision.workflow_run_id,
                'input_data': decision.input_data,
                'current_metrics': decision.current_metrics,
                'history_trend': decision.history_trend,
                'should_alert': decision.should_alert,
                'alert_level': decision.alert_level,
                'alert_reason': decision.alert_reason,
                'decision_output': decision.decision_output,
                'recommendation': decision.recommendation,
                'action_items': decision.action_items,
                'executed': decision.executed,
                'execution_result': decision.execution_result,
                'human_feedback': decision.human_feedback,
                'feedback_comment': decision.feedback_comment,
                'created_at': decision.created_at.isoformat() if decision.created_at else None,
                'executed_at': decision.executed_at.isoformat() if decision.executed_at else None,
                'feedback_at': decision.feedback_at.isoformat() if decision.feedback_at else None
            })
        except Exception as e:
            return response(code=500, message=f'Failed to get decision: {str(e)}')
    
    @admin_required
    def put(self, decision_id):
        try:
            data = request.json or {}
            decision = DifyDecision.query.get(decision_id)
            if not decision:
                return response(code=404, message='Decision not found')
            
            if 'human_feedback' in data:
                decision.human_feedback = data['human_feedback']
                decision.feedback_comment = data.get('feedback_comment')
                decision.feedback_at = db.func.now()
            
            db.session.commit()
            return response(message='Feedback updated')
        except Exception as e:
            db.session.rollback()
            return response(code=500, message=f'Failed to update decision: {str(e)}')


class SmartAlertRuleAPI(Resource):
    @admin_required
    def get(self):
        try:
            server_id = request.args.get('server_id', type=int)
            
            query = SmartAlertRule.query
            if server_id:
                query = query.filter_by(server_id=server_id)
            
            rules = query.order_by(SmartAlertRule.priority.desc()).all()
            
            rule_list = []
            for rule in rules:
                rule_list.append({
                    'id': rule.id,
                    'server_id': rule.server_id,
                    'rule_name': rule.rule_name,
                    'rule_description': rule.rule_description,
                    'dify_workflow_id': rule.dify_workflow_id,
                    'trigger_condition': rule.trigger_condition,
                    'is_enabled': rule.is_enabled,
                    'priority': rule.priority,
                    'silent_minutes': rule.silent_minutes,
                    'created_at': rule.created_at.isoformat() if rule.created_at else None,
                    'updated_at': rule.updated_at.isoformat() if rule.updated_at else None
                })
            
            return response(data=rule_list)
        except Exception as e:
            return response(code=500, message=f'Failed to get rules: {str(e)}')
    
    @admin_required
    def post(self):
        try:
            data = request.json or {}
            
            rule = SmartAlertRule(
                server_id=data['server_id'],
                rule_name=data['rule_name'],
                rule_description=data.get('rule_description'),
                dify_workflow_id=data.get('dify_workflow_id'),
                dify_api_key=data.get('dify_api_key'),
                trigger_condition=data.get('trigger_condition'),
                is_enabled=data.get('is_enabled', True),
                priority=data.get('priority', 0),
                silent_minutes=data.get('silent_minutes', 30)
            )
            
            db.session.add(rule)
            db.session.commit()
            return response(data={'id': rule.id}, message='Rule created')
        except Exception as e:
            db.session.rollback()
            return response(code=500, message=f'Failed to create rule: {str(e)}')


class SmartAlertRuleDetailAPI(Resource):
    @admin_required
    def get(self, rule_id):
        try:
            rule = SmartAlertRule.query.get(rule_id)
            if not rule:
                return response(code=404, message='Rule not found')
            
            return response(data={
                'id': rule.id,
                'server_id': rule.server_id,
                'rule_name': rule.rule_name,
                'rule_description': rule.rule_description,
                'dify_workflow_id': rule.dify_workflow_id,
                'dify_api_key': rule.dify_api_key,
                'trigger_condition': rule.trigger_condition,
                'is_enabled': rule.is_enabled,
                'priority': rule.priority,
                'silent_minutes': rule.silent_minutes,
                'created_at': rule.created_at.isoformat() if rule.created_at else None,
                'updated_at': rule.updated_at.isoformat() if rule.updated_at else None
            })
        except Exception as e:
            return response(code=500, message=f'Failed to get rule: {str(e)}')
    
    @admin_required
    def put(self, rule_id):
        try:
            data = request.json or {}
            rule = SmartAlertRule.query.get(rule_id)
            if not rule:
                return response(code=404, message='Rule not found')
            
            if 'rule_name' in data:
                rule.rule_name = data['rule_name']
            if 'rule_description' in data:
                rule.rule_description = data['rule_description']
            if 'dify_workflow_id' in data:
                rule.dify_workflow_id = data['dify_workflow_id']
            if 'dify_api_key' in data:
                rule.dify_api_key = data['dify_api_key']
            if 'trigger_condition' in data:
                rule.trigger_condition = data['trigger_condition']
            if 'is_enabled' in data:
                rule.is_enabled = data['is_enabled']
            if 'priority' in data:
                rule.priority = data['priority']
            if 'silent_minutes' in data:
                rule.silent_minutes = data['silent_minutes']
            
            db.session.commit()
            return response(message='Rule updated')
        except Exception as e:
            db.session.rollback()
            return response(code=500, message=f'Failed to update rule: {str(e)}')
    
    @admin_required
    def delete(self, rule_id):
        try:
            rule = SmartAlertRule.query.get(rule_id)
            if not rule:
                return response(code=404, message='Rule not found')
            
            db.session.delete(rule)
            db.session.commit()
            return response(message='Rule deleted')
        except Exception as e:
            db.session.rollback()
            return response(code=500, message=f'Failed to delete rule: {str(e)}')


class DifyTriggerAPI(Resource):
    @admin_required
    def post(self, server_id):
        try:
            latest_data = MonitorData.get_latest_by_server(server_id)
            if not latest_data:
                return response(code=404, message='No monitor data found')
            
            current_metrics = {
                'cpu': float(latest_data.cpu_value),
                'memory': float(latest_data.memory_value),
                'disk': float(latest_data.disk_value)
            }
            
            result = dify_service.trigger_workflow(server_id, current_metrics)
            
            if result.get('success'):
                decision_output = dify_service.parse_decision(result)
                if decision_output:
                    DifyDecision.create(
                        server_id=server_id,
                        workflow_id=dify_service.workflow_id,
                        input_data=result.get('inputs', {}),
                        decision_output=decision_output
                    )
                
                return response(data=result, message='Workflow triggered')
            else:
                return response(code=500, message=result.get('error', 'Failed to trigger workflow'))
        except Exception as e:
            return response(code=500, message=f'Failed to trigger workflow: {str(e)}')
