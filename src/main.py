"""CLI entry point for open-dictate."""

import sys

from src.app import OpenDictateApp
from src.config import Config
from src.key_codes import KeyCodes
from src.model_downloader import ModelDownloader
from src.transcriber import Transcriber
from src.version import VERSION


def print_usage():
    """Print usage information."""
    print(f"""
open-dictate v{VERSION} — Push-to-talk voice dictation for Windows

USAGE:
    open-dictate start              Start the dictation daemon
    open-dictate set-hotkey <key>   Set the push-to-talk hotkey
    open-dictate get-hotkey         Show current hotkey
    open-dictate set-model <size>   Set the Whisper model
    open-dictate download-model [size]  Download a Whisper model
    open-dictate status             Show configuration and status
    open-dictate --help             Show this help message

HOTKEY EXAMPLES:
    open-dictate set-hotkey rightctrl       Right Ctrl key (default)
    open-dictate set-hotkey f13             F13 key (no conflicts)
    open-dictate set-hotkey f24             F24 key (no conflicts)
    open-dictate set-hotkey ctrl+space      Ctrl + Space
    open-dictate set-hotkey insert          Insert key

NOTE: Avoid 'alt' modifiers as they activate menu bars in many apps,
      causing text to paste in the wrong place.

AVAILABLE MODELS:
    tiny.en, tiny, base.en, base, small.en, small, medium.en, medium, large
""")


def cmd_start():
    """Start the dictation daemon."""
    app = OpenDictateApp()
    app.run()


def cmd_set_hotkey(key_string: str):
    """Set the hotkey."""
    parsed = KeyCodes.parse(key_string)
    
    if not parsed:
        print(f"Error: Unknown key '{key_string}'")
        print("Run 'open-dictate --help' for examples")
        sys.exit(1)
    
    vk_code, modifiers = parsed
    config = Config.load()
    config.hotkey.key_code = vk_code
    config.hotkey.modifiers = modifiers
    
    try:
        config.save()
        desc = KeyCodes.describe(vk_code, modifiers)
        print(f"Hotkey set to: {desc}")
    except Exception as e:
        print(f"Error saving config: {e}")
        sys.exit(1)


def cmd_set_model(size: str):
    """Set the model size."""
    valid_sizes = ["tiny.en", "tiny", "base.en", "base", "small.en", "small", 
                   "medium.en", "medium", "large"]
    
    if size not in valid_sizes:
        print(f"Error: Unknown model '{size}'")
        print(f"Available: {', '.join(valid_sizes)}")
        sys.exit(1)
    
    config = Config.load()
    config.model_size = size
    
    try:
        config.save()
        print(f"Model set to: {size}")
        if not Transcriber.model_exists(size):
            print("Model will be downloaded on next start.")
    except Exception as e:
        print(f"Error saving config: {e}")
        sys.exit(1)


def cmd_get_hotkey():
    """Show current hotkey."""
    config = Config.load()
    desc = KeyCodes.describe(config.hotkey.key_code, config.hotkey.modifiers)
    print(f"Current hotkey: {desc}")


def cmd_download_model(size: str):
    """Download a model."""
    try:
        ModelDownloader.download(model_size=size)
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)


def cmd_status():
    """Show status."""
    config = Config.load()
    hotkey_desc = KeyCodes.describe(config.hotkey.key_code, config.hotkey.modifiers)
    
    print(f"open-dictate v{VERSION}")
    print(f"Config:      {Config.get_config_file()}")
    print(f"Hotkey:      {hotkey_desc}")
    print(f"Model:       {config.model_size}")
    print(f"Model ready: {'yes' if Transcriber.model_exists(config.model_size) else 'no'}")
    print(f"whisper-cli: {'yes' if Transcriber.find_whisper_binary() else 'no'}")


def main():
    """Main entry point."""
    args = sys.argv[1:]
    command = args[0] if args else None
    
    if command == "start":
        cmd_start()
    elif command == "set-hotkey":
        if len(args) < 2:
            print("Usage: open-dictate set-hotkey <key>")
            sys.exit(1)
        cmd_set_hotkey(args[1])
    elif command == "set-model":
        if len(args) < 2:
            print("Usage: open-dictate set-model <size>")
            sys.exit(1)
        cmd_set_model(args[1])
    elif command == "get-hotkey":
        cmd_get_hotkey()
    elif command == "download-model":
        size = args[1] if len(args) > 1 else "base.en"
        cmd_download_model(size)
    elif command == "status":
        cmd_status()
    elif command in ("--help", "-h", "help"):
        print_usage()
    elif command is None:
        print_usage()
    else:
        print(f"Unknown command: {command}")
        print_usage()
        sys.exit(1)


if __name__ == "__main__":
    main()
