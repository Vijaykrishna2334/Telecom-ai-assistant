# Deployment Guide

## Quick Start (Docker Compose)

### Prerequisites
- Docker 24.0+
- Docker Compose 2.0+
- 8GB RAM minimum (16GB recommended)
- 10GB free disk space

### Step 1: Clone and Configure

```bash
# Clone the repository
git clone https://github.com/Vijaykrishna2334/Telecom-ai-assistant.git
cd Telecom-ai-assistant

# Copy environment file
cp .env.example .env

# Edit .env with your settings (optional for local testing)
nano .env
```

### Step 2: Start Services

```bash
# Start all services
docker-compose up -d

# Watch logs
docker-compose logs -f

# Wait for services to be healthy (check with)
docker-compose ps
```

### Step 3: Download LLM Model

```bash
# Download the Llama 3.2 3B model (first time only)
docker exec -it telecom-ai-assistant-ollama-1 ollama pull llama3.2:3b

# Or use Mistral 7B for production
docker exec -it telecom-ai-assistant-ollama-1 ollama pull mistral:7b
```

### Step 4: Initialize Database

```bash
# Initialize database tables
docker exec -it telecom-ai-assistant-backend-1 python /app/../scripts/init_db.py

# Seed knowledge base
docker exec -it telecom-ai-assistant-backend-1 python /app/../scripts/seed_knowledge.py
```

### Step 5: Access the Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8080
- **API Documentation**: http://localhost:8080/api/v1/docs
- **Health Check**: http://localhost:8080/health

## Development Setup

### Backend Development

```bash
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Start development services (DB, Redis, ChromaDB, Ollama)
docker-compose -f ../docker-compose.dev.yml up -d

# Run backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### Frontend Development

```bash
cd frontend

# Install dependencies
npm install

# Start dev server
npm run dev

# Access at http://localhost:5173
```

## Production Deployment

### Environment Variables

Key variables to set in production:

```bash
# Security
SECRET_KEY=<generate-strong-key>
DEBUG=false

# CORS
CORS_ORIGINS=["https://yourdomain.com"]

# Database
DATABASE_URL=postgresql://user:pass@host:5432/telecom_ai

# LLM Model
OLLAMA_MODEL=mistral:7b  # Use larger model for production
```

### SSL/TLS Configuration

1. Update `docker/nginx/nginx.conf` with SSL certificates
2. Add certificates to nginx container volume
3. Update CORS origins in `.env`

### Resource Requirements

**Minimum**:
- 2 CPU cores
- 8GB RAM
- 20GB disk space

**Recommended**:
- 4+ CPU cores
- 16GB RAM
- 50GB disk space
- GPU (for faster LLM inference)

### With GPU Support

Update `docker-compose.yml`:

```yaml
ollama:
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: 1
            capabilities: [gpu]
```

## Monitoring & Logs

### View Logs

```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f backend

# Last 100 lines
docker-compose logs --tail=100 backend
```

### Health Checks

```bash
# Check service health
curl http://localhost:8080/health

# Check readiness
curl http://localhost:8080/ready
```

## Troubleshooting

### Services Won't Start

```bash
# Check service status
docker-compose ps

# Restart specific service
docker-compose restart backend

# Rebuild and restart
docker-compose up -d --build backend
```

### Database Issues

```bash
# Reset database
docker-compose down -v
docker-compose up -d db
docker exec -it telecom-ai-assistant-backend-1 python scripts/init_db.py
```

### Ollama Model Not Found

```bash
# List downloaded models
docker exec -it telecom-ai-assistant-ollama-1 ollama list

# Pull model
docker exec -it telecom-ai-assistant-ollama-1 ollama pull llama3.2:3b
```

### Port Conflicts

Edit `docker-compose.yml` to change ports:

```yaml
services:
  backend:
    ports:
      - "8081:8000"  # Change from 8080 to 8081
```

## Backup & Restore

### Backup Database

```bash
docker exec telecom-ai-assistant-db-1 pg_dump -U postgres telecom_ai > backup.sql
```

### Restore Database

```bash
docker exec -i telecom-ai-assistant-db-1 psql -U postgres telecom_ai < backup.sql
```

## Scaling

### Horizontal Scaling

Update `docker-compose.yml`:

```yaml
backend:
  deploy:
    replicas: 3
```

### Load Balancer

Use nginx or traefik as load balancer in front of multiple backend instances.

## Security Checklist

- [ ] Change default SECRET_KEY
- [ ] Set DEBUG=false in production
- [ ] Configure proper CORS origins
- [ ] Use strong database passwords
- [ ] Enable SSL/TLS certificates
- [ ] Set up firewall rules
- [ ] Enable rate limiting
- [ ] Regular security updates
- [ ] Monitor logs for suspicious activity

## Updates & Maintenance

### Update Application

```bash
# Pull latest code
git pull origin main

# Rebuild and restart
docker-compose down
docker-compose up -d --build
```

### Update Dependencies

```bash
# Backend
cd backend
pip install -r requirements.txt --upgrade

# Frontend
cd frontend
npm update
```

## Support

For issues or questions:
- GitHub Issues: https://github.com/Vijaykrishna2334/Telecom-ai-assistant/issues
- Documentation: See README.md
- Email: support@telecom-ai.example.com
