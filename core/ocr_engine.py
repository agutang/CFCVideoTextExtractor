import os
import sys
from pathlib import Path
import cv2
import tesserocr
from PIL import Image

class OCREngine:
    def __init__(self):
        root = Path(getattr(sys, '_MEIPASS', Path(__file__).resolve().parents[1]))
        candidates = [Path(os.environ['TESSDATA_PREFIX'])] if os.environ.get('TESSDATA_PREFIX') else []
        candidates += [root/'resources'/'tessdata', root/'resources'/'tesseract'/'tessdata', Path('C:/Program Files/Tesseract-OCR/tessdata')]
        self.path = next((p for p in candidates if p.is_dir()), candidates[0])
        self.engines = {}

    def check(self, language):
        missing = {lang for lang in language.split('+') if not lang or not (self.path / f'{lang}.traineddata').is_file()}
        if missing:
            raise ValueError(f'OCR 언어 모델이 없습니다: {", ".join(sorted(missing))}')
        if language not in self.engines:
            try:
                self.engines[language] = tesserocr.PyTessBaseAPI(path=str(self.path), lang=language, psm=tesserocr.PSM.SINGLE_BLOCK)
            except Exception as exc:
                raise ValueError(f'OCR 엔진 초기화 실패 ({language}): {exc}') from exc

    def read(self, image, item):
        self.check(item.language)
        image = cv2.resize(image, None, fx=item.zoom, fy=item.zoom, interpolation=cv2.INTER_CUBIC)
        if item.grayscale or item.binary:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        image = cv2.convertScaleAbs(image, alpha=item.contrast)
        if item.denoise:
            image = cv2.medianBlur(image, 3)
        if item.binary:
            _, image = cv2.threshold(image, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        if image.ndim == 3:
            image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        engine = self.engines[item.language]
        engine.SetImage(Image.fromarray(image))
        try:
            if not engine.Recognize(timeout=30000):
                raise RuntimeError('OCR 인식에 실패했거나 제한시간을 초과했습니다.')
            return engine.GetUTF8Text().strip() or item.fallback
        finally:
            engine.Clear()

    def close(self):
        for engine in self.engines.values():
            engine.End()
        self.engines.clear()
