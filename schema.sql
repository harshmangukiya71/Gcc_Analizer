-- =============================================================================
-- GCC COMPASS DATABASE SCHEMA (PostgreSQL)
-- =============================================================================

-- 1. Main GCC Registry Table (populated from CSV/Excel)
CREATE TABLE IF NOT EXISTS gcc_registry (
    id BIGSERIAL PRIMARY KEY,
    company_name TEXT NOT NULL,
    website TEXT,
    parent_hq_country TEXT,
    city TEXT NOT NULL,
    city_raw TEXT,
    sector TEXT,
    india_headcount TEXT,                      -- Preserves original values such as '1,000+' and '200–500'
    key_roles_hired TEXT,                      -- Preserves source text listing
    gcc_notes TEXT,
    source_url TEXT,
    source_name TEXT DEFAULT 'GCC Journal India',
    last_verified_at DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT uq_gcc_registry_company_city UNIQUE (company_name, city)
);

CREATE INDEX IF NOT EXISTS idx_gcc_registry_city ON gcc_registry(city);
CREATE INDEX IF NOT EXISTS idx_gcc_registry_sector ON gcc_registry(sector);
CREATE INDEX IF NOT EXISTS idx_gcc_registry_company_name ON gcc_registry(company_name);
CREATE INDEX IF NOT EXISTS idx_gcc_registry_city_sector ON gcc_registry(city, sector);

-- 2. Talent Salary Benchmarks
CREATE TABLE IF NOT EXISTS talent_salary_benchmarks (
    id BIGSERIAL PRIMARY KEY,
    city TEXT,                                 -- NULL for national benchmarks
    gcc_type TEXT,
    sector TEXT,
    job_family TEXT,
    job_title TEXT NOT NULL,
    required_skills TEXT,
    experience_min_years INTEGER,
    experience_max_years INTEGER,
    seniority_level TEXT,
    salary_min NUMERIC(14, 2),
    salary_max NUMERIC(14, 2),
    currency VARCHAR(10) NOT NULL DEFAULT 'INR',
    compensation_type TEXT,
    salary_period TEXT,
    data_year INTEGER NOT NULL,
    sample_size INTEGER,
    source_name TEXT,
    source_url TEXT,
    source_notes TEXT,
    confidence_level TEXT,
    last_verified_at DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_salary_min_max CHECK (salary_min IS NULL OR salary_max IS NULL OR salary_min <= salary_max),
    CONSTRAINT chk_exp_min_max CHECK (experience_min_years IS NULL OR experience_max_years IS NULL OR experience_min_years <= experience_max_years)
);

CREATE INDEX IF NOT EXISTS idx_talent_salary_city_job_seniority 
ON talent_salary_benchmarks(city, job_family, seniority_level);

-- 3. Office Market Metrics (Colliers Benchmark)
CREATE TABLE IF NOT EXISTS office_market_metrics (
    id BIGSERIAL PRIMARY KEY,
    rent_level VARCHAR(30) NOT NULL,
    city VARCHAR(100) NOT NULL,
    micro_market VARCHAR(150),
    rent_inr_per_sqft_per_month NUMERIC(10, 2) NOT NULL,

    CONSTRAINT valid_rent_level
        CHECK (rent_level IN ('city_average', 'micro_market')),

    CONSTRAINT valid_rent
        CHECK (rent_inr_per_sqft_per_month > 0),

    CONSTRAINT valid_micro_market
        CHECK (
            (rent_level = 'city_average' AND micro_market IS NULL)
            OR
            (rent_level = 'micro_market'
             AND micro_market IS NOT NULL
             AND micro_market <> '')
        )
);

CREATE UNIQUE INDEX IF NOT EXISTS uq_office_city_average 
ON office_market_metrics (city) 
WHERE rent_level = 'city_average';

CREATE UNIQUE INDEX IF NOT EXISTS uq_office_micro_market 
ON office_market_metrics (city, micro_market) 
WHERE rent_level = 'micro_market';

CREATE INDEX IF NOT EXISTS idx_office_rents_city ON office_market_metrics (city);
CREATE INDEX IF NOT EXISTS idx_office_rents_level ON office_market_metrics (rent_level);
CREATE INDEX IF NOT EXISTS idx_office_rents_city_level ON office_market_metrics (city, rent_level);

-- 4. Incentive Schemes
CREATE TABLE IF NOT EXISTS incentive_schemes (
    id BIGSERIAL PRIMARY KEY,
    policy_name TEXT NOT NULL,
    city TEXT,
    state_or_ut TEXT NOT NULL,
    gcc_type TEXT,
    incentive_category TEXT,
    benefit_description TEXT NOT NULL,
    incentive_formula TEXT,
    maximum_benefit NUMERIC(14, 2),
    currency VARCHAR(10),
    eligibility_criteria TEXT,
    effective_from DATE,
    effective_until DATE,
    application_deadline DATE,
    policy_status TEXT NOT NULL,
    official_source_url TEXT,
    source_notes TEXT,
    last_verified_at DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_effective_dates CHECK (effective_from IS NULL OR effective_until IS NULL OR effective_from <= effective_until)
);

CREATE INDEX IF NOT EXISTS idx_incentive_state_status 
ON incentive_schemes(state_or_ut, policy_status);

-- 5. GCC Expansion Events
CREATE TABLE IF NOT EXISTS gcc_expansion_events (
    id BIGSERIAL PRIMARY KEY,
    company_name TEXT NOT NULL,
    city TEXT NOT NULL,
    state_or_ut TEXT,
    event_type TEXT NOT NULL,
    sector TEXT,
    announcement_date DATE,
    expected_opening_date DATE,
    announced_investment NUMERIC(16, 2),
    investment_currency VARCHAR(10),
    announced_jobs INTEGER,
    actual_jobs_created INTEGER,
    event_status TEXT NOT NULL,
    source_name TEXT,
    source_url TEXT,
    source_notes TEXT,
    confidence_level TEXT,
    last_verified_at DATE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    CONSTRAINT chk_announced_jobs_positive CHECK (announced_jobs IS NULL OR announced_jobs >= 0),
    CONSTRAINT chk_actual_jobs_positive CHECK (actual_jobs_created IS NULL OR actual_jobs_created >= 0),
    CONSTRAINT chk_investment_positive CHECK (announced_investment IS NULL OR announced_investment >= 0)
);

CREATE INDEX IF NOT EXISTS idx_expansion_city_status 
ON gcc_expansion_events(city, event_status);
