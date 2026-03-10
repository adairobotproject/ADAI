"""
PyInstaller runtime hook: force UTF-8 encoding on Windows console streams.

Without this, print() calls with non-ASCII characters (Spanish text, etc.)
can raise UnicodeEncodeError when the frozen app runs on a system whose
console code page is not UTF-8.
"""

import sys
import io

if sys.platform == 'win32':
    if sys.stdout is not None and hasattr(sys.stdout, 'buffer'):
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    if sys.stderr is not None and hasattr(sys.stderr, 'buffer'):
        sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')
