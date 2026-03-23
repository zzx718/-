from flask import Blueprint
from flask_restful import Api

#创建蓝图实例，用于管理路由
# 1. "mon_bp"：蓝图的唯一标识名称（内部使用，一般与变量名保持一致）
# 2. __name__：表示当前模块的名称，Flask用它来定位资源路径
# 3. url_prefix="/api"：为该蓝图下所有路由统一添加前缀"/api"
mon_bp = Blueprint("monitor",__name__,url_prefix="/api")

#创建flask_restful  api实例并将其绑定到蓝图,这样所有通过该Api注册的路由都会自动归属到蓝图下
api = Api(mon_bp)


#将蓝图注册到flask核心对象进行绑定
def init_app(app):
    # 把蓝图注册到app核心对象，使其路由生效，把蓝图和核心对象绑定
    app.register_blueprint(mon_bp)

    # # ==================== API资源导入 ====================
    # # 导入所有API资源类
    from .auth import Auth
    from .user import UserManagement
    from .server import ServerManagement, UserServers, ServerUserAPI, ServerGroupManagement
    from .monitor import MonitorDataAPI, MonitorStats
    from .alert import AlertRuleAPI, AlertRuleDetailAPI, AlertHistoryAPI
    from .audit import AuditLogAPI
    from .dify import DifyDecisionAPI, DifyDecisionDetailAPI, SmartAlertRuleAPI, SmartAlertRuleDetailAPI, DifyTriggerAPI
    from .logs import LogSearchAPI, LogStatsAPI, RelatedLogsAPI

    #
    # 资源类绑定api，注册路由
    # ==================== 认证路由 ====================
    # 用户登录认证（无需认证）
    api.add_resource(Auth, '/auth/login')

    # ==================== 用户管理路由 ====================
    # 用户CRUD操作（仅管理员）
    api.add_resource(UserManagement, '/users', '/users/<int:user_id>')

    # ==================== 服务器管理路由 ====================
    # 服务器CRUD操作（仅管理员）
    api.add_resource(ServerGroupManagement, '/server-groups')
    api.add_resource(ServerManagement, '/servers', '/servers/<int:server_id>')
    # 用户关联的服务器列表（需要认证）
    api.add_resource(UserServers, '/user-servers')
    # 服务器多用户关联管理（仅管理员）
    api.add_resource(ServerUserAPI, '/servers/<int:server_id>/users', '/servers/<int:server_id>/users/<int:user_id>')

    # ==================== 监控数据路由 ====================
    # 监控数据提交（API密钥认证）和查询（管理员认证）
    api.add_resource(MonitorDataAPI, '/monitor/data')
    # 监控数据统计（需要认证）
    api.add_resource(MonitorStats, '/monitor/stats')
    
    # ==================== 告警管理路由 ====================
    # 告警规则 CRUD
    api.add_resource(AlertRuleAPI, '/alert-rules')
    api.add_resource(AlertRuleDetailAPI, '/alert-rules/<int:rule_id>')
    # 告警历史
    api.add_resource(AlertHistoryAPI, '/alert-history')

    # ==================== 审计日志路由 ====================
    # 审计日志查询（管理员专用）
    api.add_resource(AuditLogAPI, '/audit-logs')
    
    # ==================== Dify决策路由 ====================
    api.add_resource(DifyDecisionAPI, '/dify/decisions')
    api.add_resource(DifyDecisionDetailAPI, '/dify/decisions/<int:decision_id>')
    api.add_resource(SmartAlertRuleAPI, '/dify/smart-rules')
    api.add_resource(SmartAlertRuleDetailAPI, '/dify/smart-rules/<int:rule_id>')
    api.add_resource(DifyTriggerAPI, '/dify/trigger/<int:server_id>')
    
    # ==================== 日志查询路由 ====================
    api.add_resource(LogSearchAPI, '/logs/search')
    api.add_resource(LogStatsAPI, '/logs/stats')
    api.add_resource(RelatedLogsAPI, '/logs/related')
