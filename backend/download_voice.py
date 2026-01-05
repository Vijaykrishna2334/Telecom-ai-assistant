import httpx
import os
from pathlib import Path

def download_file(url, target_path):
    print(f"Downloading {url} to {target_path}...")
    with httpx.stream("GET", url, follow_redirects=True) as response:
        response.raise_for_status()
        with open(target_path, "wb") as f:
            for chunk in response.iter_bytes():
                f.write(chunk)
    print(f"Downloaded {target_path}")

models_dir = Path("app/services/voice/models")
models_dir.mkdir(parents=True, exist_ok=True)

models = [
    ("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx", models_dir / "en_US-amy-medium.onnx"),
    ("https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/amy/medium/en_US-amy-medium.onnx.json", models_dir / "en_US-amy-medium.onnx.json")
]

for url, path in models:
    if not path.exists():
        download_file(url, path)
    else:
        print(f"{path} already exists")
