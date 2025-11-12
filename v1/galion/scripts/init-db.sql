-- GALION Database Initialization Script
-- Creates both GALION.APP and GALION.STUDIO databases
-- Run automatically by Docker on first start

-- Create GALION.APP database (already created by default)
-- Nothing to do here, main database is created automatically

-- Create GALION.STUDIO database
SELECT 'Creating galion_studio database...' AS message;
CREATE DATABASE galion_studio;

-- Enable required extensions for both databases
\c galion;
SELECT 'Installing extensions for galion database...' AS message;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

\c galion_studio;
SELECT 'Installing extensions for galion_studio database...' AS message;
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Success message
\c postgres;
SELECT 'Database initialization complete!' AS message;
SELECT 'Databases created: galion, galion_studio' AS message;

