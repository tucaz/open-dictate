"""Windows permissions checking."""

import sys

import pyaudio


class MicrophoneError(Exception):
    """Microphone access error with diagnostics."""
    
    def __init__(self, message, devices=None):
        super().__init__(message)
        self.devices = devices or []


class Permissions:
    """Handles Windows permission checks."""
    
    @staticmethod
    def find_input_device(audio: pyaudio.PyAudio) -> int:
        """
        Find a suitable input device.
        
        Returns:
            Device index of an input device, or -1 if none found
        """
        try:
            # Try to get default input device first
            default_device = audio.get_default_input_device_info()
            return default_device['index']
        except Exception:
            pass
        
        # Find first device with input channels
        for i in range(audio.get_device_count()):
            try:
                info = audio.get_device_info_by_index(i)
                if info.get('maxInputChannels', 0) > 0:
                    return i
            except Exception:
                continue
        
        return -1
    
    @staticmethod
    def check_microphone_access() -> bool:
        """
        Check if we have microphone access.
        
        Returns:
            True if microphone is accessible, False otherwise
        """
        try:
            audio = pyaudio.PyAudio()
            
            # Find an input device
            device_index = Permissions.find_input_device(audio)
            if device_index < 0:
                audio.terminate()
                return False
            
            # Try to open the input device
            stream = audio.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=16000,
                input=True,
                input_device_index=device_index,
                frames_per_buffer=1024
            )
            
            # Try to read a small amount of data
            stream.read(1024, exception_on_overflow=False)
            
            stream.stop_stream()
            stream.close()
            audio.terminate()
            
            return True
            
        except Exception as e:
            return False
    
    @staticmethod
    def list_input_devices() -> list[dict]:
        """List all available input devices."""
        devices = []
        try:
            audio = pyaudio.PyAudio()
            for i in range(audio.get_device_count()):
                try:
                    info = audio.get_device_info_by_index(i)
                    if info.get('maxInputChannels', 0) > 0:
                        devices.append({
                            'index': i,
                            'name': info['name'],
                            'channels': info['maxInputChannels']
                        })
                except Exception:
                    pass
            audio.terminate()
        except Exception:
            pass
        return devices
    
    @staticmethod
    def ensure_microphone() -> None:
        """
        Ensure microphone access, printing status and guiding user if needed.
        
        On Windows, microphone permissions are typically granted at app level
        in Settings > Privacy > Microphone.
        """
        if Permissions.check_microphone_access():
            print("Microphone: granted")
            return
        
        print("Microphone: denied or not available")
        
        # List available devices for diagnostics
        devices = Permissions.list_input_devices()
        if devices:
            print("\nAvailable input devices:")
            for d in devices:
                print(f"  [{d['index']}] {d['name']}")
        else:
            print("\nNo input devices detected!")
        
        print("\nTroubleshooting steps:")
        print("1. Check Settings > Privacy & Security > Microphone")
        print("   - Ensure 'Microphone access' is ON")
        print("   - Ensure 'Let apps access your microphone' is ON")
        print("   - If Python is listed, ensure it's allowed")
        print("2. Check that a microphone is connected and not muted")
        print("3. Try running this terminal as Administrator")
        print("4. Check your sound settings to ensure a default input device is set")
        
        sys.exit(1)
    
    @staticmethod
    def is_running_as_admin() -> bool:
        """Check if the application is running with administrator privileges."""
        try:
            import ctypes
            return ctypes.windll.shell32.IsUserAnAdmin()
        except:
            return False
