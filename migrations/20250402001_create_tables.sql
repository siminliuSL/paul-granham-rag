create table public.documents (
  uuid DEFAULT uuid_generate_v4 ()
  created_at timestamp with time zone not null default now(),
  title text null,
  url text null,
  constraint Documents_pkey primary key (id)
) TABLESPACE pg_default;

create table public.document_chunks (
  uuid DEFAULT uuid_generate_v4 ()  
  document_uuid integer null,
  embedding public.vector null,
  chunk text not null,
  constraint document_chunks_pkey primary key (uuid),
  constraint document_chunks_document_udid_fkey foreign KEY (document_uuid) references documents (uuid) on delete CASCADE
) TABLESPACE pg_default;