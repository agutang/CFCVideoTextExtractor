import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import ast
from pathlib import Path
import pytest
import numpy as np
from PySide6.QtCore import QMimeData, QUrl, QPointF, Qt
from PySide6.QtGui import QDropEvent, QPixmap
from PySide6.QtWidgets import QApplication, QPushButton, QMessageBox, QFileDialog
from models.preset import Preset, ExtractionItem, Region
from core.extraction_processor import Processor
from gui.main_window import MainWindow, TestWorker as FrameTestWorker
from gui.video_preview import VideoPreview
from gui.output_format_dialog import OutputFormatDialog
from services import preset_service, configuration
from services.i18n import set_language, tr, CATALOG
from services.text_format import render_template, validate_template

@pytest.fixture(autouse=True)
def language():
    set_language('ko')
    yield
    set_language('ko')

@pytest.fixture
def app():
    return QApplication.instance() or QApplication([])

@pytest.mark.parametrize('template,names,values,expected', [
    ('{Name}: {Score}', ['Name', 'Score'], ['A', '12'], 'A: 12'),
    ('{{{A}}}', ['A'], ['x'], '{x}'),
    ('{a.b} / {a b}', ['a.b', 'a b'], ['1', '2'], '1 / 2')])
def test_template(template, names, values, expected):
    assert render_template(template, names, values) == expected

@pytest.mark.parametrize('template,names', [('{missing}', ['A']), ('{A', ['A']), ('{A!r}', ['A']), ('{A:>5}', ['A']), ('{A}', ['A', 'A']), ('{A}', ['A', ''])])
def test_invalid_template(template, names):
    with pytest.raises(ValueError):
        validate_template(template, names)

def test_custom_presence_and_formatting():
    item = ExtractionItem(kind='image', region=Region(0, 0, 2, 2), present_text='YES 123', absent_text='')
    p = Processor(Preset(items=[item]))
    frame = np.zeros((2, 2, 3), np.uint8)
    p.detector.score = lambda *args: 1
    assert p.extract(frame) == ['YES 123']
    p.detector.score = lambda *args: 0
    assert p.extract(frame) == ['']
    p.close()

def test_legacy_and_new_presets_roundtrip(tmp_path):
    preset = Preset(items=[ExtractionItem()])
    legacy = preset.to_dict()
    for key in ('present_text', 'absent_text'):
        legacy['items'][0].pop(key)
    item = Preset.from_dict(legacy).items[0]
    assert (item.present_text, item.absent_text) == ('True', 'False')
    item.present_text, item.absent_text = '있음', 'なし'
    preset.output_template = '{' + item.name + '}'
    preset.items = [item]
    path = tmp_path/'new.json'
    preset_service.save(preset, path)
    assert preset_service.load(path).to_dict() == preset.to_dict()
    archive = tmp_path/'new.zip'
    preset_service.export_zip(preset, archive)
    assert preset_service.import_zip(archive, tmp_path/'imports').to_dict() == preset.to_dict()

def test_presets_folder_source_and_exe(tmp_path, monkeypatch):
    monkeypatch.setattr(configuration, '__file__', str(tmp_path/'services'/'configuration.py'))
    assert configuration.presets_dir() == tmp_path/'presets'
    monkeypatch.setattr(configuration.sys, 'frozen', True, raising=False)
    monkeypatch.setattr(configuration.sys, 'executable', str(tmp_path/'binary'/'app.exe'))
    assert configuration.presets_dir() == tmp_path/'binary'/'presets'
    assert configuration.presets_dir().is_dir()

def test_default_preset_dialog_locations(app, monkeypatch):
    window = MainWindow()
    calls = []
    monkeypatch.setattr(QFileDialog, 'getOpenFileName', lambda *a, **kw: (calls.append(a[2]) or '', ''))
    monkeypatch.setattr(QFileDialog, 'getSaveFileName', lambda *a, **kw: (calls.append(a[2]) or '', ''))
    window.load_preset()
    window.save_preset()
    assert calls == [str(configuration.presets_dir()), str(configuration.presets_dir()/'preset.json')]
    window.close()

def test_without_event_reference_allows_test_but_not_analysis(app):
    item = ExtractionItem(kind='image', image='item.png', region=Region(0, 0, 2, 2))
    preset = Preset(items=[item])
    frame = np.zeros((2, 2, 3), np.uint8)
    processor = Processor(preset)
    calls = []
    def score(frame, region, path, scales):
        calls.append(path)
        if not path:
            raise ValueError('missing event')
        return 1
    processor.detector.score = score
    processor.validate(frame, require_event=False)
    assert calls == ['item.png']
    with pytest.raises(ValueError):
        processor.validate(frame)
    processor.close()

