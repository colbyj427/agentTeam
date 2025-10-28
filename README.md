# Agent Team - Multi-Agent Coding Environment

A messaging-based AI system where you manage a virtual dev team of coding agents — each with its own role, tools, and personality. Agents can collaborate, critique, and push code through Git.

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- OpenAI API key
- Supabase account

### 1. Database Setup (Supabase)

1. Create a new Supabase project at [supabase.com](https://supabase.com)
2. Copy your project URL and API keys
3. Run the SQL migration in `backend/db/migrations/001_initial_schema.sql` in your Supabase SQL editor

### 2. Backend Setup

```bash
cd backend
pip install -r requirements.txt
cp env.example .env
# Edit .env with your API keys
```

Configure your `.env` file:
```
OPENAI_API_KEY=your_openai_api_key_here
SUPABASE_URL=your_supabase_project_url
SUPABASE_ANON_KEY=your_supabase_anon_key
SUPABASE_SERVICE_KEY=your_supabase_service_role_key
WORKSPACE_PATH=./workspace
```

Start the backend:
```bash
python main.py
```

### 3. Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

The frontend will be available at `http://localhost:3000`

## 🧩 Architecture

### Backend (Python + FastAPI)
- **REST API** for message handling
- **Supabase** for message persistence
- **OpenAI GPT-4** for agent responses
- **File tools** for safe workspace operations

### Frontend (React + TypeScript + Vite)
- **Real-time messaging** interface
- **Agent selection** and status
- **Message history** from database
- **Modern chat UI** with Tailwind CSS

### Developer Agent
- Responds to coding prompts
- Can read/write files in workspace
- Uses OpenAI for intelligent responses
- Logs all actions to database

## 📁 Project Structure

```
agent-team/
├── backend/
│   ├── main.py                    # FastAPI app
│   ├── requirements.txt           # Python dependencies
│   ├── agents/
│   │   ├── base_agent.py         # Abstract agent class
│   │   └── developer_agent.py    # Developer agent
│   ├── db/
│   │   ├── supabase_client.py    # Database client
│   │   └── migrations/
│   │       └── 001_initial_schema.sql
│   └── tools/
│       └── file_tools.py         # File operations
├── frontend/
│   ├── src/
│   │   ├── components/           # React components
│   │   ├── services/             # API services
│   │   └── types/                # TypeScript types
│   └── package.json
└── workspace/                    # Agent workspace
```

## 🎯 Week 1 Features

- ✅ **Messaging Interface** - Chat with AI agents
- ✅ **Developer Agent** - Coding assistance with file tools
- ✅ **Message Persistence** - All conversations saved to Supabase
- ✅ **File Operations** - Safe read/write in workspace
- ✅ **Real-time UI** - Modern chat interface
- ✅ **Agent Selection** - Choose which agent to talk to

## 🔧 API Endpoints

- `GET /api/agents` - List available agents
- `GET /api/messages` - Get message history
- `POST /api/messages` - Send message to agent
- `GET /api/projects` - Get project information

## 🛠️ Development

### Backend Development
```bash
cd backend
python main.py  # Starts on localhost:8000
```

### Frontend Development
```bash
cd frontend
npm run dev     # Starts on localhost:3000
```

### Testing the System
1. Start both backend and frontend
2. Open `http://localhost:3000`
3. Send a message like "Create a hello.py file with a simple function"
4. Watch the Developer Agent respond and create files!

## 📋 Next Steps (Week 2+)

- Add more agent types (Critic, Manager, RAG)
- Implement GitHub integration
- Add tool confirmation flows
- Enhance file operation safety
- Add agent-to-agent communication

## 🐛 Troubleshooting

### Common Issues

1. **Backend won't start**: Check your `.env` file has all required keys
2. **Frontend can't connect**: Ensure backend is running on port 8000
3. **Database errors**: Verify Supabase credentials and run migrations
4. **Agent not responding**: Check OpenAI API key and quota

### Logs
- Backend logs: Check terminal where you ran `python main.py`
- Frontend logs: Check browser console (F12)
- Database logs: Check Supabase dashboard

## 📚 Documentation

- [Agent Team Architecture](docs/agentTeam.md)
- [Database Schema](docs/databases.md)
- [6-Week Roadmap](goals.md)
