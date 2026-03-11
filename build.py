"""Build script to create a standalone executable using PyInstaller."""

import os
import shutil
import subprocess
import sys
from pathlib import Path


def clean_build_dirs():
    """Remove previous build artifacts."""
    dirs_to_remove = ["build", "dist"]
    for dir_name in dirs_to_remove:
        if os.path.exists(dir_name):
            print(f"Removing {dir_name}/...")
            shutil.rmtree(dir_name)
    
    # Remove spec file and temp files
    for f in ["open-dictate.spec", "cli.py", "icon.ico"]:
        if os.path.exists(f):
            os.remove(f)


def create_entry_point():
    """Create a standalone entry point script for PyInstaller."""
    entry_point = '''#!/usr/bin/env python3
"""Standalone entry point for PyInstaller."""

import sys
from pathlib import Path

# Ensure src package is importable
if __name__ == "__main__":
    # Add src directory to path
    script_dir = Path(__file__).parent.resolve()
    package_dir = script_dir / 'src'
    if package_dir.exists():
        sys.path.insert(0, str(script_dir))
    
    # Import after path setup
    from src.main import main
    main()
'''
    with open("cli.py", "w") as f:
        f.write(entry_point)


def create_icon():
    """Create icon.ico from logo.png."""
    from PIL import Image
    
    # Look for logo in docs folder
    logo_paths = [
        Path("docs/logo.png"),
        Path("../docs/logo.png"),
    ]
    
    for logo_path in logo_paths:
        if logo_path.exists():
            img = Image.open(logo_path)
            # Convert to RGBA if needed
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Create multiple sizes for the icon
            sizes = [16, 32, 48, 64, 128, 256]
            icons = []
            for size in sizes:
                resized = img.resize((size, size), Image.Resampling.LANCZOS)
                icons.append(resized)
            
            # Save as ICO
            icons[0].save("icon.ico", format='ICO', sizes=[(s, s) for s in sizes])
            print("Created icon.ico from logo.png")
            return True
    
    raise FileNotFoundError("logo.png not found in docs/ folder")


def create_spec_file():
    """Create a PyInstaller spec file."""
    spec_content = '''
# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['cli.py'],
    pathex=[],
    binaries=[],
    datas=[('src', 'src')],
    hiddenimports=[
        'pyaudio',
        'pynput.keyboard._win32',
        'pynput.mouse._win32',
        'pystray._win32',
        'PIL',
        'src',
        'src.app',
        'src.audio_recorder',
        'src.config',
        'src.hotkey_manager',
        'src.key_codes',
        'src.model_downloader',
        'src.permissions',
        'src.recording_store',
        'src.text_inserter',
        'src.text_processor',
        'src.transcriber',
        'src.tray_controller',
        'src.version',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='open-dictate',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='icon.ico' if os.path.exists('icon.ico') else None,
)
'''
    with open("open-dictate.spec", "w") as f:
        f.write(spec_content.strip())


def build():
    """Build the executable."""
    print("Building open-dictate executable...")
    
    # Check if PyInstaller is installed
    try:
        import PyInstaller
    except ImportError:
        print("PyInstaller not found. Installing...")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
    
    # Clean previous builds
    clean_build_dirs()
    
    # Create icon from logo if icon.ico doesn't exist
    if not os.path.exists("icon.ico"):
        create_icon()
    
    # Create entry point and spec file
    create_entry_point()
    create_spec_file()
    
    # Run PyInstaller using spec file
    cmd = [
        sys.executable, "-m", "PyInstaller",
        "open-dictate.spec"
    ]
    
    print(f"Running: {' '.join(cmd)}")
    result = subprocess.run(cmd)
    
    if result.returncode != 0:
        print("Build failed!")
        sys.exit(1)
    
    print("\\nBuild successful!")
    print("Executable location: dist/open-dictate.exe")
    
    # Copy to root for convenience
    if os.path.exists("dist/open-dictate.exe"):
        shutil.copy("dist/open-dictate.exe", "open-dictate.exe")
        print("Copied to: open-dictate.exe")
    
    # Clean up temporary cli.py
    if os.path.exists("cli.py"):
        os.remove("cli.py")
        print("Cleaned up temporary files")


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Build open-dictate executable")
    parser.add_argument("--clean", action="store_true", help="Clean build directories only")
    args = parser.parse_args()
    
    if args.clean:
        clean_build_dirs()
        print("Cleaned build directories.")
        return
    
    build()


if __name__ == "__main__":
    main()
