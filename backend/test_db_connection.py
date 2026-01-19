"""
Quick test script to diagnose database connection issues
"""
import os
import sys
import psycopg2
from urllib.parse import urlparse

# Fix encoding for Windows console
if sys.platform == 'win32':
    sys.stdout.reconfigure(encoding='utf-8')

def test_connection():
    database_url = os.getenv('DATABASE_URL')
    
    if not database_url:
        print("[ERROR] DATABASE_URL environment variable not set!")
        print("Please set it in your .env file or environment")
        return
    
    print(f"[TEST] Testing connection to: {database_url[:50]}...")
    
    try:
        # Parse the URL
        result = urlparse(database_url)
        print(f"   Host: {result.hostname}")
        print(f"   Port: {result.port or 5432}")
        print(f"   Database: {result.path[1:]}")
        print(f"   User: {result.username}")
        print()
        
        # Try to connect
        print("[TEST] Attempting connection...")
        conn = psycopg2.connect(database_url)
        print("[SUCCESS] Database connection established!")
        
        # Test a simple query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()
        print(f"[INFO] PostgreSQL version: {version[0][:50]}...")
        
        cursor.close()
        conn.close()
        print("\n[SUCCESS] All tests passed! Your database connection is working.")
        
    except psycopg2.OperationalError as e:
        print(f"[ERROR] CONNECTION FAILED!")
        print(f"   Error: {str(e)}")
        print()
        print("[SOLUTIONS] Possible fixes:")
        print("   1. Check if your Supabase project is paused (free tier)")
        print("   2. Verify your DATABASE_URL is correct")
        print("   3. Check if port 5432 is blocked by firewall")
        print("   4. Try connecting from Supabase dashboard to wake it up")
        
    except Exception as e:
        print(f"[ERROR] UNEXPECTED ERROR: {str(e)}")

if __name__ == "__main__":
    test_connection()
