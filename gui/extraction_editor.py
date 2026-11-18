from PySide6.QtCore import Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (QWidget, QFormLayout, QHBoxLayout, QVBoxLayout, QLineEdit,
    QPushButton, QDoubleSpinBox, QSpinBox, QComboBox, QCheckBox, QFileDialog, QLabel)
from models.preset import Region

def number(value=0, maximum=100000, decimals=3):
    widget = QDoubleSpinBox()
    widget.setDecimals(decimals)
    widget.setRange(0, maximum)
    widget.setValue(value)
    return widget

class RegionEditor(QWidget):
    changed = Signal()

    def __init__(self):
        super().__init__()
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        self.values = []
        for name in ('X', 'Y', '폭', '높이'):
            layout.addWidget(QLabel(name))
            spin = QSpinBox()
            spin.setRange(0, 100000)
            spin.valueChanged.connect(self.changed)
            self.values.append(spin)
            layout.addWidget(spin)
        self.set_region(Region())

    def region(self):
        return Region(*(v.value() for v in self.values))

    def set_region(self, region):
        for spin, value in zip(self.values, (region.x, region.y, region.width, region.height)):
            spin.blockSignals(True)
            spin.setValue(value)
            spin.blockSignals(False)
        self.changed.emit()

class ImageEditor(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        row = QHBoxLayout()
        self.path = QLineEdit()
        button = QPushButton('이미지 선택')
        button.clicked.connect(self.browse)
        row.addWidget(self.path)
        row.addWidget(button)
        layout.addLayout(row)
        self.preview = QLabel()
        self.preview.setMaximumHeight(70)
        layout.addWidget(self.preview)
        self.path.textChanged.connect(self.refresh)

    def browse(self):
        path, _ = QFileDialog.getOpenFileName(self, '기준 이미지', '', '이미지 (*.png *.jpg *.jpeg)')
        if path:
            self.path.setText(path)

    def refresh(self):
        pixmap = QPixmap(self.path.text())
        self.preview.setPixmap(pixmap.scaledToHeight(64) if not pixmap.isNull() else QPixmap())

class ItemEditor(QWidget):
    changed = Signal()

    def __init__(self):
        super().__init__()
        self.item = None
        form = QFormLayout(self)
        self.name = QLineEdit()
        self.enabled = QCheckBox('활성화')
        self.kind = QComboBox()
        self.kind.addItem('문자열 (OCR)', 'ocr')
        self.kind.addItem('이미지 존재 여부', 'image')
        self.region = RegionEditor()
        self.image = ImageEditor()
        self.threshold = number(.9, 1)
        self.scales = QLineEdit('1.0')
        self.language = QComboBox()
        self.language.setEditable(True)
        self.language.addItems(['eng', 'kor', 'jpn', 'kor+eng', 'jpn+eng'])
        self.fallback = QLineEdit()
        self.zoom = number(2, 10)
        self.zoom.setMinimum(.1)
        self.contrast = number(1, 10)
        self.contrast.setMinimum(.1)
        self.gray = QCheckBox('그레이스케일')
        self.binary = QCheckBox('이진화')
        self.denoise = QCheckBox('노이즈 제거')
        fields = [('이름', self.name), ('사용', self.enabled), ('유형', self.kind), ('원본 좌표', self.region),
                  ('기준 이미지', self.image), ('유사도', self.threshold), ('스케일 (쉼표 구분)', self.scales),
                  ('OCR 언어', self.language), ('실패 기본값', self.fallback), ('확대 배율', self.zoom),
                  ('대비', self.contrast), ('전처리', self.gray), ('', self.binary), ('', self.denoise)]
        self.form = form
        for label, widget in fields:
            form.addRow(label, widget)
        self.image_widgets = [self.image, self.threshold, self.scales]
        self.ocr_widgets = [self.language, self.fallback, self.zoom, self.contrast, self.gray, self.binary, self.denoise]
        self.kind.currentIndexChanged.connect(self.visibility)
        self.region.changed.connect(self.changed)
        self.name.textChanged.connect(self.changed)
        self.enabled.toggled.connect(self.changed)
        self.setEnabled(False)

    def visibility(self):
        is_image = self.kind.currentData() == 'image'
        for widget in self.image_widgets:
            self.form.setRowVisible(widget, is_image)
        for widget in self.ocr_widgets:
            self.form.setRowVisible(widget, not is_image)

    def load(self, item):
        self.item = item
        self.setEnabled(item is not None)
        if item is None:
            return
        self.name.setText(item.name)
        self.enabled.setChecked(item.enabled)
        self.kind.setCurrentIndex(0 if item.kind == 'ocr' else 1)
        self.region.set_region(item.region)
        self.image.path.setText(item.image)
        self.threshold.setValue(item.threshold)
        self.scales.setText(', '.join(map(str, item.scales)))
        self.language.setCurrentText(item.language)
        self.fallback.setText(item.fallback)
        self.zoom.setValue(item.zoom)
        self.contrast.setValue(item.contrast)
        self.gray.setChecked(item.grayscale)
        self.binary.setChecked(item.binary)
        self.denoise.setChecked(item.denoise)
        self.visibility()

    def apply(self):
        if self.item is None:
            return
        item = self.item
        item.name, item.enabled, item.kind = self.name.text(), self.enabled.isChecked(), self.kind.currentData()
        item.region = self.region.region()
        item.image, item.threshold = self.image.path.text(), self.threshold.value()
        item.scales = [float(v.strip()) for v in self.scales.text().split(',')]
        item.language, item.fallback = self.language.currentText(), self.fallback.text()
        item.zoom, item.contrast = self.zoom.value(), self.contrast.value()
        item.grayscale, item.binary, item.denoise = self.gray.isChecked(), self.binary.isChecked(), self.denoise.isChecked()
