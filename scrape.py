import requests
from bs4 import BeautifulSoup
from db import store_document, get_document_by_uuid
import os
from dotenv import load_dotenv
from supabase import create_client
from gpt4all import Embed4All
import time
from datetime import datetime
from openai import OpenAI

load_dotenv()

BASE_URL = os.getenv("DOCUMENT_URL")

supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_KEY")
)

embedding_model = "text-embedding-ada-002"

def main():    
    try:
        response = requests.get(BASE_URL)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        
        essay_links = soup.find_all('a', href=lambda x: x and x.endswith('.html'))
        
        for link in essay_links:
            url = f"{BASE_URL}/{link['href']}"
            print(f"\nProcessing: {url}")
            
            #Find and store essays as documents 
            store_essays_as_documents(url)
            
            #Chunk and embed essays
            chunk_and_embed_essays(url)
            
            time.sleep(1)
            
    except Exception as e:
        print(f"Error in main: {str(e)}")

def store_essays_as_documents(url: str):
    try:
        essay_urls = find_essays(url)

        for essay_url in essay_urls:
            try:
                print(f"\nProcessing essay: {essay_url}")
                response = requests.get(essay_url)
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser')
                
                content = soup.find('font', {'size': '-1'})
                if not content:
                    content = soup.find('body')
                
                if content:
                    title = content.find('b')
                    title_text = title.text if title else essay_url.split('/')[-1].replace('.html', '')
                    
                    data = {
                        'title': title_text,
                        'url': essay_url,
                    }
                    
                    result = supabase.table('documents').insert(data).execute()
                    print(f"Successfully stored essay: {title_text}")
                    
                else:
                    print(f"Could not find content for essay: {essay_url}")
                    
            except Exception as e:
                print(f"Error processing essay {essay_url}: {e}")
                continue
                
        print("\nFinished processing all essays")
        
    except Exception as e:
        print(f"Error in process_essays: {e}")
        raise

def find_essays(url: str):
    try:
        response = requests.get(url)
        response.raise_for_status()    
        soup = BeautifulSoup(response.text, 'html.parser')

        links = soup.find_all('a')
        essay_links = []
        
        for link in links:
            href = link.get('href')
            if href and href.endswith('.html'):
                if href.startswith('/'):
                    href = f"https://www.paulgraham.com{href}"
                elif not href.startswith('http'):
                    href = f"https://www.paulgraham.com/{href}"
                essay_links.append(href)
        return essay_links
        
    except requests.RequestException as e:
        print(f"Error fetching page: {e}")
        raise
    except Exception as e:
        print(f"Error processing page: {e}")
        raise

def chunk_essay(text: str, chunk_size: int = 500, overlap: int = 50):
    if not text or len(text.strip()) == 0:
        return []
        
    chunks = []
    start = 0
    text = text.strip()
    text_len = len(text)
    
    while start < text_len:
        end = start + chunk_size
        
        if start > 0:
            start = start - overlap
            
        if end >= text_len:
            chunk = text[start:].strip()
            if chunk:
                chunks.append(chunk)
            break
            
        last_period = text.rfind('.', start, end)
        last_newline = text.rfind('\n', start, end)
        split_point = max(last_period, last_newline)
        
        if split_point == -1 or split_point <= start:
            split_point = end
        
        chunk = text[start:split_point].strip()
        if chunk:  
            chunks.append(chunk)
            
        start = split_point + 1  
        
    return chunks

def chunk_and_embed_essays(url: str):
    client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

    try:
        result = supabase.table('documents').select('*').execute()
        documents = result.data
        print(f"\nFound {len(documents)} documents to process")
        
        print("Initialized embedder")
        
        for i, doc in enumerate(documents, 1):
            doc_start_time = time.time()
            try:
                print(f"\nProcessing document {i}/{len(documents)}: {doc['url']}")
                response = requests.get(doc['url'])
                response.raise_for_status()
                soup = BeautifulSoup(response.text, 'html.parser') 
                
                content = soup.find('font', {'size': '-1'})
                if not content:
                    content = soup.find('body')
                
                if content:
                    content_text = content.get_text(separator='\n', strip=True)
                    if not content_text:
                        print(f"No content found for document: {doc['url']}")
                        continue
                        
                    chunks = chunk_essay(content_text)
                    if not chunks:
                        print(f"No chunks created for document: {doc['url']}")
                        continue
                        
                    print(f"Split into {len(chunks)} chunks")
                    
                    for chunk_idx, chunk in enumerate(chunks, 1):
                        try:
                            if not chunk or len(chunk.strip()) == 0:
                                print(f"Skipping empty chunk {chunk_idx}")
                                continue
                                
                            print(f"Creating embedding for chunk {chunk_idx}/{len(chunks)}")

                            try:
                                embedding_response = client.embeddings.create(
                                    model=embedding_model,
                                    input=chunk
                                )
                                embedding = embedding_response.data[0].embedding
                            except Exception as e:
                                print(f"Error getting embedding: {str(e)}")
                                continue
                            
                            chunk_data = {
                                'document_uuid': doc['uuid'],
                                'chunk': chunk,
                                'embedding': embedding
                            }
                            
                            try:
                                result = supabase.table("document_chunks").insert(chunk_data).execute()
                            except Exception as e:
                                print(f"Error storing chunk {chunk_idx} in database: {str(e)}")
                                continue
                            
                            time.sleep(0.1)
                            
                        except Exception as e:
                            print(f"Error processing chunk {chunk_idx}: {str(e)}")
                            continue
                    
                else:
                    print(f"Could not find content for document: {doc['url']}")
                    
            except Exception as e:
                print(f"Error processing document {doc['url']}: {str(e)}")
                continue
        
    except Exception as e:
        print(f"Error in chunk_and_embed_essays: {str(e)}")
    
if __name__ == "__main__":
    main()

   

