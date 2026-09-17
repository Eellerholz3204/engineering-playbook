"""Resolve immutable resources and prepare external processes in packaged builds."""

import os
from pathlib import Path
import sys


def resource_root() -> Path:
    if getattr(sys, "frozen", False):
        return Path(sys.executable).resolve().parent.parent / "playbook"
    return Path(__file__).resolve().parents[1]


def configure_desktop() -> None:
    if not getattr(sys, "frozen", False):
        return
    client = Path(sys._MEIPASS) / "flet-client"
    if not (client / "flet.exe").is_file():
        raise RuntimeError("The desktop runtime is missing. Extract the entire portable ZIP or reinstall the app.")
    os.environ["FLET_VIEW_PATH"] = str(client)
    # PyInstaller changes the process DLL search path. External PowerShell/Git/
    # Python must use their own DLLs, not those included with this application.
    # Imports are already loaded; bundled extensions resolve via absolute paths.
    if sys.platform == "win32":
        import ctypes
        ctypes.windll.kernel32.SetDllDirectoryW(None)
