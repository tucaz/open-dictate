"""System tray icon and menu controller."""

import io
import threading
import time
from datetime import datetime
from enum import Enum, auto
from pathlib import Path
from typing import Callable, List, Optional

import pystray
from PIL import Image, ImageDraw

from src.config import Config
from src.key_codes import KeyCodes
from src.recording_store import Recording, RecordingStore
from src.version import VERSION


class State(Enum):
    """Tray icon states."""
    IDLE = auto()
    RECORDING = auto()
    TRANSCRIBING = auto()
    DOWNLOADING = auto()
    WAITING_FOR_PERMISSION = auto()
    COPIED_TO_CLIPBOARD = auto()


class TrayController:
    """Manages the system tray icon and menu."""
    
    ICON_SIZE = 64  # Size of the generated icon
    ANIMATION_FPS = 30
    
    # Brand color: rgb(0, 81, 162)
    BRAND_COLOR = (0, 81, 162, 255)
    BRAND_COLOR_LIGHT = (0, 120, 200, 255)
    
    def __init__(self):
        self.icon = pystray.Icon("open-dictate")
        self._state = State.IDLE
        self._animation_thread: Optional[threading.Thread] = None
        self._stop_animation = threading.Event()
        self._download_progress: Optional[str] = None
        self._copied_feedback = False
        self._menu_actions: List[Callable] = []
        
        # Handlers that can be set externally
        self.reprocess_handler: Optional[Callable[[Path], None]] = None
        self.reload_config_handler: Optional[Callable[[], None]] = None
        self.open_config_handler: Optional[Callable[[], None]] = None
        self.copy_last_handler: Optional[Callable[[], None]] = None
        self.get_last_transcription: Optional[Callable[[], Optional[str]]] = None
        self.restart_handler: Optional[Callable[[], None]] = None
        
        # Build initial icon
        self.icon.icon = self._draw_idle_icon()
        self.icon.title = "open-dictate"
        self._build_menu()
    
    def set_state(self, state: State) -> None:
        """Update the tray icon state."""
        if self._state == state:
            return
        
        self._state = state
        self._stop_animation.set()
        
        if self._animation_thread and self._animation_thread.is_alive():
            self._animation_thread.join(timeout=0.5)
        
        self._stop_animation.clear()
        
        if state == State.IDLE:
            self.icon.icon = self._draw_idle_icon()
        elif state == State.RECORDING:
            self._start_recording_animation()
        elif state == State.TRANSCRIBING:
            self._start_transcribing_animation()
        elif state == State.DOWNLOADING:
            self._start_downloading_animation()
        elif state == State.WAITING_FOR_PERMISSION:
            self.icon.icon = self._draw_lock_icon()
        elif state == State.COPIED_TO_CLIPBOARD:
            self.icon.icon = self._draw_checkmark_icon()
        
        self._build_menu()
    
    def update_download_progress(self, text: Optional[str]) -> None:
        """Update the download progress text."""
        self._download_progress = text
        self._build_menu()
    
    def _build_menu(self) -> None:
        """Build the context menu."""
        config = Config.load()
        hotkey_desc = KeyCodes.describe(config.hotkey.key_code, config.hotkey.modifiers)
        
        # Get last transcription
        last_text = None
        if self.get_last_transcription:
            last_text = self.get_last_transcription()
        
        # State text
        state_texts = {
            State.IDLE: "Ready",
            State.RECORDING: "Recording...",
            State.TRANSCRIBING: "Transcribing...",
            State.DOWNLOADING: "Downloading model...",
            State.WAITING_FOR_PERMISSION: "Waiting for permission...",
            State.COPIED_TO_CLIPBOARD: "Copied to clipboard",
        }
        
        items = [
            pystray.MenuItem(f"open-dictate v{VERSION}", None, enabled=False),
            pystray.Menu.SEPARATOR,
        ]
        
        if self._download_progress:
            items.append(pystray.MenuItem(self._download_progress, None, enabled=False))
            items.append(pystray.Menu.SEPARATOR)
        
        items.extend([
            pystray.MenuItem(state_texts[self._state], None, enabled=False),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem(f"Hotkey: {hotkey_desc}", None, enabled=False),
            pystray.MenuItem(f"Model: {config.model_size}", None, enabled=False),
            pystray.Menu.SEPARATOR,
        ])
        
        # Copy last dictation
        copy_title = "Copied!" if self._copied_feedback else "Copy Last Dictation"
        can_copy = last_text is not None and not self._copied_feedback
        items.append(pystray.MenuItem(
            copy_title,
            self._on_copy_last if can_copy else None,
            enabled=can_copy
        ))
        
        # Recent recordings submenu
        recordings = RecordingStore.list_recordings()
        recording_items = []
        
        if not recordings:
            recording_items.append(pystray.MenuItem("No recordings", None, enabled=False))
        else:
            for i, recording in enumerate(recordings[:10]):  # Show last 10
                date_str = recording.date.strftime("%Y-%m-%d %H:%M")
                label = f"{date_str} ({i + 1})"
                # Create closure to capture path; pystray passes (icon, item)
                def make_handler(p):
                    return lambda icon, item: self._on_reprocess(p)
                recording_items.append(pystray.MenuItem(
                    label,
                    make_handler(recording.path)
                ))
        
        items.append(pystray.MenuItem("Recent Recordings", pystray.Menu(*recording_items)))
        items.append(pystray.Menu.SEPARATOR)
        
        items.extend([
            pystray.MenuItem("Reload Configuration", self._on_reload_config),
            pystray.MenuItem("Open Configuration", self._on_open_config),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem("Restart", self._on_restart),
            pystray.MenuItem("Quit", self._on_quit),
        ])
        
        self.icon.menu = pystray.Menu(*items)
    
    def _on_copy_last(self) -> None:
        """Handle copy last dictation menu item."""
        if self.copy_last_handler:
            self.copy_last_handler()
        
        self._copied_feedback = True
        self._build_menu()
        
        # Reset feedback after 2 seconds
        threading.Timer(2.0, self._reset_copied_feedback).start()
    
    def _reset_copied_feedback(self) -> None:
        """Reset the copied feedback state."""
        self._copied_feedback = False
        self._build_menu()
    
    def _on_reprocess(self, path: Path) -> None:
        """Handle reprocess menu item."""
        if self.reprocess_handler:
            self.reprocess_handler(path)
    
    def _on_reload_config(self) -> None:
        """Handle reload config menu item."""
        if self.reload_config_handler:
            self.reload_config_handler()
        self._build_menu()
    
    def _on_restart(self) -> None:
        """Handle restart menu item."""
        if self.restart_handler:
            self.restart_handler()
    
    def _on_open_config(self) -> None:
        """Handle open config menu item."""
        if self.open_config_handler:
            self.open_config_handler()
    
    def _on_quit(self) -> None:
        """Handle quit menu item."""
        self.icon.stop()
    
    def run(self) -> None:
        """Run the tray icon (blocking)."""
        self.icon.run()
    
    def stop(self) -> None:
        """Stop the tray icon."""
        self._stop_animation.set()
        self.icon.stop()
    
    # ==================== Icon Drawing ====================
    
    def _create_image(self) -> Image.Image:
        """Create a new transparent image."""
        return Image.new('RGBA', (self.ICON_SIZE, self.ICON_SIZE), (0, 0, 0, 0))
    
    def _load_logo_icon(self) -> Image.Image:
        """Load the logo image for the idle state."""
        # Look for logo in various locations
        logo_paths = [
            Path(__file__).parent.parent.parent / "website" / "logo.png",
            Path(__file__).parent.parent.parent / "assets" / "logo.png",
            Path.cwd() / "website" / "logo.png",
            Path.cwd() / "assets" / "logo.png",
        ]
        
        for logo_path in logo_paths:
            if logo_path.exists():
                try:
                    img = Image.open(logo_path)
                    # Resize to icon size if needed
                    if img.size != (self.ICON_SIZE, self.ICON_SIZE):
                        img = img.resize((self.ICON_SIZE, self.ICON_SIZE), Image.Resampling.LANCZOS)
                    # Ensure RGBA mode
                    if img.mode != 'RGBA':
                        img = img.convert('RGBA')
                    return img
                except Exception:
                    pass
        
        # Fallback: draw waveform with brand color
        return self._draw_waveform_icon()
    
    def _draw_waveform_icon(self) -> Image.Image:
        """Draw the waveform icon with brand color."""
        img = self._create_image()
        draw = ImageDraw.Draw(img)
        
        # Draw 5 bars of different heights
        bar_width = 7
        gap = 9
        heights = [16, 32, 48, 32, 16]  # Scaled for 64x64
        radius = 3
        
        center_x = self.ICON_SIZE // 2
        center_y = self.ICON_SIZE // 2
        total_width = len(heights) * bar_width + (len(heights) - 1) * gap
        start_x = center_x - total_width // 2
        
        for i, height in enumerate(heights):
            x = start_x + i * (bar_width + gap)
            y = center_y - height // 2
            draw.rounded_rectangle(
                [x, y, x + bar_width, y + height],
                radius=radius,
                fill=self.BRAND_COLOR
            )
        
        return img
    
    def _draw_idle_icon(self) -> Image.Image:
        """Draw the idle state icon (logo or waveform)."""
        return self._load_logo_icon()
    
    def _start_recording_animation(self) -> None:
        """Start the recording animation (bouncing waveform)."""
        def animate():
            frame_count = 30
            bar_width = 7
            gap = 9
            base_heights = [16, 32, 48, 32, 16]
            radius = 3
            min_scale = 0.3
            phase_offsets = [0.0, 0.15, 0.3, 0.45, 0.6]
            
            frame = 0
            while not self._stop_animation.is_set():
                t = frame / frame_count
                
                img = self._create_image()
                draw = ImageDraw.Draw(img)
                
                center_x = self.ICON_SIZE // 2
                center_y = self.ICON_SIZE // 2
                total_width = len(base_heights) * bar_width + (len(base_heights) - 1) * gap
                start_x = center_x - total_width // 2
                
                for i, base_height in enumerate(base_heights):
                    phase = t - phase_offsets[i]
                    import math
                    scale = min_scale + (1.0 - min_scale) * ((math.sin(phase * 2.0 * math.pi) + 1.0) / 2.0)
                    height = base_height * scale
                    x = start_x + i * (bar_width + gap)
                    y = center_y - height / 2
                    draw.rounded_rectangle(
                        [x, y, x + bar_width, y + height],
                        radius=radius,
                        fill=self.BRAND_COLOR
                    )
                
                self.icon.icon = img
                
                frame = (frame + 1) % frame_count
                time.sleep(1.0 / self.ANIMATION_FPS)
        
        self._animation_thread = threading.Thread(target=animate, daemon=True)
        self._animation_thread.start()
    
    def _start_transcribing_animation(self) -> None:
        """Start the transcribing animation (bouncing dots)."""
        def animate():
            frame_count = 30
            dot_size = 10
            gap = 12
            max_bounce = 10
            
            frame = 0
            while not self._stop_animation.is_set():
                t = frame / frame_count
                
                img = self._create_image()
                draw = ImageDraw.Draw(img)
                
                center_y = self.ICON_SIZE // 2 - dot_size // 2
                total_width = 3 * dot_size + 2 * gap
                start_x = (self.ICON_SIZE - total_width) // 2
                
                import math
                for i in range(3):
                    phase = t - i * 0.15
                    bounce = max_bounce * max(0, math.sin(phase * 2.0 * math.pi))
                    x = start_x + i * (dot_size + gap)
                    y = center_y - bounce
                    draw.ellipse(
                        [x, y, x + dot_size, y + dot_size],
                        fill=self.BRAND_COLOR
                    )
                
                self.icon.icon = img
                
                frame = (frame + 1) % frame_count
                time.sleep(1.0 / self.ANIMATION_FPS)
        
        self._animation_thread = threading.Thread(target=animate, daemon=True)
        self._animation_thread.start()
    
    def _start_downloading_animation(self) -> None:
        """Start the downloading animation (arrow moving down)."""
        def animate():
            frame_count = 3
            frame = 0
            
            while not self._stop_animation.is_set():
                img = self._create_image()
                draw = ImageDraw.Draw(img)
                
                center_x = self.ICON_SIZE // 2
                offset = frame * 5
                
                # Draw base line
                base_y = 12
                draw.line(
                    [(center_x - 18, base_y), (center_x + 18, base_y)],
                    fill=self.BRAND_COLOR,
                    width=5
                )
                
                # Draw arrow
                arrow_y = 48 - offset
                draw.line(
                    [(center_x, arrow_y), (center_x, base_y + 8)],
                    fill=self.BRAND_COLOR,
                    width=5
                )
                
                # Draw arrow head
                draw.polygon(
                    [(center_x - 10, base_y + 18), (center_x, base_y + 8), (center_x + 10, base_y + 18)],
                    fill=self.BRAND_COLOR
                )
                
                self.icon.icon = img
                
                frame = (frame + 1) % frame_count
                time.sleep(0.5)
        
        self._animation_thread = threading.Thread(target=animate, daemon=True)
        self._animation_thread.start()
    
    def _draw_lock_icon(self) -> Image.Image:
        """Draw a lock icon for waiting state."""
        img = self._create_image()
        draw = ImageDraw.Draw(img)
        
        center_x = self.ICON_SIZE // 2
        
        # Draw lock body
        body_rect = [center_x - 16, 24, center_x + 16, 56]
        draw.rounded_rectangle(body_rect, radius=4, fill=self.BRAND_COLOR)
        
        # Draw lock shackle
        shackle_rect = [center_x - 10, 8, center_x + 10, 32]
        draw.arc(shackle_rect, start=0, end=180, fill=self.BRAND_COLOR, width=5)
        
        return img
    
    def _draw_checkmark_icon(self) -> Image.Image:
        """Draw a checkmark icon for copied state."""
        img = self._create_image()
        draw = ImageDraw.Draw(img)
        
        center_x = self.ICON_SIZE // 2
        center_y = self.ICON_SIZE // 2
        
        # Draw checkmark
        points = [
            (center_x - 20, center_y),
            (center_x - 8, center_y + 12),
            (center_x + 20, center_y - 16)
        ]
        draw.line(points, fill=self.BRAND_COLOR, width=7, joint="curve")
        
        return img
