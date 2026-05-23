"""add organizations and user roles (manual)

Revision ID: manual_add_orgs_roles
Revises: c6bf041771ee
Create Date: 2024-05-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision = 'manual_add_orgs_roles'
down_revision = 'c6bf041771ee'
branch_labels = None
depends_on = None


def upgrade():
    # 1. Create organizations table
    op.create_table(
        'organizations',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_organizations_id'), 'organizations', ['id'], unique=False)
    op.create_index(op.f('ix_organizations_name'), 'organizations', ['name'], unique=True)

    # 2. Add role, organization_id, manager_id to users
    op.add_column('users', sa.Column('role', sa.String(length=20), nullable=True, server_default='worker'))
    op.add_column('users', sa.Column('organization_id', sa.Integer(), nullable=True))
    op.add_column('users', sa.Column('manager_id', sa.Integer(), nullable=True))
    
    # 3. Create indexes and foreign keys
    op.create_index(op.f('ix_users_role'), 'users', ['role'], unique=False)
    op.create_index(op.f('ix_users_organization_id'), 'users', ['organization_id'], unique=False)
    op.create_index(op.f('ix_users_manager_id'), 'users', ['manager_id'], unique=False)
    
    op.create_foreign_key(None, 'users', 'organizations', ['organization_id'], ['id'])
    op.create_foreign_key(None, 'users', 'users', ['manager_id'], ['id'])


def downgrade():
    # Reverse the changes
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_constraint(None, 'users', type_='foreignkey')
    op.drop_index(op.f('ix_users_manager_id'), table_name='users')
    op.drop_index(op.f('ix_users_organization_id'), table_name='users')
    op.drop_index(op.f('ix_users_role'), table_name='users')
    op.drop_column('users', 'manager_id')
    op.drop_column('users', 'organization_id')
    op.drop_column('users', 'role')
    op.drop_index(op.f('ix_organizations_name'), table_name='organizations')
    op.drop_index(op.f('ix_organizations_id'), table_name='organizations')
    op.drop_table('organizations')