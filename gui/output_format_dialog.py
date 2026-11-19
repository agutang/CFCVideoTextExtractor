from PySide6.QtWidgets import QDialog, QFormLayout, QLineEdit, QDialogButtonBox, QMessageBox, QLabel
from services.text_format import validate_template
from services.i18n import tr

class OutputFormatDialog(QDialog):
    def __init__(self, preset, parent=None):
        super().__init__(parent)
        self.names = [i.name for i in preset.items if i.enabled]
        self.setWindowTitle(tr('Output formatting'))
        self.resize(600, 180)
        layout = QFormLayout(self)
        self.template = QLineEdit(preset.output_template)
        layout.addRow(tr('Template (empty=original output)'), self.template)
        available = QLabel(', '.join('{' + name + '}' for name in self.names))
        available.setWordWrap(True)
        layout.addRow(tr('Available fields'), available)
        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addRow(buttons)

    def accept(self):
        try:
            validate_template(self.template.text(), self.names)
        except ValueError as exc:
            QMessageBox.warning(self, tr('Error'), str(exc))
            return
        super().accept()
