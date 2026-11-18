from pathlib import Path
from PySide6.QtGui import QFont, QFontDatabase

def configure_app(app):
    # Register the OS font explicitly: the offscreen Qt backend has no font fallback.
    font = Path('C:/Windows/Fonts/malgun.ttf')
    if font.is_file():
        QFontDatabase.addApplicationFont(str(font))
        app.setFont(QFont('Malgun Gothic', 9))
