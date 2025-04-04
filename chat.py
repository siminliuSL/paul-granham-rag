import os
from openai import OpenAI
from dotenv import load_dotenv
from supabase import create_client

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
print("OpenAI client initialized now!")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)


def get_relevant_chunks(query: str, match_count: int = 3):
    try:
        ########Do embedding of query
        try:
            print("Start query embedding")
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
            'query_embedding': query_embedding.data[0].embedding,
            'match_count': match_count
        }

        print("Start matching documents")
            
        result = supabase.rpc('match_documents', query_data).execute()
        
        if not result.data:
            print("No matching chunks found")
            return []
        print(result.data)
        # Get document details for each chunk
        chunks_with_metadata = []
        for chunk in result.data:
            try:
                # Get document details
                doc_result = supabase.table('documents').select('*').eq('uuid', chunk['document_id']).execute()
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
        return []

def chat_with_model(user_input: str):
    try:
        chunks = get_relevant_chunks(user_input,3)
        context = []

        for chunk in chunks:
            try:
                context.append(f"From '{chunk['document_title']}' ({chunk['document_url']}):\n{chunk['chunk']}")
            except Exception as e:
                print(f"Error formatting chunk: {str(e)}")
                continue

        context_text = "\n\n".join(context)
        print(context_text)
        system_input = (
            """
            You're an AI assistant who answers questions.
            You're only allowed to use the documents below to answer the question:
            {context_text}
            Your responses must follow these rules:

            1. RESPONSE STRUCTURE:
               - Keep responses concise and focused
               - Start with the most relevant citation
               - Start each statement with the reference number in square brackets. Example: "[1]To be a good founder, you need..."
               - Add a new line and start with "References" in bold.
               - List each reference in a new line. Startwith a number in square brackets, followed by title and URL.
               - Example: 
                 References:

                    [1] “Founder Mode”
                    [2] “The Right Kind of Stubborn”
                    [3] “What We Look for in Founders”

            2. If the question isn't related to these documents, say:  "Sorry, I couldn't find any information on that."
            3. If the information isn't available in the below documents, say: "Sorry, I couldn't find any information on that."   
            4. Do not go off topic.
           """
        ).format(context_text=context_text)
        
        try:
            print("Sending request to OpenAI for chat completion...")
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
        return "Error occurred while processing your request. Please try again."
