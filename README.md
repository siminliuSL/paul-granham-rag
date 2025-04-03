# Paul Graham Essays RAG System

A lightweight RAG system for search and analysis of essays on https://www.paulgraham.com/articles.html



## Setup

1. Install dependencies:
pip install -r requirements.txt
```
2. Create .env file
     ```
     OPENAI_API_KEY=
     SUPABASE_KEY=
     SUPABASE_URL=
     DOCUMENT_URL=https://www.paulgraham.com/articles.html
     ```
4. Prepare the database:
```
Run the migraion scripts to create
Extension:
* pgvector
Tables:
* Documents
* Document_chunks
Function:
* Match_documents
```
5. Pre-load the documents
Run scrape.py
It will do the following:
* Get a list of html pages on https://www.paulgraham.com/articles.html
* Store info of each essay in Documents table
* Divide each essay into chunk
* Run embedding on each chunk
* Store content and embedding of each chunk in Document_chunks
