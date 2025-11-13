#!/usr/bin/env python3
"""
Database Setup Script for NexusLang v2
=========================================

This script initializes the PostgreSQL database with all migrations and seed data.

Features:
- Creates database if it doesn't exist
- Runs all migration files in order
- Seeds initial data (admin user, roles, etc.)
- Verifies database connectivity
- Provides detailed logging

Usage:
    python scripts/setup_database.py [--force] [--seed-only]

Options:
    --force: Drop and recreate database
    --seed-only: Only run seed data, skip migrations
"""

import argparse
import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
import logging
from pathlib import Path

# Add backend directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from core.database import DATABASE_URL

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('database_setup.log')
    ]
)
logger = logging.getLogger(__name__)

class DatabaseSetup:
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.migrations_dir = Path(__file__).parent.parent / "migrations"

        # Parse connection details
        url_parts = db_url.replace('postgresql://', '').split('/')
        self.db_name = url_parts[1].split('?')[0]
        self.base_url = '/'.join(url_parts[:-1])

    def connect(self, db_name=None):
        """Connect to database (optionally different database)"""
        conn_str = f"{self.base_url}/{db_name or self.db_name}"
        return psycopg2.connect(conn_str)

    def database_exists(self):
        """Check if database exists"""
        try:
            conn = self.connect('postgres')
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.db_name,))
            exists = cursor.fetchone() is not None

            cursor.close()
            conn.close()

            return exists
        except Exception as e:
            logger.error(f"Error checking if database exists: {e}")
            return False

    def create_database(self):
        """Create the database"""
        logger.info(f"Creating database: {self.db_name}")

        try:
            conn = self.connect('postgres')
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            cursor.execute(f'CREATE DATABASE "{self.db_name}"')
            logger.info(f"Database '{self.db_name}' created successfully")

            cursor.close()
            conn.close()

            return True
        except Exception as e:
            logger.error(f"Error creating database: {e}")
            return False

    def drop_database(self):
        """Drop the database (with confirmation)"""
        logger.warning(f"Dropping database: {self.db_name}")

        try:
            conn = self.connect('postgres')
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()

            # Terminate all connections to the database
            cursor.execute("""
                SELECT pg_terminate_backend(pid)
                FROM pg_stat_activity
                WHERE datname = %s AND pid <> pg_backend_pid()
            """, (self.db_name,))

            cursor.execute(f'DROP DATABASE IF EXISTS "{self.db_name}"')
            logger.info(f"Database '{self.db_name}' dropped successfully")

            cursor.close()
            conn.close()

            return True
        except Exception as e:
            logger.error(f"Error dropping database: {e}")
            return False

    def run_migration(self, migration_file: Path):
        """Run a single migration file"""
        logger.info(f"Running migration: {migration_file.name}")

        try:
            conn = self.connect()
            cursor = conn.cursor()

            with open(migration_file, 'r', encoding='utf-8') as f:
                sql = f.read()

            # Split SQL by semicolon and execute each statement
            statements = [stmt.strip() for stmt in sql.split(';') if stmt.strip()]
            for statement in statements:
                if statement:
                    cursor.execute(statement)

            conn.commit()
            cursor.close()
            conn.close()

            logger.info(f"Migration '{migration_file.name}' completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error running migration {migration_file.name}: {e}")
            return False

    def run_migrations(self):
        """Run all migration files in order"""
        logger.info("Running database migrations...")

        if not self.migrations_dir.exists():
            logger.error(f"Migrations directory not found: {self.migrations_dir}")
            return False

        migration_files = sorted([
            f for f in self.migrations_dir.glob("*.sql")
            if f.name.startswith(('001_', '002_', '003_', '004_'))
        ])

        if not migration_files:
            logger.warning("No migration files found")
            return True

        for migration_file in migration_files:
            if not self.run_migration(migration_file):
                return False

        logger.info("All migrations completed successfully")
        return True

    def seed_database(self):
        """Seed the database with initial data"""
        logger.info("Seeding database with initial data...")

        try:
            conn = self.connect()
            cursor = conn.cursor()

            # Create admin user
            cursor.execute("""
                INSERT INTO users (
                    email, username, hashed_password, full_name, is_admin, credits
                ) VALUES (
                    'admin@nexuslang.app',
                    'admin',
                    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Le1H1lOvWpHn1fGa', -- 'admin123!'
                    'System Administrator',
                    true,
                    1000000.00
                ) ON CONFLICT (email) DO NOTHING
            """)

            # Create sample user
            cursor.execute("""
                INSERT INTO users (
                    email, username, hashed_password, full_name, credits
                ) VALUES (
                    'user@nexuslang.app',
                    'demo_user',
                    '$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/Le1H1lOvWpHn1fGa', -- 'user123!'
                    'Demo User',
                    1000.00
                ) ON CONFLICT (email) DO NOTHING
            """)

            # Create sample project
            cursor.execute("""
                INSERT INTO projects (
                    user_id, name, description, code
                ) SELECT
                    u.id,
                    'Hello World',
                    'A simple NexusLang program',
                    'fn main() {
    say("Hello, NexusLang!", emotion="excited")
    let result = 2 + 2
    println("2 + 2 = " + result)
}'
                FROM users u WHERE u.username = 'demo_user'
                ON CONFLICT DO NOTHING
            """)

            conn.commit()
            cursor.close()
            conn.close()

            # Seed RBAC system using async context
            logger.info("Seeding RBAC system...")
            import asyncio
            from .seed_rbac import seed_permissions, seed_roles, seed_feature_flags, assign_admin_role

            async def seed_rbac():
                from core.database import get_db
                async for db in get_db():
                    try:
                        await seed_permissions(db)
                        await seed_roles(db)
                        await seed_feature_flags(db)
                        await assign_admin_role(db)
                        logger.info("RBAC seeding completed")
                    except Exception as e:
                        logger.error(f"RBAC seeding failed: {e}")
                    finally:
                        await db.close()

            asyncio.run(seed_rbac())

            # Seed mail providers
            logger.info("Seeding mail providers...")
            from .seed_mail_providers import seed_mail_providers
            asyncio.run(seed_mail_providers())

            logger.info("Database seeding completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error seeding database: {e}")
            return False

    def verify_setup(self):
        """Verify database setup is working"""
        logger.info("Verifying database setup...")

        try:
            conn = self.connect()
            cursor = conn.cursor()

            # Check if tables exist
            cursor.execute("""
                SELECT table_name
                FROM information_schema.tables
                WHERE table_schema = 'public'
                AND table_name IN ('users', 'projects', 'roles', 'permissions', 'knowledge_entries', 'knowledge_graph', 'contributions')
                ORDER BY table_name
            """)

            tables = cursor.fetchall()
            table_names = [row[0] for row in tables]

            expected_tables = ['users', 'projects', 'roles', 'permissions', 'knowledge_entries', 'knowledge_graph', 'contributions']
            missing_tables = [t for t in expected_tables if t not in table_names]

            if missing_tables:
                logger.error(f"Missing tables: {missing_tables}")
                return False

            # Check if admin user exists
            cursor.execute("SELECT COUNT(*) FROM users WHERE is_admin = true")
            admin_count = cursor.fetchone()[0]

            if admin_count == 0:
                logger.warning("No admin user found")
            else:
                logger.info(f"Found {admin_count} admin user(s)")

            cursor.close()
            conn.close()

            logger.info("Database verification completed successfully")
            return True

        except Exception as e:
            logger.error(f"Error verifying database: {e}")
            return False

    def setup(self, force=False, seed_only=False):
        """Run complete database setup"""
        logger.info("Starting database setup...")

        # Check if database exists
        db_exists = self.database_exists()

        if db_exists and force:
            logger.info("Dropping existing database (--force flag)")
            if not self.drop_database():
                return False

            db_exists = False

        if not db_exists and not seed_only:
            logger.info("Database does not exist, creating...")
            if not self.create_database():
                return False

        if not seed_only:
            if not self.run_migrations():
                return False

        if not self.seed_database():
            return False

        if not self.verify_setup():
            return False

        logger.info("Database setup completed successfully! 🎉")
        return True


