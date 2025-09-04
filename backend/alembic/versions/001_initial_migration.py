"""Initial migration: Create users and tenants tables

Revision ID: 001
Revises: 
Create Date: 2024-09-04 20:00:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create initial database schema."""
    
    # Create tenants table
    op.create_table('tenants',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('domain', sa.String(length=255), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('industry', sa.String(length=100), nullable=True),
        sa.Column('contact_email', sa.String(length=254), nullable=True),
        sa.Column('contact_phone', sa.String(length=20), nullable=True),
        sa.Column('address_line1', sa.String(length=255), nullable=True),
        sa.Column('address_line2', sa.String(length=255), nullable=True),
        sa.Column('city', sa.String(length=100), nullable=True),
        sa.Column('state', sa.String(length=100), nullable=True),
        sa.Column('postal_code', sa.String(length=20), nullable=True),
        sa.Column('country', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_trial', sa.Boolean(), nullable=False),
        sa.Column('trial_ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('subscription_plan', sa.String(length=50), nullable=False),
        sa.Column('subscription_status', sa.String(length=20), nullable=False),
        sa.Column('subscription_ends_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('features', sa.Text(), nullable=True),
        sa.Column('max_users', sa.String(length=10), nullable=False),
        sa.Column('max_storage_mb', sa.String(length=10), nullable=False),
        sa.Column('max_transactions', sa.String(length=10), nullable=False),
        sa.Column('billing_email', sa.String(length=254), nullable=True),
        sa.Column('billing_address', sa.Text(), nullable=True),
        sa.Column('tax_id', sa.String(length=50), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('date_format', sa.String(length=20), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for tenants table
    op.create_index('idx_tenants_slug', 'tenants', ['slug'], unique=True)
    op.create_index('idx_tenants_domain', 'tenants', ['domain'], unique=True)
    op.create_index('idx_tenants_active', 'tenants', ['is_active'])
    op.create_index('idx_tenants_subscription', 'tenants', ['subscription_status'])
    op.create_index(op.f('ix_tenants_tenant_id'), 'tenants', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_tenants_is_deleted'), 'tenants', ['is_deleted'], unique=False)
    
    # Create users table
    op.create_table('users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.Column('email', sa.String(length=254), nullable=False),
        sa.Column('username', sa.String(length=50), nullable=True),
        sa.Column('password_hash', sa.String(length=255), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_verified', sa.Boolean(), nullable=False),
        sa.Column('is_superuser', sa.Boolean(), nullable=False),
        sa.Column('totp_secret', sa.String(length=32), nullable=True),
        sa.Column('totp_enabled', sa.Boolean(), nullable=False),
        sa.Column('first_name', sa.String(length=100), nullable=True),
        sa.Column('last_name', sa.String(length=100), nullable=True),
        sa.Column('phone_number', sa.String(length=20), nullable=True),
        sa.Column('last_login', sa.DateTime(timezone=True), nullable=True),
        sa.Column('failed_login_attempts', sa.String(length=10), nullable=False),
        sa.Column('locked_until', sa.DateTime(timezone=True), nullable=True),
        sa.Column('password_reset_token', sa.String(length=255), nullable=True),
        sa.Column('password_reset_expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('email_verification_token', sa.String(length=255), nullable=True),
        sa.Column('email_verification_expires', sa.DateTime(timezone=True), nullable=True),
        sa.Column('timezone', sa.String(length=50), nullable=False),
        sa.Column('language', sa.String(length=10), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Create indexes for users table
    op.create_index('idx_users_tenant_email', 'users', ['tenant_id', 'email'])
    op.create_index('idx_users_tenant_active', 'users', ['tenant_id', 'is_active'])
    op.create_index('idx_users_last_login', 'users', ['last_login'])
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)
    op.create_index(op.f('ix_users_tenant_id'), 'users', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_users_is_active'), 'users', ['is_active'], unique=False)
    op.create_index(op.f('ix_users_is_deleted'), 'users', ['is_deleted'], unique=False)


def downgrade() -> None:
    """Drop initial database schema."""
    
    # Drop users table and indexes
    op.drop_index(op.f('ix_users_is_deleted'), table_name='users')
    op.drop_index(op.f('ix_users_is_active'), table_name='users')
    op.drop_index(op.f('ix_users_tenant_id'), table_name='users')
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index('idx_users_last_login', table_name='users')
    op.drop_index('idx_users_tenant_active', table_name='users')
    op.drop_index('idx_users_tenant_email', table_name='users')
    op.drop_table('users')
    
    # Drop tenants table and indexes
    op.drop_index(op.f('ix_tenants_is_deleted'), table_name='tenants')
    op.drop_index(op.f('ix_tenants_tenant_id'), table_name='tenants')
    op.drop_index('idx_tenants_subscription', table_name='tenants')
    op.drop_index('idx_tenants_active', table_name='tenants')
    op.drop_index('idx_tenants_domain', table_name='tenants')
    op.drop_index('idx_tenants_slug', table_name='tenants')
    op.drop_table('tenants')
