# Supabase Schema and Setup for Multi-Agent Coding Team

This document defines the Supabase database schema and data design for your Multi-Agent Coding Team project.

It is designed to store:

- Messaging history
- Agent configurations
- Project metadata
- Agent memory summaries
- Tool usage logs
- RAG document metadata (paired with ChromaDB for embeddings)

## Overview

You will use:

- **Supabase (PostgreSQL)** for structured and relational data.
- **ChromaDB** for vector embeddings and semantic retrieval.

Supabase acts as the system-of-record for your project, maintaining state, user data, and project logs.  
ChromaDB acts as the context provider, storing document chunks and embeddings that the RAG Agent queries.

## Table Schema

### 1. messages

Stores all chat and message exchanges between agents and the user.

| Column      | Type         | Description                                      |
|-------------|--------------|--------------------------------------------------|
| id          | uuid (PK)    | Unique message ID                                |
| thread_id   | uuid         | Thread or sprint ID                              |
| sender      | text         | Agent name or user                               |
| recipient   | text         | Target agent or system                           |
| content     | text         | Message body                                     |
| role        | text         | One of: user, assistant, manager, critic, rag    |
| metadata    | jsonb        | Optional (e.g. related PR ID, document references)|
| created_at  | timestamp    | Auto timestamp                                   |

**Indexes:**

```sql
CREATE INDEX ON messages (thread_id);
CREATE INDEX ON messages (created_at DESC);
```

---

### 2. agents

Configuration and profile data for each agent in the system.

| Column      | Type         | Description                                  |
|-------------|--------------|----------------------------------------------|
| id          | uuid (PK)    | Unique agent ID                              |
| name        | text         | e.g., "Developer", "Critic", "Manager", "RAG"|
| role        | text         | Role label                                   |
| description | text         | Prompt or system context                     |
| tools       | jsonb        | List of available tools (e.g., ["git", "file_write", "rag_search"])|
| memory_id   | uuid         | FK to memory_summaries                       |
| created_at  | timestamp    | Auto timestamp                               |
| updated_at  | timestamp    | Auto timestamp                               |

---

### 3. projects

Tracks repository and workspace configurations.

| Column      | Type         | Description                          |
|-------------|--------------|--------------------------------------|
| id          | uuid (PK)    | Project ID                           |
| name        | text         | Project name                         |
| repo_url    | text         | GitHub or GitLab repo                |
| branch      | text         | Active branch name                   |
| settings    | jsonb        | Configurations (e.g., allowed tools, file paths)|
| created_at  | timestamp    | Auto timestamp                       |
| updated_at  | timestamp    | Auto timestamp                       |

---

### 4. memory_summaries

Stores summarized memory or knowledge of each agent/project.

| Column        | Type         | Description                                      |
|---------------|--------------|--------------------------------------------------|
| id            | uuid (PK)    | Memory record ID                                 |
| agent_id      | uuid         | FK to agents                                     |
| project_id    | uuid         | FK to projects                                   |
| summary       | text         | Text summary of previous context or tasks        |
| embedding_ref | text         | Reference ID in ChromaDB (if linked)             |
| created_at    | timestamp    | Auto timestamp                                   |

---

### 5. actions

Logs all tool usage and execution events by agents.

| Column      | Type         | Description                                         |
|-------------|--------------|-----------------------------------------------------|
| id          | uuid (PK)    | Action ID                                           |
| agent_id    | uuid         | FK to agents                                        |
| tool_name   | text         | Tool used (e.g., "git_push", "file_write")          |
| input       | jsonb        | Input parameters                                    |
| output      | jsonb        | Tool result                                         |
| status      | text         | success, error, pending                             |
| created_at  | timestamp    | Auto timestamp                                      |

---

### 6. rag_documents

Metadata about RAG documents (the text chunks themselves live in ChromaDB).

| Column        | Type         | Description                                         |
|---------------|--------------|-----------------------------------------------------|
| id            | uuid (PK)    | Document ID                                         |
| project_id    | uuid         | FK to projects                                      |
| file_path     | text         | Source file path                                    |
| title         | text         | Optional human-readable title                       |
| metadata      | jsonb        | Any extra metadata (e.g., tags, code section)       |
| embedding_ref | text         | Corresponding ID in ChromaDB                        |
| last_updated  | timestamp    | Auto timestamp                                      |

---

## Relationships

```
projects ───< rag_documents
   │
   ├──< messages
   │
   ├──< memory_summaries
   │
   └──< actions
        │
        └──< agents
```

---

## Recommended Indexes

```sql
CREATE INDEX idx_messages_thread ON messages(thread_id);
CREATE INDEX idx_actions_agent ON actions(agent_id);
CREATE INDEX idx_rag_project ON rag_documents(project_id);
CREATE INDEX idx_memory_agent ON memory_summaries(agent_id);
```

---

## Integration Notes

### With ChromaDB

- Use the `embedding_ref` field in both `rag_documents` and `memory_summaries` to connect Supabase records to embeddings in ChromaDB.
- When updating a document or memory:
  1. Update Supabase row.
  2. Upsert embedding in ChromaDB using the same `embedding_ref`.

### With Agents

- Each agent can have a persistent `agent_id` used to log messages, actions, and memory updates.
- The Manager Agent can query Supabase for:
  - Current project info
  - Unresolved threads
  - Previous sprint summaries

### With RAG Agent

- The RAG Agent queries ChromaDB by text similarity.
- It records each retrieved document’s `embedding_ref` and metadata back into `rag_documents`.

---

## Setup Notes

1. Create a new Supabase project.
2. Run SQL migrations (the table definitions above).
3. Enable Row Level Security (RLS) if deploying publicly.
4. Set up a service role key for your backend to handle writes.
5. (Optional) Use Supabase Storage for binary artifacts (file snapshots or images).

---

## Summary

| Data Type         | Storage                | Notes                       |
|-------------------|-----------------------|-----------------------------|
| Messages          | Supabase              | Chat and coordination logs  |
| Agents            | Supabase              | Role, tools, permissions    |
| Projects          | Supabase              | Repo and configuration data |
| Memory Summaries  | Supabase + ChromaDB   | Long-term recall            |
| Tool Actions      | Supabase              | Execution history           |
| RAG Documents     | Supabase + ChromaDB   | Metadata + embeddings       |

