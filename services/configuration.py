import os
from pathlib import Path

def data_dir():
    path = Path(os.environ.get('LOCALAPPDATA', Path.home())) / 'CFCVideoTextExtractor'
    path.mkdir(parents=True, exist_ok=True)
    return path
