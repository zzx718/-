"""add_dify_tables

Revision ID: add_dify_tables
Revises: 51ffba2471b7
Create Date: 2026-03-22

"""
from alembic import op
import sqlalchemy as sa


revision = 'add_dify_tables'
down_revision = '51ffba2471b7'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table('dify_decisions',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('server_id', sa.Integer(), nullable=False, comment='关联服务器ID'),
        sa.Column('workflow_id', sa.String(length=100), nullable=True, comment='Dify工作流ID'),
        sa.Column('workflow_run_id', sa.String(length=100), nullable=True, comment='Dify工作流运行ID'),
        sa.Column('input_data', sa.JSON(), nullable=True, comment='发送给Dify的完整输入数据'),
        sa.Column('current_metrics', sa.JSON(), nullable=True, comment='当前指标快照'),
        sa.Column('history_trend', sa.JSON(), nullable=True, comment='历史趋势数据'),
        sa.Column('should_alert', sa.Boolean(), nullable=True, comment='是否需要告警'),
        sa.Column('alert_level', sa.Enum('info', 'warning', 'critical', 'emergency'), nullable=True, comment='告警级别'),
        sa.Column('alert_reason', sa.Text(), nullable=True, comment='告警原因说明'),
        sa.Column('decision_output', sa.JSON(), nullable=True, comment='Dify返回的完整决策结果'),
        sa.Column('recommendation', sa.Text(), nullable=True, comment='处理建议'),
        sa.Column('action_items', sa.JSON(), nullable=True, comment='建议执行的操作列表'),
        sa.Column('executed', sa.Boolean(), nullable=True, comment='是否已执行'),
        sa.Column('execution_result', sa.Text(), nullable=True, comment='执行结果'),
        sa.Column('human_feedback', sa.Enum('correct', 'wrong', 'neutral'), nullable=True, comment='人工反馈: 正确/错误/中性'),
        sa.Column('feedback_comment', sa.Text(), nullable=True, comment='反馈备注'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('executed_at', sa.DateTime(), nullable=True, comment='执行时间'),
        sa.Column('feedback_at', sa.DateTime(), nullable=True, comment='反馈时间'),
        sa.ForeignKeyConstraint(['server_id'], ['servers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_dify_decisions_created_at'), 'dify_decisions', ['created_at'], unique=False)
    
    op.create_table('smart_alert_rules',
        sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('server_id', sa.Integer(), nullable=False, comment='关联服务器ID'),
        sa.Column('rule_name', sa.String(length=100), nullable=False, comment='规则名称'),
        sa.Column('rule_description', sa.Text(), nullable=True, comment='规则描述'),
        sa.Column('dify_workflow_id', sa.String(length=100), nullable=True, comment='绑定的Dify工作流ID'),
        sa.Column('dify_api_key', sa.String(length=200), nullable=True, comment='Dify API Key (可选，单独配置)'),
        sa.Column('trigger_condition', sa.JSON(), nullable=True, comment='前置触发条件'),
        sa.Column('is_enabled', sa.Boolean(), nullable=True, comment='是否启用'),
        sa.Column('priority', sa.Integer(), nullable=True, comment='优先级，数字越大优先级越高'),
        sa.Column('silent_minutes', sa.Integer(), nullable=True, comment='告警静默期(分钟)'),
        sa.Column('created_at', sa.DateTime(), nullable=True, comment='创建时间'),
        sa.Column('updated_at', sa.DateTime(), nullable=True, comment='更新时间'),
        sa.ForeignKeyConstraint(['server_id'], ['servers.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('smart_alert_rules')
    op.drop_index(op.f('ix_dify_decisions_created_at'), table_name='dify_decisions')
    op.drop_table('dify_decisions')
