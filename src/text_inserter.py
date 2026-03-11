"""Text insertion via clipboard paste simulation."""

import threading
import time
from typing import Any

import pyperclip
from pynput.keyboard import Controller, Key


class TextInserter:
    """Inserts text at the current cursor position using clipboard paste."""
    
    def __init__(self):
        self._keyboard = Controller()
        self._lock = threading.Lock()
    
    def insert(self, text: str) -> None:
        """
        Insert text at the current cursor position.
        
        This saves the current clipboard content, copies the text to clipboard,
        simulates Ctrl+V paste, then restores the original clipboard content.
        
        Args:
            text: The text to insert
        """
        with self._lock:
            # Save current clipboard content
            original_clipboard = self._save_clipboard()
            
            try:
                # Copy text to clipboard
                pyperclip.copy(text)
                
                # Small delay to ensure clipboard is updated
                time.sleep(0.05)
                
                # Simulate Ctrl+V
                self._simulate_paste()
                
                # Schedule clipboard restore after a short delay
                threading.Timer(0.1, lambda: self._restore_clipboard(original_clipboard)).start()
                
            except Exception as e:
                print(f"Error inserting text: {e}")
                # Try to restore clipboard even on error
                self._restore_clipboard(original_clipboard)
    
    def _save_clipboard(self) -> Any:
        """Save the current clipboard content."""
        try:
            return pyperclip.paste()
        except:
            return ""
    
    def _restore_clipboard(self, content: Any) -> None:
        """Restore clipboard content."""
        try:
            if content:
                pyperclip.copy(content)
            else:
                # If original was empty, try to clear it
                pyperclip.copy("")
        except Exception as e:
            print(f"Warning: Could not restore clipboard: {e}")
    
    def _simulate_paste(self) -> None:
        """Simulate Ctrl+V keyboard shortcut."""
        try:
            # Press Ctrl+V
            with self._keyboard.pressed(Key.ctrl):
                self._keyboard.press('v')
                self._keyboard.release('v')
        except Exception as e:
            print(f"Error simulating paste: {e}")
    
    def copy_to_clipboard(self, text: str) -> None:
        """
        Copy text to clipboard without pasting.
        
        Args:
            text: The text to copy
        """
        try:
            pyperclip.copy(text)
        except Exception as e:
            print(f"Error copying to clipboard: {e}")
