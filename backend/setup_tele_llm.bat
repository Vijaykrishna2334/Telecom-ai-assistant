@echo off
REM ============================================================================
REM  TELE-LLM GGUF SETUP SCRIPT
REM ============================================================================
REM  Downloads and sets up Yale's Tele-LLM (telecom-specialized) for Ollama
REM  Model: Llama-3.2-3B-Tele-Q4_K_M-GGUF (~2GB)
REM  Source: https://huggingface.co/actuator-x/Llama-3.2-3B-Tele-Q4_K_M-GGUF
REM ============================================================================

echo.
echo ================================================================
echo   Tele-LLM GGUF Setup for Telecom AI Assistant
echo   Model: Yale Tele-LLM (Telecom-Specialized)
echo ================================================================
echo.

REM Check if Ollama is installed
where ollama >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] Ollama is not installed or not in PATH
    echo Please install Ollama from: https://ollama.com/download
    pause
    exit /b 1
)

REM Create models directory
if not exist "models" mkdir models
cd models

echo [1/4] Downloading Tele-LLM GGUF from HuggingFace...
echo       This may take a few minutes (~2GB download)
echo.

REM Check if curl is available
where curl >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERROR] curl not found. Please install curl or download manually:
    echo https://huggingface.co/actuator-x/Llama-3.2-3B-Tele-Q4_K_M-GGUF/resolve/main/llama-3.2-3b-tele-q4_k_m.gguf
    pause
    exit /b 1
)

REM Download the GGUF file
if not exist "llama-3.2-3b-tele-q4_k_m.gguf" (
    curl -L -o llama-3.2-3b-tele-q4_k_m.gguf "https://huggingface.co/actuator-x/Llama-3.2-3B-Tele-Q4_K_M-GGUF/resolve/main/llama-3.2-3b-tele-q4_k_m.gguf"
    if %ERRORLEVEL% NEQ 0 (
        echo [ERROR] Download failed. Please check your internet connection.
        pause
        exit /b 1
    )
) else (
    echo       Model already downloaded, skipping...
)

cd ..

echo.
echo [2/4] Creating Ollama Modelfile...

REM Create Modelfile for the GGUF
(
echo # Tele-LLM: Telecom-Specialized LLM
echo # Based on Yale's Llama-3.2-3B-Tele trained on 2.5B telecom tokens
echo.
echo FROM ./models/llama-3.2-3b-tele-q4_k_m.gguf
echo.
echo # Optimal parameters for telecom customer support
echo PARAMETER temperature 0.7
echo PARAMETER top_p 0.9
echo PARAMETER num_predict 256
echo PARAMETER stop "^<^|eot_id^|^>"
echo.
echo SYSTEM """You are JioCare, an AI customer support assistant for Reliance Jio.
echo.
echo CRITICAL RULES:
echo 1. ONLY use information from the provided context
echo 2. If you don't have the information, say "Let me transfer you to 1800-88-99999"
echo 3. NEVER make up plan prices or features
echo 4. Be concise - keep responses to 1-3 sentences for voice
echo.
echo GREETING ^(first message only^): "Namaste! Welcome to JioCare. How may I help you?"
echo.
echo CLOSING: "Is there anything else I can help with?"
echo """
) > Modelfile.tele-gguf

echo.
echo [3/4] Creating Ollama model from GGUF...
ollama create tele-llm -f Modelfile.tele-gguf

echo.
echo [4/4] Verifying model...
ollama list | findstr "tele-llm"

echo.
echo ================================================================
echo   Setup Complete!
echo ================================================================
echo.
echo To use Tele-LLM, update your .env:
echo   OLLAMA_MODEL=tele-llm
echo.
echo To test manually:
echo   ollama run tele-llm "What is 5G handover?"
echo.
echo The model understands telecom terms like:
echo   - 3GPP, SCTP, MME, APN, handover, 5G NR
echo   - Network protocols, standards, configurations
echo.
pause
