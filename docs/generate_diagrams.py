#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
毕业论文图表生成工具（黑白灰配色版）
用于自动生成论文中的架构图和流程图
"""

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle, Circle
import os

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['SimHei', 'Microsoft YaHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

# 黑白灰配色方案
COLORS = {
    'black': '#000000',        # 纯黑 - 主要文字和边框
    'dark_gray': '#404040',    # 深灰 - 重要模块背景
    'medium_gray': '#808080',  # 中灰 - 次要模块背景
    'light_gray': '#C0C0C0',   # 浅灰 - 辅助元素背景
    'very_light_gray': '#E8E8E8',  # 极浅灰 - 基础背景
    'white': '#FFFFFF'         # 纯白 - 留白区域
}

def ensure_output_dir():
    """确保输出目录存在"""
    output_dir = 'docs/images'
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return output_dir


def draw_debounce_mechanism():
    """绘制防抖锁工作原理 - 图1 (黑白灰版)
    
    核心原理：双重检查机制（threading.Lock + 内存字典 + 数据库持久化）
    - 第1层：内存锁 LAST_ALERT_CACHE，防多线程并发穿透
    - 第2层：数据库 AlertHistory，防服务重启后内存丢失
    - 冷却期：3分钟（180秒）
    - 锁粒度：server_id + metric_type（如 "1_cpu"）
    """
    fig, ax = plt.subplots(figsize=(14, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # 标题
    ax.text(6, 7.5, '防抖锁工作原理（双重检查机制）', fontsize=16, ha='center', weight='bold', color=COLORS['black'])
    
    # 时间轴
    ax.plot([1, 11], [6, 6], 'k-', linewidth=2, color=COLORS['black'])
    ax.arrow(11, 6, 0.3, 0, head_width=0.15, head_length=0.15, fc=COLORS['black'], ec=COLORS['black'])
    ax.text(11.5, 6, '时间', fontsize=10, va='center', color=COLORS['black'])
    
    # 时间点标记
    times = [
        (2, 'T0\n首次超阈值'),
        (5, 'T1\n90秒后\n再次超阈值'),
        (8, 'T2\n5分钟后\n第三次超阈值'),
    ]
    
    for x, label in times:
        ax.plot([x, x], [5.7, 6.3], 'k-', linewidth=1.5, color=COLORS['black'])
        ax.text(x, 5.3, label, fontsize=9, ha='center', va='top', color=COLORS['black'])
    
    # 第一次告警（T0）
    rect1 = FancyBboxPatch((1.5, 3.5), 1, 0.8, boxstyle="round,pad=0.05", 
                           edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=2)
    ax.add_patch(rect1)
    ax.text(2, 3.9, '检查内存锁\n无记录', fontsize=9, ha='center', weight='bold', color=COLORS['black'])
    
    rect2 = FancyBboxPatch((1.5, 2.3), 1, 0.8, boxstyle="round,pad=0.05", 
                           edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=2)
    ax.add_patch(rect2)
    ax.text(2, 2.7, '检查数据库\n无记录', fontsize=9, ha='center', weight='bold', color=COLORS['black'])
    
    rect3 = FancyBboxPatch((1.5, 1.1), 1, 0.8, boxstyle="round,pad=0.05", 
                           edgecolor=COLORS['black'], facecolor=COLORS['dark_gray'], linewidth=2.5)
    ax.add_patch(rect3)
    ax.text(2, 1.5, '✓ 获取锁\n发送告警', fontsize=9, ha='center', weight='bold', color=COLORS['white'])
    
    # 连接箭头
    ax.annotate('', xy=(2, 2.3), xytext=(2, 3.5), 
                arrowprops=dict(arrowstyle='->', lw=1.5, color=COLORS['black']))
    ax.annotate('', xy=(2, 1.9), xytext=(2, 2.3), 
                arrowprops=dict(arrowstyle='->', lw=1.5, color=COLORS['black']))
    
    # 第二次告警（T1 = T0 + 90秒）
    rect4 = FancyBboxPatch((4.5, 3.5), 1, 0.8, boxstyle="round,pad=0.05", 
                           edgecolor=COLORS['black'], facecolor=COLORS['medium_gray'], linewidth=2)
    ax.add_patch(rect4)
    ax.text(5, 3.9, '检查内存锁\n有记录', fontsize=9, ha='center', weight='bold', color=COLORS['white'])
    
    circle1 = Circle((5, 2.5), 0.4, edgecolor=COLORS['black'], facecolor=COLORS['white'], linewidth=2)
    ax.add_patch(circle1)
    ax.text(5, 2.5, '距上次\n90秒', fontsize=8, ha='center', va='center', color=COLORS['black'])
    
    rect5 = FancyBboxPatch((4.5, 1.1), 1, 0.8, boxstyle="round,pad=0.05", 
                           edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], linewidth=2)
    ax.add_patch(rect5)
    ax.text(5, 1.5, '✗ 拦截\n不发送', fontsize=9, ha='center', weight='bold', color=COLORS['black'])
    
    ax.annotate('', xy=(5, 2.1), xytext=(5, 3.5), 
                arrowprops=dict(arrowstyle='->', lw=1.5, color=COLORS['black']))
    ax.annotate('', xy=(5, 1.9), xytext=(5, 2.1), 
                arrowprops=dict(arrowstyle='->', lw=1.5, color=COLORS['black']))
    ax.text(5.7, 2.5, '< 3分钟\n冷却期内', fontsize=8, ha='left', color=COLORS['black'], style='italic')
    
    # 第三次告警（T2 = T0 + 5分钟）
    rect6 = FancyBboxPatch((7.5, 3.5), 1, 0.8, boxstyle="round,pad=0.05", 
                           edgecolor=COLORS['black'], facecolor=COLORS['medium_gray'], linewidth=2)
    ax.add_patch(rect6)
    ax.text(8, 3.9, '检查内存锁\n有记录', fontsize=9, ha='center', weight='bold', color=COLORS['white'])
    
    circle2 = Circle((8, 2.5), 0.4, edgecolor=COLORS['black'], facecolor=COLORS['white'], linewidth=2)
    ax.add_patch(circle2)
    ax.text(8, 2.5, '距上次\n5分钟', fontsize=8, ha='center', va='center', color=COLORS['black'])
    
    rect7 = FancyBboxPatch((7.5, 1.1), 1, 0.8, boxstyle="round,pad=0.05", 
                           edgecolor=COLORS['black'], facecolor=COLORS['dark_gray'], linewidth=2.5)
    ax.add_patch(rect7)
    ax.text(8, 1.5, '✓ 获取锁\n发送告警', fontsize=9, ha='center', weight='bold', color=COLORS['white'])
    
    ax.annotate('', xy=(8, 2.1), xytext=(8, 3.5), 
                arrowprops=dict(arrowstyle='->', lw=1.5, color=COLORS['black']))
    ax.annotate('', xy=(8, 1.9), xytext=(8, 2.1), 
                arrowprops=dict(arrowstyle='->', lw=1.5, color=COLORS['black']))
    ax.text(8.7, 2.5, '≥ 3分钟\n冷却期结束', fontsize=8, ha='left', color=COLORS['black'], style='italic')
    
    # 核心机制说明框
    info_box = FancyBboxPatch((0.5, 0.05), 11, 0.7, boxstyle="round,pad=0.1", 
                              edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], 
                              linewidth=1.5, linestyle='--')
    ax.add_patch(info_box)
    ax.text(6, 0.55, '核心机制：以 server_id + metric_type 为粒度（如"1_cpu"），维护双重防抖状态', 
            fontsize=9, ha='center', weight='bold', color=COLORS['black'])
    ax.text(6, 0.3, '第1层：threading.Lock() + 内存字典 LAST_ALERT_CACHE（防多线程并发穿透）', 
            fontsize=8, ha='center', color=COLORS['dark_gray'])
    ax.text(6, 0.1, '第2层：数据库 AlertHistory 表（防服务重启后内存丢失）| 冷却期：3分钟', 
            fontsize=8, ha='center', color=COLORS['dark_gray'])
    
    plt.tight_layout()
    output_dir = ensure_output_dir()
    plt.savefig(f'{output_dir}/图1_防抖锁工作原理.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print('✅ 图1: 防抖锁工作原理 已生成（黑白灰版）')


def draw_alert_flow():
    """绘制监控告警业务流程 - 图3 (黑白灰版)"""
    fig, ax = plt.subplots(figsize=(10, 14))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 16)
    ax.axis('off')
    
    # 标题
    ax.text(5, 15.5, '监控告警业务流程', fontsize=16, ha='center', weight='bold', color=COLORS['black'])
    
    y = 14.5
    steps = [
        ('开始：监控探针上报数据', COLORS['dark_gray'], True),
        ('存入 MonitorData 表', COLORS['light_gray'], False),
        ('获取告警规则\n（AlertRule 表）', COLORS['light_gray'], False),
        ('判断是否超阈值？', COLORS['medium_gray'], False),
        ('时序分析：80%数据点超阈？', COLORS['medium_gray'], False),
        ('防抖锁检查\n（内存+数据库双重验证）', COLORS['dark_gray'], True),
        ('AI智能诊断\n（Dify工作流）', COLORS['dark_gray'], True),
        ('判断：是否需要告警？', COLORS['medium_gray'], False),
        ('异步任务队列\n（发送邮件）', COLORS['light_gray'], False),
        ('写入 AlertHistory 表', COLORS['light_gray'], False),
        ('审计日志记录\n（AuditLog 表）', COLORS['light_gray'], False),
        ('结束', COLORS['dark_gray'], True),
    ]
    
    for i, (text, bg_color, is_bold) in enumerate(steps):
        # 判断是否为菱形（决策节点）
        is_decision = '？' in text or '判断' in text
        
        if is_decision:
            # 菱形决策框
            diamond = patches.FancyBboxPatch((4, y-0.4), 2, 0.8, boxstyle="round,pad=0.1",
                                            edgecolor=COLORS['black'], facecolor=bg_color, linewidth=2)
            ax.add_patch(diamond)
        else:
            # 矩形流程框
            rect = FancyBboxPatch((3.5, y-0.4), 3, 0.8, boxstyle="round,pad=0.05",
                                 edgecolor=COLORS['black'], facecolor=bg_color, 
                                 linewidth=2.5 if is_bold else 1.5)
            ax.add_patch(rect)
        
        # 文字颜色：深色背景用白色文字，浅色背景用黑色文字
        text_color = COLORS['white'] if bg_color == COLORS['dark_gray'] else COLORS['black']
        ax.text(5, y, text, fontsize=10 if is_bold else 9, ha='center', va='center',
               weight='bold' if is_bold else 'normal', color=text_color)
        
        # 绘制连接箭头（除了最后一个）
        if i < len(steps) - 1:
            # 特殊处理：决策节点的分支
            if '是否超阈值' in text:
                # 右分支：否
                ax.annotate('', xy=(7, y-0.5), xytext=(6, y),
                           arrowprops=dict(arrowstyle='->', lw=1.5, color=COLORS['black']))
                ax.text(6.5, y-0.2, '否', fontsize=8, ha='center', color=COLORS['black'])
                ax.text(8.5, y-0.5, '忽略', fontsize=8, ha='center', 
                       bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS['very_light_gray'], 
                                edgecolor=COLORS['black']), color=COLORS['black'])
                # 主分支：是
                ax.annotate('', xy=(5, y-0.8), xytext=(5, y-0.4),
                           arrowprops=dict(arrowstyle='->', lw=1.5, color=COLORS['black']))
                ax.text(4.5, y-0.6, '是', fontsize=8, ha='center', color=COLORS['black'])
            
            elif '是否需要告警' in text:
                # 右分支：否
                ax.annotate('', xy=(7, y-0.5), xytext=(6, y),
                           arrowprops=dict(arrowstyle='->', lw=1.5, color=COLORS['black']))
                ax.text(6.5, y-0.2, '否', fontsize=8, ha='center', color=COLORS['black'])
                ax.text(8.5, y-0.5, '抑制', fontsize=8, ha='center',
                       bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS['very_light_gray'], 
                                edgecolor=COLORS['black']), color=COLORS['black'])
                # 主分支：是
                ax.annotate('', xy=(5, y-0.8), xytext=(5, y-0.4),
                           arrowprops=dict(arrowstyle='->', lw=1.5, color=COLORS['black']))
                ax.text(4.5, y-0.6, '是', fontsize=8, ha='center', color=COLORS['black'])
            
            else:
                # 普通直线箭头
                ax.annotate('', xy=(5, y-0.8), xytext=(5, y-0.4),
                           arrowprops=dict(arrowstyle='->', lw=1.5, color=COLORS['black']))
        
        y -= 1.2
    
    # 亮点标注
    highlight_box = FancyBboxPatch((0.3, 0.3), 9.4, 1.2, boxstyle="round,pad=0.1",
                                  edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], 
                                  linewidth=1.5, linestyle='--')
    ax.add_patch(highlight_box)
    ax.text(5, 1.3, '创新点', fontsize=11, ha='center', weight='bold', color=COLORS['black'])
    ax.text(5, 0.95, '① 防抖锁（双重检查）：避免大模型API延迟导致的并发告警穿透', 
            fontsize=9, ha='center', color=COLORS['dark_gray'])
    ax.text(5, 0.65, '② 时序分析：80%数据点超阈才告警，避免瞬时抖动误报', 
            fontsize=9, ha='center', color=COLORS['dark_gray'])
    ax.text(5, 0.35, '③ AI智能诊断：Dify工作流分析历史趋势，精准判断真实故障', 
            fontsize=9, ha='center', color=COLORS['dark_gray'])
    
    plt.tight_layout()
    output_dir = ensure_output_dir()
    plt.savefig(f'{output_dir}/图3_监控告警业务流程.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print('✅ 图3: 监控告警业务流程 已生成（黑白灰版）')


def draw_system_architecture():
    """绘制系统总体架构图 - 图5 (黑白灰版)"""
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 标题
    ax.text(7, 9.5, '系统总体架构（分层设计）', fontsize=16, ha='center', weight='bold', color=COLORS['black'])
    
    # 第1层：表现层
    layer1 = FancyBboxPatch((1, 8.2), 12, 0.9, boxstyle="round,pad=0.05",
                           edgecolor=COLORS['black'], facecolor=COLORS['dark_gray'], linewidth=2)
    ax.add_patch(layer1)
    ax.text(7, 8.65, '表现层（Presentation Layer）', fontsize=11, ha='center', weight='bold', color=COLORS['white'])
    
    components = ['Vue 3 前端', 'ECharts图表', 'Element Plus组件', 'Pinia状态管理']
    x_start = 2
    for comp in components:
        box = FancyBboxPatch((x_start, 8.3), 2.2, 0.5, boxstyle="round,pad=0.03",
                            edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=1)
        ax.add_patch(box)
        ax.text(x_start+1.1, 8.55, comp, fontsize=8, ha='center', color=COLORS['black'])
        x_start += 2.5
    
    # 第2层：业务逻辑层
    layer2 = FancyBboxPatch((1, 6.9), 12, 0.9, boxstyle="round,pad=0.05",
                           edgecolor=COLORS['black'], facecolor=COLORS['medium_gray'], linewidth=2)
    ax.add_patch(layer2)
    ax.text(7, 7.35, '业务逻辑层（Business Logic Layer）', fontsize=11, ha='center', weight='bold', color=COLORS['white'])
    
    components2 = ['Flask Blueprint路由', '用户认证模块', '监控数据处理', '告警规则引擎', '审计日志']
    x_start = 1.5
    for comp in components2:
        box = FancyBboxPatch((x_start, 7.0), 2, 0.5, boxstyle="round,pad=0.03",
                            edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=1)
        ax.add_patch(box)
        ax.text(x_start+1, 7.25, comp, fontsize=8, ha='center', color=COLORS['black'])
        x_start += 2.3
    
    # 第3层：并发控制层（创新亮点）
    layer3 = FancyBboxPatch((1, 5.6), 12, 0.9, boxstyle="round,pad=0.05",
                           edgecolor=COLORS['black'], facecolor=COLORS['dark_gray'], linewidth=2.5)
    ax.add_patch(layer3)
    ax.text(7, 6.05, '并发控制层（Concurrency Control Layer）★核心创新★', 
            fontsize=11, ha='center', weight='bold', color=COLORS['white'])
    
    components3 = ['防抖锁（内存）', '冷却期管理', '异步任务队列', '线程池控制']
    x_start = 2.5
    for comp in components3:
        box = FancyBboxPatch((x_start, 5.7), 2, 0.5, boxstyle="round,pad=0.03",
                            edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], linewidth=1.5)
        ax.add_patch(box)
        ax.text(x_start+1, 5.95, comp, fontsize=8, ha='center', weight='bold', color=COLORS['black'])
        x_start += 2.5
    
    # 第4层：数据持久层
    layer4 = FancyBboxPatch((1, 4.3), 5.5, 0.9, boxstyle="round,pad=0.05",
                           edgecolor=COLORS['black'], facecolor=COLORS['medium_gray'], linewidth=2)
    ax.add_patch(layer4)
    ax.text(3.75, 4.75, '数据持久层（Data Layer）', fontsize=11, ha='center', weight='bold', color=COLORS['white'])
    
    components4 = ['MySQL 8.0', 'SQLAlchemy ORM', 'Alembic迁移']
    x_start = 1.5
    for comp in components4:
        box = FancyBboxPatch((x_start, 4.4), 1.5, 0.5, boxstyle="round,pad=0.03",
                            edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=1)
        ax.add_patch(box)
        ax.text(x_start+0.75, 4.65, comp, fontsize=8, ha='center', color=COLORS['black'])
        x_start += 1.7
    
    # 第5层：日志采集层
    layer5 = FancyBboxPatch((7.5, 4.3), 5.5, 0.9, boxstyle="round,pad=0.05",
                           edgecolor=COLORS['black'], facecolor=COLORS['medium_gray'], linewidth=2)
    ax.add_patch(layer5)
    ax.text(10.25, 4.75, '日志采集层（Log Layer）', fontsize=11, ha='center', weight='bold', color=COLORS['white'])
    
    components5 = ['Filebeat 8.x', 'Elasticsearch 8.x']
    x_start = 8.5
    for comp in components5:
        box = FancyBboxPatch((x_start, 4.4), 2, 0.5, boxstyle="round,pad=0.03",
                            edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=1)
        ax.add_patch(box)
        ax.text(x_start+1, 4.65, comp, fontsize=8, ha='center', color=COLORS['black'])
        x_start += 2.2
    
    # 第6层：AI计算层
    layer6 = FancyBboxPatch((1, 2.8), 12, 0.9, boxstyle="round,pad=0.05",
                           edgecolor=COLORS['black'], facecolor=COLORS['dark_gray'], linewidth=2)
    ax.add_patch(layer6)
    ax.text(7, 3.25, 'AI计算层（AI Intelligence Layer）', fontsize=11, ha='center', weight='bold', color=COLORS['white'])
    
    box = FancyBboxPatch((5, 2.9), 4, 0.5, boxstyle="round,pad=0.03",
                        edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=1)
    ax.add_patch(box)
    ax.text(7, 3.15, 'Dify 工作流编排 + LLM推理', fontsize=9, ha='center', weight='bold', color=COLORS['black'])
    
    # 底层：硬件探针 + 业务容器
    layer7 = FancyBboxPatch((1, 1.3), 5.5, 0.9, boxstyle="round,pad=0.05",
                           edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=2)
    ax.add_patch(layer7)
    ax.text(3.75, 1.75, '硬件探针（Probe）', fontsize=11, ha='center', weight='bold', color=COLORS['black'])
    ax.text(3.75, 1.5, 'psutil（CPU/内存/磁盘）', fontsize=8, ha='center', color=COLORS['black'])
    
    layer8 = FancyBboxPatch((7.5, 1.3), 5.5, 0.9, boxstyle="round,pad=0.05",
                           edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=2)
    ax.add_patch(layer8)
    ax.text(10.25, 1.75, '业务容器（Business Apps）', fontsize=11, ha='center', weight='bold', color=COLORS['black'])
    ax.text(10.25, 1.5, 'Nginx/MySQL/Redis等', fontsize=8, ha='center', color=COLORS['black'])
    
    # 数据流向箭头
    ax.annotate('', xy=(7, 8.2), xytext=(7, 7.8),
               arrowprops=dict(arrowstyle='<->', lw=2, color=COLORS['black']))
    ax.annotate('', xy=(7, 6.9), xytext=(7, 6.5),
               arrowprops=dict(arrowstyle='<->', lw=2, color=COLORS['black']))
    ax.annotate('', xy=(3.75, 5.6), xytext=(3.75, 5.2),
               arrowprops=dict(arrowstyle='<->', lw=2, color=COLORS['black']))
    ax.annotate('', xy=(10.25, 5.6), xytext=(10.25, 5.2),
               arrowprops=dict(arrowstyle='<->', lw=2, color=COLORS['black']))
    ax.annotate('', xy=(7, 4.3), xytext=(7, 3.7),
               arrowprops=dict(arrowstyle='<->', lw=2, color=COLORS['black']))
    ax.annotate('', xy=(3.75, 2.8), xytext=(3.75, 2.2),
               arrowprops=dict(arrowstyle='->', lw=1.5, color=COLORS['black']))
    ax.annotate('', xy=(10.25, 2.8), xytext=(10.25, 2.2),
               arrowprops=dict(arrowstyle='->', lw=1.5, color=COLORS['black']))
    
    # 图例说明
    legend_box = FancyBboxPatch((0.5, 0.1), 13, 0.8, boxstyle="round,pad=0.1",
                               edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], 
                               linewidth=1.5, linestyle='--')
    ax.add_patch(legend_box)
    ax.text(7, 0.7, '技术栈：Flask 2.3 + Vue 3.5 + MySQL 8.0 + Elasticsearch 8.x + Dify AI', 
            fontsize=9, ha='center', weight='bold', color=COLORS['black'])
    ax.text(7, 0.4, '部署模式：Windows物理机（代码运行） + Linux虚拟机（中间件运行）', 
            fontsize=9, ha='center', color=COLORS['dark_gray'])
    
    plt.tight_layout()
    output_dir = ensure_output_dir()
    plt.savefig(f'{output_dir}/图5_系统总体架构图.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print('✅ 图5: 系统总体架构图 已生成（黑白灰版）')


def draw_deployment_topology():
    """绘制部署拓扑图 - 图6 (黑白灰版)
    
    部署架构说明：
    - Windows物理机：运行Flask后端代码 + Vue前端代码 + Python监控探针
    - Linux虚拟机：运行所有中间件（MySQL, ES, Filebeat, Nginx, Redis等Docker容器）
    """
    fig, ax = plt.subplots(figsize=(14, 10))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 标题
    ax.text(7, 9.5, '部署拓扑图（混合架构）', fontsize=16, ha='center', weight='bold', color=COLORS['black'])
    
    # ========== Windows 物理机区域 ==========
    windows_box = FancyBboxPatch((0.5, 4.5), 6, 4.3, boxstyle="round,pad=0.1",
                                edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], 
                                linewidth=2.5)
    ax.add_patch(windows_box)
    ax.text(3.5, 8.6, '🖥 Windows 物理机', fontsize=13, ha='center', weight='bold', color=COLORS['black'])
    ax.text(3.5, 8.25, 'IP: 192.168.1.100', fontsize=9, ha='center', color=COLORS['dark_gray'])
    
    # Flask 后端
    flask_box = FancyBboxPatch((1, 7.2), 2, 0.8, boxstyle="round,pad=0.05",
                              edgecolor=COLORS['black'], facecolor=COLORS['dark_gray'], linewidth=2)
    ax.add_patch(flask_box)
    ax.text(2, 7.75, 'Flask后端', fontsize=10, ha='center', weight='bold', color=COLORS['white'])
    ax.text(2, 7.4, 'app.py', fontsize=8, ha='center', color=COLORS['white'])
    ax.text(2, 7.1, 'Port: 5000', fontsize=7, ha='center', color=COLORS['white'])
    
    # Vue 前端
    vue_box = FancyBboxPatch((4, 7.2), 2, 0.8, boxstyle="round,pad=0.05",
                            edgecolor=COLORS['black'], facecolor=COLORS['dark_gray'], linewidth=2)
    ax.add_patch(vue_box)
    ax.text(5, 7.75, 'Vue前端', fontsize=10, ha='center', weight='bold', color=COLORS['white'])
    ax.text(5, 7.4, 'Vite开发服务器', fontsize=8, ha='center', color=COLORS['white'])
    ax.text(5, 7.1, 'Port: 5173', fontsize=7, ha='center', color=COLORS['white'])
    
    # 监控探针
    probe_box = FancyBboxPatch((1.5, 5.8), 4, 0.8, boxstyle="round,pad=0.05",
                              edgecolor=COLORS['black'], facecolor=COLORS['medium_gray'], linewidth=2)
    ax.add_patch(probe_box)
    ax.text(3.5, 6.35, '监控探针（Python）', fontsize=10, ha='center', weight='bold', color=COLORS['white'])
    ax.text(3.5, 6, 'psutil采集CPU/内存/磁盘', fontsize=8, ha='center', color=COLORS['white'])
    
    # Python 环境
    python_box = FancyBboxPatch((1.5, 4.8), 4, 0.6, boxstyle="round,pad=0.05",
                               edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=1.5)
    ax.add_patch(python_box)
    ax.text(3.5, 5.1, 'Python 3.12 + venv', fontsize=9, ha='center', color=COLORS['black'])
    
    # ========== Linux 虚拟机区域 ==========
    linux_box = FancyBboxPatch((7.5, 0.8), 6, 7.9, boxstyle="round,pad=0.1",
                              edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], 
                              linewidth=2.5)
    ax.add_patch(linux_box)
    ax.text(10.5, 8.6, '🐧 Linux 虚拟机（CentOS/Ubuntu）', fontsize=13, ha='center', weight='bold', color=COLORS['black'])
    ax.text(10.5, 8.25, 'IP: 192.168.1.101', fontsize=9, ha='center', color=COLORS['dark_gray'])
    
    # Docker 容器组
    docker_title = FancyBboxPatch((8, 7.5), 5, 0.4, boxstyle="round,pad=0.03",
                                 edgecolor=COLORS['black'], facecolor=COLORS['medium_gray'], linewidth=1.5)
    ax.add_patch(docker_title)
    ax.text(10.5, 7.7, 'Docker Compose 容器集群', fontsize=10, ha='center', weight='bold', color=COLORS['white'])
    
    # MySQL 容器
    mysql_box = FancyBboxPatch((8, 6.6), 2.2, 0.7, boxstyle="round,pad=0.05",
                              edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=1.5)
    ax.add_patch(mysql_box)
    ax.text(9.1, 7.05, 'MySQL 8.0', fontsize=9, ha='center', weight='bold', color=COLORS['black'])
    ax.text(9.1, 6.8, 'Port: 3306', fontsize=7, ha='center', color=COLORS['black'])
    
    # Elasticsearch 容器
    es_box = FancyBboxPatch((10.8, 6.6), 2.2, 0.7, boxstyle="round,pad=0.05",
                           edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=1.5)
    ax.add_patch(es_box)
    ax.text(11.9, 7.05, 'Elasticsearch', fontsize=9, ha='center', weight='bold', color=COLORS['black'])
    ax.text(11.9, 6.8, 'Port: 9200', fontsize=7, ha='center', color=COLORS['black'])
    
    # Filebeat 容器
    filebeat_box = FancyBboxPatch((8, 5.5), 2.2, 0.7, boxstyle="round,pad=0.05",
                                 edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=1.5)
    ax.add_patch(filebeat_box)
    ax.text(9.1, 5.95, 'Filebeat', fontsize=9, ha='center', weight='bold', color=COLORS['black'])
    ax.text(9.1, 5.7, '日志采集', fontsize=7, ha='center', color=COLORS['black'])
    
    # Nginx 容器
    nginx_box = FancyBboxPatch((10.8, 5.5), 2.2, 0.7, boxstyle="round,pad=0.05",
                              edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=1.5)
    ax.add_patch(nginx_box)
    ax.text(11.9, 5.95, 'Nginx', fontsize=9, ha='center', weight='bold', color=COLORS['black'])
    ax.text(11.9, 5.7, 'Port: 80', fontsize=7, ha='center', color=COLORS['black'])
    
    # Redis 容器
    redis_box = FancyBboxPatch((8, 4.4), 2.2, 0.7, boxstyle="round,pad=0.05",
                              edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=1.5)
    ax.add_patch(redis_box)
    ax.text(9.1, 4.85, 'Redis', fontsize=9, ha='center', weight='bold', color=COLORS['black'])
    ax.text(9.1, 4.6, 'Port: 6379', fontsize=7, ha='center', color=COLORS['black'])
    
    # Kibana 容器
    kibana_box = FancyBboxPatch((10.8, 4.4), 2.2, 0.7, boxstyle="round,pad=0.05",
                               edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=1.5)
    ax.add_patch(kibana_box)
    ax.text(11.9, 4.85, 'Kibana', fontsize=9, ha='center', weight='bold', color=COLORS['black'])
    ax.text(11.9, 4.6, 'Port: 5601', fontsize=7, ha='center', color=COLORS['black'])
    
    # Docker 环境说明
    docker_env = FancyBboxPatch((8, 3.3), 5, 0.6, boxstyle="round,pad=0.05",
                               edgecolor=COLORS['black'], facecolor=COLORS['medium_gray'], linewidth=1.5)
    ax.add_patch(docker_env)
    ax.text(10.5, 3.6, 'Docker Engine + docker-compose', fontsize=9, ha='center', weight='bold', color=COLORS['white'])
    
    # 业务应用容器
    business_title = FancyBboxPatch((8, 2.5), 5, 0.4, boxstyle="round,pad=0.03",
                                   edgecolor=COLORS['black'], facecolor=COLORS['dark_gray'], linewidth=1.5)
    ax.add_patch(business_title)
    ax.text(10.5, 2.7, '业务应用容器（被监控对象）', fontsize=10, ha='center', weight='bold', color=COLORS['white'])
    
    business_box = FancyBboxPatch((8.5, 1.2), 4, 1, boxstyle="round,pad=0.05",
                                 edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=1.5)
    ax.add_patch(business_box)
    ax.text(10.5, 1.95, 'Java应用 / Node.js服务', fontsize=9, ha='center', color=COLORS['black'])
    ax.text(10.5, 1.65, 'Python服务 / Go微服务', fontsize=9, ha='center', color=COLORS['black'])
    ax.text(10.5, 1.35, '...(各类业务容器)', fontsize=8, ha='center', style='italic', color=COLORS['dark_gray'])
    
    # ========== 网络连接箭头 ==========
    # Flask -> MySQL
    ax.annotate('', xy=(8, 7), xytext=(3, 7),
               arrowprops=dict(arrowstyle='<->', lw=2, color=COLORS['black']))
    ax.text(5.5, 7.2, 'SQL查询', fontsize=8, ha='center', 
           bbox=dict(boxstyle='round,pad=0.2', facecolor=COLORS['white'], edgecolor=COLORS['black']))
    
    # Flask -> Elasticsearch
    ax.annotate('', xy=(10.8, 6.95), xytext=(3, 7.5),
               arrowprops=dict(arrowstyle='<->', lw=1.5, color=COLORS['black'], linestyle='--'))
    ax.text(6.5, 7.8, '日志查询', fontsize=7, ha='center', color=COLORS['dark_gray'])
    
    # Filebeat -> Elasticsearch
    ax.annotate('', xy=(10.8, 5.85), xytext=(10.2, 5.85),
               arrowprops=dict(arrowstyle='->', lw=1.5, color=COLORS['black']))
    ax.text(10.5, 6.15, '推送', fontsize=7, ha='center', color=COLORS['dark_gray'])
    
    # 监控探针 -> Flask
    ax.annotate('', xy=(2, 7.2), xytext=(2, 6.6),
               arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['black']))
    ax.text(2.5, 6.9, '上报', fontsize=8, ha='left', color=COLORS['black'])
    
    # ========== 底部说明框 ==========
    info_box = FancyBboxPatch((0.5, 0.05), 13, 0.65, boxstyle="round,pad=0.1",
                             edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], 
                             linewidth=1.5, linestyle='--')
    ax.add_patch(info_box)
    ax.text(7, 0.55, '网络拓扑：局域网 192.168.1.0/24 | 虚拟机类型：VirtualBox/VMware Workstation', 
            fontsize=9, ha='center', weight='bold', color=COLORS['black'])
    ax.text(7, 0.3, '数据流向：Windows探针 → Flask后端 → MySQL/ES（虚拟机） | 日志流：业务容器 → Filebeat → ES', 
            fontsize=8, ha='center', color=COLORS['dark_gray'])
    
    plt.tight_layout()
    output_dir = ensure_output_dir()
    plt.savefig(f'{output_dir}/图6_部署拓扑图.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print('✅ 图6: 部署拓扑图 已生成（黑白灰版）')


def draw_er_relationship():
    """绘制ER关系图 - 图2 (黑白灰版)
    
    展示核心实体关系：User（用户）、Server（服务器）、AlertRule（告警规则）
    """
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # 标题
    ax.text(6, 7.5, 'ER关系图（核心实体关联）', fontsize=16, ha='center', weight='bold', color=COLORS['black'])
    
    # User 实体（左侧）
    user_box = FancyBboxPatch((0.5, 4.5), 3, 2, boxstyle="round,pad=0.1",
                             edgecolor=COLORS['black'], facecolor=COLORS['dark_gray'], linewidth=2.5)
    ax.add_patch(user_box)
    ax.text(2, 6.2, 'User（用户）', fontsize=12, ha='center', weight='bold', color=COLORS['white'])
    ax.text(2, 5.7, 'id (PK)', fontsize=9, ha='center', color=COLORS['white'])
    ax.text(2, 5.4, 'username', fontsize=9, ha='center', color=COLORS['white'])
    ax.text(2, 5.1, 'email', fontsize=9, ha='center', color=COLORS['white'])
    ax.text(2, 4.8, 'role (admin/user)', fontsize=9, ha='center', color=COLORS['white'])
    
    # Server 实体（右侧）
    server_box = FancyBboxPatch((8.5, 4.5), 3, 2, boxstyle="round,pad=0.1",
                               edgecolor=COLORS['black'], facecolor=COLORS['dark_gray'], linewidth=2.5)
    ax.add_patch(server_box)
    ax.text(10, 6.2, 'Server（服务器）', fontsize=12, ha='center', weight='bold', color=COLORS['white'])
    ax.text(10, 5.7, 'id (PK)', fontsize=9, ha='center', color=COLORS['white'])
    ax.text(10, 5.4, 'server_name', fontsize=9, ha='center', color=COLORS['white'])
    ax.text(10, 5.1, 'ip_address', fontsize=9, ha='center', color=COLORS['white'])
    ax.text(10, 4.8, 'description', fontsize=9, ha='center', color=COLORS['white'])
    
    # AlertRule 实体（中下方）
    alert_box = FancyBboxPatch((4.5, 1), 3, 2.2, boxstyle="round,pad=0.1",
                              edgecolor=COLORS['black'], facecolor=COLORS['medium_gray'], linewidth=2.5)
    ax.add_patch(alert_box)
    ax.text(6, 2.9, 'AlertRule（告警规则）', fontsize=11, ha='center', weight='bold', color=COLORS['white'])
    ax.text(6, 2.5, 'id (PK)', fontsize=9, ha='center', color=COLORS['white'])
    ax.text(6, 2.2, 'server_id (FK)', fontsize=9, ha='center', color=COLORS['white'])
    ax.text(6, 1.9, 'metric_type', fontsize=9, ha='center', color=COLORS['white'])
    ax.text(6, 1.6, 'threshold', fontsize=9, ha='center', color=COLORS['white'])
    ax.text(6, 1.3, 'silence_minutes', fontsize=9, ha='center', color=COLORS['white'])
    
    # 关系：User - Server (多对多)
    relationship1 = FancyBboxPatch((4, 5.2), 4, 0.6, boxstyle="round,pad=0.05",
                                  edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=1.5)
    ax.add_patch(relationship1)
    ax.text(6, 5.5, 'user_server（关联表）', fontsize=10, ha='center', weight='bold', color=COLORS['black'])
    
    # 连接线：User -> 关联表
    ax.annotate('', xy=(4, 5.5), xytext=(3.5, 5.5),
               arrowprops=dict(arrowstyle='-', lw=2, color=COLORS['black']))
    ax.text(3.7, 5.8, 'N', fontsize=10, ha='center', weight='bold', color=COLORS['black'])
    
    # 连接线：关联表 -> Server
    ax.annotate('', xy=(8.5, 5.5), xytext=(8, 5.5),
               arrowprops=dict(arrowstyle='-', lw=2, color=COLORS['black']))
    ax.text(8.3, 5.8, 'M', fontsize=10, ha='center', weight='bold', color=COLORS['black'])
    
    # 关系：Server -> AlertRule (一对多)
    ax.annotate('', xy=(6, 3.2), xytext=(10, 4.5),
               arrowprops=dict(arrowstyle='-', lw=2, color=COLORS['black']))
    ax.text(9.5, 4.2, '1', fontsize=10, ha='center', weight='bold', color=COLORS['black'])
    ax.text(6.5, 3.5, 'N', fontsize=10, ha='center', weight='bold', color=COLORS['black'])
    
    # 关系标注
    relation_box = FancyBboxPatch((7.5, 3.5), 2, 0.5, boxstyle="round,pad=0.05",
                                 edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], linewidth=1)
    ax.add_patch(relation_box)
    ax.text(8.5, 3.75, 'has_rules', fontsize=9, ha='center', style='italic', color=COLORS['black'])
    
    # 说明文字
    info_box = FancyBboxPatch((0.5, 0.05), 11, 0.7, boxstyle="round,pad=0.1",
                             edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], 
                             linewidth=1.5, linestyle='--')
    ax.add_patch(info_box)
    ax.text(6, 0.55, '关系说明：用户与服务器为多对多关系（user_server关联表）', 
            fontsize=9, ha='center', weight='bold', color=COLORS['black'])
    ax.text(6, 0.25, '一个服务器可以有多个告警规则（AlertRule.server_id 外键）', 
            fontsize=9, ha='center', color=COLORS['dark_gray'])
    
    plt.tight_layout()
    output_dir = ensure_output_dir()
    plt.savefig(f'{output_dir}/图2_ER关系图.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print('✅ 图2: ER关系图 已生成（黑白灰版）')


def draw_log_collection_flow():
    """绘制日志采集数据流向图 - 图4 (黑白灰版)"""
    fig, ax = plt.subplots(figsize=(12, 8))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 8)
    ax.axis('off')
    
    # 标题
    ax.text(6, 7.5, '日志采集数据流向图', fontsize=16, ha='center', weight='bold', color=COLORS['black'])
    
    # 业务容器（起点）
    container_box = FancyBboxPatch((0.5, 5.5), 2.5, 1.2, boxstyle="round,pad=0.1",
                                  edgecolor=COLORS['black'], facecolor=COLORS['dark_gray'], linewidth=2)
    ax.add_patch(container_box)
    ax.text(1.75, 6.5, '业务容器', fontsize=11, ha='center', weight='bold', color=COLORS['white'])
    ax.text(1.75, 6.1, 'Nginx/Java', fontsize=9, ha='center', color=COLORS['white'])
    ax.text(1.75, 5.8, 'Node.js等', fontsize=9, ha='center', color=COLORS['white'])
    
    # 日志文件
    log_file = FancyBboxPatch((3.5, 5.7), 1.8, 0.8, boxstyle="round,pad=0.05",
                             edgecolor=COLORS['black'], facecolor=COLORS['light_gray'], linewidth=1.5)
    ax.add_patch(log_file)
    ax.text(4.4, 6.25, '日志文件', fontsize=10, ha='center', weight='bold', color=COLORS['black'])
    ax.text(4.4, 5.9, '*.log', fontsize=9, ha='center', color=COLORS['black'])
    
    # Filebeat
    filebeat_box = FancyBboxPatch((6, 5.5), 2.2, 1.2, boxstyle="round,pad=0.1",
                                 edgecolor=COLORS['black'], facecolor=COLORS['medium_gray'], linewidth=2)
    ax.add_patch(filebeat_box)
    ax.text(7.1, 6.5, 'Filebeat', fontsize=11, ha='center', weight='bold', color=COLORS['white'])
    ax.text(7.1, 6.1, '轻量级日志', fontsize=9, ha='center', color=COLORS['white'])
    ax.text(7.1, 5.8, '采集器', fontsize=9, ha='center', color=COLORS['white'])
    
    # Elasticsearch
    es_box = FancyBboxPatch((9, 5.5), 2.5, 1.2, boxstyle="round,pad=0.1",
                           edgecolor=COLORS['black'], facecolor=COLORS['dark_gray'], linewidth=2)
    ax.add_patch(es_box)
    ax.text(10.25, 6.5, 'Elasticsearch', fontsize=11, ha='center', weight='bold', color=COLORS['white'])
    ax.text(10.25, 6.1, '全文搜索', fontsize=9, ha='center', color=COLORS['white'])
    ax.text(10.25, 5.8, '日志存储', fontsize=9, ha='center', color=COLORS['white'])
    
    # 数据流向箭头
    # 容器 -> 日志文件
    ax.annotate('', xy=(3.5, 6.1), xytext=(3, 6.1),
               arrowprops=dict(arrowstyle='->', lw=2.5, color=COLORS['black']))
    ax.text(3.25, 6.4, '写入', fontsize=9, ha='center', color=COLORS['black'])
    
    # 日志文件 -> Filebeat
    ax.annotate('', xy=(6, 6.1), xytext=(5.3, 6.1),
               arrowprops=dict(arrowstyle='->', lw=2.5, color=COLORS['black']))
    ax.text(5.65, 6.4, '监听读取', fontsize=9, ha='center', color=COLORS['black'])
    
    # Filebeat -> ES
    ax.annotate('', xy=(9, 6.1), xytext=(8.2, 6.1),
               arrowprops=dict(arrowstyle='->', lw=2.5, color=COLORS['black']))
    ax.text(8.6, 6.4, 'HTTP推送', fontsize=9, ha='center', color=COLORS['black'])
    
    # 详细流程（下方）
    y = 4.5
    steps = [
        ('1. 业务容器输出日志到文件系统', COLORS['light_gray']),
        ('2. Filebeat监听指定目录的*.log文件', COLORS['light_gray']),
        ('3. 文件内容变化时，Filebeat读取新增行', COLORS['light_gray']),
        ('4. 添加元数据（host、timestamp等）', COLORS['medium_gray']),
        ('5. 批量发送到Elasticsearch索引', COLORS['medium_gray']),
        ('6. Elasticsearch存储并建立全文索引', COLORS['dark_gray']),
    ]
    
    for i, (text, bg_color) in enumerate(steps):
        step_box = FancyBboxPatch((1, y - i*0.65), 10, 0.5, boxstyle="round,pad=0.05",
                                 edgecolor=COLORS['black'], facecolor=bg_color, linewidth=1.5)
        ax.add_patch(step_box)
        text_color = COLORS['white'] if bg_color == COLORS['dark_gray'] else COLORS['black']
        ax.text(6, y - i*0.65 + 0.25, text, fontsize=9, ha='center', va='center', color=text_color)
    
    # Filebeat配置示例
    config_box = FancyBboxPatch((0.5, 0.05), 11, 0.7, boxstyle="round,pad=0.1",
                               edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], 
                               linewidth=1.5, linestyle='--')
    ax.add_patch(config_box)
    ax.text(6, 0.55, 'Filebeat配置：paths: ["/var/log/nginx/*.log"] | output.elasticsearch.hosts: ["localhost:9200"]', 
            fontsize=8, ha='center', weight='bold', color=COLORS['black'], family='monospace')
    ax.text(6, 0.25, '优势：轻量级（占用资源少）、可靠性高（断点续传）、自动重试机制', 
            fontsize=9, ha='center', color=COLORS['dark_gray'])
    
    plt.tight_layout()
    output_dir = ensure_output_dir()
    plt.savefig(f'{output_dir}/图4_日志采集数据流向图.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print('✅ 图4: 日志采集数据流向图 已生成（黑白灰版）')


def draw_database_er():
    """绘制系统E-R图 - 图7 (黑白灰版)
    
    完整的数据库实体关系图，包含所有9张核心表
    """
    fig, ax = plt.subplots(figsize=(15, 11))
    ax.set_xlim(0, 15)
    ax.set_ylim(0, 11)
    ax.axis('off')
    
    # 标题
    ax.text(7.5, 10.5, '系统E-R图（完整数据库实体关系 - 9张表）', fontsize=16, ha='center', weight='bold', color=COLORS['black'])
    
    # 核心实体定义 - 重新布局以容纳9张表
    entities = [
        # (x, y, width, height, name, attributes)
        # 第一行：用户相关（3个）
        (0.3, 7.8, 2.4, 2.0, 'User', ['id (PK)', 'username', 'password', 'email', 'role', 'created_at']),
        (3.2, 7.8, 2.6, 2.0, 'ServerGroup', ['id (PK)', 'name', 'description', 'created_at']),
        (6.3, 7.8, 2.6, 2.0, 'Server', ['id (PK)', 'group_id (FK)', 'server_name', 'ip_address', 'port', 'created_at']),
        
        # 第二行：告警相关（3个）
        (9.4, 7.8, 2.7, 2.0, 'AlertRule', ['id (PK)', 'server_id (FK)', 'metric_type', 'threshold', 'silence_minutes', 'is_enabled']),
        (12.6, 7.8, 2.1, 2.0, 'user_server', ['user_id (FK)', 'server_id (FK)', '关联表']),
        
        # 第三行：监控与AI相关（4个）
        (0.3, 4.8, 2.6, 2.0, 'MonitorData', ['id (PK)', 'server_id (FK)', 'cpu_value', 'memory_value', 'disk_value', 'recorded_at']),
        (3.4, 4.8, 3.0, 2.0, 'AlertHistory', ['id (PK)', 'server_id (FK)', 'metric_type', 'current_value', 'status', 'triggered_at', 'resolved_at']),
        (6.9, 4.8, 3.0, 2.0, 'DifyDecision', ['id (PK)', 'server_id (FK)', 'workflow_id', 'should_alert', 'alert_level', 'decision_output', 'created_at']),
        (10.4, 4.8, 2.5, 2.0, 'AuditLog', ['id (PK)', 'user_id (FK)', 'action', 'target', 'details', 'created_at']),
    ]
    
    # 绘制所有实体
    for x, y, w, h, name, attrs in entities:
        # 实体框
        is_relation_table = name == 'user_server'
        bg_color = COLORS['light_gray'] if is_relation_table else COLORS['dark_gray']
        entity_box = FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.08",
                                   edgecolor=COLORS['black'], facecolor=bg_color, 
                                   linewidth=1.5 if is_relation_table else 2)
        ax.add_patch(entity_box)
        
        # 实体名称
        text_color = COLORS['black'] if is_relation_table else COLORS['white']
        ax.text(x + w/2, y + h - 0.25, name, fontsize=9, ha='center', weight='bold', color=text_color)
        
        # 属性列表
        attr_y = y + h - 0.5
        for attr in attrs:
            attr_y -= 0.22
            ax.text(x + w/2, attr_y, attr, fontsize=6.5, ha='center', color=text_color)
    
    # 关系连线
    # ServerGroup -> Server (1:N)
    ax.plot([4.5, 7.6], [7.8, 7.8], '-', lw=1.5, color=COLORS['black'])
    ax.text(4.7, 8.1, '1', fontsize=8, weight='bold', color=COLORS['black'])
    ax.text(7.3, 8.1, 'N', fontsize=8, weight='bold', color=COLORS['black'])
    
    # User <-> user_server (N:M)
    ax.plot([1.5, 13.7], [7.8, 7.8], '-', lw=1.2, color=COLORS['medium_gray'])
    ax.text(1.8, 8.1, 'N', fontsize=8, weight='bold', color=COLORS['black'])
    
    # Server <-> user_server (N:M)
    ax.plot([7.6, 13.7], [8.8, 8.8], '-', lw=1.2, color=COLORS['medium_gray'])
    ax.text(13.4, 9.1, 'M', fontsize=8, weight='bold', color=COLORS['black'])
    
    # Server -> AlertRule (1:N)
    ax.plot([7.6, 10.7], [8.8, 8.8], '-', lw=1.5, color=COLORS['black'])
    ax.text(7.8, 9.1, '1', fontsize=8, weight='bold', color=COLORS['black'])
    ax.text(10.4, 9.1, 'N', fontsize=8, weight='bold', color=COLORS['black'])
    
    # Server -> MonitorData (1:N)
    ax.plot([7.6, 1.6], [7.8, 6.8], '-', lw=1.5, color=COLORS['black'])
    ax.text(7.3, 7.5, '1', fontsize=8, weight='bold', color=COLORS['black'])
    ax.text(2, 6.9, 'N', fontsize=8, weight='bold', color=COLORS['black'])
    
    # Server -> AlertHistory (1:N)
    ax.plot([7.6, 4.9], [7.8, 6.8], '-', lw=1.5, color=COLORS['black'])
    ax.text(7.3, 7.5, '1', fontsize=8, weight='bold', color=COLORS['black'])
    ax.text(5.2, 6.9, 'N', fontsize=8, weight='bold', color=COLORS['black'])
    
    # Server -> DifyDecision (1:N)
    ax.plot([7.6, 8.4], [7.8, 6.8], '-', lw=1.5, color=COLORS['black'])
    ax.text(7.8, 7.5, '1', fontsize=8, weight='bold', color=COLORS['black'])
    ax.text(8.2, 6.9, 'N', fontsize=8, weight='bold', color=COLORS['black'])
    
    # User -> AuditLog (1:N)
    ax.plot([1.5, 11.65], [7.8, 6.8], '-', lw=1.5, color=COLORS['black'])
    ax.text(1.8, 7.5, '1', fontsize=8, weight='bold', color=COLORS['black'])
    ax.text(11.3, 6.9, 'N', fontsize=8, weight='bold', color=COLORS['black'])
    
    # 外键关系说明（右下角）
    fk_box = FancyBboxPatch((9, 3.5), 5.7, 1, boxstyle="round,pad=0.1",
                           edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], 
                           linewidth=1.5, linestyle='--')
    ax.add_patch(fk_box)
    ax.text(11.85, 4.25, '外键关系统计', fontsize=9, ha='center', weight='bold', color=COLORS['black'])
    ax.text(11.85, 3.95, '• server_id (FK) → 5次引用', fontsize=7.5, ha='center', color=COLORS['dark_gray'])
    ax.text(11.85, 3.7, '（AlertRule, AlertHistory, MonitorData, DifyDecision）', fontsize=6.5, ha='center', color=COLORS['dark_gray'])
    
    # 图例说明（左下角）
    legend_box = FancyBboxPatch((0.3, 3.5), 8.3, 1, boxstyle="round,pad=0.1",
                               edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], 
                               linewidth=1.5, linestyle='--')
    ax.add_patch(legend_box)
    
    legend_items = [
        ('实体表（深灰）', 0.6, COLORS['dark_gray']),
        ('关联表（浅灰）', 3.2, COLORS['light_gray']),
        ('1:N 一对多', 5.8, None),
    ]
    
    legend_y = 4.0
    for text, x_pos, box_color in legend_items:
        if box_color:
            box = Rectangle((x_pos, legend_y - 0.12), 0.35, 0.25, 
                          facecolor=box_color, edgecolor=COLORS['black'], linewidth=1)
            ax.add_patch(box)
            ax.text(x_pos + 0.5, legend_y, text, fontsize=7.5, ha='left', color=COLORS['dark_gray'])
        else:
            ax.plot([x_pos, x_pos + 0.35], [legend_y, legend_y], '-', lw=1.5, color=COLORS['black'])
            ax.text(x_pos + 0.5, legend_y, text, fontsize=7.5, ha='left', color=COLORS['dark_gray'])
    
    # 数据库信息（底部）
    info_box = FancyBboxPatch((0.3, 0.05), 14.4, 3.1, boxstyle="round,pad=0.15",
                             edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], 
                             linewidth=2, linestyle='--')
    ax.add_patch(info_box)
    ax.text(7.5, 2.9, '数据库技术栈', fontsize=10, ha='center', weight='bold', color=COLORS['black'])
    
    info_lines = [
        '数据库：MySQL 8.0 | ORM：SQLAlchemy 2.0 | 迁移工具：Alembic',
        '核心表：9张（User, ServerGroup, Server, AlertRule, AlertHistory, MonitorData, DifyDecision, AuditLog, user_server）',
        '关联关系：user_server（多对多中间表）| ServerGroup → Server（1:N资产分组）',
        '外键约束：server_id (5次), user_id (2次), group_id (1次)',
        '创新点：① ServerGroup资产分组管理 ② DifyDecision AI决策记录 ③ AuditLog审计追溯',
    ]
    
    info_y = 2.5
    for line in info_lines:
        ax.text(7.5, info_y, line, fontsize=7.5, ha='center', color=COLORS['dark_gray'])
        info_y -= 0.45
    
    plt.tight_layout()
    output_dir = ensure_output_dir()
    plt.savefig(f'{output_dir}/图7_系统E-R图.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print('✅ 图7: 系统E-R图 已生成（黑白灰版 - 9张表完整版）')


def draw_async_task_flow():
    """绘制异步任务流程图 - 图8 (黑白灰版)
    
    展示异步任务的执行流程（线程池 + 邮件发送 + AI诊断）
    """
    fig, ax = plt.subplots(figsize=(12, 10))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 10)
    ax.axis('off')
    
    # 标题
    ax.text(6, 9.5, '异步任务执行流程', fontsize=16, ha='center', weight='bold', color=COLORS['black'])
    
    # 主线程区域
    main_thread_box = FancyBboxPatch((0.3, 5), 5, 4, boxstyle="round,pad=0.15",
                                    edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], 
                                    linewidth=2, linestyle='--')
    ax.add_patch(main_thread_box)
    ax.text(2.8, 8.8, '主线程（Flask请求处理）', fontsize=11, ha='center', weight='bold', color=COLORS['black'])
    
    # 异步线程池区域
    async_pool_box = FancyBboxPatch((6.7, 5), 5, 4, boxstyle="round,pad=0.15",
                                   edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], 
                                   linewidth=2, linestyle='--')
    ax.add_patch(async_pool_box)
    ax.text(9.2, 8.8, '异步线程池（后台执行）', fontsize=11, ha='center', weight='bold', color=COLORS['black'])
    
    # 主线程流程
    y = 8.2
    main_steps = [
        ('监控数据上报', COLORS['light_gray']),
        ('超阈值判断', COLORS['light_gray']),
        ('防抖锁检查', COLORS['dark_gray']),
        ('通过验证', COLORS['medium_gray']),
    ]
    
    for i, (text, bg_color) in enumerate(main_steps):
        box = FancyBboxPatch((1, y - i*0.8), 3.5, 0.6, boxstyle="round,pad=0.05",
                           edgecolor=COLORS['black'], facecolor=bg_color, linewidth=2)
        ax.add_patch(box)
        text_color = COLORS['white'] if bg_color in [COLORS['dark_gray'], COLORS['medium_gray']] else COLORS['black']
        ax.text(2.75, y - i*0.8 + 0.3, text, fontsize=10, ha='center', weight='bold', color=text_color)
        
        if i < len(main_steps) - 1:
            ax.annotate('', xy=(2.75, y - (i+1)*0.8 + 0.6), xytext=(2.75, y - i*0.8),
                       arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['black']))
    
    # 提交异步任务
    submit_box = FancyBboxPatch((1.5, 5.2), 2.5, 0.5, boxstyle="round,pad=0.05",
                               edgecolor=COLORS['black'], facecolor=COLORS['dark_gray'], linewidth=2)
    ax.add_patch(submit_box)
    ax.text(2.75, 5.45, '提交异步任务', fontsize=10, ha='center', weight='bold', color=COLORS['white'])
    
    ax.annotate('', xy=(2.75, 5.7), xytext=(2.75, 5.8),
               arrowprops=dict(arrowstyle='->', lw=2, color=COLORS['black']))
    
    # 跨区域箭头（主线程 -> 异步线程池）
    ax.annotate('', xy=(7.2, 7.8), xytext=(4.5, 5.45),
               arrowprops=dict(arrowstyle='->', lw=3, color=COLORS['black'], linestyle='--'))
    ax.text(5.5, 6.8, '线程池提交', fontsize=9, ha='center', weight='bold', 
           bbox=dict(boxstyle='round,pad=0.3', facecolor=COLORS['white'], edgecolor=COLORS['black']))
    
    # 异步任务流程
    async_y = 8.2
    async_tasks = [
        ('任务1：AI智能诊断', COLORS['medium_gray'], 'Dify工作流调用'),
        ('任务2：发送告警邮件', COLORS['medium_gray'], 'SMTP协议发送'),
        ('任务3：写入告警历史', COLORS['light_gray'], 'AlertHistory表'),
        ('任务4：记录审计日志', COLORS['light_gray'], 'AuditLog表'),
    ]
    
    for i, (title, bg_color, detail) in enumerate(async_tasks):
        task_box = FancyBboxPatch((7.2, async_y - i*0.8), 4, 0.6, boxstyle="round,pad=0.05",
                                 edgecolor=COLORS['black'], facecolor=bg_color, linewidth=1.5)
        ax.add_patch(task_box)
        text_color = COLORS['white'] if bg_color == COLORS['medium_gray'] else COLORS['black']
        ax.text(9.2, async_y - i*0.8 + 0.4, title, fontsize=9, ha='center', weight='bold', color=text_color)
        ax.text(9.2, async_y - i*0.8 + 0.15, detail, fontsize=8, ha='center', color=text_color)
        
        if i < len(async_tasks) - 1:
            ax.annotate('', xy=(9.2, async_y - (i+1)*0.8 + 0.6), xytext=(9.2, async_y - i*0.8),
                       arrowprops=dict(arrowstyle='->', lw=1.5, color=COLORS['black']))
    
    # 异步完成
    complete_box = FancyBboxPatch((7.7, 5.2), 3, 0.5, boxstyle="round,pad=0.05",
                                 edgecolor=COLORS['black'], facecolor=COLORS['dark_gray'], linewidth=2)
    ax.add_patch(complete_box)
    ax.text(9.2, 5.45, '异步任务完成', fontsize=10, ha='center', weight='bold', color=COLORS['white'])
    
    ax.annotate('', xy=(9.2, 5.7), xytext=(9.2, 5.8),
               arrowprops=dict(arrowstyle='->', lw=1.5, color=COLORS['black']))
    
    # 时间线对比
    timeline_box = FancyBboxPatch((0.5, 3.5), 11, 1.2, boxstyle="round,pad=0.1",
                                 edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], 
                                 linewidth=1.5, linestyle='--')
    ax.add_patch(timeline_box)
    ax.text(6, 4.4, '时间对比', fontsize=11, ha='center', weight='bold', color=COLORS['black'])
    
    # 同步执行（假设）
    sync_bar = Rectangle((1, 3.9), 9, 0.2, facecolor=COLORS['dark_gray'], edgecolor=COLORS['black'])
    ax.add_patch(sync_bar)
    ax.text(0.7, 4, '同步', fontsize=8, ha='right', color=COLORS['black'])
    ax.text(10.3, 4, '~5秒', fontsize=8, ha='left', weight='bold', color=COLORS['black'])
    
    # 异步执行（实际）
    async_bar = Rectangle((1, 3.6), 1.5, 0.2, facecolor=COLORS['medium_gray'], edgecolor=COLORS['black'])
    ax.add_patch(async_bar)
    ax.text(0.7, 3.7, '异步', fontsize=8, ha='right', color=COLORS['black'])
    ax.text(2.8, 3.7, '~200ms（主线程立即返回）', fontsize=8, ha='left', weight='bold', color=COLORS['black'])
    
    # 优势说明
    advantage_box = FancyBboxPatch((0.5, 0.05), 11, 3, boxstyle="round,pad=0.1",
                                  edgecolor=COLORS['black'], facecolor=COLORS['very_light_gray'], 
                                  linewidth=1.5, linestyle='--')
    ax.add_patch(advantage_box)
    ax.text(6, 2.7, '异步执行优势', fontsize=11, ha='center', weight='bold', color=COLORS['black'])
    
    advantages = [
        '✓ 主线程不阻塞：用户请求200ms内快速响应，不等待AI诊断（可能耗时2-3秒）',
        '✓ 并发能力强：线程池可同时处理多个告警任务，避免串行排队',
        '✓ 容错性好：单个任务失败不影响其他任务执行',
        '✓ 隔离性强：AI调用超时不会拖垮整个Flask应用',
    ]
    
    adv_y = 2.3
    for adv in advantages:
        ax.text(6, adv_y, adv, fontsize=9, ha='center', color=COLORS['dark_gray'])
        adv_y -= 0.5
    
    # 技术实现
    ax.text(6, 0.25, '技术实现：concurrent.futures.ThreadPoolExecutor（线程池） + threading.Lock（防抖锁）', 
            fontsize=8, ha='center', weight='bold', color=COLORS['black'], family='monospace')
    
    plt.tight_layout()
    output_dir = ensure_output_dir()
    plt.savefig(f'{output_dir}/图8_异步任务流程图.png', dpi=300, bbox_inches='tight', facecolor='white')
    plt.close()
    print('✅ 图8: 异步任务流程图 已生成（黑白灰版）')


def main():
    """主函数：生成所有图表"""
    print('开始生成论文图表（黑白灰配色版）...\n')
    
    draw_debounce_mechanism()      # 图1
    draw_er_relationship()         # 图2
    draw_alert_flow()              # 图3
    draw_log_collection_flow()     # 图4
    draw_system_architecture()     # 图5
    draw_deployment_topology()     # 图6
    draw_database_er()             # 图7
    draw_async_task_flow()         # 图8
    
    print(f'\n✅ 所有架构图和流程图生成完成！')
    print(f'📁 图片保存在: docs/images/ 目录')
    print(f'\n已生成的图表（8张）：')
    print(f'- 图1：防抖锁工作原理')
    print(f'- 图2：ER关系图')
    print(f'- 图3：监控告警业务流程')
    print(f'- 图4：日志采集数据流向图')
    print(f'- 图5：系统总体架构图')
    print(f'- 图6：部署拓扑图')
    print(f'- 图7：系统E-R图')
    print(f'- 图8：异步任务流程图')
    print(f'\n还需要截图的界面（11张）：')
    print(f'- 图9-19：登录、管理、监控等界面截图（需运行系统）')


if __name__ == '__main__':
    main()
