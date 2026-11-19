import os
import sys
from pathlib import Path

def presets_dir():
    """Resolve from the application location, independent of the working directory."""
    root = Path(sys.executable).parent if getattr(sys, 'frozen', False) else Path(__file__).resolve().parents[1]
    path = root / 'presets'
    path.mkdir(parents=True, exist_ok=True)
    return path

def data_dir():
    path = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CFCVideoTextExtractor'
    path.mkdir(parents=True, exist_ok=True)
    return path
