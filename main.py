"""
main.py — Sage entry point.  Run with: python main.py
"""
import sys
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from guru.ui.main_window import MainWindow

def main():
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )
    app = QApplication(sys.argv)
    app.setApplicationName("Guru")
    app.setApplicationDisplayName("Offline PDF_READER_GURU")
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
