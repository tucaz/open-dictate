"""Recording file management."""

import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import List
from uuid import uuid4

from src.config import Config


@dataclass
class Recording:
    """Represents a saved recording."""
    path: Path
    date: datetime


class RecordingStore:
    """Manages recording file storage and retrieval."""
    
    FILE_PREFIX = "recording-"
    FILE_EXTENSION = "wav"
    DATE_FORMAT = "%Y-%m-%d-%H%M%S"
    
    @staticmethod
    def _ensure_directory() -> None:
        """Ensure the recordings directory exists."""
        Config.get_recordings_dir().mkdir(parents=True, exist_ok=True)
    
    @staticmethod
    def get_temp_path() -> Path:
        """
        Get a path for a temporary recording.
        
        Returns:
            Path in the system temp directory
        """
        import tempfile
        return Path(tempfile.gettempdir()) / "open-dictate-recording.wav"
    
    @staticmethod
    def new_recording_path() -> Path:
        """
        Get a path for a new recording with timestamp.
        
        Returns:
            Path in the recordings directory
        """
        RecordingStore._ensure_directory()
        
        timestamp = datetime.now().strftime(RecordingStore.DATE_FORMAT)
        unique = str(uuid4())[:8]
        filename = f"{RecordingStore.FILE_PREFIX}{timestamp}-{unique}.{RecordingStore.FILE_EXTENSION}"
        
        return Config.get_recordings_dir() / filename
    
    @staticmethod
    def list_recordings() -> List[Recording]:
        """
        List all saved recordings sorted by date (newest first).
        
        Returns:
            List of Recording objects
        """
        RecordingStore._ensure_directory()
        recordings_dir = Config.get_recordings_dir()
        
        recordings = []
        pattern = re.compile(
            rf"^{RecordingStore.FILE_PREFIX}(\d{{4}}-\d{{2}}-\d{{2}}-\d{{6}})-.*\.{RecordingStore.FILE_EXTENSION}$"
        )
        
        for file_path in recordings_dir.iterdir():
            if not file_path.is_file():
                continue
            
            match = pattern.match(file_path.name)
            if not match:
                continue
            
            date_str = match.group(1)
            try:
                date = datetime.strptime(date_str, RecordingStore.DATE_FORMAT)
                recordings.append(Recording(path=file_path, date=date))
            except ValueError:
                continue
        
        # Sort by date, newest first
        recordings.sort(key=lambda r: r.date, reverse=True)
        return recordings
    
    @staticmethod
    def prune(max_count: int) -> None:
        """
        Remove oldest recordings to keep only max_count.
        
        Args:
            max_count: Maximum number of recordings to keep
        """
        recordings = RecordingStore.list_recordings()
        
        if len(recordings) <= max_count:
            return
        
        to_remove = recordings[max_count:]
        for recording in to_remove:
            try:
                recording.path.unlink()
            except OSError as e:
                print(f"Warning: Could not remove old recording {recording.path}: {e}")
    
    @staticmethod
    def delete_all() -> None:
        """Delete all saved recordings."""
        recordings = RecordingStore.list_recordings()
        
        for recording in recordings:
            try:
                recording.path.unlink()
            except OSError as e:
                print(f"Warning: Could not remove recording {recording.path}: {e}")
    
    @staticmethod
    def delete_recording(path: Path) -> bool:
        """
        Delete a specific recording.
        
        Args:
            path: Path to the recording file
        
        Returns:
            True if deleted successfully, False otherwise
        """
        try:
            path.unlink()
            return True
        except OSError as e:
            print(f"Warning: Could not remove recording {path}: {e}")
            return False
