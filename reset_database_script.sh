#!/bin/bash
# Complete Reset Script for ProzLab Backend (Correct Migration Path)

echo "🚀 Starting complete database and migration reset..."

# Step 1: Delete all migration files from correct location
echo "🗑️  Deleting old migration files..."
rm -f migrations/versions/*.py
touch migrations/versions/__init__.py
echo "✅ Migration files cleaned from migrations/versions/"

# Step 2: Reset database completely
echo "🗑️  Resetting database..."
psql -d prozlab_db -U proz_user << 'EOF'
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
GRANT ALL ON SCHEMA public TO proz_user;
GRANT ALL ON SCHEMA public TO public;
SELECT 'Database reset complete!' as result;
EOF

echo "✅ Database reset complete"

# Step 3: Apply fresh migration
echo "🏗️  Creating fresh database schema..."
psql -d prozlab_db -U proz_user << 'EOF'

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM types
CREATE TYPE user_role AS ENUM ('user', 'admin', 'superuser');
CREATE TYPE verification_status AS ENUM ('pending', 'verified', 'rejected');
CREATE TYPE task_status AS ENUM ('pending', 'assigned', 'accepted', 'in_progress', 'completed', 'cancelled', 'rejected');
CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high', 'urgent');

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    role user_role DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Specialties table
CREATE TABLE specialties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Professional profiles table
CREATE TABLE proz_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20),
    profile_image_url TEXT,
    bio TEXT,
    location VARCHAR(255),
    years_experience INTEGER,
    hourly_rate DECIMAL(10,2),
    availability VARCHAR(50),
    education TEXT,
    certifications TEXT,
    website VARCHAR(255),
    linkedin VARCHAR(255),
    preferred_contact_method VARCHAR(50),
    verification_status verification_status DEFAULT 'pending',
    is_featured BOOLEAN DEFAULT FALSE,
    rating DECIMAL(3,2) DEFAULT 0.00,
    review_count INTEGER DEFAULT 0,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Professional specialties junction table
CREATE TABLE proz_specialties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proz_id UUID NOT NULL REFERENCES proz_profiles(id) ON DELETE CASCADE,
    specialty_id UUID NOT NULL REFERENCES specialties(id) ON DELETE CASCADE,
    UNIQUE(proz_id, specialty_id)
);

-- Service requests table
CREATE TABLE service_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name VARCHAR(200) NOT NULL,
    client_name VARCHAR(100) NOT NULL,
    client_email VARCHAR(255) NOT NULL,
    client_phone VARCHAR(20),
    service_title VARCHAR(200) NOT NULL,
    service_description TEXT NOT NULL,
    service_category VARCHAR(100) NOT NULL,
    required_skills TEXT,
    budget_min DECIMAL(10,2),
    budget_max DECIMAL(10,2),
    expected_duration VARCHAR(100),
    deadline TIMESTAMP WITH TIME ZONE,
    location_preference VARCHAR(255),
    remote_work_allowed BOOLEAN DEFAULT TRUE,
    status task_status DEFAULT 'pending' NOT NULL,
    priority task_priority DEFAULT 'medium' NOT NULL,
    admin_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Task assignments table
CREATE TABLE task_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_request_id UUID NOT NULL REFERENCES service_requests(id) ON DELETE CASCADE,
    proz_id UUID NOT NULL REFERENCES proz_profiles(id) ON DELETE CASCADE,
    assigned_by_user_id UUID REFERENCES users(id),
    assignment_notes TEXT,
    estimated_hours DECIMAL(8,2),
    proposed_rate DECIMAL(10,2),
    status task_status DEFAULT 'assigned' NOT NULL,
    proz_response TEXT,
    proz_response_at TIMESTAMP WITH TIME ZONE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(service_request_id, proz_id)
);

-- Task notifications table
CREATE TABLE task_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proz_id UUID NOT NULL REFERENCES proz_profiles(id) ON DELETE CASCADE,
    task_assignment_id UUID REFERENCES task_assignments(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    is_email_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);

-- Create essential indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_proz_profiles_email ON proz_profiles(email);
CREATE INDEX idx_proz_profiles_verification_status ON proz_profiles(verification_status);
CREATE INDEX idx_service_requests_status ON service_requests(status);
CREATE INDEX idx_task_assignments_proz_id ON task_assignments(proz_id);
CREATE INDEX idx_task_notifications_proz_id ON task_notifications(proz_id);

-- Insert default specialties
INSERT INTO specialties (name, description, icon) VALUES
('Web Development', 'Frontend and backend web development', 'code'),
('Mobile Development', 'iOS and Android app development', 'smartphone'),
('UI/UX Design', 'User interface and experience design', 'palette'),
('Digital Marketing', 'SEO, social media, and online marketing', 'trending-up'),
('Data Science', 'Data analysis and machine learning', 'bar-chart'),
('DevOps', 'Cloud infrastructure and deployment', 'server'),
('Graphic Design', 'Visual design and branding', 'image'),
('Content Writing', 'Copywriting and content creation', 'edit'),
('Project Management', 'Project planning and coordination', 'calendar'),
('Consulting', 'Business and technical consulting', 'users');

-- Create admin user (password: admin123)
INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, is_verified) VALUES
('admin@prozlab.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeRQdOkSMWL.ZYPYm', 'Admin', 'User', 'superuser', true, true);

SELECT 'Fresh database schema created successfully!' as result;
SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public';

EOF

echo "✅ Fresh database schema created"

# Step 4: Initialize Alembic with current state
echo "🔧 Initializing Alembic..."
alembic revision --autogenerate -m "Initial schema with task management"
alembic upgrade head

echo "✅ Alembic initialized"

# Step 5: Verify everything
echo "🔍 Verifying setup..."
echo "Database tables:"
psql -d prozlab_db -U proz_user -c "\dt"

echo "Alembic status:"
alembic current

echo "Migration files:"
ls -la migrations/versions/

echo "🎉 Complete reset finished successfully!"
echo "📋 Default admin user: admin@prozlab.com / admin123"

# Step 2: Reset database completely
echo "🗑️  Resetting database..."
psql -d prozlab_db -U proz_user << 'EOF'
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
GRANT ALL ON SCHEMA public TO proz_user;
GRANT ALL ON SCHEMA public TO public;
SELECT 'Database reset complete!' as result;
EOF

echo "✅ Database reset complete"

# Step 3: Apply fresh migration
echo "🏗️  Creating fresh database schema..."
psql -d prozlab_db -U proz_user << 'EOF'

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create ENUM types
CREATE TYPE user_role AS ENUM ('user', 'admin', 'superuser');
CREATE TYPE verification_status AS ENUM ('pending', 'verified', 'rejected');
CREATE TYPE task_status AS ENUM ('pending', 'assigned', 'accepted', 'in_progress', 'completed', 'cancelled', 'rejected');
CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high', 'urgent');

-- Users table
CREATE TABLE users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    email VARCHAR(255) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    is_verified BOOLEAN DEFAULT FALSE,
    role user_role DEFAULT 'user',
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Specialties table
CREATE TABLE specialties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    name VARCHAR(100) UNIQUE NOT NULL,
    description TEXT,
    icon VARCHAR(50),
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Professional profiles table
CREATE TABLE proz_profiles (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID UNIQUE REFERENCES users(id) ON DELETE CASCADE,
    email VARCHAR(255) UNIQUE NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    last_name VARCHAR(100) NOT NULL,
    phone_number VARCHAR(20),
    profile_image_url TEXT,
    bio TEXT,
    location VARCHAR(255),
    years_experience INTEGER,
    hourly_rate DECIMAL(10,2),
    availability VARCHAR(50),
    education TEXT,
    certifications TEXT,
    website VARCHAR(255),
    linkedin VARCHAR(255),
    preferred_contact_method VARCHAR(50),
    verification_status verification_status DEFAULT 'pending',
    is_featured BOOLEAN DEFAULT FALSE,
    rating DECIMAL(3,2) DEFAULT 0.00,
    review_count INTEGER DEFAULT 0,
    email_verified BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Professional specialties junction table
CREATE TABLE proz_specialties (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proz_id UUID NOT NULL REFERENCES proz_profiles(id) ON DELETE CASCADE,
    specialty_id UUID NOT NULL REFERENCES specialties(id) ON DELETE CASCADE,
    UNIQUE(proz_id, specialty_id)
);

-- Service requests table
CREATE TABLE service_requests (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    company_name VARCHAR(200) NOT NULL,
    client_name VARCHAR(100) NOT NULL,
    client_email VARCHAR(255) NOT NULL,
    client_phone VARCHAR(20),
    service_title VARCHAR(200) NOT NULL,
    service_description TEXT NOT NULL,
    service_category VARCHAR(100) NOT NULL,
    required_skills TEXT,
    budget_min DECIMAL(10,2),
    budget_max DECIMAL(10,2),
    expected_duration VARCHAR(100),
    deadline TIMESTAMP WITH TIME ZONE,
    location_preference VARCHAR(255),
    remote_work_allowed BOOLEAN DEFAULT TRUE,
    status task_status DEFAULT 'pending' NOT NULL,
    priority task_priority DEFAULT 'medium' NOT NULL,
    admin_notes TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Task assignments table
CREATE TABLE task_assignments (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    service_request_id UUID NOT NULL REFERENCES service_requests(id) ON DELETE CASCADE,
    proz_id UUID NOT NULL REFERENCES proz_profiles(id) ON DELETE CASCADE,
    assigned_by_user_id UUID REFERENCES users(id),
    assignment_notes TEXT,
    estimated_hours DECIMAL(8,2),
    proposed_rate DECIMAL(10,2),
    status task_status DEFAULT 'assigned' NOT NULL,
    proz_response TEXT,
    proz_response_at TIMESTAMP WITH TIME ZONE,
    assigned_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    due_date TIMESTAMP WITH TIME ZONE,
    completed_at TIMESTAMP WITH TIME ZONE,
    UNIQUE(service_request_id, proz_id)
);

-- Task notifications table
CREATE TABLE task_notifications (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    proz_id UUID NOT NULL REFERENCES proz_profiles(id) ON DELETE CASCADE,
    task_assignment_id UUID REFERENCES task_assignments(id) ON DELETE CASCADE,
    title VARCHAR(200) NOT NULL,
    message TEXT NOT NULL,
    notification_type VARCHAR(50) NOT NULL,
    is_read BOOLEAN DEFAULT FALSE,
    is_email_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    read_at TIMESTAMP WITH TIME ZONE
);

-- Create essential indexes
CREATE INDEX idx_users_email ON users(email);
CREATE INDEX idx_proz_profiles_email ON proz_profiles(email);
CREATE INDEX idx_proz_profiles_verification_status ON proz_profiles(verification_status);
CREATE INDEX idx_service_requests_status ON service_requests(status);
CREATE INDEX idx_task_assignments_proz_id ON task_assignments(proz_id);
CREATE INDEX idx_task_notifications_proz_id ON task_notifications(proz_id);

-- Insert default specialties
INSERT INTO specialties (name, description, icon) VALUES
('Web Development', 'Frontend and backend web development', 'code'),
('Mobile Development', 'iOS and Android app development', 'smartphone'),
('UI/UX Design', 'User interface and experience design', 'palette'),
('Digital Marketing', 'SEO, social media, and online marketing', 'trending-up'),
('Data Science', 'Data analysis and machine learning', 'bar-chart'),
('DevOps', 'Cloud infrastructure and deployment', 'server'),
('Graphic Design', 'Visual design and branding', 'image'),
('Content Writing', 'Copywriting and content creation', 'edit'),
('Project Management', 'Project planning and coordination', 'calendar'),
('Consulting', 'Business and technical consulting', 'users');

-- Create admin user (password: admin123)
INSERT INTO users (email, password_hash, first_name, last_name, role, is_active, is_verified) VALUES
('admin@prozlab.com', '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LeRQdOkSMWL.ZYPYm', 'Admin', 'User', 'superuser', true, true);

SELECT 'Fresh database schema created successfully!' as result;
SELECT COUNT(*) as table_count FROM information_schema.tables WHERE table_schema = 'public';

EOF

echo "✅ Fresh database schema created"

# Step 4: Initialize Alembic with current state
echo "🔧 Initializing Alembic..."
alembic revision --autogenerate -m "Initial schema with task management"
alembic upgrade head

echo "✅ Alembic initialized"

# Step 5: Verify everything
echo "🔍 Verifying setup..."
echo "Database tables:"
psql -d prozlab_db -U proz_user -c "\dt"

echo "Alembic status:"
alembic current

echo "Migration files:"
ls -la alembic/versions/

echo "🎉 Complete reset finished successfully!"
echo "📋 Default admin user: admin@prozlab.com / admin123"