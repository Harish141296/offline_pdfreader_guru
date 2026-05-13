"""
guru/ui/viewer.py

PDF viewer panel with floating bottom navigation overlay.
The controls appear on hover over the bottom area — clean reading
experience, controls always accessible without toolbar.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QScrollArea,
    QLabel, QSizePolicy, QPushButton, QHBoxLayout,
)
from PyQt6.QtCore import Qt, pyqtSignal, QTimer, QPropertyAnimation, QEasingCurve, QRect
from PyQt6.QtGui import QPixmap, QKeyEvent, QEnterEvent, QColor
import guru.ui.theme as T
from guru.core.pdf_reader import PDFReader


class FloatingNavBar(QWidget):
    """
    Pill-shaped floating control bar that sits at the bottom
    of the PDF viewer. Fades in on mouse proximity, fades out
    when the mouse leaves the viewer area.
    """

    prev_clicked  = pyqtSignal()
    next_clicked  = pyqtSignal()
    zoomin_clicked  = pyqtSignal()
    zoomout_clicked = pyqtSignal()

    def __init__(self, parent: QWidget) -> None:
        super().__init__(parent)
        self.setFixedHeight(48)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)

        self._build_ui()
        self.setVisible(True)
        self.setWindowOpacity(0.0)

        # Fade animation
        self._anim = QPropertyAnimation(self, b"windowOpacity")
        self._anim.setDuration(200)
        self._anim.setEasingCurve(QEasingCurve.Type.InOutCubic)

        # Auto-hide timer — hide 2s after mouse leaves
        self._hide_timer = QTimer(self)
        self._hide_timer.setSingleShot(True)
        self._hide_timer.timeout.connect(self.fade_out)

    def _build_ui(self) -> None:
        layout = QHBoxLayout(self)
        layout.setContentsMargins(16, 6, 16, 6)
        layout.setSpacing(8)

        pill_style = f"""
            QWidget {{
                background: rgba(22, 24, 28, 0.92);
                border-radius: 24px;
                border: 1px solid {T.BORDER};
            }}
        """
        btn_style = f"""
            QPushButton {{
                background: transparent;
                color: {T.TEXT_PRIMARY};
                border: none;
                font-size: 16px;
                padding: 0px 14px;
                border-radius: 0px;
                min-width: 36px;
                min-height: 36px;
            }}
            QPushButton:hover {{
                color: {T.ACCENT};
                background: rgba(200,169,110,0.10);
                border-radius: 8px;
            }}
            QPushButton:disabled {{
                color: {T.TEXT_DIM};
            }}
        """
        sep_style = f"color: {T.BORDER}; font-size: 18px; padding: 0 2px;"

        # Pill container
        pill = QWidget()
        pill.setStyleSheet(pill_style)
        pill_layout = QHBoxLayout(pill)
        pill_layout.setContentsMargins(8, 4, 8, 4)
        pill_layout.setSpacing(0)

        self._prev_btn = QPushButton("◀")
        self._prev_btn.setStyleSheet(btn_style)
        self._prev_btn.setToolTip("Previous page  [←]")
        self._prev_btn.clicked.connect(self.prev_clicked)

        self._page_lbl = QLabel("— / —")
        self._page_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._page_lbl.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 13px; "
            f"font-family: Consolas, monospace; min-width: 72px; background: transparent; border: none;"
        )

        self._next_btn = QPushButton("▶")
        self._next_btn.setStyleSheet(btn_style)
        self._next_btn.setToolTip("Next page  [→]")
        self._next_btn.clicked.connect(self.next_clicked)

        sep = QLabel("|")
        sep.setStyleSheet(sep_style + " background: transparent; border: none;")

        self._zout_btn = QPushButton("−")
        self._zout_btn.setStyleSheet(btn_style)
        self._zout_btn.setToolTip("Zoom out")
        self._zout_btn.clicked.connect(self.zoomout_clicked)

        self._zoom_lbl = QLabel("100%")
        self._zoom_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._zoom_lbl.setStyleSheet(
            f"color: {T.TEXT_SECONDARY}; font-size: 12px; "
            f"font-family: Consolas, monospace; min-width: 44px; background: transparent; border: none;"
        )

        self._zin_btn = QPushButton("+")
        self._zin_btn.setStyleSheet(btn_style)
        self._zin_btn.setToolTip("Zoom in")
        self._zin_btn.clicked.connect(self.zoomin_clicked)

        pill_layout.addWidget(self._prev_btn)
        pill_layout.addWidget(self._page_lbl)
        pill_layout.addWidget(self._next_btn)
        pill_layout.addWidget(sep)
        pill_layout.addWidget(self._zout_btn)
        pill_layout.addWidget(self._zoom_lbl)
        pill_layout.addWidget(self._zin_btn)

        layout.addStretch()
        layout.addWidget(pill)
        layout.addStretch()

    # ── Public API ────────────────────────────────────────────

    def update_labels(self, current: int, total: int, zoom_pct: int) -> None:
        self._page_lbl.setText(f"{current} / {total}")
        self._zoom_lbl.setText(f"{zoom_pct}%")
        self._prev_btn.setEnabled(current > 1)
        self._next_btn.setEnabled(current < total)

    def fade_in(self) -> None:
        self._hide_timer.stop()
        self._anim.stop()
        self._anim.setStartValue(self.windowOpacity())
        self._anim.setEndValue(1.0)
        self._anim.start()

    def fade_out(self) -> None:
        self._anim.stop()
        self._anim.setStartValue(self.windowOpacity())
        self._anim.setEndValue(0.0)
        self._anim.start()

    def schedule_hide(self, ms: int = 2000) -> None:
        self._hide_timer.start(ms)


class PDFViewer(QWidget):
    """
    PDF viewer with floating bottom nav bar.

    Signals:
        page_changed(int, int, int):  current(1-based), total, zoom_pct
    """

    page_changed = pyqtSignal(int, int, int)   # current_1based, total, zoom_pct

    def __init__(self, reader: PDFReader, parent=None) -> None:
        super().__init__(parent)
        self._reader = reader
        self._current_page = 0
        self._zoom = 1.5
        self.setMouseTracking(True)
        self._build_ui()

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self._scroll = QScrollArea()
        self._scroll.setWidgetResizable(True)
        self._scroll.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._scroll.setMouseTracking(True)
        self._scroll.setStyleSheet(
            f"QScrollArea {{ background: {T.BG_DEEP}; border: none; }}"
        )

        self._page_label = QLabel()
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._page_label.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        self._page_label.setStyleSheet(
            f"QLabel {{ background: {T.BG_DEEP}; padding: 24px; }}"
        )
        self._page_label.setMouseTracking(True)
        self._show_drop_hint()

        self._scroll.setWidget(self._page_label)
        layout.addWidget(self._scroll)

        # Floating nav bar — child of THIS widget so it overlays the scroll area
        self._nav = FloatingNavBar(self)
        self._nav.prev_clicked.connect(self.prev_page)
        self._nav.next_clicked.connect(self.next_page)
        self._nav.zoomin_clicked.connect(self.zoom_in)
        self._nav.zoomout_clicked.connect(self.zoom_out)
        self._position_nav()

    # ── Overlay positioning ───────────────────────────────────

    def _position_nav(self) -> None:
        """Place the nav bar 20px above the bottom edge, full width."""
        w = self.width()
        h = self.height()
        bar_h = self._nav.height()
        self._nav.setGeometry(0, h - bar_h - 20, w, bar_h)

    def resizeEvent(self, event) -> None:
        super().resizeEvent(event)
        self._position_nav()

    # ── Mouse tracking for show/hide ──────────────────────────

    def mouseMoveEvent(self, event) -> None:
        """Show nav when mouse enters bottom 120px of viewer."""
        if not self._reader.is_open:
            return
        in_trigger_zone = event.position().y() > (self.height() - 120)
        if in_trigger_zone:
            self._nav.fade_in()
            self._nav.schedule_hide(2500)
        super().mouseMoveEvent(event)

    def leaveEvent(self, event) -> None:
        self._nav.schedule_hide(800)
        super().leaveEvent(event)

    # ── Public API ────────────────────────────────────────────

    def load_page(self, page_num: int) -> None:
        if not self._reader.is_open:
            return
        page_num = max(0, min(page_num, self._reader.page_count - 1))
        self._current_page = page_num

        pixmap = self._reader.render_page(page_num, zoom=self._zoom)
        if pixmap:
            self._page_label.setPixmap(pixmap)
            self._page_label.adjustSize()
        else:
            self._page_label.setText("Could not render this page.")

        cur = page_num + 1
        total = self._reader.page_count
        pct = self.zoom_percent
        self._nav.update_labels(cur, total, pct)
        self.page_changed.emit(cur, total, pct)

    def next_page(self) -> None:
        if self._reader.is_open and self._current_page < self._reader.page_count - 1:
            self.load_page(self._current_page + 1)

    def prev_page(self) -> None:
        if self._reader.is_open and self._current_page > 0:
            self.load_page(self._current_page - 1)

    def zoom_in(self) -> None:
        self._zoom = min(3.0, self._zoom + 0.25)
        self.load_page(self._current_page)

    def zoom_out(self) -> None:
        self._zoom = max(0.5, self._zoom - 0.25)
        self.load_page(self._current_page)

    def on_pdf_opened(self) -> None:
        self._current_page = 0
        self.load_page(0)
        # Show nav briefly on open so user discovers it
        self._nav.fade_in()
        self._nav.schedule_hide(3000)

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

    def _show_drop_hint(self) -> None:
        self._page_label.setText(
            '<div style="text-align:center; color:#4a4d56; font-family: Georgia, serif;">'
            '<p style="font-size:48px; margin-bottom:8px;">📖</p>'
            '<p style="font-size:18px; margin-bottom:8px;">Open a PDF to begin</p>'
            '<p style="font-size:13px;">Click <b style="color:#c8a96e;">Open PDF</b> '
            'or drag a file here</p>'
            '</div>'
        )