def main():
    parser = argparse.ArgumentParser(description="NexusLang v2 Database Setup")
    parser.add_argument('--force', action='store_true',
                       help='Drop and recreate database')
    parser.add_argument('--seed-only', action='store_true',
                       help='Only run seed data, skip migrations')

    args = parser.parse_args()

    if args.force and args.seed_only:
        logger.error("--force and --seed-only cannot be used together")
        sys.exit(1)

    # Initialize setup
    setup = DatabaseSetup(DATABASE_URL)

    # Run setup
    success = setup.setup(force=args.force, seed_only=args.seed_only)

    if success:
        print("\n" + "="*50)
        print("🎉 DATABASE SETUP COMPLETED SUCCESSFULLY!")
        print("="*50)
        print("\nDatabase Details:")
        print(f"  Host: {setup.db_url.split('@')[1].split(':')[0]}")
        print(f"  Port: {setup.db_url.split(':')[-1].split('/')[0]}")
        print(f"  Database: {setup.db_name}")
        print(f"  User: nexus")
        print("\nAdmin Credentials:")
        print("  Email: admin@nexuslang.app")
        print("  Password: admin123!")
        print("\nDemo User Credentials:")
        print("  Email: user@nexuslang.app")
        print("  Password: user123!")
        print("\nNext Steps:")
        print("1. Start the backend server: python main.py")
        print("2. Start the frontend: npm run dev")
        print("3. Visit http://localhost:3000")
        print("="*50)
    else:
        print("\n" + "❌ DATABASE SETUP FAILED!")
        print("Check the logs above for error details.")
        sys.exit(1)


if __name__ == "__main__":
    main()
