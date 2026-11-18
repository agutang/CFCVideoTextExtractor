"""Optional offline check for both source and frozen Windows distributions."""
import json
import os
from pathlib import Path
import traceback

def run(output):
    os.environ['QT_QPA_PLATFORM'] = 'offscreen'
    report = {}
    try:
        import av
        import cv2
        import numpy as np
        import tesserocr
        from PySide6.QtWidgets import QApplication
        from gui.main_window import MainWindow
        from gui.application import configure_app
        from core.ocr_engine import OCREngine
        from models.preset import ExtractionItem
        app = QApplication.instance() or QApplication([])
        configure_app(app)
        window = MainWindow()
        window.show()
        app.processEvents()
        window.grab().save(str(Path(output).with_suffix('.png')))
        report['gui'] = 'ok'
        report['av'] = av.__version__
        report['opencv'] = cv2.__version__
        report['tesseract'] = tesserocr.tesseract_version().splitlines()[0]
        engine = OCREngine()
        try:
            for language in ('eng', 'kor', 'jpn'):
                engine.check(language)
            frame = np.full((100, 600, 3), 255, dtype=np.uint8)
            cv2.putText(frame, 'HELLO 123', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
            report['ocr'] = engine.read(frame, ExtractionItem(language='eng', zoom=1))
            if '123' not in report['ocr']:
                raise ValueError('OCR check failed')
        finally:
            engine.close()
        window.close()
        report['success'] = True
    except Exception:
        report['success'] = False
        report['error'] = traceback.format_exc()
    Path(output).write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    return 0 if report['success'] else 1
