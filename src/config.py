"""Configuration management for open-dictate."""

import json
import os
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import List, Optional, Any


@dataclass
class HotkeyConfig:
    """Hotkey configuration."""
    key_code: int = 124  # F13 (no globe key on Windows)
    modifiers: List[str] = field(default_factory=list)

    @property
    def modifier_flags(self) -> int:
        """Convert modifier strings to Windows modifier bitmask."""
        flags = 0
        for mod in self.modifiers:
            mod_lower = mod.lower()
            if mod_lower in ("ctrl", "control"):
                flags |= 0x0002  # MOD_CONTROL
            elif mod_lower == "shift":
                flags |= 0x0004  # MOD_SHIFT
            elif mod_lower in ("alt", "menu"):
                flags |= 0x0001  # MOD_ALT
            elif mod_lower in ("win", "windows", "cmd", "command"):
                flags |= 0x0008  # MOD_WIN
        return flags


class FlexBool:
    """Flexible boolean that can be parsed from bool, string, or int."""
    
    def __init__(self, value: Any):
        self.value = self._parse(value)
    
    @staticmethod
    def _parse(value: Any) -> bool:
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.lower() in ("true", "yes", "1", "on", "enabled")
        if isinstance(value, (int, float)):
            return value != 0
        return False
    
    def __bool__(self) -> bool:
        return self.value
    
    def __repr__(self) -> str:
        return f"FlexBool({self.value})"


@dataclass
class Config:
    """Application configuration."""
    hotkey: HotkeyConfig = field(default_factory=HotkeyConfig)
    model_path: Optional[str] = None
    model_size: str = "base.en"
    language: str = "en"
    spoken_punctuation: Optional[FlexBool] = None
    max_recordings: Optional[int] = None

    DEFAULT_MAX_RECORDINGS = 0

    @staticmethod
    def effective_max_recordings(value: Optional[int]) -> int:
        """Get effective max recordings value."""
        raw = value if value is not None else Config.DEFAULT_MAX_RECORDINGS
        if raw == 0:
            return 0
        return min(max(1, raw), 100)

    @classmethod
    def default_config(cls) -> "Config":
        """Create default configuration."""
        # Default: Right Ctrl (163) - good for push-to-talk, works on all keyboards
        # Avoid Alt modifiers as they activate menu bars in many apps
        return cls(
            hotkey=HotkeyConfig(key_code=163, modifiers=[]),  # Right Ctrl
            model_path=None,
            model_size="base.en",
            language="en",
            spoken_punctuation=FlexBool(False),
            max_recordings=None
        )

    @staticmethod
    def get_config_dir() -> Path:
        """Get configuration directory."""
        app_data = os.environ.get("APPDATA")
        if app_data:
            return Path(app_data) / "open-dictate"
        return Path.home() / ".config" / "open-dictate"

    @staticmethod
    def get_config_file() -> Path:
        """Get configuration file path."""
        return Config.get_config_dir() / "config.json"

    @staticmethod
    def get_models_dir() -> Path:
        """Get models directory."""
        return Config.get_config_dir() / "models"

    @staticmethod
    def get_recordings_dir() -> Path:
        """Get recordings directory."""
        return Config.get_config_dir() / "recordings"

    @classmethod
    def load(cls) -> "Config":
        """Load configuration from file or create default."""
        config_file = cls.get_config_file()
        
        if not config_file.exists():
            config = cls.default_config()
            config.save()
            return config

        try:
            # Use utf-8-sig to handle BOM that PowerShell might add
            with open(config_file, "r", encoding="utf-8-sig") as f:
                data = json.load(f)
            
            # Parse hotkey
            hotkey_data = data.get("hotkey", {})
            hotkey = HotkeyConfig(
                key_code=hotkey_data.get("keyCode", 124),
                modifiers=hotkey_data.get("modifiers", [])
            )

            # Parse spoken_punctuation
            sp = data.get("spokenPunctuation")
            spoken_punctuation = FlexBool(sp) if sp is not None else None

            return cls(
                hotkey=hotkey,
                model_path=data.get("modelPath"),
                model_size=data.get("modelSize", "base.en"),
                language=data.get("language", "en"),
                spoken_punctuation=spoken_punctuation,
                max_recordings=data.get("maxRecordings")
            )
        except (json.JSONDecodeError, KeyError, TypeError) as e:
            print(f"Warning: Unable to parse {config_file}: {e}")
            return cls.default_config()

    def save(self) -> None:
        """Save configuration to file."""
        config_dir = self.get_config_dir()
        config_dir.mkdir(parents=True, exist_ok=True)

        data = {
            "hotkey": {
                "keyCode": self.hotkey.key_code,
                "modifiers": self.hotkey.modifiers
            },
            "modelPath": self.model_path,
            "modelSize": self.model_size,
            "language": self.language,
            "spokenPunctuation": self.spoken_punctuation.value if self.spoken_punctuation else False,
            "maxRecordings": self.max_recordings
        }

        with open(self.get_config_file(), "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)
