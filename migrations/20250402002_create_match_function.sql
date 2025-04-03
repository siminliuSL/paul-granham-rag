-- Create a function to match documents based on embedding similarity
create or replace function match_documents(
    query_embedding vector(384),
    match_count int default 3
)
returns table (
    uuid uuid,
    document_uuid uuid,
    chunk text,
    similarity float
)
language plpgsql
as $$
begin
    return query
    select
        document_chunks.uuid,
        document_chunks.document_uuid,
        document_chunks.chunk,
        1 - (document_chunks.embedding <=> query_embedding) as similarity
    from document_chunks
    order by document_chunks.embedding <=> query_embedding
    limit match_count;
end;
$$; 