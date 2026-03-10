"""
Resolve application paths for both development and PyInstaller-installed modes.

- Development: all paths relative to the ia-clases/ directory (current behavior)
- Installed (PyInstaller):
  - Read-only bundled resources: sys._MEIPASS (the _internal/ dir)
  - Writable user data: %LOCALAPPDATA%/RobotAtlas/
"""
import os
import sys


def is_frozen() -> bool:
    """Check if running as a PyInstaller bundle."""
    return getattr(sys, 'frozen', False)


def get_bundle_dir() -> str:
    """Where bundled read-only resources live (code, bundled data)."""
    if is_frozen():
        return sys._MEIPASS
    return os.path.dirname(os.path.abspath(__file__))


def get_data_dir() -> str:
    """Where writable user data should be stored (configs, classes, students, etc.)."""
    if is_frozen():
        base = os.path.join(
            os.environ.get('LOCALAPPDATA', os.path.expanduser('~')),
            'RobotAtlas'
        )
        os.makedirs(base, exist_ok=True)
        return base
    return os.path.dirname(os.path.abspath(__file__))
