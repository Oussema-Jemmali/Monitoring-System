"""Add user system information

Revision ID: add_user_system_info
Revises: 
Create Date: 2024-12-14 13:30:40.000000

"""
from alembic import op
import sqlalchemy as sa

def upgrade():
    # Add new columns to users table
    op.add_column('users', sa.Column('ip_address', sa.String(45)))
    op.add_column('users', sa.Column('mac_address', sa.String(17)))
    op.add_column('users', sa.Column('hostname', sa.String(64)))
    op.add_column('users', sa.Column('os_info', sa.String(128)))
    op.add_column('users', sa.Column('cpu_info', sa.String(128)))
    op.add_column('users', sa.Column('ram_total', sa.Float))
    op.add_column('users', sa.Column('is_online', sa.Boolean, default=True))
    op.add_column('users', sa.Column('location', sa.String(128)))
    op.add_column('users', sa.Column('department', sa.String(64)))
    op.add_column('users', sa.Column('role', sa.String(64)))

def downgrade():
    # Remove the columns if needed
    op.drop_column('users', 'ip_address')
    op.drop_column('users', 'mac_address')
    op.drop_column('users', 'hostname')
    op.drop_column('users', 'os_info')
    op.drop_column('users', 'cpu_info')
    op.drop_column('users', 'ram_total')
    op.drop_column('users', 'is_online')
    op.drop_column('users', 'location')
    op.drop_column('users', 'department')
    op.drop_column('users', 'role')
