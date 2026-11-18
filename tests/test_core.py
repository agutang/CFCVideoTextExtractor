import csv
import json
import zipfile
from pathlib import Path
import pytest
import numpy as np
import cv2
from models.preset import Preset, ExtractionItem, Region
from core.event_detector import EventDetector
from core.extraction_scheduler import Scheduler
from core.analysis_worker import analyze
from core.image_detector import ImageDetector
from core.extraction_processor import Processor
from services.output_writer import OutputWriter, format_row, timestamp
from services import preset_service

def test_edges_and_initial_presence():
    detector = EventDetector()
    assert [detector.update(v, t) for t, v in enumerate([True, True, False, True, True])] == [True, False, False, True, False]

def test_absence_stabilization():
    detector = EventDetector(.5)
    assert detector.update(True, 0)
    assert not detector.update(False, .1)
    assert not detector.update(True, .3)
    detector.update(False, .5)
    detector.update(False, 1)
    assert detector.update(True, 1.1)

def test_scheduler_overlap():
    scheduler = Scheduler(.25)
    first = scheduler.add(1)
    second = scheduler.add(1.1)
    assert list(scheduler.due(1.2)) == []
    assert list(scheduler.due(1.4)) == [first, second]
    assert list(scheduler.due(2)) == []

class FakeProcessor:
    def validate(self, frame):
        pass
    def detected(self, frame):
        return frame[0]
    def extract(self, frame):
        return [frame[1]]

@pytest.mark.parametrize('delay,expected', [(0, ['0, 00:00:00.000', '3, 00:00:00.300']), (.25, ['3, 00:00:00.300', '6, 00:00:00.610']), (2, [])])
def test_analysis_delay_actual_frame_and_eof(tmp_path, delay, expected):
    p = Preset(delay=delay, interval=0)
    frames = [(0, (True, 0)), (.1, (True, 1)), (.2, (False, 2)), (.3, (True, 3)), (.4, (False, 4)), (.61, (False, 6))]
    output = tmp_path/'out.txt'
    writer = OutputWriter(output)
    logs = []
    analyze(frames, p, FakeProcessor(), writer, logs.append, lambda *a: None)
    writer.close()
    assert output.read_text(encoding='utf-8-sig').splitlines() == expected
    if delay == 2:
        assert sum('기록 제외' in line for line in logs) == 2

def test_cancel_preserves_output(tmp_path):
    output = tmp_path/'out.txt'
    writer = OutputWriter(output)
    states = iter([True, True, False])
    analyze([(0, (True, 'first')), (1, (False, 'next'))], Preset(interval=0), FakeProcessor(), writer, lambda s: None, lambda *a: None, lambda: next(states))
    writer.close()
    assert output.read_text(encoding='utf-8-sig').strip() == 'first, 00:00:00.000'

def test_csv_and_bom(tmp_path):
    path = tmp_path/'out.txt'
    writer = OutputWriter(path)
    assert path.read_bytes() == b'\xef\xbb\xbf'
    writer.write(['A, B', '"quote"', 'one\ntwo', True], 3723.456)
    writer.close()
    assert list(csv.reader(path.read_text(encoding='utf-8-sig').splitlines(), skipinitialspace=True)) == [['A, B', '"quote"', 'one\\ntwo', 'True', '01:02:03.456']]
    with pytest.raises(FileExistsError):
        OutputWriter(path)

def test_timestamp_carry():
    assert timestamp(59.9999) == '00:01:00.000'

def image_fixture(tmp_path):
    rng = np.random.default_rng(123)
    template = rng.integers(0, 255, (12, 12, 3), dtype=np.uint8)
    path = tmp_path/'기준.png'
    cv2.imencode('.png', template)[1].tofile(path)
    frame = np.zeros((50, 50, 3), dtype=np.uint8)
    frame[15:27, 20:32] = template
    return path, frame

def test_matching_multiscale_and_bounds(tmp_path):
    path, frame = image_fixture(tmp_path)
    detector = ImageDetector()
    assert detector.score(frame, Region(0, 0, 50, 50), str(path), [.8, 1, 1.2]) > .99
    with pytest.raises(ValueError):
        detector.score(frame, Region(49, 0, 10, 10), str(path), [1])
    with pytest.raises(ValueError):
        detector.score(frame, Region(0, 0, 5, 5), str(path), [1])

def test_mixed_items_order_disabled_and_fallback(tmp_path):
    path, frame = image_fixture(tmp_path)
    items = [ExtractionItem(name='text', fallback='fallback'), ExtractionItem(kind='image', image=str(path), region=Region(0, 0, 50, 50)), ExtractionItem(enabled=False)]
    preset = Preset(items=items)
    processor = Processor(preset)
    processor.ocr.read = lambda *args: (_ for _ in ()).throw(RuntimeError('OCR error'))
    assert processor.extract(frame) == ['fallback', True]
    preset.items.reverse()
    assert processor.extract(frame) == [True, 'fallback']
    assert items[1].language == 'eng'

def test_presets_roundtrip_zip_and_independence(tmp_path):
    path, _ = image_fixture(tmp_path)
    p = Preset(image=str(path), delay=2.25, items=[ExtractionItem(kind='image', image=str(path)), ExtractionItem(enabled=False, language='kor')])
    first, second = tmp_path/'first.json', tmp_path/'second.json'
    preset_service.save(p, first)
    preset_service.save(p, second)
    restored = preset_service.load(first)
    assert restored.to_dict() == p.to_dict()
    restored.items[0].name = 'changed'
    assert p.items[0].name != restored.items[0].name
    preset_service.save(restored, first)
    assert preset_service.load(first).items[0].name == 'changed'
    archive = tmp_path/'export.zip'
    preset_service.export_zip(p, archive)
    imported = preset_service.import_zip(archive, tmp_path/'imports')
    assert Path(imported.image).read_bytes() == path.read_bytes()
    assert Path(imported.items[0].image).is_file()
    assert [i.id for i in imported.items] == [i.id for i in p.items]
    first.unlink()
    assert second.is_file()

@pytest.mark.parametrize('name', ['../escape', '/absolute', 'C:/escape', 'images\\escape'])
def test_zip_rejects_traversal(tmp_path, name):
    path = tmp_path/'bad.zip'
    with zipfile.ZipFile(path, 'w') as archive:
        archive.writestr(zipfile.ZipInfo(name), 'bad')
    with pytest.raises(ValueError):
        preset_service.import_zip(path, tmp_path/'imports')

def test_invalid_preset():
    with pytest.raises(ValueError):
        Preset(delay=float('nan')).validate()
    with pytest.raises(ValueError):
        Preset.from_dict({'schema_version': 99})
