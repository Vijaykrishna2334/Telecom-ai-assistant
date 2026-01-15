#!/bin/bash
set -e

echo "============================================"
echo "🚀 TELECOM AI ASSISTANT - STARTUP"
echo "============================================"

# Default model if not specified
OLLAMA_MODEL=${OLLAMA_MODEL:-"qwen2.5:7b"}

echo ""
echo "[1/4] Starting Ollama server..."
echo "============================================"

# Start Ollama in the background
ollama serve &
OLLAMA_PID=$!

# Wait for Ollama to be ready
echo "Waiting for Ollama to start..."
max_attempts=30
attempt=0
while ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    attempt=$((attempt + 1))
    if [ $attempt -ge $max_attempts ]; then
        echo "❌ ERROR: Ollama failed to start after ${max_attempts} attempts"
        exit 1
    fi
    echo "  Waiting... (attempt $attempt/$max_attempts)"
    sleep 2
done
echo "✅ Ollama server is running!"

echo ""
echo "[2/4] Pulling LLM model: ${OLLAMA_MODEL}"
echo "============================================"

# Pull the model (this will download if not present)
if ollama pull "$OLLAMA_MODEL"; then
    echo "✅ Model ${OLLAMA_MODEL} is ready!"
else
    echo "❌ ERROR: Failed to pull model ${OLLAMA_MODEL}"
    exit 1
fi

echo ""
echo "[3/4] Verifying model is available..."
echo "============================================"
ollama list
echo "✅ Model verification complete!"

echo ""
echo "[4/4] Starting FastAPI application..."
echo "============================================"
echo "  - API: http://0.0.0.0:8080"
echo "  - Docs: http://0.0.0.0:8080/api/v1/docs"
echo "  - Ollama: http://0.0.0.0:11434"
echo "============================================"

# Run the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port 8080
