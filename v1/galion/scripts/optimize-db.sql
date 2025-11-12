-- ====================================================================
-- Database Optimization Script for GALION
-- Creates indexes for common query patterns
-- Usage: psql -U galion -d galion < scripts/optimize-db.sql
-- ====================================================================

-- Use CONCURRENTLY to avoid locking tables during index creation
-- This allows the database to remain available during indexing

\echo '================================================'
\echo 'Creating indexes for GALION.APP...'
\echo '================================================'

-- Switch to GALION.APP database
\c galion

-- Users table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_email 
  ON users(email);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_status 
  ON users(status) 
  WHERE status = 'active';
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_users_created_at 
  ON users(created_at DESC);

-- Sessions table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_user_id 
  ON sessions(user_id);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_token 
  ON sessions(token);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_sessions_expires_at 
  ON sessions(expires_at) 
  WHERE expires_at > NOW();

-- Conversations table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_user_id 
  ON conversations(user_id);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_user_created 
  ON conversations(user_id, created_at DESC);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_conversations_created_at 
  ON conversations(created_at DESC);

-- Messages table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_conversation_id 
  ON messages(conversation_id);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_conversation_created 
  ON messages(conversation_id, created_at ASC);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_messages_created_at 
  ON messages(created_at DESC);

-- Voice recordings table indexes (if exists)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_voice_recordings_user_id 
  ON voice_recordings(user_id);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_voice_recordings_conversation_id 
  ON voice_recordings(conversation_id);

\echo '✓ GALION.APP indexes created'
\echo ''

\echo '================================================'
\echo 'Creating indexes for GALION.STUDIO...'
\echo '================================================'

-- Switch to GALION.STUDIO database
\c galion_studio

-- Workspaces table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workspaces_owner_id 
  ON workspaces(owner_id);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workspaces_slug 
  ON workspaces(slug);

-- Projects table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_projects_workspace_id 
  ON projects(workspace_id);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_projects_workspace_status 
  ON projects(workspace_id, status);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_projects_created_at 
  ON projects(created_at DESC);

-- Tasks table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_project_id 
  ON tasks(project_id);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_assignee_id 
  ON tasks(assignee_id);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_status 
  ON tasks(status);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_project_status 
  ON tasks(project_id, status);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_assignee_status 
  ON tasks(assignee_id, status);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_tasks_created_at 
  ON tasks(created_at DESC);

-- Time logs table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_time_logs_task_id 
  ON time_logs(task_id);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_time_logs_user_id 
  ON time_logs(user_id);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_time_logs_work_date 
  ON time_logs(work_date DESC);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_time_logs_user_date 
  ON time_logs(user_id, work_date DESC);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_time_logs_user_date_task 
  ON time_logs(user_id, work_date DESC, task_id);

-- Payments table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_user_id 
  ON payments(user_id);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_status 
  ON payments(status);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_user_status 
  ON payments(user_id, status);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_payments_period 
  ON payments(period_start, period_end);

-- Job postings table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_job_postings_workspace_id 
  ON job_postings(workspace_id);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_job_postings_status 
  ON job_postings(status) 
  WHERE status = 'open';

-- Applications table indexes
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_applications_job_posting_id 
  ON applications(job_posting_id);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_applications_status 
  ON applications(status);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_applications_job_status 
  ON applications(job_posting_id, status);

-- Workspace members table indexes (if exists)
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workspace_members_workspace_id 
  ON workspace_members(workspace_id);
  
CREATE INDEX CONCURRENTLY IF NOT EXISTS idx_workspace_members_user_id 
  ON workspace_members(user_id);

\echo '✓ GALION.STUDIO indexes created'
\echo ''

\echo '================================================'
\echo 'Analyzing tables for query optimization...'
\echo '================================================'

-- Analyze tables to update statistics
-- This helps the query planner make better decisions

\c galion
ANALYZE users;
ANALYZE sessions;
ANALYZE conversations;
ANALYZE messages;

\c galion_studio
ANALYZE workspaces;
ANALYZE projects;
ANALYZE tasks;
ANALYZE time_logs;
ANALYZE payments;
ANALYZE job_postings;
ANALYZE applications;

\echo '✓ Table analysis complete'
\echo ''

\echo '================================================'
\echo 'Index creation complete!'
\echo '================================================'
\echo ''
\echo 'Created indexes for:'
\echo '  - GALION.APP: users, sessions, conversations, messages'
\echo '  - GALION.STUDIO: workspaces, projects, tasks, time_logs, payments, job_postings, applications'
\echo ''
\echo 'All tables analyzed for optimal query planning.'
\echo ''

-- Show index sizes
\c galion
\echo 'GALION.APP index sizes:'
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 10;

\c galion_studio
\echo ''
\echo 'GALION.STUDIO index sizes:'
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) as size
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC
LIMIT 10;

