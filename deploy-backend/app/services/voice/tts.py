"""
Text-to-Speech service using Kokoro TTS.
Runs fully locally without cloud dependencies.
"""
import re
from app.core.config import settings
from app.core.logging import get_logger
from app.services.voice.kokoro_tts import KokoroTTSService

logger = get_logger(__name__)


def sanitize_text_for_tts(text: str) -> str:
    """
    Clean text for TTS to avoid speaking symbols.
    Converts symbols to spoken words.
    
    Args:
        text: Raw text with potential symbols
        
    Returns:
        Clean text suitable for speech synthesis
    """
    if not text:
        return text
    
    # Replace currency symbols with words
    text = text.replace("₹", "rupees ")
    text = text.replace("$", "dollars ")
    text = text.replace("€", "euros ")
    text = text.replace("£", "pounds ")
    
    # Replace emoji symbols with nothing or words
    text = text.replace("❌", "")
    text = text.replace("✅", "")
    text = text.replace("📱", "")
    text = text.replace("🚨", "")
    text = text.replace("📞", "")
    text = text.replace("📋", "")
    text = text.replace("✓", "")
    text = text.replace("✗", "")
    text = text.replace("→", "to")
    text = text.replace("←", "from")
    text = text.replace("•", "")
    text = text.replace("·", "")
    
    # Replace markdown symbols
    text = re.sub(r'\*\*([^*]+)\*\*', r'\1', text)  # Remove **bold**
    text = re.sub(r'\*([^*]+)\*', r'\1', text)  # Remove *italic*
    text = re.sub(r'#{1,6}\s*', '', text)  # Remove markdown headers
    text = re.sub(r'\|[^\n]+\|', '', text)  # Remove table rows
    text = re.sub(r'-{3,}', '', text)  # Remove horizontal rules
    
    # Replace pipe characters (from tables)
    text = text.replace("|", "")
    
    # Clean up multiple spaces and newlines
    text = re.sub(r'\n\s*\n', '\n', text)
    text = re.sub(r'[ \t]+', ' ', text)
    text = text.strip()
    
    return text


# Global TTS service instance using Kokoro
tts_service = KokoroTTSService(
    voice=settings.kokoro_voice,
    lang_code=settings.kokoro_lang_code
)
