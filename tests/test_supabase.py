from db import supabase
import sys

def test_connection():
    try:
        # Try to query the essays table
        result = supabase.table("essays").select("count").execute()
        print("✅ Successfully connected to Supabase!")
        print(f"Number of essays in database: {result.data[0]['count'] if result.data else 0}")
        return True
    except Exception as e:
        print("❌ Failed to connect to Supabase:")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    success = test_connection()
    sys.exit(0 if success else 1) 