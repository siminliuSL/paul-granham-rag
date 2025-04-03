import os
from openai import OpenAI
from dotenv import load_dotenv
from db import supabase
import traceback

# Load environment variables
load_dotenv()

# Initialize OpenAI client at module level
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print("OpenAI client initialized!")

def get_relevant_chunks(query: str, match_count: int = 3):
    try:

        ########Do embedding of query
        try:
            query_embedding = client.embeddings.create(
                model="text-embedding-ada-002",
                input=query
            )
        except Exception as e:
            print(f"Error getting embedding: {str(e)}")
            return None

        if query_embedding is None:
            print("Failed to generate query embedding")
            return [] 
        ###################

        # Prepare the query
        query_data = {
            'query_embedding': query_embedding.tolist(),
            'match_count': match_count
        }
            
        result = supabase.rpc('match_documents', query_data).execute()
        
        if not result.data:
            print("No matching chunks found")
            return []
            
        # Get document details for each chunk
        chunks_with_metadata = []
        for chunk in result.data:
            try:
                # Get document details
                doc_result = supabase.table('documents').select('*').eq('uuid', chunk['document_uuid']).execute()
                if doc_result.data:
                    doc = doc_result.data[0]
                    chunks_with_metadata.append({
                        'chunk': chunk['chunk'],
                        'similarity': chunk['similarity'],
                        'document_title': doc['title'],
                        'document_url': doc['url']
                    })
            except Exception as e:
                print(f"Error getting document details for chunk: {str(e)}")
                continue
                
        return chunks_with_metadata
        
    except Exception as e:
        print(f"Error in get_relevant_chunks: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return []

def chat_with_model(user_input: str):
    try:
        chunks = get_relevant_chunks(user_input)
        
        if not chunks:
            return "I couldn't find any relevant information in the database to help answer your question."
            
        context = []
        for chunk in chunks:
            try:
                context.append(f"From '{chunk['document_title']}' ({chunk['document_url']}):\n{chunk['chunk']}")
            except Exception as e:
                print(f"Error formatting chunk: {str(e)}")
                continue

        system_input = (
            """
            You're an AI assistant who answers questions based on Paul Graham's essays. You're a chat bot, so keep your replies succinct.
            You're only allowed to use the documents below to answer the question. f"\n\n{context_text}\n\n"
            If the question isn't related to these documents, say:  "Sorry, I couldn't find any information on that."
            If the information isn't available in the below documents, say: "Sorry, I couldn't find any information on that."   
            Do not go off topic.
           """
        )
        
        try:
            response = client.chat.completions.create(
                model="gpt-4-turbo-preview",
                messages=[
                    {"role": "system", "content": system_input},
                    {"role": "user", "content": user_input}
                ],
                temperature=0.7,
                max_tokens=500
            )
            return response.choices[0].message.content
        except Exception as e:
            return "Error occurred while generating response. Please try again."
            
    except Exception as e:
        print(f"Error in chat_with_model: {str(e)}")
        print(f"Traceback: {traceback.format_exc()}")
        return "Error occurred while processing your request. Please try again."

def main():
    print("You can start chatting (type 'quit' to exit)")
    
    while True:
        user_input = input("\nYou: ").strip()
        if user_input.lower() == 'quit':
            break
            
        print("\nAssistant: ", end='')
        response = chat_with_model(user_input)
        print(response)

if __name__ == "__main__":
    main() 