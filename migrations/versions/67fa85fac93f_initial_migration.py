"""initial migration

Revision ID: 67fa85fac93f
Revises: 
Create Date: 2025-03-13 20:13:23.098206

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '67fa85fac93f'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('User',
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('username', sa.String(length=50), nullable=False),
    sa.Column('role', sa.String(length=50), nullable=False),
    sa.Column('password', sa.String(length=255), nullable=False),
    sa.PrimaryKeyConstraint('user_id')
    )
    op.create_table('HrLead',
    sa.Column('hr_lead_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('sla', sa.String(length=100), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ),
    sa.PrimaryKeyConstraint('hr_lead_id')
    )
    op.create_table('Hr',
    sa.Column('hr_id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('hr_lead_id', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['hr_lead_id'], ['HrLead.hr_lead_id'], ),
    sa.ForeignKeyConstraint(['user_id'], ['User.user_id'], ),
    sa.PrimaryKeyConstraint('hr_id')
    )
    op.create_table('Resume',
    sa.Column('resume_id', sa.Integer(), nullable=False),
    sa.Column('vacancy', sa.String(length=50), nullable=False),
    sa.Column('age', sa.Integer(), nullable=False),
    sa.Column('status', sa.String(length=50), nullable=False),
    sa.Column('date_last_changes', sa.Date(), nullable=True),
    sa.Column('source', sa.String(length=50), nullable=False),
    sa.Column('hr_id', sa.Integer(), nullable=False),
    sa.Column('archiv', sa.Boolean(), nullable=True),
    sa.ForeignKeyConstraint(['hr_id'], ['Hr.hr_id'], ),
    sa.PrimaryKeyConstraint('resume_id')
    )
    op.create_table('StatusChangeLogs',
    sa.Column('log_id', sa.Integer(), nullable=False),
    sa.Column('resume_id', sa.Integer(), nullable=False),
    sa.Column('old_status', sa.String(length=50), nullable=False),
    sa.Column('new_status', sa.String(length=50), nullable=False),
    sa.Column('change_date', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['resume_id'], ['Resume.resume_id'], ),
    sa.PrimaryKeyConstraint('log_id')
    )
    op.drop_table('hrlead')
    op.drop_table('statuschangelogs')
    op.drop_table('user')
    op.drop_table('hr')
    op.drop_table('resume')
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('resume',
    sa.Column('resume_id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('vacancy', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('age', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('status', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('date_last_changes', sa.DATE(), nullable=True),
    sa.Column('source', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('hr_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('archiv', mysql.TINYINT(display_width=1), autoincrement=False, nullable=True),
    sa.ForeignKeyConstraint(['hr_id'], ['hr.hr_id'], name='resume_ibfk_1'),
    sa.PrimaryKeyConstraint('resume_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('hr',
    sa.Column('hr_id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('hr_lead_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.ForeignKeyConstraint(['hr_lead_id'], ['hrlead.hr_lead_id'], name='hr_ibfk_1'),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], name='hr_ibfk_2'),
    sa.PrimaryKeyConstraint('hr_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('user',
    sa.Column('user_id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('username', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('role', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('password', mysql.VARCHAR(length=255), nullable=False),
    sa.PrimaryKeyConstraint('user_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('statuschangelogs',
    sa.Column('log_id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('resume_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('old_status', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('new_status', mysql.VARCHAR(length=50), nullable=False),
    sa.Column('change_date', mysql.DATETIME(), nullable=False),
    sa.ForeignKeyConstraint(['resume_id'], ['resume.resume_id'], name='statuschangelogs_ibfk_1'),
    sa.PrimaryKeyConstraint('log_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.create_table('hrlead',
    sa.Column('hr_lead_id', mysql.INTEGER(), autoincrement=True, nullable=False),
    sa.Column('user_id', mysql.INTEGER(), autoincrement=False, nullable=False),
    sa.Column('sla', mysql.VARCHAR(length=100), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.user_id'], name='hrlead_ibfk_1'),
    sa.PrimaryKeyConstraint('hr_lead_id'),
    mysql_collate='utf8mb4_0900_ai_ci',
    mysql_default_charset='utf8mb4',
    mysql_engine='InnoDB'
    )
    op.drop_table('StatusChangeLogs')
    op.drop_table('Resume')
    op.drop_table('Hr')
    op.drop_table('HrLead')
    op.drop_table('User')
    # ### end Alembic commands ###
