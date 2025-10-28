-- Initial schema for Agent Team Multi-Agent Coding Environment
-- Based on databases.md specification

-- 1. messages table - stores all chat and message exchanges
CREATE TABLE messages (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id UUID,
    sender TEXT NOT NULL,
    recipient TEXT NOT NULL,
    content TEXT NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'assistant', 'manager', 'critic', 'rag')),
    metadata JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 2. agents table - configuration and profile data for each agent
CREATE TABLE agents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    role TEXT NOT NULL,
    description TEXT,
    tools JSONB,
    memory_id UUID,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. projects table - tracks repository and workspace configurations
CREATE TABLE projects (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    name TEXT NOT NULL,
    repo_url TEXT,
    branch TEXT DEFAULT 'main',
    settings JSONB,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. memory_summaries table - stores summarized memory or knowledge
CREATE TABLE memory_summaries (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    summary TEXT NOT NULL,
    embedding_ref TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. actions table - logs all tool usage and execution events
CREATE TABLE actions (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    agent_id UUID REFERENCES agents(id) ON DELETE CASCADE,
    tool_name TEXT NOT NULL,
    input JSONB,
    output JSONB,
    status TEXT NOT NULL CHECK (status IN ('success', 'error', 'pending')),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 6. rag_documents table - metadata about RAG documents
CREATE TABLE rag_documents (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    project_id UUID REFERENCES projects(id) ON DELETE CASCADE,
    file_path TEXT NOT NULL,
    title TEXT,
    metadata JSONB,
    embedding_ref TEXT,
    last_updated TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for performance
CREATE INDEX idx_messages_thread ON messages(thread_id);
CREATE INDEX idx_messages_created_at ON messages(created_at DESC);
CREATE INDEX idx_actions_agent ON actions(agent_id);
CREATE INDEX idx_rag_project ON rag_documents(project_id);
CREATE INDEX idx_memory_agent ON memory_summaries(agent_id);

-- Insert initial Developer Agent
INSERT INTO agents (name, role, description, tools) VALUES 
('Developer', 'developer', 'A coding agent that can write, read, and modify files. Specializes in software development tasks.', 
 '["read_file", "write_file", "list_directory"]'::jsonb);

-- Insert default project
INSERT INTO projects (name, repo_url, branch, settings) VALUES 
('Agent Team Workspace', null, 'main', '{"workspace_path": "./workspace", "allowed_tools": ["read_file", "write_file", "list_directory"]}'::jsonb);
