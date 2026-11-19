from services.i18n import tr
import logging
from core.image_detector import ImageDetector
from core.ocr_engine import OCREngine

class Processor:
    def __init__(self, preset, log=None):
        self.preset = preset
        self.detector = ImageDetector()
        self.ocr = OCREngine()
        self.log = log or logging.warning

    def validate(self, frame, require_event=True):
        self.preset.validate()
        if require_event or self.preset.image:
            self.detector.score(frame, self.preset.region, self.preset.image, self.preset.scales)
        if not any(i.enabled for i in self.preset.items):
            raise ValueError(tr('활성화된 추출 항목이 없습니다.'))
        for item in self.preset.items:
            if not item.enabled:
                continue
            item.region.crop(frame)
            if item.kind == 'image':
                self.detector.score(frame, item.region, item.image, item.scales)
            else:
                self.ocr.check(item.language)

    def detected(self, frame):
        p = self.preset
        return self.detector.score(frame, p.region, p.image, p.scales) >= p.threshold

    def close(self):
        self.ocr.close()

    def extract(self, frame):
        values = []
        for item in self.preset.items:
            if not item.enabled:
                continue
            if item.kind == 'image':
                present = self.detector.score(frame, item.region, item.image, item.scales) >= item.threshold
                # Preserve the original boolean API for the default texts.
                value = present if (item.present_text, item.absent_text) == ('True', 'False') else (item.present_text if present else item.absent_text)
                values.append(value)
            else:
                try:
                    values.append(self.ocr.read(item.region.crop(frame), item))
                except Exception as exc:
                    self.log(tr('OCR 실패 [{0}]: {1}; 기본값 사용').format(item.name, exc))
                    values.append(item.fallback)
        return values
