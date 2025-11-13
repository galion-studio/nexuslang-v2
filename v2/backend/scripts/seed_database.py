#!/usr/bin/env python3
"""
Database Seeding Script
Creates initial data for development and testing.

Creates:
- Admin user (maci.grajczyk@gmail.com)
- Sample projects
- Knowledge base entries
- Test users
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from sqlalchemy.orm import Session
from core.database import SessionLocal, engine
from core.auth import hash_password
from models.user import User, Base
from models.project import Project
from datetime import datetime, timedelta


def create_tables():
    """Create all database tables."""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created")


def seed_admin_user(db: Session):
    """Create admin user."""
    print("Creating admin user...")
    
    # Check if admin already exists
    admin = db.query(User).filter(User.email == "maci.grajczyk@gmail.com").first()
    
    if admin:
        print("✅ Admin user already exists")
        return admin
    
    # Create admin user
    admin = User(
        email="maci.grajczyk@gmail.com",
        username="maciej",
        hashed_password=hash_password("Admin123!@#SecurePassword"),
        full_name="Maciej Grajczyk",
        is_admin=True,
        is_active=True,
        is_verified=True,
        subscription_tier="enterprise",
        subscription_status="active",
        subscription_start=datetime.utcnow(),
        subscription_end=datetime.utcnow() + timedelta(days=365),
        credits=1000000.0,  # 1M credits for admin
        created_at=datetime.utcnow()
    )
    
    db.add(admin)
    db.commit()
    db.refresh(admin)
    
    print(f"✅ Admin user created: {admin.email}")
    print(f"   Default password: Admin123!@#SecurePassword")
    print(f"   Please change this password after first login!")
    
    return admin


def seed_test_users(db: Session):
    """Create test users for development."""
    print("Creating test users...")
    
    test_users = [
        {
            "email": "test@example.com",
            "username": "testuser",
            "full_name": "Test User",
            "subscription_tier": "free"
        },
        {
            "email": "pro@example.com",
            "username": "prouser",
            "full_name": "Pro User",
            "subscription_tier": "professional",
            "credits": 5000.0
        }
    ]
    
    created_count = 0
    
    for user_data in test_users:
        # Check if user exists
        existing = db.query(User).filter(User.email == user_data["email"]).first()
        if existing:
            continue
        
        # Create user
        user = User(
            email=user_data["email"],
            username=user_data["username"],
            hashed_password=hash_password("Test123!@#Password"),
            full_name=user_data["full_name"],
            subscription_tier=user_data.get("subscription_tier", "free"),
            subscription_status="active",
            credits=user_data.get("credits", 100.0),
            is_active=True,
            is_verified=True,
            created_at=datetime.utcnow()
        )
        
        db.add(user)
        created_count += 1
    
    if created_count > 0:
        db.commit()
        print(f"✅ Created {created_count} test users")
    else:
        print("✅ Test users already exist")


def seed_sample_projects(db: Session):
    """Create sample projects."""
    print("Creating sample projects...")
    
    # Get admin user
    admin = db.query(User).filter(User.email == "maci.grajczyk@gmail.com").first()
    if not admin:
        print("⚠️  Admin user not found, skipping projects")
        return
    
    # Check if projects exist
    existing_projects = db.query(Project).filter(Project.user_id == admin.id).count()
    if existing_projects > 0:
        print("✅ Sample projects already exist")
        return
    
    # Sample projects
    projects = [
        {
            "name": "Hello NexusLang",
            "description": "A simple Hello World program in NexusLang",
            "language": "nexuslang",
            "code": '''# Hello World in NexusLang
print("Hello, NexusLang!")
print("The future of AI-native programming")
''',
            "status": "active",
            "visibility": "public"
        },
        {
            "name": "AI Chat Example",
            "description": "Example of using built-in AI chat capabilities",
            "language": "nexuslang",
            "code": '''# AI Chat Integration
response = ai.chat("What is quantum computing?")
print(response)

# Generate code
code = ai.generate_code("Create a fibonacci function")
print(code)
''',
            "status": "active",
            "visibility": "public"
        },
        {
            "name": "Data Analysis Demo",
            "description": "Data analysis with NexusLang",
            "language": "nexuslang",
            "code": '''# Data Analysis
data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

mean = sum(data) / len(data)
print(f"Mean: {mean}")

# AI-powered insights
insights = ai.analyze(data)
print(insights)
''',
            "status": "active",
            "visibility": "public"
        }
    ]
    
    for project_data in projects:
        project = Project(
            user_id=admin.id,
            name=project_data["name"],
            description=project_data["description"],
            language=project_data["language"],
            code=project_data["code"],
            status=project_data["status"],
            visibility=project_data["visibility"],
            created_at=datetime.utcnow()
        )
        db.add(project)
    
    db.commit()
    print(f"✅ Created {len(projects)} sample projects")


def main():
    """Main seeding function."""
    print("=" * 60)
    print("NexusLang v2 - Database Seeding")
    print("=" * 60)
    print()
    
    # Create session
    db = SessionLocal()
    
    try:
        # Create tables
        create_tables()
        print()
        
        # Seed data
        seed_admin_user(db)
        print()
        
        seed_test_users(db)
        print()
        
        seed_sample_projects(db)
        print()
        
        print("=" * 60)
        print("✅ Database seeding completed successfully!")
        print("=" * 60)
        print()
        print("Admin credentials:")
        print("  Email: maci.grajczyk@gmail.com")
        print("  Password: Admin123!@#SecurePassword")
        print()
        print("Test user credentials:")
        print("  Email: test@example.com")
        print("  Password: Test123!@#Password")
        print()
        
    except Exception as e:
        print(f"❌ Error during seeding: {e}")
        db.rollback()
        raise
    
    finally:
        db.close()


if __name__ == "__main__":
    main()

