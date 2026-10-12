"""initial gcc compass schema

Revision ID: 0001_initial_schema
Revises: 
Create Date: 2026-10-11 20:30:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = '0001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # 1. gcc_registry
    op.create_table(
        'gcc_registry',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('company_name', sa.Text(), nullable=False),
        sa.Column('website', sa.Text(), nullable=True),
        sa.Column('parent_hq_country', sa.Text(), nullable=True),
        sa.Column('city', sa.Text(), nullable=False),
        sa.Column('city_raw', sa.Text(), nullable=True),
        sa.Column('sector', sa.Text(), nullable=True),
        sa.Column('india_headcount', sa.Text(), nullable=True),
        sa.Column('key_roles_hired', sa.Text(), nullable=True),
        sa.Column('gcc_notes', sa.Text(), nullable=True),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('source_name', sa.Text(), nullable=True, server_default='GCC Journal India'),
        sa.Column('last_verified_at', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('company_name', 'city', name='uq_gcc_registry_company_city')
    )
    op.create_index('idx_gcc_registry_city', 'gcc_registry', ['city'])
    op.create_index('idx_gcc_registry_sector', 'gcc_registry', ['sector'])
    op.create_index('idx_gcc_registry_company_name', 'gcc_registry', ['company_name'])
    op.create_index('idx_gcc_registry_city_sector', 'gcc_registry', ['city', 'sector'])

    # 2. talent_salary_benchmarks
    op.create_table(
        'talent_salary_benchmarks',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('city', sa.Text(), nullable=True),
        sa.Column('gcc_type', sa.Text(), nullable=True),
        sa.Column('sector', sa.Text(), nullable=True),
        sa.Column('job_family', sa.Text(), nullable=True),
        sa.Column('job_title', sa.Text(), nullable=False),
        sa.Column('required_skills', sa.Text(), nullable=True),
        sa.Column('experience_min_years', sa.Integer(), nullable=True),
        sa.Column('experience_max_years', sa.Integer(), nullable=True),
        sa.Column('seniority_level', sa.Text(), nullable=True),
        sa.Column('salary_min', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('salary_max', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=10), server_default='INR', nullable=False),
        sa.Column('compensation_type', sa.Text(), nullable=True),
        sa.Column('salary_period', sa.Text(), nullable=True),
        sa.Column('data_year', sa.Integer(), nullable=False),
        sa.Column('sample_size', sa.Integer(), nullable=True),
        sa.Column('source_name', sa.Text(), nullable=True),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('source_notes', sa.Text(), nullable=True),
        sa.Column('confidence_level', sa.Text(), nullable=True),
        sa.Column('last_verified_at', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max', name='chk_salary_min_max'),
        sa.CheckConstraint('experience_min_years IS NULL OR experience_max_years IS NULL OR experience_min_years <= experience_max_years', name='chk_exp_min_max'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_talent_salary_city_job_seniority', 'talent_salary_benchmarks', ['city', 'job_family', 'seniority_level'])

    # 3. office_market_metrics
    op.create_table(
        'office_market_metrics',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('rent_level', sa.String(length=30), nullable=False),
        sa.Column('city', sa.String(length=100), nullable=False),
        sa.Column('micro_market', sa.String(length=150), nullable=True),
        sa.Column('rent_inr_per_sqft_per_month', sa.Numeric(precision=10, scale=2), nullable=False),
        sa.CheckConstraint("rent_level IN ('city_average', 'micro_market')", name='valid_rent_level'),
        sa.CheckConstraint("rent_inr_per_sqft_per_month > 0", name='valid_rent'),
        sa.CheckConstraint(
            "(rent_level = 'city_average' AND micro_market IS NULL) OR "
            "(rent_level = 'micro_market' AND micro_market IS NOT NULL AND micro_market <> '')",
            name='valid_micro_market'
        ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('uq_office_city_average', 'office_market_metrics', ['city'], unique=True, postgresql_where=sa.text("rent_level = 'city_average'"))
    op.create_index('uq_office_micro_market', 'office_market_metrics', ['city', 'micro_market'], unique=True, postgresql_where=sa.text("rent_level = 'micro_market'"))
    op.create_index('idx_office_rents_city', 'office_market_metrics', ['city'])
    op.create_index('idx_office_rents_level', 'office_market_metrics', ['rent_level'])
    op.create_index('idx_office_rents_city_level', 'office_market_metrics', ['city', 'rent_level'])

    # 4. incentive_schemes
    op.create_table(
        'incentive_schemes',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('policy_name', sa.Text(), nullable=False),
        sa.Column('city', sa.Text(), nullable=True),
        sa.Column('state_or_ut', sa.Text(), nullable=False),
        sa.Column('gcc_type', sa.Text(), nullable=True),
        sa.Column('incentive_category', sa.Text(), nullable=True),
        sa.Column('benefit_description', sa.Text(), nullable=False),
        sa.Column('incentive_formula', sa.Text(), nullable=True),
        sa.Column('maximum_benefit', sa.Numeric(precision=14, scale=2), nullable=True),
        sa.Column('currency', sa.String(length=10), nullable=True),
        sa.Column('eligibility_criteria', sa.Text(), nullable=True),
        sa.Column('effective_from', sa.Date(), nullable=True),
        sa.Column('effective_until', sa.Date(), nullable=True),
        sa.Column('application_deadline', sa.Date(), nullable=True),
        sa.Column('policy_status', sa.Text(), nullable=False),
        sa.Column('official_source_url', sa.Text(), nullable=True),
        sa.Column('source_notes', sa.Text(), nullable=True),
        sa.Column('last_verified_at', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('effective_from IS NULL OR effective_until IS NULL OR effective_from <= effective_until', name='chk_effective_dates'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_incentive_state_status', 'incentive_schemes', ['state_or_ut', 'policy_status'])

    # 5. gcc_expansion_events
    op.create_table(
        'gcc_expansion_events',
        sa.Column('id', sa.BigInteger(), autoincrement=True, nullable=False),
        sa.Column('company_name', sa.Text(), nullable=False),
        sa.Column('city', sa.Text(), nullable=False),
        sa.Column('state_or_ut', sa.Text(), nullable=True),
        sa.Column('event_type', sa.Text(), nullable=False),
        sa.Column('sector', sa.Text(), nullable=True),
        sa.Column('announcement_date', sa.Date(), nullable=True),
        sa.Column('expected_opening_date', sa.Date(), nullable=True),
        sa.Column('announced_investment', sa.Numeric(precision=16, scale=2), nullable=True),
        sa.Column('investment_currency', sa.String(length=10), nullable=True),
        sa.Column('announced_jobs', sa.Integer(), nullable=True),
        sa.Column('actual_jobs_created', sa.Integer(), nullable=True),
        sa.Column('event_status', sa.Text(), nullable=False),
        sa.Column('source_name', sa.Text(), nullable=True),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('source_notes', sa.Text(), nullable=True),
        sa.Column('confidence_level', sa.Text(), nullable=True),
        sa.Column('last_verified_at', sa.Date(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.CheckConstraint('announced_jobs IS NULL OR announced_jobs >= 0', name='chk_announced_jobs_positive'),
        sa.CheckConstraint('actual_jobs_created IS NULL OR actual_jobs_created >= 0', name='chk_actual_jobs_positive'),
        sa.CheckConstraint('announced_investment IS NULL OR announced_investment >= 0', name='chk_investment_positive'),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index('idx_expansion_city_status', 'gcc_expansion_events', ['city', 'event_status'])

def downgrade() -> None:
    op.drop_table('gcc_expansion_events')
    op.drop_table('incentive_schemes')
    op.drop_table('office_market_metrics')
    op.drop_table('talent_salary_benchmarks')
    op.drop_table('gcc_registry')
