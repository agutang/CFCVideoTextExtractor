import os
os.environ.setdefault('QT_QPA_PLATFORM', 'offscreen')
import json
import pytest
from PySide6.QtWidgets import QApplication, QInputDialog
from services import configuration
from services.i18n import get_language, set_language
from gui.application import configure_app
from gui.main_window import MainWindow

@pytest.fixture(autouse=True)
def isolated_settings(tmp_path, monkeypatch):
    monkeypatch.setattr(configuration, 'data_dir', lambda: tmp_path)
    set_language('ko')
    yield tmp_path
    set_language('ko')

@pytest.mark.parametrize('content', [None, 'broken', '[]', '{"language":"xx"}', '{"language":null}'])
def test_invalid_settings_default_to_korean(isolated_settings, content):
    if content is not None:
        (isolated_settings/'settings.json').write_text(content, encoding='utf-8')
    assert configuration.load_language() == 'ko'

@pytest.mark.parametrize('language', ['ko', 'en', 'ja'])
def test_save_and_restore_on_startup(language):
    app = QApplication.instance() or QApplication([])
    configuration.save_language(language)
    set_language('ko')
    configure_app(app)
    assert get_language() == language
    window = MainWindow()
    assert window.start_button.text() == {'ko': '분석 시작', 'en': 'Start analysis', 'ja': '解析開始'}[language]
    window.close()

def test_language_dialog_persists_and_cancel_preserves(monkeypatch):
    app = QApplication.instance() or QApplication([])
    window = MainWindow()
    monkeypatch.setattr(QInputDialog, 'getItem', lambda *args: ('日本語', True))
    window.change_language()
    assert configuration.load_language() == 'ja'
    monkeypatch.setattr(QInputDialog, 'getItem', lambda *args: ('English', False))
    window.change_language()
    assert configuration.load_language() == 'ja'
    window.close()

def test_save_preserves_other_settings(isolated_settings):
    path = isolated_settings/'settings.json'
    path.write_text(json.dumps({'other': 42}), encoding='utf-8')
    configuration.save_language('en')
    assert json.loads(path.read_text(encoding='utf-8')) == {'other': 42, 'language': 'en'}
