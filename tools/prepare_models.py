"""Explicit, one-time online setup. The application never imports this module."""
from pathlib import Path
import urllib.request

def main():
    target = Path(__file__).resolve().parents[1] / 'resources' / 'tessdata'
    target.mkdir(parents=True, exist_ok=True)
    base = 'https://raw.githubusercontent.com/tesseract-ocr/tessdata_fast/4.1.0/'
    for name in ['eng.traineddata', 'kor.traineddata', 'jpn.traineddata', 'LICENSE']:
        path = target / name
        if path.exists():
            print(f'Already exists: {name}')
            continue
        print(f'Downloading {name} ...')
        request = urllib.request.Request(base + name, headers={'User-Agent': 'CFCVideoTextExtractor-Setup'})
        with urllib.request.urlopen(request, timeout=60) as response:
            content = response.read()
        temporary = path.with_suffix('.download')
        temporary.write_bytes(content)
        temporary.replace(path)
    print(f'Models ready: {target}')

if __name__ == '__main__':
    main()
