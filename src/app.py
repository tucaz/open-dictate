"""Main application orchestrator."""

import subprocess
import threading
import time
from pathlib import Path

from src.audio_recorder import AudioRecorder
from src.config import Config
from src.hotkey_manager import HotkeyManager
from src.key_codes import KeyCodes
from src.launcher import launch_tray_process
from src.model_downloader import ModelDownloader
from src.permissions import Permissions
from src.recording_store import RecordingStore
from src.text_inserter import TextInserter
from src.text_processor import TextPostProcessor
from src.transcriber import Transcriber
from src.tray_controller import State, TrayController
from src.version import VERSION


class OpenDictateApp:
    """Main application class that orchestrates all components."""
    
    def __init__(self):
        self.config: Config = Config.default_config()
        self.tray = TrayController()
        self.recorder = AudioRecorder()
        self.transcriber: Transcriber = None
        self.inserter = TextInserter()
        self.hotkey_manager: HotkeyManager = None
        
        self.is_pressed = False
        self.is_ready = False
        self.last_transcription: str = None
        self._is_shutting_down = False
        
        # Set up tray handlers
        self.tray.reprocess_handler = self.reprocess
        self.tray.reload_config_handler = self.reload_config
        self.tray.open_config_handler = self.open_config
        self.tray.copy_last_handler = self.copy_last_transcription
        self.tray.get_last_transcription = lambda: self.last_transcription
        self.tray.restart_handler = self.restart
    
    def run(self) -> None:
        """Run the application."""
        # Run setup in a background thread
        setup_thread = threading.Thread(target=self._setup, daemon=True)
        setup_thread.start()
        
        # Run the tray icon (blocking)
        self.tray.run()
        
        # Clean up
        self.shutdown()
    
    def _setup(self) -> None:
        """Set up the application components."""
        try:
            self._setup_inner()
        except Exception as e:
            print(f"Fatal setup error: {e}")
            self.tray.set_state(State.WAITING_FOR_PERMISSION)
    
    def _setup_inner(self) -> None:
        """Internal setup logic."""
        # Load configuration
        self.config = Config.load()
        
        # Clean up recordings if in privacy mode
        if Config.effective_max_recordings(self.config.max_recordings) == 0:
            RecordingStore.delete_all()
        
        # Initialize transcriber
        self.transcriber = Transcriber(
            model_size=self.config.model_size,
            language=self.config.language
        )
        if self.config.spoken_punctuation:
            self.transcriber.spoken_punctuation = bool(self.config.spoken_punctuation)
        
        # Check for whisper-cli
        if not Transcriber.find_whisper_binary():
            print("Error: whisper-cli not found")
            print("Please install whisper.cpp or place whisper-cli.exe in PATH")
            self.tray.set_state(State.WAITING_FOR_PERMISSION)
            return
        
        # Check microphone permission
        Permissions.ensure_microphone()
        
        # Download model if needed
        if not Transcriber.model_exists(self.config.model_size):
            self.tray.set_state(State.DOWNLOADING)
            self.tray.update_download_progress(f"Downloading {self.config.model_size} model...")
            print(f"Downloading {self.config.model_size} model...")
            
            try:
                ModelDownloader.download(self.config.model_size)
                self.tray.update_download_progress(None)
            except Exception as e:
                print(f"Failed to download model: {e}")
                self.tray.set_state(State.WAITING_FOR_PERMISSION)
                return
        
        # Start hotkey listener on main thread
        self._start_listening()
    
    def _start_listening(self) -> None:
        """Start the hotkey listener."""
        self.hotkey_manager = HotkeyManager(
            key_code=self.config.hotkey.key_code,
            modifiers=self.config.hotkey.modifiers
        )
        
        self.hotkey_manager.start(
            on_key_down=self.handle_key_down,
            on_key_up=self.handle_key_up
        )
        
        self.is_ready = True
        self.tray.set_state(State.IDLE)
        
        hotkey_desc = KeyCodes.describe(
            self.config.hotkey.key_code,
            self.config.hotkey.modifiers
        )
        
        print(f"open-dictate v{VERSION}")
        print(f"Hotkey: {hotkey_desc}")
        print(f"Model: {self.config.model_size}")
        print("Ready.")
    
    def reload_config(self) -> None:
        """Reload configuration and restart hotkey listener."""
        if not self.is_ready:
            return
        
        print("Reloading configuration...")
        
        # Load new config
        self.config = Config.load()
        
        # Update transcriber
        self.transcriber = Transcriber(
            model_size=self.config.model_size,
            language=self.config.language
        )
        if self.config.spoken_punctuation:
            self.transcriber.spoken_punctuation = bool(self.config.spoken_punctuation)
        
        # Restart hotkey listener
        if self.hotkey_manager:
            self.hotkey_manager.stop()
        
        self.hotkey_manager = HotkeyManager(
            key_code=self.config.hotkey.key_code,
            modifiers=self.config.hotkey.modifiers
        )
        self.hotkey_manager.start(
            on_key_down=self.handle_key_down,
            on_key_up=self.handle_key_up
        )
        
        hotkey_desc = KeyCodes.describe(
            self.config.hotkey.key_code,
            self.config.hotkey.modifiers
        )
        print(f"Config reloaded: hotkey={hotkey_desc} model={self.config.model_size}")
        
        self.tray._build_menu()
    
    def open_config(self) -> None:
        """Open the configuration file in default editor."""
        config_file = Config.get_config_file()
        
        if not config_file.exists():
            Config.default_config().save()
        
        # Open with default editor
        try:
            subprocess.run(["notepad", str(config_file)], check=False)
        except Exception as e:
            print(f"Could not open config: {e}")
            # Try alternative method
            import os
            os.startfile(str(config_file))
    
    def handle_key_down(self) -> None:
        """Handle hotkey press - start recording."""
        if not self.is_ready or self.is_pressed:
            return
        
        self.is_pressed = True
        self.tray.set_state(State.RECORDING)
        
        try:
            # Determine output path
            max_recordings = Config.effective_max_recordings(self.config.max_recordings)
            if max_recordings == 0:
                output_path = RecordingStore.get_temp_path()
            else:
                output_path = RecordingStore.new_recording_path()
            
            self.recorder.start_recording(output_path)
            
        except Exception as e:
            print(f"Error starting recording: {e}")
            self.is_pressed = False
            self.tray.set_state(State.IDLE)
    
    def handle_key_up(self) -> None:
        """Handle hotkey release - stop recording and transcribe."""
        if not self.is_pressed:
            return
        
        self.is_pressed = False
        
        # Stop recording
        audio_path = self.recorder.stop_recording()
        if not audio_path:
            self.tray.set_state(State.IDLE)
            return
        
        self.tray.set_state(State.TRANSCRIBING)
        
        # Process in background thread
        thread = threading.Thread(
            target=self._process_audio,
            args=(audio_path,),
            daemon=True
        )
        thread.start()
    
    def _process_audio(self, audio_path: Path) -> None:
        """Process the recorded audio file."""
        max_recordings = Config.effective_max_recordings(self.config.max_recordings)
        
        try:
            # Transcribe
            raw_text = self.transcriber.transcribe(audio_path)
            
            # Post-process if needed
            if self.config.spoken_punctuation and self.config.spoken_punctuation.value:
                text = TextPostProcessor.process(raw_text)
            else:
                text = raw_text
            
            # Clean up recording if in privacy mode
            if max_recordings == 0:
                try:
                    audio_path.unlink()
                except:
                    pass
            else:
                # Prune old recordings
                RecordingStore.prune(max_count=max_recordings)
            
            # Insert text if we got something
            if text.strip():
                self.last_transcription = text
                self.inserter.insert(text)
            
            # Update UI
            self.tray.set_state(State.IDLE)
            self.tray._build_menu()
            
        except Exception as e:
            print(f"Transcription error: {e}")
            
            # Clean up on error
            if max_recordings == 0:
                try:
                    audio_path.unlink()
                except:
                    pass
            else:
                RecordingStore.prune(max_count=max_recordings)
            
            self.tray.set_state(State.IDLE)
            self.tray._build_menu()
    
    def reprocess(self, audio_path: Path) -> None:
        """Re-transcribe an existing recording."""
        if self.tray._state != State.IDLE:
            return
        
        self.tray.set_state(State.TRANSCRIBING)
        
        thread = threading.Thread(
            target=self._reprocess_audio,
            args=(audio_path,),
            daemon=True
        )
        thread.start()
    
    def _reprocess_audio(self, audio_path: Path) -> None:
        """Re-transcribe and copy to clipboard."""
        try:
            # Transcribe
            raw_text = self.transcriber.transcribe(audio_path)
            
            # Post-process if needed
            if self.config.spoken_punctuation and self.config.spoken_punctuation.value:
                text = TextPostProcessor.process(raw_text)
            else:
                text = raw_text
            
            if text.strip():
                self.last_transcription = text
                self.inserter.copy_to_clipboard(text)
                
                # Show copied feedback
                self.tray.set_state(State.COPIED_TO_CLIPBOARD)
                time.sleep(1.5)
            
            self.tray.set_state(State.IDLE)
            
        except Exception as e:
            print(f"Reprocess error: {e}")
            self.tray.set_state(State.IDLE)
    
    def copy_last_transcription(self) -> None:
        """Copy the last transcription to clipboard."""
        if self.last_transcription:
            self.inserter.copy_to_clipboard(self.last_transcription)
    
    def restart(self) -> None:
        """Restart the application."""
        print("Restarting...")

        try:
            launch_tray_process()
        except OSError as e:
            print(f"Restart failed: {e}")
            return

        self.shutdown()
    
    def shutdown(self) -> None:
        """Clean up resources before exit."""
        if self._is_shutting_down:
            return

        self._is_shutting_down = True
        print("Shutting down...")
        
        if self.hotkey_manager:
            self.hotkey_manager.stop()
        
        if self.recorder.is_recording:
            self.recorder.stop_recording()
        
        self.tray.stop()
