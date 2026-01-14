# 🤖 Telecom AI Voice Assistant

An intelligent AI-powered customer service assistant for Reliance Jio, featuring voice interaction, RAG-based knowledge retrieval, and real-time chat capabilities.

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.109-green)
![Ollama](https://img.shields.io/badge/LLM-Ollama-orange)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 🌟 Features

### 💬 Chat Interface
- Real-time text chat with AI assistant
- Streaming responses (token-by-token)
- Session management and chat history
- WebSocket support for instant messaging

### 🎙️ Voice Interface
- **Speech-to-Text (STT)**: Faster-Whisper (Whisper base.en model)
- **Text-to-Speech (TTS)**: Kokoro-82M (lightweight, high-quality)
- **Voice Activity Detection (VAD)**: Silero-VAD (neural network-based)
- Real-time voice conversations

### 🔍 RAG (Retrieval-Augmented Generation)
- **Hybrid Search**: Vector (BGE embeddings) + BM25 keyword search
- **CRAG**: Corrective RAG with relevance grading
- **Knowledge Base**: Comprehensive Jio plans, services, and FAQs
- **ChromaDB**: Vector database for efficient retrieval

### 📊 Supported Jio Services
- ✅ Prepaid Mobile Plans
- ✅ Postpaid Mobile Plans
- ✅ JioFiber Broadband
- ✅ JioAirFiber (5G Wireless Broadband)
- ✅ International Roaming
- ✅ ISD Calling Rates
- ✅ Digital Services (JioTV, JioCinema, etc.)

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         Frontend (React)                         │
│                    telecom-voice-companion-main                  │
├─────────────────────────────────────────────────────────────────┤
│                         Backend (FastAPI)                        │
├──────────────┬──────────────┬──────────────┬────────────────────┤
│   Chat API   │   Voice API  │   RAG API    │   WebSockets       │
├──────────────┼──────────────┼──────────────┼────────────────────┤
│              │              │              │                    │
│  Ollama LLM  │ Whisper STT  │  ChromaDB    │  Silero VAD        │
│ (llama3.1:8b)│ (base.en)    │  (Vector DB) │                    │
│              │              │              │                    │
│              │ Kokoro TTS   │  BM25 Index  │                    │
│              │ (82M model)  │  (Keyword)   │                    │
└──────────────┴──────────────┴──────────────┴────────────────────┘
```

---

## 🛠️ Tech Stack

### Backend
| Component | Technology | Description |
|-----------|------------|-------------|
| **Framework** | FastAPI 0.109 | Async Python web framework |
| **LLM** | Ollama + llama3.1:8b | Local LLM inference |
| **STT** | Faster-Whisper (base.en) | Speech-to-Text using Whisper |
| **TTS** | Kokoro-82M | Lightweight 82M param TTS model |
| **VAD** | Silero-VAD | Neural network voice activity detection |
| **Embeddings** | BGE-base-en-v1.5 | State-of-the-art embedding model |
| **Vector DB** | ChromaDB | Vector database for RAG |
| **Search** | BM25 + Vector | Hybrid search (RRF fusion) |
| **Database** | PostgreSQL | Session and chat history storage |
| **Cache** | Redis | Response caching |

### Frontend
| Component | Technology | Description |
|-----------|------------|-------------|
| **Framework** | React + Vite | Modern frontend tooling |
| **Styling** | TailwindCSS | Utility-first CSS |
| **UI** | shadcn/ui | Beautiful component library |
| **Voice** | Web Audio API | Browser audio recording |

---

## 📋 Prerequisites

### Required Software
- **Python 3.12+** (required for Kokoro TTS compatibility)
- **Node.js 18+** (for frontend)
- **Ollama** (for local LLM)
- **PostgreSQL** (optional, for persistence)
- **Redis** (optional, for caching)

### For GPU Acceleration (Recommended for TTS)
> ⚡ **CUDA is highly recommended for Kokoro TTS** - provides 5-10x faster audio generation

```bash
# Check if CUDA is available
python -c "import torch; print('CUDA:', torch.cuda.is_available())"
```

**CUDA Setup:**
1. Install [NVIDIA CUDA Toolkit 12.x](https://developer.nvidia.com/cuda-downloads)
2. Install [cuDNN](https://developer.nvidia.com/cudnn)
3. Reinstall PyTorch with CUDA:
```bash
pip uninstall torch torchaudio
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

---

## 🚀 Quick Start

### 1. Clone Repository
```bash
git clone https://github.com/your-username/Telecom-ai-assistant.git
cd Telecom-ai-assistant
```

### 2. Install Ollama & Pull Model
```bash
# Install from https://ollama.ai
ollama pull llama3.1:8b
```

### 3. Setup Backend
```bash
cd backend

# Create virtual environment
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Activate (Linux/Mac)
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# For CUDA/GPU support (recommended for Kokoro TTS):
pip uninstall torch torchaudio -y
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### 4. Configure Environment
```bash
# Copy example env
copy .env.example .env  # Windows
cp .env.example .env    # Linux/Mac

# Edit .env with your settings
```

**Key `.env` settings:**
```ini
# LLM
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=llama3.1:8b

# Voice (Both STT and TTS auto-detect GPU/CUDA)
STT_MODEL=base.en
# Device is auto-detected - uses CUDA if available

# Kokoro TTS (auto-detects GPU)
KOKORO_VOICE=af_heart
KOKORO_LANG_CODE=a
```

### 5. Start Backend
```bash
cd backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8080
```

Backend runs at: **http://localhost:8080**

### 6. Setup Frontend
```bash
cd telecom-voice-companion-main

# Install dependencies
npm install

# Start development server
npm run dev
```

Frontend runs at: **http://localhost:5173**

---

## 📁 Project Structure

```
Telecom-ai-assistant/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API routes
│   │   │   ├── routes/        # REST endpoints
│   │   │   └── websockets/    # WebSocket handlers
│   │   ├── core/              # Config, logging, security
│   │   ├── models/            # Database models
│   │   └── services/
│   │       ├── llm/           # LLM (Ollama) integration
│   │       ├── rag/           # RAG pipeline (CRAG)
│   │       │   ├── crag_chain.py      # CRAG orchestrator
│   │       │   ├── hybrid_retriever.py # Vector + BM25
│   │       │   └── ingestion.py       # Document chunking
│   │       └── voice/         # Voice processing
│   │           ├── stt.py     # Faster-Whisper STT
│   │           ├── kokoro_tts.py  # Kokoro TTS
│   │           └── vad.py     # Silero VAD
│   ├── requirements.txt
│   └── Dockerfile
│
├── knowledge/                 # RAG knowledge base
│   ├── plans/                # Jio plan documents
│   ├── faqs/                 # FAQ documents
│   ├── services/             # Service information
│   └── policies/             # Terms, conditions
│
├── telecom-voice-companion-main/  # React frontend
│   ├── src/
│   │   ├── components/       # UI components
│   │   ├── pages/           # Page components
│   │   └── hooks/           # Custom hooks
│   └── package.json
│
├── docker-compose.yml        # Docker orchestration
└── README.md
```

---

## 🎙️ Voice Components

### Speech-to-Text (Faster-Whisper)
- **Model**: `base.en` (English optimized)
- **Device**: Auto-detects CUDA GPU (falls back to CPU)
- **Compute Type**: `float16` (GPU) or `int8` (CPU)
- **Features**: VAD filtering, beam search, Jio vocabulary hints

```python
# Auto-detection in stt.py
# Uses CUDA GPU if available: RTX 4090 → ~3x faster transcription
# Falls back to CPU with int8 quantization
```

### Text-to-Speech (Kokoro-82M)
- **Model**: Kokoro-82M (82 million parameters)
- **Voice**: `af_heart` (American female)
- **Sample Rate**: 24kHz
- **Device**: Auto-detects GPU (CUDA) for faster synthesis

```python
# Configuration in config.py
kokoro_voice: str = "af_heart"
kokoro_lang_code: str = "a"  # 'a' = American English
```

**Available Voices:**
| Voice Code | Description |
|------------|-------------|
| `af_heart` | American Female (warm) |
| `af_bella` | American Female (professional) |
| `am_adam` | American Male |
| `bf_emma` | British Female |
| `bm_george` | British Male |

### Voice Activity Detection (Silero-VAD)
- **Model**: Silero-VAD (neural network)
- **Threshold**: 0.85 (adjustable)
- **Fallback**: Energy-based detection

---

## 🔧 Configuration

### Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `OLLAMA_BASE_URL` | `http://localhost:11434` | Ollama API URL |
| `OLLAMA_MODEL` | `llama3.1:8b` | LLM model name |
| `STT_MODEL` | `base.en` | Whisper model size |
| `STT_DEVICE` | `cpu` | STT device (cpu/cuda) |
| `KOKORO_VOICE` | `af_heart` | TTS voice |
| `VAD_THRESHOLD` | `0.85` | VAD sensitivity |
| `CRAG_TOP_K` | `10` | Documents to retrieve |
| `DATABASE_URL` | `postgresql://...` | PostgreSQL connection |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection |

---

## 🐳 Docker Deployment

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f backend

# Stop services
docker-compose down
```

---

## 📚 API Endpoints

### Chat
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/chat` | Send message, get response |
| POST | `/api/v1/chat/stream` | Streaming response (SSE) |
| GET | `/api/v1/chat/history/{session_id}` | Get chat history |

### Voice
| Method | Endpoint | Description |
|--------|----------|-------------|
| WS | `/api/v1/ws/voice` | Real-time voice WebSocket |
| POST | `/api/v1/voice/transcribe` | Transcribe audio |
| POST | `/api/v1/voice/synthesize` | Generate speech |

### Knowledge
| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/knowledge/search` | Search knowledge base |
| POST | `/api/v1/knowledge/ingest` | Ingest documents |

---

## 🧪 Testing

```bash
cd backend

# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test
pytest tests/test_rag.py -v
```

---

## 🔧 Troubleshooting

### Ollama Connection Error
```
Error: Cannot connect to Ollama
```
**Solution:** Ensure Ollama is running:
```bash
ollama serve
# In another terminal:
ollama pull llama3.1:8b
```

### CUDA/GPU Not Detected
```
CUDA available: False
```
**Solution:** Install PyTorch with CUDA support:
```bash
pip uninstall torch torchaudio -y
pip install torch torchaudio --index-url https://download.pytorch.org/whl/cu121
```

### Kokoro TTS Installation Error
```
ModuleNotFoundError: No module named 'kokoro'
```
**Solution:**
```bash
pip install 'kokoro>=0.9.2' soundfile
```

### ChromaDB Errors
```
Error: Collection not found
```
**Solution:** Knowledge base auto-ingests on startup. If issues persist:
```bash
cd backend
python reingest_knowledge.py
```

### Port Already in Use
```
Error: Address already in use :8080
```
**Solution:** Change port in `.env`:
```ini
PORT=8081
```

### FFmpeg Warnings (Can Ignore)
```
Failed to load FFmpeg extension
```
This is a non-critical warning from torchaudio. TTS will still work.

---

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing`)
3. Commit changes (`git commit -m 'Add amazing feature'`)
4. Push to branch (`git push origin feature/amazing`)
5. Open a Pull Request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🙏 Acknowledgments

- [Ollama](https://ollama.ai) - Local LLM inference
- [Faster-Whisper](https://github.com/guillaumekln/faster-whisper) - Fast Whisper implementation
- [Kokoro TTS](https://github.com/hexgrad/kokoro) - Lightweight TTS model
- [Silero-VAD](https://github.com/snakers4/silero-vad) - Voice activity detection
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework

---

## 📞 Support

For issues or questions:
- Create a [GitHub Issue](https://github.com/your-username/Telecom-ai-assistant/issues)
- Email: your-email@example.com

---

**Built with ❤️ for better customer service**
