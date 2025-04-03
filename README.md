# Paul Graham Essays RAG System

A lightweight RAG system for search and analysis of essays on https://www.paulgraham.com/articles.html
It provides an API for chat  

## Setup

1. Install dependencies:
pip install -r requirements.txt

2. Create .env file
   
     OPENAI_API_KEY=
     SUPABASE_KEY=
     SUPABASE_URL=
     DOCUMENT_URL=https://www.paulgraham.com/articles.html
     
3. Run the migraion scripts to create
Extension:
* pgvector
Tables:
* Documents
* Document_chunks
Function:
* Match_documents
  
4. Pre-load the documents
Run scrape.py
It will do the following:
* Get a list of html pages on https://www.paulgraham.com/articles.html
* Store info of each essay in Documents table
* Divide each essay into chunk
* Run embedding on each chunk
* Store content and embedding of each chunk in Document_chunks

## TODO
* Compare embedding models. Try smaller dimensions.
* Create trigger(s) for scraping. It can either be a schedule, or a "refresh" request from UI.
* Improve performance when chunking and Embedding

