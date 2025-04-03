from db import supabase

def test_connection():
    try:
        # Try to query the documents table
        result = supabase.table("documents").select("count").execute()
        print("✅ Successfully connected to documents table!")
        print(f"Number of documents: {result.data[0]['count'] if result.data else 0}")
        
        # Try to query the document_chunks table
        result = supabase.table("document_chunks").select("count").execute()
        print("✅ Successfully connected to document_chunks table!")
        print(f"Number of chunks: {result.data[0]['count'] if result.data else 0}")
        
        return True
    except Exception as e:
        print("❌ Failed to connect to Supabase tables:")
        print(f"Error: {str(e)}")
        return False

if __name__ == "__main__":
    test_connection() 