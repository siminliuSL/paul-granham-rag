import os
from dotenv import load_dotenv
from supabase import create_client, Client

def test_db_connection():
    # Load environment variables
    load_dotenv()
    
    # Get Supabase credentials
    supabase_url = os.getenv("SUPABASE_URL")
    supabase_key = os.getenv("SUPABASE_KEY")
    
    print(f"Testing connection to Supabase at: {supabase_url}")
    
    try:
        # Initialize Supabase client
        supabase: Client = create_client(supabase_url, supabase_key)
        
        # Try to query a simple table
        result = supabase.table('documents').select('count').limit(1).execute()
        
        if result.data is not None:
            print("✅ Database connection successful!")
            print(f"Found {len(result.data)} documents")
            return True
        else:
            print("❌ Database connection failed: No data returned")
            return False
            
    except Exception as e:
        print(f"❌ Database connection failed: {str(e)}")
        return False

if __name__ == "__main__":
    test_db_connection() 