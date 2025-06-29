-- Lysobacter Database Initialization Script
-- This script runs automatically when the PostgreSQL container starts for the first time

-- Set client encoding
SET client_encoding = 'UTF8';

-- Create the lysobacter schema
CREATE SCHEMA IF NOT EXISTS lysobacter;

-- Set search path to include our schema
SET search_path TO lysobacter, public;

-- Log initialization
DO $$
BEGIN
    RAISE NOTICE 'Initializing Lysobacter database schema...';
    RAISE NOTICE 'Schema lysobacter created successfully';
    RAISE NOTICE 'Ready for table creation and data import';
END $$; 