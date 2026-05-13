"""
guru/ui/viewer.py

PDF viewer panel — renders pages, handles zoom, scrolls.

This widget is the left half of the main window.
It owns a QScrollArea containing a QLabel that displays
the rendered QPixmap from PDFReader.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea,
    QLabel, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QPixmap, QKeyEvent

from guru.core.pdf_reader import PDFReader
import guru.ui.theme as T


class PDFViewer(QWidget):
    """
    Renders a single PDF page at a time.

    Signals:
        page_changed(int):   Emitted with new 0-based page number.
    """

    page_changed = pyqtSignal(int)

    def __init__(self, reader: PDFReader, parent=None) -> None:
        super().__init__(parent)
        self._reader = reader
        self._current_page = 0
        self._zoom = 1.5

        self._build_ui()

    # ── UI construction ───────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Scroll area contains the page label
        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll.setStyleSheet(
            f"QScrollArea {{ background: {T.BG_DEEP}; border: none; }}"
        )

        # The page label — holds the rendered pixmap
        self._page_label = QLabel()
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._page_label.setSizePolicy(
            QSizePolicy.Policy.Expanding,
            QSizePolicy.Policy.Expanding,
        )
        self._page_label.setStyleSheet(
            f"QLabel {{ background: {T.BG_DEEP}; padding: 24px; }}"
        )

        # Drop zone text — shown before a PDF is opened
        self._show_drop_hint()

        self._scroll.setWidget(self._page_label)
        layout.addWidget(self._scroll)

    # ── Public API ────────────────────────────────────────────

    def load_page(self, page_num: int) -> None:
        """
        Render and display a specific page.

        Args:
            page_num: 0-based page index.
        """
        if not self._reader.is_open:
            return

        # Clamp to valid range
        page_num = max(0, min(page_num, self._reader.page_count - 1))
        self._current_page = page_num

        pixmap = self._reader.render_page(page_num, zoom=self._zoom)
        if pixmap:
            self._page_label.setPixmap(pixmap)
            self._page_label.adjustSize()
        else:
            self._page_label.setText("Could not render this page.")

        self.page_changed.emit(page_num)

    def next_page(self) -> None:
        if self._reader.is_open and self._current_page < self._reader.page_count - 1:
            self.load_page(self._current_page + 1)

    def prev_page(self) -> None:
        if self._reader.is_open and self._current_page > 0:
            self.load_page(self._current_page - 1)

    def zoom_in(self) -> None:
        self._zoom = min(3.0, self._zoom + 0.2)
        self.load_page(self._current_page)

    def zoom_out(self) -> None:
        self._zoom = max(0.5, self._zoom - 0.2)
        self.load_page(self._current_page)

    def on_pdf_opened(self) -> None:
        """Called by MainWindow after a PDF is successfully opened."""
        self._current_page = 0
        self.load_page(0)

    @property
    def current_page(self) -> int:
        return self._current_page

    @property
    def zoom(self) -> float:
        return self._zoom

    @property
    def zoom_percent(self) -> int:
        return int(self._zoom / 1.5 * 100)

    # ── Keyboard navigation ───────────────────────────────────

    def keyPressEvent(self, event: QKeyEvent) -> None:
        key = event.key()
        if key in (Qt.Key.Key_Right, Qt.Key.Key_Down, Qt.Key.Key_PageDown):
            self.next_page()
        elif key in (Qt.Key.Key_Left, Qt.Key.Key_Up, Qt.Key.Key_PageUp):
            self.prev_page()
        else:
            super().keyPressEvent(event)

    # ── Private ───────────────────────────────────────────────

    def _show_drop_hint(self) -> None:
        self._page_label.setText(
            '<div style="text-align:center; color:#4a4d56; font-family: Georgia, serif;">'
            '<p style="font-size:48px; margin-bottom:8px;">📖</p>'
            '<p style="font-size:18px; margin-bottom:8px;">Open a PDF to begin</p>'
            '<p style="font-size:13px;">Click <b style="color:#c8a96e;">Open PDF</b> '
            'or drag a file here</p>'
            '</div>'
        )
