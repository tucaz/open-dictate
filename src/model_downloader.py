"""Download Whisper models from HuggingFace."""

from pathlib import Path
from typing import Callable, Optional

import requests

from src.config import Config


class ModelDownloadError(Exception):
    """Error downloading a model."""
    pass


class ModelDownloader:
    """Downloads Whisper models from HuggingFace."""
    
    BASE_URL = "https://huggingface.co/ggerganov/whisper.cpp/resolve/main"
    
    @staticmethod
    def download(
        model_size: str,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> Path:
        """
        Download a Whisper model.
        
        Args:
            model_size: Model size (e.g., "base.en", "small", "large")
            progress_callback: Optional callback(bytes_downloaded, total_bytes)
        
        Returns:
            Path to the downloaded model file
        
        Raises:
            ModelDownloadError: If download fails
        """
        model_filename = f"ggml-{model_size}.bin"
        models_dir = Config.get_models_dir()
        dest_path = models_dir / model_filename
        
        # Check if already exists
        if dest_path.exists():
            print(f"Model '{model_size}' already exists at {dest_path}")
            return dest_path
        
        # Ensure directory exists
        models_dir.mkdir(parents=True, exist_ok=True)
        
        url = f"{ModelDownloader.BASE_URL}/{model_filename}"
        print(f"Downloading {model_size} model from {url}...")
        
        try:
            response = requests.get(url, stream=True, timeout=30)
            response.raise_for_status()
            
            total_size = int(response.headers.get('content-length', 0))
            downloaded = 0
            
            with open(dest_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded += len(chunk)
                        if progress_callback:
                            progress_callback(downloaded, total_size)
            
            print(f"Model downloaded to {dest_path}")
            return dest_path
            
        except requests.RequestException as e:
            # Clean up partial download
            if dest_path.exists():
                try:
                    dest_path.unlink()
                except:
                    pass
            raise ModelDownloadError(f"Failed to download model: {e}")
    
    @staticmethod
    def get_model_path(model_size: str) -> Optional[Path]:
        """
        Get the path to a model if it exists.
        
        Args:
            model_size: Model size (e.g., "base.en")
        
        Returns:
            Path to the model file, or None if not found
        """
        model_filename = f"ggml-{model_size}.bin"
        models_dir = Config.get_models_dir()
        model_path = models_dir / model_filename
        
        if model_path.exists():
            return model_path
        
        return None
    
    @staticmethod
    def model_exists(model_size: str) -> bool:
        """Check if a model exists locally."""
        return ModelDownloader.get_model_path(model_size) is not None
    
    @staticmethod
    def format_size(bytes_size: int) -> str:
        """Format byte size to human readable string."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if bytes_size < 1024:
                return f"{bytes_size:.1f} {unit}"
            bytes_size /= 1024
        return f"{bytes_size:.1f} TB"
