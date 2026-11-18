from pathlib import Path
import copy
from fractions import Fraction
import threading
import tracemalloc
import av
import cv2
import numpy as np
import pytest
from PIL import Image, ImageDraw, ImageFont
from core.analysis_worker import analyze, AnalysisWorker
from core.extraction_processor import Processor
from core.ocr_engine import OCREngine
from core.video_reader import VideoReader
from models.preset import Preset, Region, ExtractionItem
from services.output_writer import OutputWriter

@pytest.mark.parametrize('extension', ['mp4', 'mkv'])
def test_real_pipeline_vfr(tmp_path, extension):
    video = tmp_path/f'events.{extension}'
    rng = np.random.default_rng(42)
    icon = rng.integers(0, 255, (16, 16, 3), dtype=np.uint8)
    image = tmp_path/'icon.png'
    cv2.imencode('.png', icon)[1].tofile(image)
    with av.open(str(video), 'w') as container:
        stream = container.add_stream('libx264', rate=25)
        stream.width, stream.height = 96, 64
        stream.pix_fmt = 'yuv444p'
        stream.options = {'crf': '0'}
        stream.codec_context.time_base = Fraction(1, 1000)
        for time, present in [(0, True), (40, True), (100, False), (160, True), (300, False), (500, False)]:
            frame = np.zeros((64, 96, 3), dtype=np.uint8)
            if present:
                frame[0:16, 0:16] = icon
            # Extraction icon exists only at 300 ms, independent from event image.
            if time == 300:
                frame[32:48, 32:48] = icon
            decoded = av.VideoFrame.from_ndarray(frame, format='bgr24')
            decoded.pts, decoded.time_base = time, Fraction(1, 1000)
            for packet in stream.encode(decoded):
                container.mux(packet)
        for packet in stream.encode():
            container.mux(packet)
    preset = Preset(image=str(image), region=Region(0, 0, 20, 20), interval=0, delay=.15,
                    items=[ExtractionItem(kind='image', image=str(image), region=Region(32, 32, 20, 20))])
    processor = Processor(preset)
    output = tmp_path/'result.txt'
    writer = OutputWriter(output)
    with VideoReader(video) as reader:
        analyze(reader.frames(), preset, processor, writer, lambda s: None, lambda *a: None)
    writer.close()
    processor.close()
    # 0 + .15 -> .16; .16 + .15 -> .50. Detection continued while pending.
    assert output.read_text(encoding='utf-8-sig').splitlines() == ['False, 00:00:00.160', 'False, 00:00:00.500']

def test_worker_snapshot_and_pause_stop():
    preset = Preset(items=[ExtractionItem(name='original')])
    worker = AnalysisWorker('video.mp4', preset, 'out.txt', False)
    preset.items[0].name = 'changed'
    assert worker.preset.items[0].name == 'original'
    worker.pause(True)
    completed = threading.Event()
    values = []
    def checkpoint():
        values.append(worker.checkpoint())
        completed.set()
    thread = threading.Thread(target=checkpoint)
    thread.start()
    assert not completed.wait(.05)
    worker.stop()
    assert completed.wait(1)
    thread.join()
    assert values == [False]

def test_streaming_memory_is_bounded():
    class ProcessorStub:
        def validate(self, frame): pass
        def detected(self, frame): return False
    class WriterStub:
        def write(self, *args): raise AssertionError('No events expected')
    tracemalloc.start()
    analyze(((i*.04, None) for i in range(100000)), Preset(interval=0), ProcessorStub(), WriterStub(), lambda s: None, lambda *a: None)
    _, peak = tracemalloc.get_traced_memory()
    tracemalloc.stop()
    assert peak < 1_000_000

@pytest.mark.parametrize('language', ['eng', 'kor', 'jpn'])
def test_real_local_ocr_and_engine_reuse(language):
    engine = OCREngine()
    if not (engine.path/f'{language}.traineddata').exists():
        pytest.skip('로컬 OCR 모델 미준비')
    frame = np.full((100, 600, 3), 255, dtype=np.uint8)
    cv2.putText(frame, 'HELLO 123', (20, 70), cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 0), 3)
    item = ExtractionItem(language=language, zoom=1)
    try:
        result = engine.read(frame, item)
        assert '123' in result
        api = engine.engines[language]
        assert engine.read(frame, item)
        assert engine.engines[language] is api
    finally:
        engine.close()
    assert not engine.engines

def test_missing_model_is_reported(tmp_path, monkeypatch):
    monkeypatch.setenv('TESSDATA_PREFIX', str(tmp_path))
    with pytest.raises(ValueError, match='OCR 언어 모델'):
        OCREngine().check('nonexistent')

@pytest.mark.parametrize('language,text,font_name', [('kor', '안녕하세요', 'malgun.ttf'), ('jpn', 'こんにちは', 'msgothic.ttc')])
def test_native_language_text(language, text, font_name):
    font_path = Path('C:/Windows/Fonts') / font_name
    engine = OCREngine()
    if not font_path.exists() or not (engine.path/f'{language}.traineddata').exists():
        pytest.skip('언어 모델 또는 테스트 글꼴 미준비')
    image = Image.new('RGB', (650, 130), 'white')
    ImageDraw.Draw(image).text((20, 15), text, font=ImageFont.truetype(str(font_path), 64), fill='black')
    frame = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
    try:
        result = engine.read(frame, ExtractionItem(language=language, zoom=1))
        assert result.replace(' ', '') == text
    finally:
        engine.close()
