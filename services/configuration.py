import os
import sys
import json
from pathlib import Path

LANGUAGES = ('ko', 'en', 'ja')

def load_language() -> str:
    try:
        settings = json.loads((data_dir() / 'settings.json').read_text(encoding='utf-8'))
        language = settings.get('language') if isinstance(settings, dict) else None
        return language if language in LANGUAGES else 'ko'
    except (OSError, ValueError):
        return 'ko'

def save_language(language: str) -> None:
    if language not in LANGUAGES:
        raise ValueError('Unsupported language')
    path = data_dir() / 'settings.json'
    try:
        settings = json.loads(path.read_text(encoding='utf-8'))
        if not isinstance(settings, dict):
            settings = {}
    except (OSError, ValueError):
        settings = {}
    settings['language'] = language
    temporary = path.with_suffix('.tmp')
    temporary.write_text(json.dumps(settings, ensure_ascii=False, indent=2), encoding='utf-8')
    temporary.replace(path)

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
