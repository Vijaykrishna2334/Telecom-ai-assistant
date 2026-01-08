# Telecom AI Assistant

**Intelligent Telecommunication Support Bot with Voice AI**

A complete, production-ready AI application that automates customer interactions for telecom service providers using open-source LLMs, RAG, and real-time voice processing.

[![FastAPI](https://img.shields.io/badge/FastAPI-0.109.0-009688.svg?style=flat&logo=FastAPI&logoColor=white)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-18.2.0-61DAFB.svg?style=flat&logo=React&logoColor=black)](https://reactjs.org)
[![Python](https://img.shields.io/badge/Python-3.11-3776AB.svg?style=flat&logo=Python&logoColor=white)](https://www.python.org)
[![Docker](https://img.shields.io/badge/Docker-Compose-2496ED.svg?style=flat&logo=Docker&logoColor=white)](https://www.docker.com)

## 🚀 Features

### Core Capabilities
- **🤖 AI-Powered Chat**: Context-aware responses using Ollama LLM (Llama 3.2 / Mistral 7B)
- **🎙️ Voice Support**: Real-time voice interactions with STT (Faster-Whisper) and TTS (Kokoro-82M)
- **📚 RAG Engine**: Semantic search with ChromaDB for accurate information retrieval
- **🔧 Function Calling**: Automated handling of plan queries, billing, network diagnostics
- **💬 WebSocket Support**: Real-time streaming for both text and voice
- **🔒 Production Ready**: Security, logging, caching, database management

### Telecom-Specific Features
- Plan recommendations and comparisons
- Billing inquiry and payment processing
- Network coverage verification
- Speed tests and diagnostics
- Troubleshooting assistance
- Human agent escalation

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│                   TypeScript + Vite + Tailwind                  │
└────────────────────────┬────────────────────────────────────────┘
                         │ REST + WebSocket
┌────────────────────────▼────────────────────────────────────────┐
│                     Backend (FastAPI)                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │     API      │  │  WebSocket   │  │   Services   │         │
│  │   Routes     │  │   Handlers   │  │   (LLM/RAG)  │         │
│  └──────────────┘  └──────────────┘  └──────────────┘         │
└────┬─────────┬──────────┬──────────┬──────────┬────────────────┘
     │         │          │          │          │
     ▼         ▼          ▼          ▼          ▼
┌─────────┐ ┌──────┐ ┌────────┐ ┌────────┐ ┌──────────┐
│PostgreSQL│ │Redis │ │ChromaDB│ │ Ollama │ │  Voice   │
│    DB    │ │Cache │ │ Vector │ │  LLM   │ │Processing│
└─────────┘ └──────┘ └────────┘ └────────┘ └──────────┘
```

## 📋 Prerequisites

- **Docker** and **Docker Compose**
- **8GB RAM minimum** (16GB recommended)
- **10GB disk space**
- **GPU optional** (for faster LLM inference)

## 🚀 Quick Start

### 1. Clone the Repository
```bash
git clone https://github.com/Vijaykrishna2334/Telecom-ai-assistant.git
cd Telecom-ai-assistant
```

### 2. Configure Environment
```bash
cp .env.example .env
# Edit .env with your settings
```

### 3. Start Services
```bash
# Start all services
docker-compose up -d

# Download LLM model (first time only)
docker exec -it telecom-ai-assistant-ollama-1 ollama pull llama3.2:3b

# View logs
docker-compose logs -f
```

### 4. Access the Application
- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **API Docs**: http://localhost:8080/api/v1/docs
- **Health Check**: http://localhost:8080/health

## 🛠️ Development Setup

### Backend Development
```bash
cd backend
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt

# Run locally
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development
```bash
cd frontend
npm install
npm run dev
```

### Run Tests
```bash
# Backend tests
cd backend
pytest tests/ -v --cov=app

# Frontend tests
cd frontend
npm test
```

## 📊 Technology Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Backend** | FastAPI | High-performance async API |
| **Frontend** | React + TypeScript | Modern reactive UI |
| **LLM Runtime** | Ollama | Local LLM inference |
| **Models** | Llama 3.2 3B / Tele-LLM | Language understanding |
| **Vector DB** | ChromaDB | Semantic search & RAG |
| **Embeddings** | sentence-transformers | Text vectorization |
| **Database** | PostgreSQL | Persistent data storage |
| **Cache** | Redis | Performance optimization |
| **STT** | Faster-Whisper | Speech-to-text |
| **TTS** | Kokoro-82M | Text-to-speech (82M params, 24kHz audio) |
| **VAD** | Silero VAD | Voice activity detection |

## 🧠 RAG (Retrieval-Augmented Generation)

The assistant uses a sophisticated RAG pipeline to provide accurate, grounded responses from the knowledge base.

### RAG Architecture
```
User Query → Embedding → ChromaDB Search → Context Retrieval → LLM Generation
                              ↓
                     knowledge/ directory
                     ├── plans/           # JioMobile, JioFiber, JioAirFiber plans
                     ├── faqs/            # Customer support FAQs
                     ├── troubleshooting/ # Network issue guides
                     └── policies/        # Terms of service
```

### Key Features
- **Semantic Search**: Uses `sentence-transformers/all-MiniLM-L6-v2` for embeddings
- **Smart Chunking**: Documents split into optimal chunks with overlap
- **Source Attribution**: Responses cite which document the info came from
- **Anti-Hallucination**: Strict prompts prevent the LLM from inventing fake plans

### Knowledge Base API
```bash
# Search the knowledge base
curl -X POST http://localhost:8080/api/v1/knowledge/search \
  -H "Content-Type: application/json" \
  -d '{"query": "5G plans with unlimited data", "top_k": 3}'

# Ingest new documents
python reingest_knowledge.py
```

### Anti-Hallucination Measures
The system includes explicit blacklists of fake plans that the LLM must never mention:
- ❌ "Basic 30" / "Standard 50" / "Premium 80" - These don't exist
- ❌ Any mobile plan under ₹199 - Jio prepaid starts at ₹199
- ✅ Only mentions plans from the retrieved context

## 📁 Project Structure

```
telecom-ai-assistant/
├── backend/                 # FastAPI backend
│   ├── app/
│   │   ├── api/            # REST & WebSocket endpoints
│   │   ├── core/           # Config, logging, security
│   │   ├── models/         # Database models & schemas
│   │   ├── services/       # Business logic
│   │   │   ├── llm/        # Ollama integration
│   │   │   ├── rag/        # ChromaDB & embeddings
│   │   │   ├── voice/      # STT, TTS, VAD
│   │   │   └── telecom/    # Telecom operations
│   │   └── main.py         # Application entry point
│   ├── tests/              # Unit tests
│   ├── requirements.txt    # Python dependencies
│   └── Dockerfile
├── frontend/               # React frontend
│   ├── src/
│   │   ├── components/     # UI components
│   │   ├── hooks/          # Custom React hooks
│   │   ├── services/       # API clients
│   │   └── types/          # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── knowledge/              # Knowledge base
│   ├── plans/             # Telecom plans
│   ├── faqs/              # FAQs
│   ├── troubleshooting/   # Guides
│   └── policies/          # Policies
├── scripts/               # Utility scripts
├── docker-compose.yml     # Service orchestration
└── .env.example           # Environment template
```

## 🔧 Configuration

Key environment variables in `.env`:

```bash
# Application
APP_NAME=Telecom AI Assistant
DEBUG=false
SECRET_KEY=your-secret-key-here

# Ollama
OLLAMA_BASE_URL=http://ollama:11434
OLLAMA_MODEL=llama3.2:3b

# Database
DATABASE_URL=postgresql://postgres:postgres@db:5432/telecom_ai

# Redis
REDIS_URL=redis://redis:6379/0

# Voice Processing
STT_MODEL=base
TTS_VOICE=en_US-lessac-medium
```

## 🎯 API Endpoints

### REST API
```
GET  /health                          # Health check
GET  /ready                           # Readiness check
POST /api/v1/chat                     # Send chat message
GET  /api/v1/plans                    # List telecom plans
GET  /api/v1/plans/{id}               # Get plan details
POST /api/v1/voice/sessions           # Create voice session
GET  /api/v1/voice/sessions/{id}      # Get session details
DELETE /api/v1/voice/sessions/{id}    # End voice session
```

### WebSocket
```
/ws/chat/{session_id}                 # Real-time text chat
/ws/voice/{session_id}                # Real-time voice streaming
```

## 🧪 Testing

### Run All Tests
```bash
make test
```

### Test Coverage
```bash
cd backend
pytest --cov=app --cov-report=html
open htmlcov/index.html
```

## 📝 Code Quality

### Linting & Formatting
```bash
# Backend
make lint
make format

# Or manually
cd backend
black app/ tests/
flake8 app/ tests/
mypy app/
```

## 🐛 Troubleshooting

### Ollama Model Issues
```bash
# Pull model manually
docker exec -it telecom-ai-assistant-ollama-1 ollama pull llama3.2:3b

# List available models
docker exec -it telecom-ai-assistant-ollama-1 ollama list
```

### Database Connection Issues
```bash
# Reset database
docker-compose down -v
docker-compose up -d db
python scripts/init_db.py
```

### Port Conflicts
If ports are in use, edit `docker-compose.yml`:
```yaml
ports:
  - "3001:80"    # Change frontend port
  - "8081:8000"  # Change backend port
```

## 🚀 Deployment

### Production Checklist
- [ ] Set strong `SECRET_KEY`
- [ ] Set `DEBUG=false`
- [ ] Configure CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Enable monitoring and logging
- [ ] Configure backup strategy
- [ ] Set resource limits
- [ ] Use production LLM model (Mistral 7B)

### Docker Production
```bash
docker-compose -f docker-compose.yml up -d
```

## 🤝 Contributing

Contributions are welcome! Please:
1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License.

## 🙏 Acknowledgments

- **Ollama** for LLM runtime
- **FastAPI** for the excellent web framework
- **ChromaDB** for vector storage
- **OpenAI Whisper** team for STT models
- **Piper** team for TTS

## 📞 Support

- **Documentation**: See `/docs` directory
- **Issues**: GitHub Issues
- **Email**: support@telecom-ai.example.com

---

**Built with ❤️ for the open-source community**
