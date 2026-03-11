"""Audio recording using PyAudio."""

import threading
import wave
from pathlib import Path
from typing import Optional

import pyaudio


class AudioRecorder:
    """Records audio from the default microphone to WAV files."""
    
    # Audio format constants (matching whisper.cpp requirements)
    SAMPLE_RATE = 16000  # 16 kHz
    CHANNELS = 1  # Mono
    FORMAT = pyaudio.paInt16  # 16-bit PCM
    CHUNK_SIZE = 4096  # Buffer size
    
    def __init__(self):
        self._audio: Optional[pyaudio.PyAudio] = None
        self._stream: Optional[pyaudio.Stream] = None
        self._frames: list[bytes] = []
        self._is_recording = False
        self._current_output_path: Optional[Path] = None
        self._lock = threading.Lock()
        self._record_thread: Optional[threading.Thread] = None
    
    def _find_input_device(self) -> int:
        """
        Find a suitable input device.
        
        Returns:
            Device index of an input device, or -1 if none found
        """
        try:
            # Try to get default input device first
            default_device = self._audio.get_default_input_device_info()
            return default_device['index']
        except Exception:
            pass
        
        # Find first device with input channels
        for i in range(self._audio.get_device_count()):
            try:
                info = self._audio.get_device_info_by_index(i)
                if info.get('maxInputChannels', 0) > 0:
                    return i
            except Exception:
                continue
        
        return -1
    
    def start_recording(self, output_path: Path) -> None:
        """
        Start recording audio to the specified file.
        
        Args:
            output_path: Path where the WAV file will be saved
        
        Raises:
            RuntimeError: If already recording
        """
        with self._lock:
            if self._is_recording:
                raise RuntimeError("Already recording")
            
            self._frames = []
            self._current_output_path = output_path
            self._is_recording = True
            
            try:
                self._audio = pyaudio.PyAudio()
                
                # Find an input device
                device_index = self._find_input_device()
                if device_index < 0:
                    raise RuntimeError("No input device found")
                
                # Open stream with callback
                self._stream = self._audio.open(
                    format=self.FORMAT,
                    channels=self.CHANNELS,
                    rate=self.SAMPLE_RATE,
                    input=True,
                    input_device_index=device_index,
                    frames_per_buffer=self.CHUNK_SIZE,
                    stream_callback=self._audio_callback
                )
                
                self._stream.start_stream()
                
            except Exception as e:
                self._cleanup()
                raise RuntimeError(f"Failed to start recording: {e}")
    
    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback for audio stream - called continuously while recording."""
        if self._is_recording:
            self._frames.append(in_data)
        return (in_data, pyaudio.paContinue)
    
    def stop_recording(self) -> Optional[Path]:
        """
        Stop recording and save the audio file.
        
        Returns:
            Path to the saved audio file, or None if recording failed or was too short
        """
        with self._lock:
            if not self._is_recording:
                return None
            
            self._is_recording = False
            output_path = self._current_output_path
            
            try:
                # Stop and close the stream
                if self._stream:
                    self._stream.stop_stream()
                    self._stream.close()
                
                # Save to WAV file
                if self._frames and output_path:
                    self._save_wav(output_path)
                    return output_path
                
                return None
                
            except Exception as e:
                print(f"Error stopping recording: {e}")
                return None
            finally:
                self._cleanup()
    
    def _save_wav(self, output_path: Path) -> None:
        """Save recorded frames to a WAV file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with wave.open(str(output_path), 'wb') as wav_file:
            wav_file.setnchannels(self.CHANNELS)
            wav_file.setsampwidth(self._audio.get_sample_size(self.FORMAT))
            wav_file.setframerate(self.SAMPLE_RATE)
            wav_file.writeframes(b''.join(self._frames))
    
    def _cleanup(self) -> None:
        """Clean up audio resources."""
        if self._stream:
            try:
                self._stream.close()
            except:
                pass
            self._stream = None
        
        if self._audio:
            try:
                self._audio.terminate()
            except:
                pass
            self._audio = None
        
        self._frames = []
        self._current_output_path = None
        self._is_recording = False
    
    @property
    def is_recording(self) -> bool:
        """Check if currently recording."""
        return self._is_recording
