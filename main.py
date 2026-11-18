import logging
import sys
from PySide6.QtWidgets import QApplication
from gui.main_window import MainWindow
from gui.application import configure_app
from services.configuration import data_dir

def main():
    if len(sys.argv) == 3 and sys.argv[1] == '--self-test':
        from core.self_test import run
        sys.exit(run(sys.argv[2]))
    logging.basicConfig(filename=data_dir() / 'application.log', encoding='utf-8',
                        level=logging.INFO, format='%(asctime)s %(levelname)s %(message)s')
    app = QApplication(sys.argv)
    configure_app(app)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == '__main__':
    main()
