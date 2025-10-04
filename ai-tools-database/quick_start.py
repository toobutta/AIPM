#!/usr/bin/env python3
"""
Quick start script for AI Tools Database with Supabase
"""

import os
import sys
from pathlib import Path

def check_env_file():
    """Check if .env file exists and has required variables"""
    env_file = Path(".env")
    if not env_file.exists():
        print("❌ .env file not found. Creating one...")
        create_env_file()
        return False

    with open(env_file, 'r') as f:
        content = f.read()
        if "YOUR_PASSWORD" in content or "YOUR_PROJECT_REF" in content:
            print("❌ Please update your .env file with your Supabase credentials")
            print("   Get these from your Supabase project dashboard")
            return False

    print("✅ .env file found")
    return True

def create_env_file():
    """Create .env file with template"""
    env_content = '''# Supabase Database Configuration
DATABASE_URL=postgresql://postgres:YOUR_PASSWORD@YOUR_PROJECT_REF.supabase.co:5432/postgres

# Optional: Supabase Client (if you want to use Supabase features directly)
# SUPABASE_URL=https://YOUR_PROJECT_REF.supabase.co
# SUPABASE_ANON_KEY=YOUR_ANON_KEY

# API Configuration
API_HOST=0.0.0.0
API_PORT=8000
API_DEBUG=true

# Security
SECRET_KEY=your-secret-key-here-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# Logging
LOG_LEVEL=INFO
'''

    with open(".env", 'w') as f:
        f.write(env_content)

    print("📝 Created .env file. Please update it with your Supabase credentials")

def install_dependencies():
    """Install required dependencies"""
    print("📦 Installing dependencies...")
    os.system("pip install -r requirements.txt")
    print("✅ Dependencies installed")

def test_database_connection():
    """Test database connection"""
    print("🔍 Testing database connection...")
    try:
        from database import get_db
        from models import Provider

        db = next(get_db())
        providers = db.query(Provider).limit(1).all()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        print("   Make sure your Supabase database is set up and schema.sql was executed")
        return False

def setup_database():
    """Guide user through database setup"""
    print("\n🗄️  Database Setup Required")
    print("1. Go to your Supabase project dashboard")
    print("2. Click on 'SQL Editor' in the left sidebar")
    print("3. Copy the entire contents of schema.sql")
    print("4. Paste it into the SQL editor and click 'Run'")
    print("5. Once completed, run this script again")

    response = input("\nHave you set up the database? (y/n): ")
    return response.lower() == 'y'

def populate_examples():
    """Populate database with example tools"""
    print("📚 Populating database with example tools...")
    try:
        import requests

        response = requests.post("http://localhost:8000/api/populate-examples")
        if response.status_code == 200:
            print("✅ Example tools populated successfully")
        else:
            print(f"⚠️  Failed to populate examples: {response.text}")
    except Exception as e:
        print(f"⚠️  Could not populate examples: {e}")

def start_api():
    """Start the API server"""
    print("\n🚀 Starting AI Tools Database API...")
    print("   API will be available at: http://localhost:8000")
    print("   API docs at: http://localhost:8000/docs")
    print("   Press Ctrl+C to stop the server")
    print()

    os.system("uvicorn main:app --reload")

def main():
    """Main setup flow"""
    print("🎯 AI Tools Database - Supabase Setup")
    print("=" * 50)

    # Check environment
    if not check_env_file():
        print("\nPlease update your .env file and run this script again")
        sys.exit(1)

    # Install dependencies
    install_dependencies()

    # Check if database is set up
    if not test_database_connection():
        if not setup_database():
            print("Database setup cancelled. Please run this script again after setting up the database.")
            sys.exit(1)

        # Test connection again
        if not test_database_connection():
            print("Database connection still failing. Please check your credentials.")
            sys.exit(1)

    # Everything is ready, start the API
    populate_examples()
    start_api()

if __name__ == "__main__":
    main()