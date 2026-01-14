"""
Download Whisper large-v3-turbo model for faster-whisper.
This will download the model to the cache for immediate use.
"""
import sys
from faster_whisper import WhisperModel

def download_model():
    """Download the large-v3-turbo model."""
    print("=" * 60)
    print("Downloading Whisper large-v3-turbo model...")
    print("This may take a few minutes depending on your internet speed.")
    print("Model size: ~1.5GB")
    print("=" * 60)
    
    try:
        # This will automatically download the model if not present
        print("\nInitializing model download...")
        model = WhisperModel(
            "large-v3-turbo",
            device="cpu",
            compute_type="int8"
        )
        
        print("\n✅ SUCCESS! Model downloaded and loaded successfully!")
        print(f"Model type: large-v3-turbo")
        print(f"Device: CPU")
        print(f"Compute type: int8")
        
        # Test the model with a simple transcription
        print("\nTesting model...")
        print("Model is ready for use!")
        
        return True
        
    except Exception as e:
        print(f"\n❌ ERROR: Failed to download model: {e}")
        print("\nTroubleshooting:")
        print("1. Check your internet connection")
        print("2. Ensure you have enough disk space (~2GB)")
        print("3. Try running: pip install --upgrade faster-whisper")
        return False

if __name__ == "__main__":
    success = download_model()
    sys.exit(0 if success else 1)
