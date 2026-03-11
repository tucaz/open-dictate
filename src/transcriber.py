"""Whisper transcription using whisper-cli."""

import shutil
import subprocess
from pathlib import Path
from typing import Optional

from src.config import Config


class TranscriberError(Exception):
    """Error during transcription."""
    pass


class Transcriber:
    """Transcribes audio files using whisper.cpp."""
    
    def __init__(self, model_size: str = "base.en", language: str = "en"):
        """
        Initialize the transcriber.
        
        Args:
            model_size: Whisper model size (e.g., "base.en", "small")
            language: Language code (e.g., "en", "de")
        """
        self.model_size = model_size
        self.language = language
        self.spoken_punctuation = False
    
    def transcribe(self, audio_path: Path) -> str:
        """
        Transcribe an audio file.
        
        Args:
            audio_path: Path to the audio file (WAV format)
        
        Returns:
            Transcribed text
        
        Raises:
            TranscriberError: If transcription fails
        """
        whisper_path = self.find_whisper_binary()
        if not whisper_path:
            raise TranscriberError("whisper-cli not found")
        
        model_path = self.find_model(self.model_size)
        if not model_path:
            raise TranscriberError(f"Model '{self.model_size}' not found")
        
        # Build command
        args = [
            str(whisper_path),
            "-m", str(model_path),
            "-f", str(audio_path),
            "-l", self.language,
            "--no-timestamps",
            "-nt",
        ]
        
        if self.spoken_punctuation:
            args.extend(["--suppress-regex", r"[,\.\?!;:\-—]"])
        
        try:
            # Set working directory to whisper-cli location so it can find DLLs
            whisper_dir = Path(whisper_path).parent
            result = subprocess.run(
                args,
                capture_output=True,
                text=True,
                encoding='utf-8',
                errors='replace',
                check=False,
                cwd=str(whisper_dir)
            )
            
            if result.returncode != 0:
                stderr = result.stderr.strip() if result.stderr else "Unknown error"
                print(f"whisper-cpp: {stderr}")
                raise TranscriberError(f"Transcription failed: {stderr}")
            
            # Return stdout, stripped of whitespace
            return result.stdout.strip()
            
        except subprocess.TimeoutExpired:
            raise TranscriberError("Transcription timed out")
        except Exception as e:
            raise TranscriberError(f"Transcription error: {e}")
    
    @staticmethod
    def find_whisper_binary() -> Optional[str]:
        """
        Find the whisper-cli binary.
        
        Returns:
            Path to whisper-cli binary, or None if not found
        """
        # Check if whisper-cli is in PATH
        whisper_cli = shutil.which("whisper-cli")
        if whisper_cli:
            return whisper_cli
        
        # Check for whisper-cli.exe (Windows)
        whisper_exe = shutil.which("whisper-cli.exe")
        if whisper_exe:
            return whisper_exe
        
        # Check common installation locations
        local_app_data = Path.home() / "AppData" / "Local"
        common_paths = [
            Path(Config.get_config_dir()) / "whisper-cli.exe",
            local_app_data / "open-dictate" / "bin" / "whisper-cli.exe",
            Path.home() / "whisper.cpp" / "build" / "bin" / "Release" / "whisper-cli.exe",
            Path.home() / "whisper.cpp" / "build" / "bin" / "whisper-cli.exe",
            Path("C:/Program Files/whisper-cpp/whisper-cli.exe"),
            Path("C:/whisper-cpp/whisper-cli.exe"),
        ]
        
        for path in common_paths:
            if path.exists():
                return str(path)
        
        return None
    
    @staticmethod
    def find_model(model_size: str) -> Optional[str]:
        """
        Find a Whisper model file.
        
        Args:
            model_size: Model size (e.g., "base.en")
        
        Returns:
            Path to the model file, or None if not found
        """
        model_filename = f"ggml-{model_size}.bin"
        
        # Check models directory
        models_dir = Config.get_models_dir()
        model_path = models_dir / model_filename
        if model_path.exists():
            return str(model_path)
        
        # Check common locations
        common_paths = [
            Path.home() / ".cache" / "whisper" / model_filename,
            Path.home() / "whisper.cpp" / "models" / model_filename,
            Path("C:/Program Files/whisper-cpp/models") / model_filename,
            Path("C:/whisper-cpp/models") / model_filename,
        ]
        
        for path in common_paths:
            if path.exists():
                return str(path)
        
        return None
    
    @staticmethod
    def model_exists(model_size: str) -> bool:
        """Check if a model exists locally."""
        return Transcriber.find_model(model_size) is not None
