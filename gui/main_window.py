import copy
import logging
from pathlib import Path
from PySide6.QtCore import Qt, QTimer, QThread, Signal
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QFormLayout,
    QPushButton, QLabel, QFileDialog, QMessageBox, QSlider, QListWidget, QTabWidget,
    QSplitter, QPlainTextEdit, QProgressBar, QLineEdit, QScrollArea, QInputDialog)
from models.preset import Preset, ExtractionItem
from gui.video_preview import VideoPreview
from gui.extraction_editor import RegionEditor, ImageEditor, ItemEditor, number
from core.video_reader import VideoReader
from core.analysis_worker import AnalysisWorker
from core.extraction_processor import Processor
from services.output_writer import timestamp, format_row
from services.configuration import data_dir, presets_dir
from services import preset_service
from services.i18n import tr, set_language, localize_widgets
from gui.output_format_dialog import OutputFormatDialog

class TestWorker(QThread):
    result = Signal(str)
    failed = Signal(str)

    def __init__(self, preset, frame, time):
        super().__init__()
        self.preset, self.frame, self.time = copy.deepcopy(preset), frame.copy(), time

    def run(self):
        processor = None
        try:
            messages = []
            processor = Processor(self.preset, messages.append)
            processor.validate(self.frame, require_event=False)
            score = processor.detector.score(self.frame, self.preset.region, self.preset.image, self.preset.scales) if self.preset.image else None
            values = processor.extract(self.frame)
            lines = [tr('이벤트 감지: {0} (유사도 {1:.4f})').format(score >= self.preset.threshold, score) if score is not None else tr('이벤트 기준 미등록: 이벤트 감지 생략')]
            lines += [f'{item.name}: {value}' for item, value in zip((i for i in self.preset.items if i.enabled), values)]
            lines += messages + [tr('TXT 미리보기: ') + format_row(values, self.time, self.preset.output_template, [i.name for i in self.preset.items if i.enabled])]
            self.result.emit('\n'.join(lines))
        except Exception as exc:
            self.failed.emit(str(exc))
        finally:
            if processor:
                processor.close()

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        presets_dir()
        self.setWindowTitle(tr('CFC 영상 데이터 추출기'))
        self.resize(1350, 900)
        self.preset = Preset()
        self.video = ''
        self.reader = None
        self.current_time = 0.0
        self.frame_times = []
        self.worker = None
        self.test_worker = None
        self.preset_path = None
        self.loading = False
        root = QWidget()
        self.setCentralWidget(root)
        layout = QVBoxLayout(root)
        toolbar = QHBoxLayout()
        self.add_button(toolbar, tr('영상 선택'), self.open_video)
        self.info = QLabel(tr('MP4 / MKV 영상을 선택하세요'))
        toolbar.addWidget(self.info, 1)
        self.add_button(toolbar, 'Language', self.change_language)
        layout.addLayout(toolbar)
        splitter = QSplitter()
        layout.addWidget(splitter, 1)
        left = QWidget()
        left_layout = QVBoxLayout(left)
        self.preview = VideoPreview()
        self.preview.selected.connect(self.region_selected)
        self.preview.video_dropped.connect(self.load_video)
        left_layout.addWidget(self.preview, 1)
        self.timeline = QSlider(Qt.Horizontal)
        self.timeline.setRange(0, 0)
        self.timeline.sliderReleased.connect(lambda: self.seek(self.timeline.value()/1000))
        left_layout.addWidget(self.timeline)
        controls = QHBoxLayout()
        self.add_button(controls, tr('이전 프레임'), self.previous_frame)
        self.add_button(controls, tr('다음 프레임'), self.next_frame)
        self.position = number(0, 10000000)
        controls.addWidget(self.position)
        self.add_button(controls, tr('초로 이동'), lambda: self.seek(self.position.value()))
        self.time_label = QLabel('00:00:00.000')
        controls.addWidget(self.time_label)
        left_layout.addLayout(controls)
        self.add_button(left_layout, tr('현재 프레임에서 감지 / 추출 테스트'), self.test_frame)
        self.tabs = QTabWidget()
        splitter.addWidget(left)
        splitter.addWidget(self.tabs)
        splitter.setSizes([800, 500])
        self.build_event_tab()
        self.build_items_tab()
        self.build_preset_tab()
        self.tabs.currentChanged.connect(self.refresh_regions)
        run = QHBoxLayout()
        self.start_button = self.add_button(run, tr('분석 시작'), self.start_analysis)
        self.pause_button = self.add_button(run, tr('일시정지'), lambda: self.set_pause(True))
        self.resume_button = self.add_button(run, tr('재개'), lambda: self.set_pause(False))
        self.stop_button = self.add_button(run, tr('분석 중단'), self.stop_analysis)
        self.progress = QProgressBar()
        run.addWidget(self.progress, 1)
        layout.addLayout(run)
        self.status = QLabel(tr('준비'))
        layout.addWidget(self.status)
        self.logs = QPlainTextEdit()
        self.logs.setReadOnly(True)
        self.logs.setMaximumBlockCount(1500)
        self.logs.setMaximumHeight(180)
        layout.addWidget(self.logs)
        self.set_running(False)
        localize_widgets(self)

    def change_language(self):
        choices = ['한국어', 'English', '日本語']
        selected, ok = QInputDialog.getItem(self, 'Language', 'Select language', choices, 0, False)
        if ok:
            self.set_ui_language(['ko', 'en', 'ja'][choices.index(selected)])

    def set_ui_language(self, language):
        set_language(language)
        localize_widgets(self)
        self.update_list(self.items.currentRow())
        if hasattr(self, '_last_progress'):
            self.on_progress(*self._last_progress)

    def edit_output_format(self):
        def action():
            self.editor.apply()
            dialog = OutputFormatDialog(self.preset, self)
            if dialog.exec():
                self.preset.output_template = dialog.template.text()
        self.guarded(action)

    @staticmethod
    def add_button(layout, text, callback):
        button = QPushButton(text)
        button.clicked.connect(callback)
        layout.addWidget(button)
        return button

    def guarded(self, action):
        try:
            return action()
        except Exception as exc:
            logging.exception(tr('작업 오류'))
            self.error(str(exc))

    def error(self, message):
        message = tr(message)
        self.log(tr('오류: ') + message)
        QMessageBox.warning(self, tr('오류'), message)

    def log(self, message):
        self.logs.appendPlainText(message)
        logging.info(message)

    def build_event_tab(self):
        widget = QWidget()
        form = QFormLayout(widget)
        self.event_image = ImageEditor()
        self.event_region = RegionEditor()
        self.event_region.changed.connect(self.refresh_regions)
        self.threshold = number(.9, 1)
        self.scales = QLineEdit('1.0')
        self.interval = number(.2, 3600)
        self.delay = number(0, 1000000)
        self.absence = number(0, 3600)
        for text, field in [(tr('이벤트 기준 이미지'), self.event_image), (tr('원본 좌표'), self.event_region),
                            (tr('유사도 임계값'), self.threshold), (tr('스케일 (예: 0.8, 1, 1.2)'), self.scales),
                            (tr('탐색 간격 (초, 0=모든 프레임)'), self.interval), (tr('추출 지연 (초)'), self.delay),
                            (tr('연속 미감지 시간 (초)'), self.absence)]:
            form.addRow(text, field)
        note = QLabel(tr('미감지 안정화는 재감지 준비만 늦춥니다.\n새 감지는 즉시 이벤트가 되며, 그 PTS부터 지연을 계산합니다.\n드래그 영역은 현재 탭의 선택 항목에 적용됩니다.'))
        note.setWordWrap(True)
        form.addRow(note)
        self.tabs.addTab(widget, tr('이벤트 감지'))

    def build_items_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.items = QListWidget()
        self.items.currentRowChanged.connect(self.select_item)
        layout.addWidget(self.items)
        row = QHBoxLayout()
        self.add_button(row, tr('항목 추가'), self.add_item)
        self.add_button(row, tr('삭제'), self.delete_item)
        self.add_button(row, tr('위로'), lambda: self.move_item(-1))
        self.add_button(row, tr('아래로'), lambda: self.move_item(1))
        layout.addLayout(row)
        self.editor = ItemEditor()
        self.editor.changed.connect(self.refresh_regions)
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setWidget(self.editor)
        layout.addWidget(scroll, 1)
        self.add_button(layout, tr('항목 편집 적용'), lambda: self.guarded(self.apply_item))
        formatting = QHBoxLayout()
        self.add_button(formatting, tr('출력 형식 변경'), self.edit_output_format)
        layout.addLayout(formatting)
        self.tabs.addTab(widget, tr('추출 항목'))

    def build_preset_tab(self):
        widget = QWidget()
        layout = QFormLayout(widget)
        self.preset_name = QLineEdit(self.preset.name)
        self.output_dir = QLineEdit()
        layout.addRow(tr('프리셋 이름'), self.preset_name)
        layout.addRow(tr('출력 폴더 (공백=영상 폴더)'), self.output_dir)
        self.add_button(layout, tr('출력 폴더 선택'), self.choose_output)
        for text, callback in [(tr('새 프리셋'), self.new_preset), (tr('프리셋 불러오기'), self.load_preset),
                               (tr('저장 / 이름 변경 반영'), self.save_preset), (tr('다른 이름으로 저장'), lambda: self.save_preset(True)),
                               (tr('현재 프리셋 삭제'), self.delete_preset), (tr('ZIP 내보내기'), self.export_preset),
                               (tr('ZIP 가져오기'), self.import_preset)]:
            self.add_button(layout, text, callback)
        self.tabs.addTab(widget, tr('프리셋 / 출력'))

    def choose_output(self):
        path = QFileDialog.getExistingDirectory(self, tr('출력 폴더'))
        if path:
            self.output_dir.setText(path)

    def sync(self):
        self.editor.apply()
        p = self.preset
        p.name = self.preset_name.text()
        p.image, p.region = self.event_image.path.text(), self.event_region.region()
        p.threshold, p.scales = self.threshold.value(), [float(v.strip()) for v in self.scales.text().split(',')]
        p.interval, p.delay, p.absence = self.interval.value(), self.delay.value(), self.absence.value()
        p.output_directory = self.output_dir.text()
        p.validate()
        return p

    def apply_item(self):
        self.editor.apply()
        self.preset.validate()
        self.update_list(self.items.currentRow())
        self.refresh_regions()

    def update_list(self, index=-1):
        self.items.blockSignals(True)
        self.items.clear()
        for item in self.preset.items:
            r = item.region
            kind = tr('문자열 (OCR)') if item.kind == 'ocr' else tr('이미지 존재 여부')
            self.items.addItem(f'{"●" if item.enabled else "○"} {item.name} [{kind}] ({r.x},{r.y},{r.width},{r.height})')
        self.items.setCurrentRow(index)
        self.items.blockSignals(False)

    def select_item(self, index):
        if self.loading:
            return
        def action():
            self.editor.apply()
            self.editor.load(self.preset.items[index] if index >= 0 else None)
            self.refresh_regions()
        self.guarded(action)

    def add_item(self):
        kind, ok = QInputDialog.getItem(self, tr('추출 항목 추가'), tr('유형'), [tr('문자열 (OCR)'), tr('이미지 존재 여부')], 0, False)
        if ok:
            def action():
                self.editor.apply()
                item = ExtractionItem(name=tr('항목 {0}').format(len(self.preset.items) + 1), kind='ocr' if kind.startswith(tr('문자열')) else 'image')
                self.preset.items.append(item)
                self.update_list(len(self.preset.items)-1)
                self.editor.load(item)
                self.tabs.setCurrentIndex(1)
            self.guarded(action)

    def delete_item(self):
        index = self.items.currentRow()
        if index >= 0:
            self.editor.item = None
            del self.preset.items[index]
            index = min(index, len(self.preset.items)-1)
            self.update_list(index)
            self.editor.load(self.preset.items[index] if index >= 0 else None)
            self.refresh_regions()

    def move_item(self, offset):
        def action():
            self.editor.apply()
            index = self.items.currentRow()
            target = index + offset
            if index >= 0 and 0 <= target < len(self.preset.items):
                self.preset.items[index], self.preset.items[target] = self.preset.items[target], self.preset.items[index]
                self.update_list(target)
                self.refresh_regions()
        self.guarded(action)

    def refresh_regions(self, *args):
        if self.loading or not hasattr(self, 'editor'):
            return
        regions = [self.event_region.region()]
        for item in self.preset.items:
            regions.append(self.editor.region.region() if item is self.editor.item else item.region)
        active = self.items.currentRow()+1 if self.tabs.currentIndex() == 1 else 0
        self.preview.show_regions(regions, active)

    def region_selected(self, region):
        if self.tabs.currentIndex() == 1 and self.editor.item:
            self.editor.region.set_region(region)
        else:
            self.event_region.set_region(region)
        self.refresh_regions()

    def open_video(self):
        path, _ = QFileDialog.getOpenFileName(self, tr('영상 선택'), '', tr('영상 (*.mkv *.mp4)'))
        self.load_video(path)

    def load_video(self, path):
        if not path:
            return
        def action():
            reader = VideoReader(path)
            try:
                time, frame = next(reader.frames())
            except Exception:
                reader.close()
                raise
            if self.reader:
                self.reader.close()
            self.reader, self.video = reader, path
            self.timeline.setRange(0, max(0, round(reader.duration*1000)))
            self.info.setText(f'{Path(path).name} | {reader.width}×{reader.height} | FPS {reader.fps:.3f} | {timestamp(reader.duration)}')
            self.show_frame(time, frame)
            self.frame_times = [time]
        self.guarded(action)

    def show_frame(self, time, frame):
        self.current_time = time
        self.preview.set_frame(frame)
        self.position.setValue(time)
        self.timeline.setValue(round(time*1000))
        self.time_label.setText(timestamp(time))
        self.refresh_regions()

    def seek(self, seconds):
        if self.reader:
            self.guarded(lambda: self.show_frame(*self.reader.at(seconds)))

    def next_frame(self):
        if self.reader:
            def action():
                # Decode from a keyframe, keeping exact PTS even for VFR video.
                self.reader.at(self.current_time)
                for time, frame in self.reader.frames():
                    if time > self.current_time + 1e-9:
                        self.show_frame(time, frame)
                        break
            self.guarded(action)

    def previous_frame(self):
        if self.reader:
            def action():
                target = self.current_time
                if target <= 0:
                    return
                start = max(0, target-1)
                while True:
                    candidate = self.reader.at(start)
                    previous = candidate if candidate[0] < target-1e-9 else None
                    for time, frame in self.reader.frames():
                        if time >= target-1e-9:
                            break
                        previous = time, frame
                    if previous or start == 0:
                        if previous:
                            self.show_frame(*previous)
                        return
                    start = max(0, start-2)
            self.guarded(action)

    def test_frame(self):
        if self.preview.frame is None:
            self.error(tr('먼저 영상을 선택하세요.'))
            return
        if self.test_worker and self.test_worker.isRunning():
            return
        def action():
            self.test_worker = TestWorker(self.sync(), self.preview.frame, self.current_time)
            self.test_worker.result.connect(self.log)
            self.test_worker.failed.connect(self.error)
            self.test_worker.start()
        self.guarded(action)

    def set_running(self, running):
        self.start_button.setEnabled(not running)
        for button in (self.pause_button, self.resume_button, self.stop_button):
            button.setEnabled(running)

    def start_analysis(self):
        def action():
            if not self.video:
                raise ValueError(tr('먼저 영상을 선택하세요.'))
            preset = self.sync()
            if not any(i.enabled for i in preset.items):
                raise ValueError(tr('활성화된 추출 항목이 없습니다.'))
            output = (Path(preset.output_directory) if preset.output_directory else Path(self.video).parent) / (Path(self.video).stem+'.txt')
            overwrite = output.exists()
            if overwrite and QMessageBox.question(self, tr('덮어쓰기 확인'), tr('{0}\n기존 결과를 덮어쓸까요?').format(output)) != QMessageBox.Yes:
                return
            self.worker = AnalysisWorker(self.video, preset, output, overwrite)
            self.worker.message.connect(self.log)
            self.worker.failed.connect(self.error)
            self.worker.progress.connect(self.on_progress)
            self.worker.finished.connect(lambda: self.set_running(False))
            self.set_running(True)
            self.progress.setValue(0)
            self.worker.start()
        self.guarded(action)

    def on_progress(self, time, detected, completed, pending):
        self._last_progress = time, detected, completed, pending
        duration = self.reader.duration if self.reader else 0
        self.progress.setValue(min(100, int(time/duration*100)) if duration else 0)
        self.status.setText(tr('{0} / {1} | 감지 {2} | 기록 {3} | 대기 {4}').format(timestamp(time), timestamp(duration), detected, completed, pending))

    def set_pause(self, paused):
        if self.worker and self.worker.isRunning():
            self.worker.pause(paused)
            self.log(tr('일시정지 요청') if paused else tr('분석 재개'))

    def stop_analysis(self):
        if self.worker:
            self.worker.stop()

    def populate(self, preset):
        self.loading = True
        self.editor.item = None
        self.preset = preset
        self.preset_name.setText(preset.name)
        self.event_image.path.setText(preset.image)
        self.event_region.set_region(preset.region)
        self.threshold.setValue(preset.threshold)
        self.scales.setText(', '.join(map(str, preset.scales)))
        self.interval.setValue(preset.interval)
        self.delay.setValue(preset.delay)
        self.absence.setValue(preset.absence)
        self.output_dir.setText(preset.output_directory)
        self.update_list(0 if preset.items else -1)
        self.editor.load(preset.items[0] if preset.items else None)
        self.loading = False
        self.refresh_regions()
        missing = [obj.image for obj in preset_service.references(preset) if obj.image and not Path(obj.image).is_file()]
        if missing:
            self.error(tr('이미지가 없습니다. 해당 이미지 선택 버튼으로 경로를 다시 지정하세요.\n')+'\n'.join(missing))

    def new_preset(self):
        self.preset_path = None
        self.populate(Preset())

    def save_preset(self, save_as=False):
        def action():
            preset = self.sync()
            path = self.preset_path
            if save_as or not path:
                path, _ = QFileDialog.getSaveFileName(self, tr('프리셋 저장'), str(presets_dir() / 'preset.json'), 'JSON (*.json)')
            if path:
                preset_service.save(preset, path)
                self.preset_path = path
                self.log(tr('프리셋 저장: {0}').format(path))
        self.guarded(action)

    def load_preset(self):
        path, _ = QFileDialog.getOpenFileName(self, tr('프리셋 불러오기'), str(presets_dir()), 'JSON (*.json)')
        if path:
            def action():
                self.populate(preset_service.load(path))
                self.preset_path = path
            self.guarded(action)

    def delete_preset(self):
        if self.preset_path and QMessageBox.question(self, tr('프리셋 삭제'), tr('현재 JSON 프리셋을 삭제할까요?')) == QMessageBox.Yes:
            def action():
                Path(self.preset_path).unlink()
                self.new_preset()
            self.guarded(action)

    def export_preset(self):
        path, _ = QFileDialog.getSaveFileName(self, tr('ZIP 내보내기'), str(presets_dir() / 'preset.zip'), 'ZIP (*.zip)')
        if path:
            self.guarded(lambda: preset_service.export_zip(self.sync(), path))

    def import_preset(self):
        path, _ = QFileDialog.getOpenFileName(self, tr('ZIP 가져오기'), str(presets_dir()), 'ZIP (*.zip)')
        if path:
            def action():
                preset = preset_service.import_zip(path, data_dir() / 'imports')
                self.preset_path = None
                self.populate(preset)
            self.guarded(action)

    def closeEvent(self, event):
        active = [w for w in (self.worker, self.test_worker) if w and w.isRunning()]
        if active:
            self.stop_analysis()
            self.log(tr('작업 종료를 기다리는 중입니다. 종료 후 창을 다시 닫아 주세요.'))
            event.ignore()
            return
        if self.reader:
            self.reader.close()
        event.accept()
