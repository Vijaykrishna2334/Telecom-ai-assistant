#!/bin/bash
# Download voice models for Faster-Whisper, Piper, and Silero VAD

set -e

echo "Downloading voice processing models..."

# Create models directory
mkdir -p models/whisper
mkdir -p models/piper
mkdir -p models/vad

echo "Note: Models will be downloaded on first use by the services."
echo "Faster-Whisper: Models cached in ~/.cache/huggingface/hub"
echo "Piper: Models cached in ~/.local/share/piper-tts"
echo "Silero VAD: Model downloaded via torch.hub"

echo ""
echo "To pre-download models, run the services once:"
echo "  docker-compose up backend"
echo ""
echo "Or manually download with:"
echo "  docker exec -it telecom-ai-assistant-backend-1 python -c 'from faster_whisper import WhisperModel; WhisperModel(\"base\")'"

echo "Models directory structure created."
