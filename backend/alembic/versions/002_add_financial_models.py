"""Add financial models: Account, Transaction, Category, CategorizationRule

Revision ID: 002_add_financial_models
Revises: 001_initial_migration
Create Date: 2025-09-08 13:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '002_add_financial_models'
down_revision = '001_initial_migration'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create accounts table
    op.create_table('accounts',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('account_number', sa.String(length=50), nullable=True),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('account_type', sa.String(length=50), nullable=False),
        sa.Column('account_subtype', sa.String(length=50), nullable=True),
        sa.Column('institution_name', sa.String(length=255), nullable=True),
        sa.Column('institution_id', sa.String(length=100), nullable=True),
        sa.Column('routing_number', sa.String(length=20), nullable=True),
        sa.Column('current_balance', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('available_balance', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('pending_balance', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_archived', sa.Boolean(), nullable=False),
        sa.Column('credit_limit', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('minimum_payment', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('interest_rate', sa.Numeric(precision=5, scale=4), nullable=True),
        sa.Column('parent_account_id', sa.Integer(), nullable=True),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('last_imported_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_updated_at', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['parent_account_id'], ['accounts.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_accounts_tenant_user', 'accounts', ['tenant_id', 'user_id'], unique=False)
    op.create_index('idx_accounts_tenant_type', 'accounts', ['tenant_id', 'account_type'], unique=False)
    op.create_index('idx_accounts_tenant_active', 'accounts', ['tenant_id', 'is_active'], unique=False)
    op.create_index('idx_accounts_user_type', 'accounts', ['user_id', 'account_type'], unique=False)
    op.create_index('idx_accounts_external_id', 'accounts', ['external_id'], unique=False)
    op.create_index('idx_accounts_institution', 'accounts', ['institution_name'], unique=False)
    op.create_index(op.f('ix_accounts_id'), 'accounts', ['id'], unique=False)
    op.create_index(op.f('ix_accounts_tenant_id'), 'accounts', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_accounts_name'), 'accounts', ['name'], unique=False)
    op.create_index(op.f('ix_accounts_account_number'), 'accounts', ['account_number'], unique=False)
    op.create_index(op.f('ix_accounts_account_type'), 'accounts', ['account_type'], unique=False)
    op.create_index(op.f('ix_accounts_account_subtype'), 'accounts', ['account_subtype'], unique=False)
    op.create_index(op.f('ix_accounts_institution_name'), 'accounts', ['institution_name'], unique=False)
    op.create_index(op.f('ix_accounts_institution_id'), 'accounts', ['institution_id'], unique=False)
    op.create_index(op.f('ix_accounts_currency'), 'accounts', ['currency'], unique=False)
    op.create_index(op.f('ix_accounts_is_active'), 'accounts', ['is_active'], unique=False)
    op.create_index(op.f('ix_accounts_is_archived'), 'accounts', ['is_archived'], unique=False)
    op.create_index(op.f('ix_accounts_user_id'), 'accounts', ['user_id'], unique=False)
    op.create_index(op.f('ix_accounts_is_deleted'), 'accounts', ['is_deleted'], unique=False)

    # Create categories table
    op.create_table('categories',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('display_name', sa.String(length=255), nullable=True),
        sa.Column('slug', sa.String(length=100), nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=True),
        sa.Column('category_type', sa.String(length=50), nullable=False),
        sa.Column('category_group', sa.String(length=100), nullable=True),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_default', sa.Boolean(), nullable=False),
        sa.Column('is_system', sa.Boolean(), nullable=False),
        sa.Column('color', sa.String(length=7), nullable=True),
        sa.Column('icon', sa.String(length=50), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('usage_count', sa.Integer(), nullable=False),
        sa.Column('last_used_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('budget_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('budget_period', sa.String(length=20), nullable=True),
        sa.Column('budget_start_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('budget_end_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(['parent_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_categories_tenant_type', 'categories', ['tenant_id', 'category_type'], unique=False)
    op.create_index('idx_categories_tenant_group', 'categories', ['tenant_id', 'category_group'], unique=False)
    op.create_index('idx_categories_tenant_active', 'categories', ['tenant_id', 'is_active'], unique=False)
    op.create_index('idx_categories_tenant_system', 'categories', ['tenant_id', 'is_system'], unique=False)
    op.create_index('idx_categories_parent', 'categories', ['parent_id'], unique=False)
    op.create_index('idx_categories_slug', 'categories', ['slug'], unique=False)
    op.create_index('idx_categories_usage', 'categories', ['usage_count'], unique=False)
    op.create_index('idx_categories_user', 'categories', ['user_id'], unique=False)
    op.create_index(op.f('ix_categories_id'), 'categories', ['id'], unique=False)
    op.create_index(op.f('ix_categories_tenant_id'), 'categories', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_categories_name'), 'categories', ['name'], unique=False)
    op.create_index(op.f('ix_categories_slug'), 'categories', ['slug'], unique=False)
    op.create_index(op.f('ix_categories_category_type'), 'categories', ['category_type'], unique=False)
    op.create_index(op.f('ix_categories_category_group'), 'categories', ['category_group'], unique=False)
    op.create_index(op.f('ix_categories_is_active'), 'categories', ['is_active'], unique=False)
    op.create_index(op.f('ix_categories_is_default'), 'categories', ['is_default'], unique=False)
    op.create_index(op.f('ix_categories_is_system'), 'categories', ['is_system'], unique=False)
    op.create_index(op.f('ix_categories_usage_count'), 'categories', ['usage_count'], unique=False)
    op.create_index(op.f('ix_categories_last_used_at'), 'categories', ['last_used_at'], unique=False)
    op.create_index(op.f('ix_categories_user_id'), 'categories', ['user_id'], unique=False)
    op.create_index(op.f('ix_categories_is_deleted'), 'categories', ['is_deleted'], unique=False)

    # Create categorization_rules table
    op.create_table('categorization_rules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('rule_type', sa.String(length=50), nullable=False),
        sa.Column('pattern', sa.Text(), nullable=False),
        sa.Column('is_case_sensitive', sa.Boolean(), nullable=False),
        sa.Column('is_regex', sa.Boolean(), nullable=False),
        sa.Column('field_to_match', sa.String(length=50), nullable=False),
        sa.Column('amount_min', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('amount_max', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('category_id', sa.Integer(), nullable=False),
        sa.Column('subcategory', sa.String(length=100), nullable=True),
        sa.Column('priority', sa.Integer(), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False),
        sa.Column('is_system', sa.Boolean(), nullable=False),
        sa.Column('match_count', sa.Integer(), nullable=False),
        sa.Column('success_count', sa.Integer(), nullable=False),
        sa.Column('last_matched_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('last_success_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('confidence_threshold', sa.Numeric(precision=3, scale=2), nullable=False),
        sa.Column('max_matches_per_day', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.String(length=255), nullable=True),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_categorization_rules_tenant_type', 'categorization_rules', ['tenant_id', 'rule_type'], unique=False)
    op.create_index('idx_categorization_rules_tenant_active', 'categorization_rules', ['tenant_id', 'is_active'], unique=False)
    op.create_index('idx_categorization_rules_tenant_priority', 'categorization_rules', ['tenant_id', 'priority'], unique=False)
    op.create_index('idx_categorization_rules_category', 'categorization_rules', ['category_id'], unique=False)
    op.create_index('idx_categorization_rules_user', 'categorization_rules', ['user_id'], unique=False)
    op.create_index('idx_categorization_rules_match_count', 'categorization_rules', ['match_count'], unique=False)
    op.create_index('idx_categorization_rules_success_count', 'categorization_rules', ['success_count'], unique=False)
    op.create_index(op.f('ix_categorization_rules_id'), 'categorization_rules', ['id'], unique=False)
    op.create_index(op.f('ix_categorization_rules_tenant_id'), 'categorization_rules', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_categorization_rules_name'), 'categorization_rules', ['name'], unique=False)
    op.create_index(op.f('ix_categorization_rules_rule_type'), 'categorization_rules', ['rule_type'], unique=False)
    op.create_index(op.f('ix_categorization_rules_field_to_match'), 'categorization_rules', ['field_to_match'], unique=False)
    op.create_index(op.f('ix_categorization_rules_priority'), 'categorization_rules', ['priority'], unique=False)
    op.create_index(op.f('ix_categorization_rules_is_active'), 'categorization_rules', ['is_active'], unique=False)
    op.create_index(op.f('ix_categorization_rules_is_system'), 'categorization_rules', ['is_system'], unique=False)
    op.create_index(op.f('ix_categorization_rules_match_count'), 'categorization_rules', ['match_count'], unique=False)
    op.create_index(op.f('ix_categorization_rules_success_count'), 'categorization_rules', ['success_count'], unique=False)
    op.create_index(op.f('ix_categorization_rules_last_matched_at'), 'categorization_rules', ['last_matched_at'], unique=False)
    op.create_index(op.f('ix_categorization_rules_user_id'), 'categorization_rules', ['user_id'], unique=False)
    op.create_index(op.f('ix_categorization_rules_is_deleted'), 'categorization_rules', ['is_deleted'], unique=False)

    # Create transactions table
    op.create_table('transactions',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('tenant_id', sa.String(length=255), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('is_deleted', sa.Boolean(), nullable=False),
        sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('created_by', sa.String(length=255), nullable=True),
        sa.Column('updated_by', sa.String(length=255), nullable=True),
        sa.Column('external_id', sa.String(length=100), nullable=True),
        sa.Column('reference_number', sa.String(length=100), nullable=True),
        sa.Column('account_id', sa.Integer(), nullable=False),
        sa.Column('amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('description', sa.String(length=500), nullable=False),
        sa.Column('original_description', sa.String(length=500), nullable=True),
        sa.Column('transaction_type', sa.String(length=50), nullable=False),
        sa.Column('transaction_category', sa.String(length=100), nullable=True),
        sa.Column('transaction_subcategory', sa.String(length=100), nullable=True),
        sa.Column('transaction_date', sa.DateTime(timezone=True), nullable=False),
        sa.Column('posted_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('effective_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('currency', sa.String(length=3), nullable=False),
        sa.Column('exchange_rate', sa.Numeric(precision=10, scale=6), nullable=False),
        sa.Column('original_amount', sa.Numeric(precision=15, scale=2), nullable=True),
        sa.Column('original_currency', sa.String(length=3), nullable=True),
        sa.Column('status', sa.String(length=20), nullable=False),
        sa.Column('is_reconciled', sa.Boolean(), nullable=False),
        sa.Column('is_duplicate', sa.Boolean(), nullable=False),
        sa.Column('is_auto_categorized', sa.Boolean(), nullable=False),
        sa.Column('categorization_confidence', sa.Numeric(precision=3, scale=2), nullable=True),
        sa.Column('categorization_rule_id', sa.Integer(), nullable=True),
        sa.Column('transfer_account_id', sa.Integer(), nullable=True),
        sa.Column('transfer_transaction_id', sa.Integer(), nullable=True),
        sa.Column('merchant_name', sa.String(length=255), nullable=True),
        sa.Column('merchant_category_code', sa.String(length=10), nullable=True),
        sa.Column('merchant_address', sa.Text(), nullable=True),
        sa.Column('payment_method', sa.String(length=50), nullable=True),
        sa.Column('check_number', sa.String(length=20), nullable=True),
        sa.Column('authorization_code', sa.String(length=50), nullable=True),
        sa.Column('fee_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('interest_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('tax_amount', sa.Numeric(precision=15, scale=2), nullable=False),
        sa.Column('import_batch_id', sa.String(length=100), nullable=True),
        sa.Column('import_source', sa.String(length=50), nullable=True),
        sa.Column('import_file_name', sa.String(length=255), nullable=True),
        sa.Column('import_date', sa.DateTime(timezone=True), nullable=True),
        sa.Column('user_id', sa.String(length=255), nullable=False),
        sa.Column('notes', sa.Text(), nullable=True),
        sa.Column('tags', sa.Text(), nullable=True),
        sa.ForeignKeyConstraint(['account_id'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['categorization_rule_id'], ['categorization_rules.id'], ),
        sa.ForeignKeyConstraint(['transfer_account_id'], ['accounts.id'], ),
        sa.ForeignKeyConstraint(['transfer_transaction_id'], ['transactions.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_transactions_tenant_user', 'transactions', ['tenant_id', 'user_id'], unique=False)
    op.create_index('idx_transactions_tenant_account', 'transactions', ['tenant_id', 'account_id'], unique=False)
    op.create_index('idx_transactions_tenant_date', 'transactions', ['tenant_id', 'transaction_date'], unique=False)
    op.create_index('idx_transactions_tenant_category', 'transactions', ['tenant_id', 'transaction_category'], unique=False)
    op.create_index('idx_transactions_account_date', 'transactions', ['account_id', 'transaction_date'], unique=False)
    op.create_index('idx_transactions_amount', 'transactions', ['amount'], unique=False)
    op.create_index('idx_transactions_status', 'transactions', ['status'], unique=False)
    op.create_index('idx_transactions_external_id', 'transactions', ['external_id'], unique=False)
    op.create_index('idx_transactions_merchant', 'transactions', ['merchant_name'], unique=False)
    op.create_index('idx_transactions_import_batch', 'transactions', ['import_batch_id'], unique=False)
    op.create_index(op.f('ix_transactions_id'), 'transactions', ['id'], unique=False)
    op.create_index(op.f('ix_transactions_tenant_id'), 'transactions', ['tenant_id'], unique=False)
    op.create_index(op.f('ix_transactions_reference_number'), 'transactions', ['reference_number'], unique=False)
    op.create_index(op.f('ix_transactions_account_id'), 'transactions', ['account_id'], unique=False)
    op.create_index(op.f('ix_transactions_amount'), 'transactions', ['amount'], unique=False)
    op.create_index(op.f('ix_transactions_description'), 'transactions', ['description'], unique=False)
    op.create_index(op.f('ix_transactions_transaction_type'), 'transactions', ['transaction_type'], unique=False)
    op.create_index(op.f('ix_transactions_transaction_category'), 'transactions', ['transaction_category'], unique=False)
    op.create_index(op.f('ix_transactions_transaction_subcategory'), 'transactions', ['transaction_subcategory'], unique=False)
    op.create_index(op.f('ix_transactions_transaction_date'), 'transactions', ['transaction_date'], unique=False)
    op.create_index(op.f('ix_transactions_posted_date'), 'transactions', ['posted_date'], unique=False)
    op.create_index(op.f('ix_transactions_effective_date'), 'transactions', ['effective_date'], unique=False)
    op.create_index(op.f('ix_transactions_currency'), 'transactions', ['currency'], unique=False)
    op.create_index(op.f('ix_transactions_status'), 'transactions', ['status'], unique=False)
    op.create_index(op.f('ix_transactions_is_reconciled'), 'transactions', ['is_reconciled'], unique=False)
    op.create_index(op.f('ix_transactions_is_duplicate'), 'transactions', ['is_duplicate'], unique=False)
    op.create_index(op.f('ix_transactions_is_auto_categorized'), 'transactions', ['is_auto_categorized'], unique=False)
    op.create_index(op.f('ix_transactions_merchant_name'), 'transactions', ['merchant_name'], unique=False)
    op.create_index(op.f('ix_transactions_merchant_category_code'), 'transactions', ['merchant_category_code'], unique=False)
    op.create_index(op.f('ix_transactions_payment_method'), 'transactions', ['payment_method'], unique=False)
    op.create_index(op.f('ix_transactions_import_batch_id'), 'transactions', ['import_batch_id'], unique=False)
    op.create_index(op.f('ix_transactions_import_source'), 'transactions', ['import_source'], unique=False)
    op.create_index(op.f('ix_transactions_user_id'), 'transactions', ['user_id'], unique=False)
    op.create_index(op.f('ix_transactions_is_deleted'), 'transactions', ['is_deleted'], unique=False)


def downgrade() -> None:
    # Drop transactions table
    op.drop_index(op.f('ix_transactions_is_deleted'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_user_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_import_source'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_import_batch_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_payment_method'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_merchant_category_code'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_merchant_name'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_is_auto_categorized'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_is_duplicate'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_is_reconciled'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_status'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_currency'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_effective_date'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_posted_date'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_transaction_date'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_transaction_subcategory'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_transaction_category'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_transaction_type'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_description'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_amount'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_account_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_reference_number'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_tenant_id'), table_name='transactions')
    op.drop_index(op.f('ix_transactions_id'), table_name='transactions')
    op.drop_index('idx_transactions_import_batch', table_name='transactions')
    op.drop_index('idx_transactions_merchant', table_name='transactions')
    op.drop_index('idx_transactions_external_id', table_name='transactions')
    op.drop_index('idx_transactions_status', table_name='transactions')
    op.drop_index('idx_transactions_amount', table_name='transactions')
    op.drop_index('idx_transactions_account_date', table_name='transactions')
    op.drop_index('idx_transactions_tenant_category', table_name='transactions')
    op.drop_index('idx_transactions_tenant_date', table_name='transactions')
    op.drop_index('idx_transactions_tenant_account', table_name='transactions')
    op.drop_index('idx_transactions_tenant_user', table_name='transactions')
    op.drop_table('transactions')

    # Drop categorization_rules table
    op.drop_index(op.f('ix_categorization_rules_is_deleted'), table_name='categorization_rules')
    op.drop_index(op.f('ix_categorization_rules_user_id'), table_name='categorization_rules')
    op.drop_index(op.f('ix_categorization_rules_last_matched_at'), table_name='categorization_rules')
    op.drop_index(op.f('ix_categorization_rules_success_count'), table_name='categorization_rules')
    op.drop_index(op.f('ix_categorization_rules_match_count'), table_name='categorization_rules')
    op.drop_index(op.f('ix_categorization_rules_is_system'), table_name='categorization_rules')
    op.drop_index(op.f('ix_categorization_rules_is_active'), table_name='categorization_rules')
    op.drop_index(op.f('ix_categorization_rules_priority'), table_name='categorization_rules')
    op.drop_index(op.f('ix_categorization_rules_field_to_match'), table_name='categorization_rules')
    op.drop_index(op.f('ix_categorization_rules_rule_type'), table_name='categorization_rules')
    op.drop_index(op.f('ix_categorization_rules_name'), table_name='categorization_rules')
    op.drop_index(op.f('ix_categorization_rules_tenant_id'), table_name='categorization_rules')
    op.drop_index(op.f('ix_categorization_rules_id'), table_name='categorization_rules')
    op.drop_index('idx_categorization_rules_success_count', table_name='categorization_rules')
    op.drop_index('idx_categorization_rules_match_count', table_name='categorization_rules')
    op.drop_index('idx_categorization_rules_user', table_name='categorization_rules')
    op.drop_index('idx_categorization_rules_category', table_name='categorization_rules')
    op.drop_index('idx_categorization_rules_tenant_priority', table_name='categorization_rules')
    op.drop_index('idx_categorization_rules_tenant_active', table_name='categorization_rules')
    op.drop_index('idx_categorization_rules_tenant_type', table_name='categorization_rules')
    op.drop_table('categorization_rules')

    # Drop categories table
    op.drop_index(op.f('ix_categories_is_deleted'), table_name='categories')
    op.drop_index(op.f('ix_categories_user_id'), table_name='categories')
    op.drop_index(op.f('ix_categories_last_used_at'), table_name='categories')
    op.drop_index(op.f('ix_categories_usage_count'), table_name='categories')
    op.drop_index(op.f('ix_categories_is_system'), table_name='categories')
    op.drop_index(op.f('ix_categories_is_default'), table_name='categories')
    op.drop_index(op.f('ix_categories_is_active'), table_name='categories')
    op.drop_index(op.f('ix_categories_category_group'), table_name='categories')
    op.drop_index(op.f('ix_categories_category_type'), table_name='categories')
    op.drop_index(op.f('ix_categories_slug'), table_name='categories')
    op.drop_index(op.f('ix_categories_name'), table_name='categories')
    op.drop_index(op.f('ix_categories_tenant_id'), table_name='categories')
    op.drop_index(op.f('ix_categories_id'), table_name='categories')
    op.drop_index('idx_categories_user', table_name='categories')
    op.drop_index('idx_categories_usage', table_name='categories')
    op.drop_index('idx_categories_slug', table_name='categories')
    op.drop_index('idx_categories_parent', table_name='categories')
    op.drop_index('idx_categories_tenant_system', table_name='categories')
    op.drop_index('idx_categories_tenant_active', table_name='categories')
    op.drop_index('idx_categories_tenant_group', table_name='categories')
    op.drop_index('idx_categories_tenant_type', table_name='categories')
    op.drop_table('categories')

    # Drop accounts table
    op.drop_index(op.f('ix_accounts_is_deleted'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_user_id'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_is_archived'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_is_active'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_currency'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_institution_id'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_institution_name'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_account_subtype'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_account_type'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_account_number'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_name'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_tenant_id'), table_name='accounts')
    op.drop_index(op.f('ix_accounts_id'), table_name='accounts')
    op.drop_index('idx_accounts_institution', table_name='accounts')
    op.drop_index('idx_accounts_external_id', table_name='accounts')
    op.drop_index('idx_accounts_user_type', table_name='accounts')
    op.drop_index('idx_accounts_tenant_active', table_name='accounts')
    op.drop_index('idx_accounts_tenant_type', table_name='accounts')
    op.drop_index('idx_accounts_tenant_user', table_name='accounts')
    op.drop_table('accounts')
