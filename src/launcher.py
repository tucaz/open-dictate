"""Helpers for launching the tray app as a detached background process."""

from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

INTERNAL_TRAY_COMMAND = "__run-tray"


def build_tray_command() -> list[str]:
    """Build the command used for the background tray process."""
    if getattr(sys, "frozen", False):
        return [sys.executable, INTERNAL_TRAY_COMMAND]

    pythonw_path = Path(sys.executable).with_name("pythonw.exe")
    python_executable = str(pythonw_path if pythonw_path.exists() else Path(sys.executable))
    return [python_executable, "-m", "src", INTERNAL_TRAY_COMMAND]


def launch_tray_process(cwd: str | None = None):
    """Launch the tray app without keeping a terminal attached."""
    env = os.environ.copy()
    if getattr(sys, "frozen", False):
        # Relaunch one-file builds as a fresh top-level app instance.
        env["PYINSTALLER_RESET_ENVIRONMENT"] = "1"

    popen_kwargs = {
        "cwd": cwd or os.getcwd(),
        "env": env,
        "stdin": subprocess.DEVNULL,
        "stdout": subprocess.DEVNULL,
        "stderr": subprocess.DEVNULL,
        "close_fds": True,
    }

    if os.name == "nt":
        creationflags = 0
        for flag_name in ("DETACHED_PROCESS", "CREATE_NEW_PROCESS_GROUP", "CREATE_NO_WINDOW"):
            creationflags |= getattr(subprocess, flag_name, 0)

        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        startupinfo.wShowWindow = getattr(subprocess, "SW_HIDE", 0)

        popen_kwargs["creationflags"] = creationflags
        popen_kwargs["startupinfo"] = startupinfo

    return subprocess.Popen(build_tray_command(), **popen_kwargs)
