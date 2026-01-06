"""
Voice downloader for Piper TTS models.
Downloads multiple high-quality voices for testing.
"""
import os
import urllib.request

VOICE_DIR = "app/services/voice/models"
os.makedirs(VOICE_DIR, exist_ok=True)

# Best voices for natural speech
VOICES = {
    "en_US-ljspeech-high": {
        "description": "Female - Very natural, expressive, clear (BEST QUALITY)",
        "size": "127 MB",
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/ljspeech/high"
    },
    "en_US-lessac-high": {
        "description": "Male - Professional speaker, extremely natural",
        "size": "112 MB", 
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/lessac/high"
    },
    "en_GB-southern_english_female-medium": {
        "description": "Female - British accent, smooth and pleasant",
        "size": "63 MB",
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_GB/southern_english_female/medium"
    },
    "en_US-amy-medium": {
        "description": "Female - Lighter, faster (ALREADY DOWNLOADED)",
        "size": "63 MB",
        "url": "https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium"
    }
}

def download_voice(voice_name):
    """Download a Piper voice model."""
    voice_info = VOICES[voice_name]
    base_url = voice_info["url"]
    
    onnx_file = f"{VOICE_DIR}/{voice_name}.onnx"
    json_file = f"{VOICE_DIR}/{voice_name}.onnx.json"
    
    # Check if already exists
    if os.path.exists(onnx_file) and os.path.exists(json_file):
        print(f"✅ {voice_name} already downloaded")
        return
    
    print(f"📥 Downloading {voice_name} ({voice_info['description']})...")
    print(f"   Size: {voice_info['size']}")
    
    # Download .onnx model
    print(f"   Downloading model file...")
    urllib.request.urlretrieve(
        f"{base_url}/{voice_name}.onnx",
        onnx_file
    )
    
    # Download .json config
    print(f"   Downloading config file...")
    urllib.request.urlretrieve(
        f"{base_url}/{voice_name}.onnx.json",
        json_file
    )
    
    print(f"✅ {voice_name} downloaded successfully!\n")

if __name__ == "__main__":
    print("=" * 60)
    print("PIPER VOICE DOWNLOADER")
    print("=" * 60)
    print("\nAvailable voices:\n")
    
    for i, (name, info) in enumerate(VOICES.items(), 1):
        print(f"{i}. {name}")
        print(f"   {info['description']}")
        print(f"   Size: {info['size']}\n")
    
    print("\nOptions:")
    print("1. Download ljspeech-high (RECOMMENDED - most natural female)")
    print("2. Download lessac-high (best male voice)")
    print("3. Download all voices")
    print("4. Skip download\n")
    
    choice = input("Enter choice (1-4): ").strip()
    
    if choice == "1":
        download_voice("en_US-ljspeech-high")
    elif choice == "2":
        download_voice("en_US-lessac-high")
    elif choice == "3":
        for voice_name in VOICES.keys():
            if voice_name != "en_US-amy-medium":  # Already have this
                download_voice(voice_name)
    else:
        print("Skipping download")
    
    print("\n" + "=" * 60)
    print("DONE! To change voice, edit backend/app/core/config.py")
    print("Change the line: tts_voice: str = \"YOUR_VOICE_NAME\"")
    print("=" * 60)
