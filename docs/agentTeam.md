# 🤖 Agent Team — Multi-Agent Coding Environment

## 🧭 Overview

**Agent Team** is a local, multi-agent development environment designed to simulate a coordinated software engineering team powered by AI.  
Each agent operates as an independent service with defined roles, tools, and communication channels. Together, they collaborate to complete coding tasks, review each other’s work, manage Git operations, and access project documentation via a shared RAG (Retrieval-Augmented Generation) system.

---

## ⚙️ Tech Stack

### **Backend**
- **Language:** Python  
- **Framework:** FastAPI (for REST and WebSocket communication)
- **Databases:**
  - **Supabase (PostgreSQL):** Persistent state, message history, configuration, memory summaries
  - **ChromaDB:** Vector database for RAG embeddings and semantic recall
- **AI Providers:**
  - **OpenAI API (GPT-4/5)** for code generation, reasoning, and communication
  - **Anthropic Claude** for advanced reasoning and text synthesis (optional hybrid)
- **Version Control:**
  - **GitHub API** integration for:
    - Branch management
    - Commit creation
    - Pull request automation
- **Auth & Config:** Supabase Auth (optional), environment-based configuration

---

### **Frontend**
- **Language:** TypeScript  
- **Framework:** React (with Vite or Next.js, local dev)
- **UI Purpose:**
  - View and manage agents (status, active tasks)
  - Display message threads and task progress
  - Visualize file diffs, code suggestions, and PRs
  - Monitor interactions between agents and the RAG system

---

## 🧩 Agent Architecture

### **Agent Model**
Each agent is an independent service (or lightweight process) with:
- A specific **role** (e.g., frontend developer, backend developer, critic, tester)
- Access to relevant **tools** and **APIs**
- Shared communication layer to interact with other agents

Agents communicate asynchronously through a **message bus** or **Supabase event channel**, with their conversations stored in the database for traceability.

---

### **Agent Roles (Initial Set)**
| Agent | Description | Key Tools |
|--------|--------------|-----------|
| **Frontend Developer** | Handles UI design, TypeScript logic, and component structure. | GitHub, RAG, Critic |
| **Backend Developer** | Builds FastAPI endpoints, manages data flow, integrates external APIs. | GitHub, RAG, Critic |
| **Critic Agent** | Reviews code diffs, checks correctness, style, and consistency. | GitHub, RAG |
| **RAG Agent** | Provides documentation access via ChromaDB, returns context snippets. | ChromaDB, Supabase |
<!-- | **Manager Agent** | Oversees progress, assigns subtasks, and coordinates merges. | All agents, GitHub | -->

---

## 🧠 Shared RAG Tool

All agents share access to a **RAG (Retrieval-Augmented Generation)** interface:
- Stores project documentation, API references, and past messages in ChromaDB.
- Returns semantically relevant chunks when agents need technical clarification or project context.
- Periodically syncs with Supabase and local repo to refresh data.

---

## 💬 Communication Flow

1. **User Initiation:** You (the human manager) issue a task via the UI or CLI.
2. **Manager Agent:** Breaks it into subtasks and delegates them to specialized agents.
3. **Developer Agents:** Collaborate via structured messages, request context from RAG Agent.
4. **Critic Agent:** Reviews results and suggests fixes or improvements.
5. **Manager Agent:** Approves and pushes to GitHub via the integration layer.

All exchanges are logged in Supabase for persistence and visibility.

---

## 🧱 Core Features

- **Multi-Agent Coordination** — Specialized agents working together on software tasks.  
- **RAG-Enhanced Context** — Agents retrieve documentation and codebase info via embeddings.  
- **GitHub Automation** — Agents push commits, open PRs, and manage branches autonomously.  
- **Critic Feedback Loop** — Automatic code review and validation pipeline.  
- **Persistent Memory** — Supabase stores conversation history, summaries, and state.  
- **Local Development** — Fully local for initial phase, scalable to cloud later.

---

## 🚀 Planned Milestones

| Milestone | Description |
|------------|-------------|
| **M1 — Local Infrastructure** | Setup Supabase, ChromaDB, FastAPI backend, and agent base classes. |
| **M2 — Agent Communication** | Enable messaging between agents via Supabase or WebSocket layer. |
| **M3 — RAG Integration** | Add ChromaDB pipeline for doc embedding and retrieval. |
| **M4 — GitHub Tooling** | Implement repo cloning, commit, and PR tools. |
| **M5 — Critic & Manager Agents** | Add automated review and coordination logic. |
| **M6 — Frontend Dashboard** | Build React UI for managing agents and viewing logs. |

---

## 🔒 Long-Term Vision

- Support **custom agent creation** with new tools or personality profiles.
- Extend RAG system to support **dynamic memory compression** for long-term learning.
- Introduce **evaluation metrics** for agent performance and team collaboration quality.
- Scale to cloud orchestration (Docker Compose → Kubernetes) for parallel agent workflows.

---

## 📁 Repository Structure (Planned)

```
agent-team/
├── backend/
│   ├── main.py
│   ├── agents/
│   │   ├── base_agent.py
│   │   ├── frontend_agent.py
│   │   ├── backend_agent.py
│   │   ├── critic_agent.py
│   │   ├── manager_agent.py
│   │   └── rag_agent.py
│   ├── db/
│   │   ├── supabase_client.py
│   │   └── chroma_client.py
│   └── tools/
│       ├── github_tools.py
│       ├── rag_tools.py
│       └── critic_tools.py
├── frontend/
│   ├── src/
│   └── package.json
├── docs/
│   ├── agentTeam.md
│   └── databases.md
└── README.md
```

---

## 🧩 Notes

- Designed to evolve from **local experimentation** → **modular micro-agent platform**.  
- Each agent can be independently extended or replaced.  
- RAG pipeline will be central for contextual reasoning and code grounding.
