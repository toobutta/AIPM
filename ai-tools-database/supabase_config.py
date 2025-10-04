"""
Supabase-specific configuration and utilities
"""

import os
from supabase import create_client, Client
from typing import Optional
from config import settings

class SupabaseClient:
    """Supabase client wrapper"""

    def __init__(self):
        self.supabase_url = self._extract_supabase_url()
        self.supabase_key = os.getenv("SUPABASE_ANON_KEY")
        self.client: Optional[Client] = None

    def _extract_supabase_url(self) -> str:
        """Extract Supabase URL from database URL"""
        database_url = settings.database_url
        # Extract URL from postgresql://...@project-ref.supabase.co:5432/postgres
        if "supabase.co" in database_url:
            # Get the project ref from the database URL
            parts = database_url.split("@")
            if len(parts) > 1:
                project_part = parts[1].split(":")[0]
                return f"https://{project_part}"
        return ""

    def get_client(self) -> Client:
        """Get Supabase client"""
        if not self.client:
            if not self.supabase_url:
                raise ValueError("Supabase URL not found in database URL")
            if not self.supabase_key:
                raise ValueError("SUPABASE_ANON_KEY environment variable not set")

            self.client = create_client(self.supabase_url, self.supabase_key)
        return self.client

    def test_connection(self) -> bool:
        """Test Supabase connection"""
        try:
            client = self.get_client()
            # Test by trying to query providers table
            result = client.table('providers').select('count').execute()
            return True
        except Exception as e:
            print(f"Supabase connection error: {e}")
            return False

# Global instance
supabase_client = SupabaseClient()

# Alternative direct database functions for Supabase
def setup_supabase_direct():
    """
    Instructions for direct Supabase setup without SQLAlchemy
    """
    print("""
    To use Supabase directly with our API, you have two options:

    OPTION 1: Keep SQLAlchemy (Recommended)
    - Use the provided DATABASE_URL in .env
    - SQLAlchemy will work with Supabase PostgreSQL
    - No code changes needed

    OPTION 2: Use Supabase Python Client
    - Set SUPABASE_URL and SUPABASE_ANON_KEY in .env
    - Replace SQLAlchemy calls with Supabase client calls
    - More work but gives you Supabase-specific features

    For now, OPTION 1 is configured and ready to use!
    Just update your .env file with the correct DATABASE_URL.
    """)

if __name__ == "__main__":
    setup_supabase_direct()

    # Test connection if environment variables are set
    if os.getenv("SUPABASE_ANON_KEY"):
        if supabase_client.test_connection():
            print("✅ Supabase connection successful!")
        else:
            print("❌ Supabase connection failed!")
    else:
        print("ℹ️  Set SUPABASE_ANON_KEY to test Supabase connection")