def test_frame_worker_without_reference(app, monkeypatch):
    monkeypatch.setattr('core.image_detector.ImageDetector.score', lambda *a: 1)
    worker = FrameTestWorker(Preset(items=[ExtractionItem(kind='image', image='item.png', region=Region(0, 0, 2, 2))]), np.zeros((2, 2, 3), np.uint8), 1.25)
    messages, errors = [], []
    worker.result.connect(messages.append)
    worker.failed.connect(errors.append)
    worker.run()
    assert not errors
    assert '이벤트 감지 생략' in messages[0]
    assert 'True, 00:00:01.250' in messages[0]

def test_drop_acceptance_and_loading(app, tmp_path):
    from test_video_gui import make_video
    video = tmp_path/'video.MP4'
    make_video(video, [0, 40])
    mime = QMimeData()
    mime.setUrls([QUrl.fromLocalFile(str(video))])
    assert VideoPreview.dropped_video(mime) == str(video)
    window = MainWindow()
    event = QDropEvent(QPointF(2, 2), Qt.CopyAction, mime, Qt.LeftButton, Qt.NoModifier)
    window.preview.dropEvent(event)
    assert event.isAccepted()
    assert window.video == str(video)
    assert window.preview.frame is not None
    for urls in [[QUrl('https://example.com/v.mp4')], [QUrl.fromLocalFile(str(tmp_path))], [QUrl.fromLocalFile(str(video))]*2]:
        mime.setUrls(urls)
        assert VideoPreview.dropped_video(mime) is None
    unsupported = tmp_path/'image.png'
    unsupported.touch()
    mime.setUrls([QUrl.fromLocalFile(str(unsupported))])
    assert VideoPreview.dropped_video(mime) is None
    window.close()

def test_language_switch_keeps_user_data(app):
    window = MainWindow()
    p = Preset(name='내 설정', items=[ExtractionItem(name='사용자 이름', present_text='있음')])
    window.populate(p)
    window.editor.name.setText('편집 중')
    window.editor.present_text.setText('있는 경우')
    window.event_image.preview.setPixmap(QPixmap(2, 2))
    for language, start, tab in [('en', 'Start analysis', 'Extraction items'), ('ja', '解析開始', '抽出項目'), ('ko', '분석 시작', '추출 항목')]:
        window.set_ui_language(language)
        assert window.start_button.text() == start
        assert window.tabs.tabText(1) == tab
        assert window.editor.name.text() == '편집 중'
        assert window.editor.present_text.text() == '있는 경우'
        assert window.preset_name.text() == '내 설정'
        assert not window.event_image.preview.pixmap().isNull()
        assert any(b.text() == 'Language' for b in window.findChildren(QPushButton))
    window.close()

def test_format_dialog_invalid_is_not_accepted(app, monkeypatch):
    dialog = OutputFormatDialog(Preset(items=[ExtractionItem(name='A')]))
    monkeypatch.setattr(QMessageBox, 'warning', lambda *args: None)
    dialog.template.setText('{missing}')
    dialog.accept()
    assert not dialog.result()
    dialog.template.setText('{A}')
    dialog.accept()
    assert dialog.result()

def test_gui_translation_catalog_coverage():
    for path in (Path('gui/main_window.py'), Path('gui/extraction_editor.py'), Path('gui/output_format_dialog.py')):
        for node in ast.walk(ast.parse(path.read_text(encoding='utf-8'))):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == 'tr' and node.args and isinstance(node.args[0], ast.Constant):
                source = node.args[0].value
                assert source in CATALOG, source

def test_template_output_and_preview_match(tmp_path, app, monkeypatch):
    import csv
    from services.output_writer import OutputWriter, format_row
    names = ['이름', '점수']
    values = ['A, B', '100']
    template = '{이름}: {점수}'
    row = format_row(values, 1.25, template, names)
    path = tmp_path/'out.txt'
    writer = OutputWriter(path, template=template, names=names)
    assert writer.write(values, 1.25) == row
    writer.close()
    assert next(csv.reader([row], skipinitialspace=True)) == ['A, B: 100', '00:00:01.250']
    assert format_row(values, 1.25) == '"A, B", 100, 00:00:01.250'

def test_no_help_button_and_native_dialog(app, monkeypatch):
    window = MainWindow()
    assert not any(b.text() == '?' for b in window.findChildren(QPushButton))
    kwargs = []
    monkeypatch.setattr(QFileDialog, 'getOpenFileName', lambda *a, **kw: (kwargs.append(kw) or '', ''))
    window.open_video()
    window.load_preset()
    window.editor.image.browse()
    assert all('options' not in kw for kw in kwargs)
    window.close()
