-- Database initialization script for TheTally
-- This script runs when the PostgreSQL container starts for the first time

-- Create extensions if they don't exist
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Set timezone
SET timezone = 'UTC';

-- Create additional schemas if needed
-- CREATE SCHEMA IF NOT EXISTS audit;

-- Grant necessary permissions on the current database (thetally_dev)
GRANT ALL PRIVILEGES ON DATABASE thetally_dev TO thetally_user;
GRANT ALL PRIVILEGES ON SCHEMA public TO thetally_user;

-- The actual tables will be created by Alembic migrations
-- This script just sets up the basic database structure
