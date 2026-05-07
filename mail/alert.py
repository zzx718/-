#告警模块

import threading
from datetime import datetime, timedelta
from config.setting import DEFAULT_THRESHOLDS, ALERT_TEMPLATES, SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASS, SMTP_SENDER
from model import Server, User, AlertRule, AlertHistory

# [新增亮点] 内存级别的并发告警锁，解决多线程因大模型API延迟导致的告警并发穿透
LAST_ALERT_CACHE = {}
ALERT_LOCK = threading.Lock()

# 获取服务器的告警阈值（优先使用自定义规则）
def get_server_thresholds(server, metric_type):
    # 尝试查询该服务器的自定义告警规则
    rule = AlertRule.query.filter_by(server_id=server.id, metric_type=metric_type, is_enabled=True).first()
    
    if rule:
        # 如果有自定义规则，统一使用该阈值
        val = float(rule.threshold)
        return {
            'warning': val,
            'critical': val,
            'emergency': val
        }
    else:
        return DEFAULT_THRESHOLDS.get(metric_type)

# 基于IP地址的持续告警检查，如果80%以上的数据都超过阈值，认为持续告警
def check_sustained_alert_by_ip(ip_address, metric_type, value, minutes=1, thresholds=None):
    from model import MonitorData

    # 获取最近N分钟的数据 (这里必须用 datetime.now() 来和存入时的时区一致，而不能用 utcnow)
    start_time = datetime.now() - timedelta(minutes=minutes)

    # 根据IP地址查询最近N分钟的数据
    recent_data = MonitorData.get_by_ip(ip_address, start_time)

    if len(recent_data) < 3:  # 至少需要3个数据点
        return False

    # 获取阈值
    if thresholds is None:
        thresholds = DEFAULT_THRESHOLDS[metric_type]
        
    alert_level = determine_alert_level(value, thresholds)

    if not alert_level:
        return False

    # 检查是否所有数据都超过对应阈值
    threshold_value = thresholds[alert_level]
    sustained_count = 0

    for data in recent_data:
        # 这里的值是 Decimal 类型所以需要 float 转换
        if metric_type == 'cpu' and float(data.cpu_value) >= float(threshold_value):
            sustained_count += 1
        elif metric_type == 'memory' and float(data.memory_value) >= float(threshold_value):
            sustained_count += 1
        elif metric_type == 'disk' and float(data.disk_value) >= float(threshold_value):
            sustained_count += 1

    # 如果80%以上的数据都超过阈值，认为持续告警
    return sustained_count >= len(recent_data) * 0.8


