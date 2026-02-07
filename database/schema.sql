-- EWU Database Schema
-- Applied via Supabase migrations

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Departments
CREATE TABLE IF NOT EXISTS departments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    code TEXT UNIQUE,
    name TEXT NOT NULL,
    faculty TEXT NOT NULL,
    url TEXT,
    description TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Programs
CREATE TABLE IF NOT EXISTS programs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    degree_type TEXT NOT NULL, -- Undergraduate, Graduate
    department_id UUID REFERENCES departments(id),
    department_name TEXT,
    credits INTEGER,
    duration TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tuition Fees
CREATE TABLE IF NOT EXISTS tuition_fees (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program TEXT NOT NULL,
    level TEXT NOT NULL, -- Undergraduate, Graduate
    fee_per_credit NUMERIC,
    total_tuition NUMERIC,
    library_lab_fees NUMERIC,
    admission_fee NUMERIC,
    grand_total NUMERIC,
    credits INTEGER,
    currency TEXT DEFAULT 'BDT',
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Faculty Members
CREATE TABLE IF NOT EXISTS faculty_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    designation TEXT,
    department_id UUID REFERENCES departments(id),
    department_name TEXT,
    email TEXT,
    phone TEXT,
    profile_url TEXT,
    specialization TEXT,
    academic_background JSONB,
    publications JSONB,
    image_url TEXT,
    profile_id TEXT,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Events
CREATE TABLE IF NOT EXISTS events (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    description TEXT,
    event_date DATE,
    end_date DATE,
    location TEXT,
    url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Notices
CREATE TABLE IF NOT EXISTS notices (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    url TEXT,
    published_date TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Scholarships
CREATE TABLE IF NOT EXISTS scholarships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    eligibility TEXT,
    amount TEXT,
    cgpa_requirement NUMERIC,
    effective_from TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Clubs
CREATE TABLE IF NOT EXISTS clubs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    description TEXT,
    url TEXT,
    logo TEXT,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Governance Members (academic_council, board_of_trustees, syndicate)
CREATE TABLE IF NOT EXISTS governance_members (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    body TEXT NOT NULL,            -- 'academic_council', 'board_of_trustees', 'syndicate'
    name TEXT NOT NULL,
    role TEXT,
    is_chairperson BOOLEAN DEFAULT FALSE,
    profile_url TEXT,
    details JSONB,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- University Documents (singleton/document-shaped JSON blobs)
CREATE TABLE IF NOT EXISTS university_documents (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    slug TEXT UNIQUE NOT NULL,
    title TEXT NOT NULL,
    content JSONB NOT NULL,
    source_file TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Admission Deadlines
CREATE TABLE IF NOT EXISTS admission_deadlines (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    program TEXT NOT NULL,
    department TEXT,
    level TEXT NOT NULL,
    semester TEXT,
    application_deadline TEXT,
    admission_test_date TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Grade Scale
CREATE TABLE IF NOT EXISTS grade_scale (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    numerical_score TEXT NOT NULL,
    letter_grade TEXT NOT NULL,
    grade_point NUMERIC NOT NULL,
    is_special BOOLEAN DEFAULT FALSE,
    description TEXT,
    note TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Notable Alumni
CREATE TABLE IF NOT EXISTS notable_alumni (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    department TEXT,
    achievement TEXT,
    details TEXT,
    position TEXT,
    company TEXT,
    awards JSONB,
    year_awarded INTEGER,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Helpdesk Contacts
CREATE TABLE IF NOT EXISTS helpdesk_contacts (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    category TEXT NOT NULL,
    department_code TEXT,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    purpose TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Proctor Schedule
CREATE TABLE IF NOT EXISTS proctor_schedule (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    semester TEXT,
    role TEXT NOT NULL,
    day_of_week TEXT,
    name TEXT NOT NULL,
    designation TEXT,
    department TEXT,
    office_extension TEXT,
    room_number TEXT,
    email TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Newsletters
CREATE TABLE IF NOT EXISTS newsletters (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    title TEXT NOT NULL,
    published_date TEXT,
    semester TEXT,
    year TEXT,
    image_url TEXT,
    pdf_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Partnerships
CREATE TABLE IF NOT EXISTS partnerships (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    acronym TEXT,
    country TEXT,
    organization_type TEXT,
    partnership_type TEXT,
    description TEXT,
    areas_of_collaboration JSONB,
    status TEXT DEFAULT 'Active',
    signed_date TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Policies
CREATE TABLE IF NOT EXISTS policies (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name TEXT NOT NULL,
    purpose TEXT,
    scope TEXT,
    principles JSONB,
    key_actions JSONB,
    committee_members JSONB,
    objectives TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Academic Calendar
CREATE TABLE IF NOT EXISTS academic_calendar (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    semester TEXT NOT NULL,
    program_type TEXT NOT NULL,
    calendar_type TEXT NOT NULL,
    event_date TEXT NOT NULL,
    day TEXT,
    event_name TEXT NOT NULL,
    source_url TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

CREATE UNIQUE INDEX IF NOT EXISTS idx_ac_unique
    ON academic_calendar (semester, program_type, calendar_type, event_date, event_name);

-- Scrape Metadata (tracking table)
CREATE TABLE IF NOT EXISTS scrape_metadata (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    scraper_name TEXT NOT NULL,
    last_run TIMESTAMPTZ NOT NULL,
    records_scraped INTEGER DEFAULT 0,
    status TEXT DEFAULT 'success',
    error_message TEXT,
    duration_seconds NUMERIC,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_programs_department ON programs(department_id);
CREATE INDEX IF NOT EXISTS idx_programs_degree_type ON programs(degree_type);
CREATE INDEX IF NOT EXISTS idx_faculty_department ON faculty_members(department_id);
CREATE INDEX IF NOT EXISTS idx_notices_published_date ON notices(published_date DESC);
CREATE INDEX IF NOT EXISTS idx_events_date ON events(event_date DESC);
CREATE INDEX IF NOT EXISTS idx_scrape_metadata_name ON scrape_metadata(scraper_name);
CREATE INDEX IF NOT EXISTS idx_scrape_metadata_run ON scrape_metadata(last_run DESC);
CREATE INDEX IF NOT EXISTS idx_governance_body ON governance_members(body);
CREATE INDEX IF NOT EXISTS idx_university_documents_slug ON university_documents(slug);
CREATE INDEX IF NOT EXISTS idx_admission_deadlines_level ON admission_deadlines(level);
CREATE INDEX IF NOT EXISTS idx_newsletters_year ON newsletters(year DESC);

-- Updated_at trigger function
CREATE OR REPLACE FUNCTION update_updated_at()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Apply updated_at triggers
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN
        SELECT unnest(ARRAY[
            'departments', 'programs', 'tuition_fees', 'faculty_members',
            'events', 'scholarships', 'clubs', 'notices',
            'governance_members', 'admission_deadlines', 'university_documents',
            'grade_scale', 'notable_alumni', 'helpdesk_contacts', 'proctor_schedule',
            'newsletters', 'partnerships', 'policies'
        ])
    LOOP
        EXECUTE format(
            'DROP TRIGGER IF EXISTS set_updated_at ON %I; CREATE TRIGGER set_updated_at BEFORE UPDATE ON %I FOR EACH ROW EXECUTE FUNCTION update_updated_at();',
            t, t
        );
    END LOOP;
END;
$$;

-- Enable Row Level Security on all tables
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN
        SELECT unnest(ARRAY[
            'departments', 'programs', 'tuition_fees', 'faculty_members',
            'events', 'scholarships', 'clubs', 'notices',
            'scrape_metadata', 'academic_calendar',
            'governance_members', 'university_documents', 'admission_deadlines',
            'grade_scale', 'notable_alumni', 'helpdesk_contacts', 'proctor_schedule',
            'newsletters', 'partnerships', 'policies'
        ])
    LOOP
        EXECUTE format('ALTER TABLE %I ENABLE ROW LEVEL SECURITY;', t);
    END LOOP;
END;
$$;

-- Public read policies for all data tables (scrape_metadata is internal only)
DO $$
DECLARE
    t TEXT;
BEGIN
    FOR t IN
        SELECT unnest(ARRAY[
            'departments', 'programs', 'tuition_fees', 'faculty_members',
            'events', 'scholarships', 'clubs', 'notices',
            'governance_members', 'university_documents', 'admission_deadlines',
            'grade_scale', 'notable_alumni', 'helpdesk_contacts', 'proctor_schedule',
            'newsletters', 'partnerships', 'policies', 'academic_calendar'
        ])
    LOOP
        EXECUTE format(
            'DROP POLICY IF EXISTS public_read ON %I; CREATE POLICY public_read ON %I FOR SELECT TO anon USING (true);',
            t, t
        );
    END LOOP;
END;
$$;
