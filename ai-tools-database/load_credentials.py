#!/usr/bin/env python3
"""
Load Supabase credentials from .env.local and configure the project
"""

import os
import sys
from pathlib import Path

def load_env_local():
    """Load credentials from .env.local file"""
    env_local_path = Path.home() / ".env.local"

    if not env_local_path.exists():
        print("❌ .env.local file not found in home directory")
        return False

    print("📁 Loading credentials from .env.local...")

    with open(env_local_path, 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#') and '=' in line:
                key, value = line.split('=', 1)
                os.environ[key] = value
                print(f"   ✅ Loaded {key}")

    return True

def update_project_env():
    """Update the project .env file with proper database URL"""
    supabase_url = os.getenv('SUPABASE_URL')
    supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')

    if not supabase_url or not supabase_anon_key:
        print("❌ Missing required credentials in .env.local")
        return False

    # Extract project ref from URL
    project_ref = supabase_url.replace('https://', '').replace('.supabase.co', '')

    print(f"\n🔧 Project details:")
    print(f"   Project URL: {supabase_url}")
    print(f"   Project Ref: {project_ref}")

    # Create the database URL
    database_url = f"postgresql://postgres.{project_ref}:YOUR_PASSWORD@{project_ref}.supabase.co:5432/postgres"

    print(f"\n📝 To complete setup:")
    print(f"   1. Go to your Supabase project dashboard")
    print(f"   2. Go to Settings → Database")
    print(f"   3. Find your database password")
    print(f"   4. Update your DATABASE_URL in .env:")
    print(f"      DATABASE_URL=postgresql://postgres.{project_ref}:ACTUAL_PASSWORD@{project_ref}.supabase.co:5432/postgres")

    return True

def test_supabase_connection():
    """Test Supabase connection with current credentials"""
    try:
        from supabase import create_client

        supabase_url = os.getenv('SUPABASE_URL')
        supabase_anon_key = os.getenv('SUPABASE_ANON_KEY')

        if not supabase_url or not supabase_anon_key:
            print("❌ Missing Supabase credentials")
            return False

        print("\n🔍 Testing Supabase connection...")
        client = create_client(supabase_url, supabase_anon_key)

        # Test connection by trying to get project info
        response = client.table('_test_connection').select('*').limit(1).execute()

    except Exception as e:
        # Expected to fail since we haven't set up the database yet
        if "does not exist" in str(e) or "relation" in str(e).lower():
            print("✅ Supabase connection successful (database not set up yet, which is expected)")
            return True
        else:
            print(f"❌ Supabase connection failed: {e}")
            return False

def main():
    """Main setup process"""
    print("🚀 AI Tools Database - Credential Setup")
    print("=" * 50)

    # Load credentials from .env.local
    if not load_env_local():
        sys.exit(1)

    # Test Supabase connection
    test_supabase_connection()

    # Provide setup instructions
    update_project_env()

    print(f"\n📋 Next Steps:")
    print(f"   1. Get your database password from Supabase dashboard")
    print(f"   2. Update DATABASE_URL in .env file")
    print(f"   3. Run schema setup in Supabase SQL Editor")
    print(f"   4. Start the API server")

if __name__ == "__main__":
    main()