# 根据IP地址找到服务器告警检查，获取服务器的所有关联用户
# 调用 check_sustained_alert_by_ip()检查是否持续超过阈值（2分钟）
# 如果开启 Dify 则调用 Dify 决策；否则向所有关联用户的邮箱发送告警
def check_and_send_alert_by_ip(ip_address, metric_type, value, current_metrics_all=None):
    try:
        # 1. 获取服务器信息
        server = Server.get_by_ip(ip_address)
        if not server:
            return False

        # 2. 获取告警用户列表
        users_to_alert = server.users if server.users else []
        
        if not users_to_alert:
            return False

        # 3. 获取告警阈值 (支持动态阈值)
        thresholds = get_server_thresholds(server, metric_type)

        # 4. 检查告警级别
        alert_level = determine_alert_level(value, thresholds)

        if alert_level:
            # 5. 检查是否持续超过阈值（1分钟）- 配合答辩演示的暴躁模式
            if not check_sustained_alert_by_ip(ip_address, metric_type, value, minutes=1, thresholds=thresholds):
                return True
                
            # [新增亮点] 告警静默期 (Cooldown) 检测（结合内存锁和数据库）
            # 解决现象：避免因为 Dify API 响应慢导致后来的并发线程穿透，瞬间触发多次相同告警和 AI 推理。
            cache_key = f"{server.id}_{metric_type}"
            
            with ALERT_LOCK:
                # 1. 优先检查内存储存（防多线程并发穿透）
                last_time = LAST_ALERT_CACHE.get(cache_key)
                if last_time and (datetime.now() - last_time) < timedelta(minutes=3):
                    return True # 还在静默期（可能正在调用中，或刚刚触发），直接拦截

                # 2. 检查持久化数据库层面（防重启服务后丢失内存）
                last_alert = AlertHistory.query.filter_by(
                    server_id=server.id, 
                    metric_type=metric_type
                ).order_by(AlertHistory.triggered_at.desc()).first()
                
                if last_alert and (datetime.now() - last_alert.triggered_at) < timedelta(minutes=3):
                    # 同步到内存中优化下次查询
                    LAST_ALERT_CACHE[cache_key] = last_alert.triggered_at
                    return True # 依然在静默期，放弃本次重复请求
                
                # 3. 内存占位：到这里说明验证通过准备大模型请求和发邮件，立即给当前指标占位，锁定未来3分钟的后续请求
                LAST_ALERT_CACHE[cache_key] = datetime.now()
                
            # 6. 【核心改造】引入 Dify 智能决策机制
            from services.dify_service import dify_service
            
            should_send_mail = True
            alert_reason_msg = ""
            
            if dify_service.is_configured():
                if current_metrics_all is None:
                    current_metrics_all = {'cpu': value} if metric_type == 'cpu' else {}
                # 提交给大模型进行判决
                dify_res = dify_service.trigger_workflow(server.id, current_metrics_all)
                # 记录或获取结果
                if dify_res and dify_res.get('success'):
                    decision_output = dify_service.parse_decision(dify_res)
                    if decision_output:
                          try:
                              from model.monitor import DifyDecision # 确保导入正确
                              d_record = DifyDecision.create(
                                  server_id=server.id,
                                  workflow_id=dify_service.workflow_id,
                                  input_data=dify_res.get('inputs', {}),
                                  decision_output=decision_output
                              )
                              print(f"[DIFY] 成功写入决策记录至数据库, ID: {d_record.id}")
                          except Exception as record_err:
                              import traceback
                              print(f"[DIFY] 写入决策记录失败: {record_err}")
                              traceback.print_exc()
                              
                          # 根据 Dify 的决定覆盖传统规则
                          should_send_mail = decision_output.get('should_alert', False)
                          alert_level = decision_output.get('alert_level', alert_level)
                          alert_reason_msg = decision_output.get('alert_reason', '')
                else:
                      print(f"[DIFY] 工作流未成功执行或超时，走默认兜底告警。错误信息: {dify_res.get('error') if dify_res else 'None'}")
            
            # 7. 根据最终决定是否发送邮件
            if not should_send_mail:
                return True # Dify 抑制了告警

            # 向所有关联用户发送告警邮件
            success_count = 0
            # 使用 float 转换阈值，确保 AlertHistory 存储正确
            threshold_val = float(thresholds[alert_level])

            from mail.alert import send_alert_email  # ensure it's available 
            for user in users_to_alert:
                success = send_alert_email(
                    user.email,
                    server.server_name,
                    metric_type,
                    value,
                    alert_level,
                    threshold_val
                )
                if success:
                    success_count += 1

            # [修复Bug] 无论邮件发送成功与否，只要判定为告警就必须把记录写到数据库，否则页面上看不到！
            try:
                msg_content = f"服务器 {server.server_name} {metric_type} 告警: 当前值 {value}%, 阈值 {threshold_val}%"
                if alert_reason_msg:
                    msg_content += f"\n【AI智能诊断】: {alert_reason_msg}"
                AlertHistory.create(
                    server_id=server.id,
                    metric_type=metric_type,
                    current_value=value,
                    threshold=threshold_val,
                    content=msg_content
                )
            except Exception as hist_err:
                print(f"告警记录存入数据库失败: {hist_err}")

            return True
        else:
            return True

    except Exception as e:
        print(f"告警检查失败: {e}")
        return False


# 确定告警级别
def determine_alert_level(value, thresholds):
    if value >= thresholds.get('emergency', 100):
        return 'emergency'
    elif value >= thresholds.get('critical', 100):
        return 'critical'
    elif value >= thresholds.get('warning', 100):
        return 'warning'
    return None


# 发送告警邮件
def send_alert_email(email, server_name, metric_type, value, level, threshold=None):
    try:
        import smtplib
        from email.mime.text import MIMEText

        if threshold is None:
             threshold = get_threshold_by_level(level, metric_type)

        # 生成告警消息
        # 简单处理，不再依赖复杂的 ALERT_TEMPLATES，或者确保 ALERT_TEMPLATES 兼容
        # 假设 ALERT_TEMPLATES 存在于 setting.py
        
        message = f"""
        【{level.upper()}】服务器监控告警
        
        服务器: {server_name}
        告警指标: {metric_type}
        当前数值: {value}%
        触发阈值: {threshold}%
        
        请及时处理。
        """

        # 创建邮件
        msg = MIMEText(message, 'plain', 'utf-8')
        msg['From'] = SMTP_SENDER
        msg['To'] = email
        msg['Subject'] = f"【{level.upper()}】服务器 {server_name} 监控告警"

        # 发送邮件
        with smtplib.SMTP_SSL(SMTP_HOST, SMTP_PORT) as server:
            server.login(SMTP_USER, SMTP_PASS)
            server.sendmail(SMTP_SENDER, email, msg.as_string())
        return True
    except Exception as e:
        print(f"发送邮件失败: {e}")
        pass  # 发送告警邮件失败
        return False


# 根据级别获取阈值 (保留辅助函数)
def get_threshold_by_level(level, metric_type):
    thresholds = DEFAULT_THRESHOLDS.get(metric_type, {})
    return thresholds.get(level, 0)

