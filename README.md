# Open-Dictate for Windows

Local, private voice dictation for Windows. Hold a key, speak, release - your words appear at the cursor.

Everything runs on-device. No audio or text ever leaves your machine.

Powered by [whisper.cpp](https://github.com/ggerganov/whisper.cpp).

## About This Project

This is a **Windows port** of the macOS app [open-wispr](https://github.com/human37/open-wispr) by [human37](https://github.com/human37). The original macOS app was written in Swift; this version is a rewrite in Python for Windows compatibility under the name **open-dictate**.

- **Original macOS app:** https://github.com/human37/open-wispr
- **This Windows port:** https://github.com/tucaz/open-dictate

## Quick Start (Choose Your Path)

**I want to USE the app ->** See [User Installation](#user-installation) below  
**I want to BUILD/DEVELOP ->** See [Developer Guide](#developer-guide) further down

## User Installation

For end users who just want to use the app.

### Requirements

- Windows 10 or Windows 11
- A microphone

### Option 1: One-liner install (recommended)

Copy and paste this into PowerShell:

```powershell
powershell -ExecutionPolicy Bypass -Command "Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://raw.githubusercontent.com/tucaz/open-dictate/main/scripts/install.ps1'))"
```

This will:

1. Download the latest release from GitHub
2. Install to `%LOCALAPPDATA%\open-dictate\`
3. Add to your PATH
4. Create Start Menu shortcuts

Then run: `open-dictate start`

### Option 2: Portable mode (no install)

1. Download `open-dictate-windows-vX.X.X.zip` from [GitHub Releases](https://github.com/tucaz/open-dictate/releases)
2. Extract to any folder (Desktop, USB drive, etc.)
3. Run: `open-dictate.exe start`

### First Run

The Whisper model (~150MB for `base.en`) is automatically downloaded on first use to:

```text
%APPDATA%\open-dictate\models\
```

### Usage

**Default hotkey: Right Ctrl**

Hold Right Ctrl -> Speak -> Release -> Text appears at cursor

Change hotkey:

```powershell
open-dictate set-hotkey rightctrl  # Right Ctrl (default)
open-dictate set-hotkey insert     # Insert key
open-dictate set-hotkey ctrl+space # Ctrl+Space
```

> Avoid Alt combinations (like Alt+R) as they activate menu bars in many apps.

### Configuration

Edit `%APPDATA%\open-dictate\config.json`:

```json
{
  "hotkey": { "keyCode": 163, "modifiers": [] },
  "modelSize": "base.en",
  "language": "en",
  "spokenPunctuation": false,
  "maxRecordings": 0
}
```

| Option | Default | Description |
|------|------|------|
| `modelSize` | `base.en` | Whisper model to use. `.en` models are English-only; use `base`, `small`, etc. for other languages |
| `language` | `en` | Whisper language code (`pt`, `es`, `fr`, etc.) |
| `spokenPunctuation` | `false` | Say "comma", "period" for punctuation |
| `maxRecordings` | `0` | Recordings to keep (0 = privacy mode) |

### Other Languages (example: pt-BR)

The default installer downloads `base.en`, which is an English-only model. For Brazilian Portuguese or other non-English languages:

```powershell
open-dictate download-model base
open-dictate set-model base
```

Then edit `%APPDATA%\open-dictate\config.json` and change:

```json
{
  "language": "pt"
}
```

Notes:

- Use `pt` for Portuguese, including Brazilian Portuguese
- If you want better recognition quality and can afford more CPU/RAM, use `small` instead of `base`
- Setting `language` to `pt` while keeping `base.en` is the wrong combination for Portuguese dictation, because `base.en` is English-only

### System Tray Menu

Right-click the waveform icon:

- **Copy Last Dictation** - Recover your most recent transcription
- **Recent Recordings** - Re-transcribe previous recordings (requires `maxRecordings > 0` in config)
- **Reload Configuration** - Reload config without restart
- **Restart** - Restart the application
- **Quit** - Exit

### Uninstall

```powershell
powershell -ExecutionPolicy Bypass -File scripts/uninstall.ps1
```

Or manually delete:

- `%LOCALAPPDATA%\open-dictate\` (if installed)
- `%APPDATA%\open-dictate\` (config, models, recordings)

## Developer Guide

For developers who want to build from source or modify the app.

### Quick Start (Development)

```powershell
# Clone
git clone https://github.com/tucaz/open-dictate.git
cd open-dictate

# Install dependencies
pip install -r requirements.txt

# Run from source
python -m src start
```

### Building a Release

```powershell
# Build complete release package
powershell -ExecutionPolicy Bypass -File scripts/build-release.ps1
```

Output:

- `release/open-dictate-v1.0.0/` - Release folder
- `release/open-dictate-windows-v1.0.0.zip` - Distribution zip

The script:

1. Builds `open-dictate.exe` using PyInstaller
2. Downloads `whisper-cli.exe` and DLLs
3. Packages everything with README and install script
4. Creates release info with checksums

### Installing Your Built Release

After building, you have two options:

**A. Install locally (for testing):**

```powershell
# From the release folder
cd release/open-dictate-v1.0.0
powershell -ExecutionPolicy Bypass -File install.ps1
```

**B. Run portable (no install):**

```powershell
cd release/open-dictate-v1.0.0
.\open-dictate.exe start
```

### Project Structure

```text
open-dictate/
|-- src/                  # Main Python package
|   |-- app.py            # Main orchestrator
|   |-- audio_recorder.py
|   |-- hotkey_manager.py
|   |-- transcriber.py
|   `-- ...
|-- scripts/
|   |-- install.ps1       # User install script (downloads from GitHub)
|   |-- build-release.ps1
|   `-- uninstall.ps1
|-- build.py              # Simple PyInstaller build
|-- requirements.txt
`-- README.md
```

### File Locations (Both Modes)

| What | Where |
|------|------|
| **Application** | Portable: Extract folder / Installed: `%LOCALAPPDATA%\open-dictate\bin\` |
| **Config** | Always `%APPDATA%\open-dictate\config.json` |
| **Models** | Always `%APPDATA%\open-dictate\models\` (auto-downloaded) |
| **Recordings** | Always `%APPDATA%\open-dictate\recordings\` (if enabled) |

### CLI Commands

```powershell
open-dictate start              # Start the daemon
open-dictate status             # Show status
open-dictate set-hotkey <key>   # Change hotkey
open-dictate set-model <size>   # Change model
open-dictate download-model     # Download model manually
```

### Troubleshooting

| Issue | Solution |
|------|------|
| "Microphone denied" | Settings -> Privacy -> Microphone -> Enable access |
| "whisper-cli not found" | Check `%LOCALAPPDATA%\open-dictate\bin\` has all DLLs |
| "Model not found" | Run `open-dictate download-model base.en` |
| Hotkey not working | Try `open-dictate set-hotkey insert` or `open-dictate set-hotkey ctrl+space`, or run as admin |
| Text pastes wrong | Don't use Alt combos; prefer Right Ctrl, Insert, or Ctrl+Space |
| Unicode issues | Use multilingual model (without `.en`) for non-English |

### Making a Release

1. Update version in `src/version.py`
2. Run build script: `scripts/build-release.ps1`
3. Test the built release
4. Create GitHub Release and upload the zip
5. The `install.ps1` script will automatically use the new release

## Attribution & Credits

- **Original macOS app:** [human37/open-wispr](https://github.com/human37/open-wispr)
- **Speech recognition:** [ggerganov/whisper.cpp](https://github.com/ggerganov/whisper.cpp)
- **Windows port:** [tucaz](https://github.com/tucaz)

## License

MIT
