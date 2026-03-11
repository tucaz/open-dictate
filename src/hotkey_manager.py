"""Global hotkey management using pynput."""

import threading
from typing import Callable, Optional, Set

from pynput import keyboard
from pynput.keyboard import Key, KeyCode

from src.key_codes import KeyCodes


class HotkeyManager:
    """Manages global hotkey detection for push-to-talk."""
    
    def __init__(self, key_code: int, modifiers: list[str]):
        """
        Initialize the hotkey manager.
        
        Args:
            key_code: Windows VK code for the trigger key
            modifiers: List of modifier names (e.g., ['ctrl', 'alt'])
        """
        self.key_code = key_code
        self.modifiers = [m.lower() for m in modifiers]
        self._listener: Optional[keyboard.Listener] = None
        self._on_key_down: Optional[Callable[[], None]] = None
        self._on_key_up: Optional[Callable[[], None]] = None
        self._is_pressed = False
        self._currently_pressed: Set[str] = set()
        self._lock = threading.Lock()
        
        # Check if this is a modifier-only key
        self._is_modifier_only = KeyCodes.is_modifier_key(key_code)
    
    def start(self, on_key_down: Callable[[], None], on_key_up: Callable[[], None]) -> None:
        """
        Start listening for global hotkey events.
        
        Args:
            on_key_down: Callback when hotkey is pressed
            on_key_up: Callback when hotkey is released
        """
        self._on_key_down = on_key_down
        self._on_key_up = on_key_up
        
        self._listener = keyboard.Listener(
            on_press=self._on_press,
            on_release=self._on_release,
            suppress=False  # Don't suppress the key events
        )
        self._listener.daemon = True
        self._listener.start()
    
    def stop(self) -> None:
        """Stop listening for hotkey events."""
        if self._listener:
            self._listener.stop()
            self._listener = None
    
    def _on_press(self, key) -> None:
        """Handle key press events."""
        # Track pressed keys
        key_name = self._get_key_name(key)
        if key_name:
            self._currently_pressed.add(key_name)
        
        # Check if this is our trigger key
        vk = self._get_vk_code(key)
        if vk != self.key_code:
            return
        
        with self._lock:
            if self._is_pressed:
                return  # Already pressed, ignore
            
            # Check modifiers
            if self._check_modifiers():
                self._is_pressed = True
                if self._on_key_down:
                    self._on_key_down()
    
    def _on_release(self, key) -> None:
        """Handle key release events."""
        # Track released keys
        key_name = self._get_key_name(key)
        if key_name in self._currently_pressed:
            self._currently_pressed.discard(key_name)
        
        # Check if this is our trigger key
        vk = self._get_vk_code(key)
        if vk != self.key_code:
            return
        
        with self._lock:
            if not self._is_pressed:
                return  # Wasn't pressed, ignore
            
            self._is_pressed = False
            if self._on_key_up:
                self._on_key_up()
    
    def _get_vk_code(self, key) -> Optional[int]:
        """Get Windows VK code from pynput key."""
        if isinstance(key, KeyCode):
            # Regular key with vk code
            return key.vk
        elif isinstance(key, Key):
            # Special key - map to VK code
            return self._key_to_vk(key)
        return None
    
    def _get_key_name(self, key) -> Optional[str]:
        """Get key name for tracking pressed state."""
        if isinstance(key, KeyCode):
            return f"vk_{key.vk}"
        elif isinstance(key, Key):
            return key.name
        return None
    
    def _key_to_vk(self, key: Key) -> Optional[int]:
        """Map pynput Key to Windows VK code."""
        key_map = {
            Key.alt: KeyCodes.VK_MENU,
            Key.alt_l: KeyCodes.VK_LMENU,
            Key.alt_r: KeyCodes.VK_RMENU,
            Key.alt_gr: KeyCodes.VK_RMENU,
            Key.backspace: KeyCodes.VK_BACK,
            Key.caps_lock: KeyCodes.VK_CAPITAL,
            Key.cmd: KeyCodes.VK_LWIN,
            Key.cmd_l: KeyCodes.VK_LWIN,
            Key.cmd_r: KeyCodes.VK_RWIN,
            Key.ctrl: KeyCodes.VK_CONTROL,
            Key.ctrl_l: KeyCodes.VK_LCONTROL,
            Key.ctrl_r: KeyCodes.VK_RCONTROL,
            Key.delete: KeyCodes.VK_DELETE,
            Key.down: KeyCodes.VK_DOWN,
            Key.end: KeyCodes.VK_END,
            Key.enter: KeyCodes.VK_RETURN,
            Key.esc: KeyCodes.VK_ESCAPE,
            Key.f1: KeyCodes.VK_F1,
            Key.f2: KeyCodes.VK_F2,
            Key.f3: KeyCodes.VK_F3,
            Key.f4: KeyCodes.VK_F4,
            Key.f5: KeyCodes.VK_F5,
            Key.f6: KeyCodes.VK_F6,
            Key.f7: KeyCodes.VK_F7,
            Key.f8: KeyCodes.VK_F8,
            Key.f9: KeyCodes.VK_F9,
            Key.f10: KeyCodes.VK_F10,
            Key.f11: KeyCodes.VK_F11,
            Key.f12: KeyCodes.VK_F12,
            Key.f13: KeyCodes.VK_F13,
            Key.f14: KeyCodes.VK_F14,
            Key.f15: KeyCodes.VK_F15,
            Key.f16: KeyCodes.VK_F16,
            Key.f17: KeyCodes.VK_F17,
            Key.f18: KeyCodes.VK_F18,
            Key.f19: KeyCodes.VK_F19,
            Key.f20: KeyCodes.VK_F20,
            Key.home: KeyCodes.VK_HOME,
            Key.insert: KeyCodes.VK_INSERT,
            Key.left: KeyCodes.VK_LEFT,
            Key.page_down: KeyCodes.VK_NEXT,
            Key.page_up: KeyCodes.VK_PRIOR,
            Key.pause: KeyCodes.VK_PAUSE,
            Key.print_screen: KeyCodes.VK_SNAPSHOT,
            Key.right: KeyCodes.VK_RIGHT,
            Key.shift: KeyCodes.VK_SHIFT,
            Key.shift_l: KeyCodes.VK_LSHIFT,
            Key.shift_r: KeyCodes.VK_RSHIFT,
            Key.space: KeyCodes.VK_SPACE,
            Key.tab: KeyCodes.VK_TAB,
            Key.up: KeyCodes.VK_UP,
        }
        return key_map.get(key)
    
    def _check_modifiers(self) -> bool:
        """Check if required modifiers are pressed."""
        if not self.modifiers:
            return True
        
        # Map required modifiers to key names
        required = set()
        for mod in self.modifiers:
            if mod in ("ctrl", "control"):
                required.add("ctrl")
                required.add("ctrl_l")
                required.add("ctrl_r")
            elif mod == "shift":
                required.add("shift")
                required.add("shift_l")
                required.add("shift_r")
            elif mod in ("alt", "menu"):
                required.add("alt")
                required.add("alt_l")
                required.add("alt_r")
                required.add("alt_gr")
            elif mod in ("win", "windows", "cmd", "command"):
                required.add("cmd")
                required.add("cmd_l")
                required.add("cmd_r")
        
        # Check if any of the currently pressed keys match the required modifiers
        # We need to track modifier state more carefully
        current_mods = set()
        for key in self._currently_pressed:
            if key.startswith("ctrl"):
                current_mods.add("ctrl")
            elif key.startswith("shift"):
                current_mods.add("shift")
            elif key.startswith("alt"):
                current_mods.add("alt")
            elif key.startswith("cmd"):
                current_mods.add("win")
        
        # Check if all required modifiers are present
        required_base = set()
        for mod in self.modifiers:
            if mod in ("ctrl", "control"):
                required_base.add("ctrl")
            elif mod == "shift":
                required_base.add("shift")
            elif mod in ("alt", "menu"):
                required_base.add("alt")
            elif mod in ("win", "windows", "cmd", "command"):
                required_base.add("win")
        
        return required_base.issubset(current_mods)
