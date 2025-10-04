#!/usr/bin/env python3
"""
Test various connection methods to Supabase
"""

import os
import sys
from pathlib import Path

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

from config import settings
from supabase import create_client
import psycopg2

def test_psycopg2_connection():
    """Test direct psycopg2 connection"""
    print("Testing psycopg2 connection...")
    try:
        conn = psycopg2.connect(settings.database_url)
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        result = cursor.fetchone()
        print(f"✅ psycopg2 connection successful: {result}")
        conn.close()
        return True
    except Exception as e:
        print(f"❌ psycopg2 connection failed: {e}")
        return False

def test_supabase_client():
    """Test Supabase Python client"""
    print("Testing Supabase client...")
    try:
        client = create_client(settings.supabase_url, settings.supabase_anon_key)
        # Try to list tables
        response = client.table('providers').select('id').limit(1).execute()
        print(f"✅ Supabase client connection successful")
        return True
    except Exception as e:
        print(f"❌ Supabase client connection failed: {e}")
        return False

def test_sqlalchemy_engine():
    """Test SQLAlchemy engine connection"""
    print("Testing SQLAlchemy engine...")
    try:
        from sqlalchemy import create_engine
        engine = create_engine(settings.database_url, connect_args={"connect_timeout": 10})
        with engine.connect() as conn:
            result = conn.execute("SELECT 1")
            print(f"✅ SQLAlchemy connection successful: {result.fetchone()}")
        return True
    except Exception as e:
        print(f"❌ SQLAlchemy connection failed: {e}")
        return False

def main():
    print("Supabase Connection Test")
    print("=" * 40)
    print(f"Database URL: {settings.database_url}")
    print(f"Supabase URL: {settings.supabase_url}")
    print()

    tests = [
        test_psycopg2_connection,
        test_supabase_client,
        test_sqlalchemy_engine
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"❌ {test.__name__} crashed: {e}")
            results.append(False)
        print()

    print("Summary:")
    print(f"Successful connections: {sum(results)}/{len(results)}")

    if all(results):
        print("🎉 All connection methods work!")
    else:
        print("⚠️  Some connection methods failed")

if __name__ == "__main__":
    main()