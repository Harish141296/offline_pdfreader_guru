"""
guru/ui/main_window.py

Main application window — the orchestrator.

Wires together:
  PDFViewer  ←→  PDFReader  ←→  TextExtractor
                                      ↓
  Sidebar    ←→  AIEngine   ←→  ExplainWorker (thread)

All business logic lives in core/. The window just connects signals.
"""

from __future__ import annotations

import os
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout,
    QToolBar, QPushButton, QLabel,
    QFileDialog, QSplitter, QStatusBar,
)
from PyQt6.QtCore import Qt, QTimer, pyqtSlot
from PyQt6.QtGui import QKeySequence, QShortcut

from guru.core.pdf_reader import PDFReader
from guru.core.extractor import TextExtractor
from guru.core.ai_engine import AIEngine, fetch_available_models, is_ollama_running
from guru.ui.viewer import PDFViewer
from guru.ui.sidebar import Sidebar
import guru.ui.theme as T


class MainWindow(QMainWindow):
    """
    Top-level application window.

    Responsibilities:
    - Build and lay out all UI widgets
    - Connect signals between UI components and core engine
    - Handle Ollama health checks (on a timer)
    - Manage keyboard shortcuts
    """

    def __init__(self) -> None:
        super().__init__()

        # ── Core objects ──
        self._reader   = PDFReader()
        self._extractor = TextExtractor(self._reader)
        self._ai       = AIEngine()

        # ── Window setup ──
        self.setWindowTitle("Offline PDF_READER_GURU")
        self.setMinimumSize(1100, 700)
        self.resize(1280, 800)

        self._build_ui()
        self._connect_signals()
        self._setup_shortcuts()

        # ── Ollama check (immediately + every 30 seconds) ──
        self._check_ollama()
        self._ollama_timer = QTimer(self)
        self._ollama_timer.timeout.connect(self._check_ollama)
        self._ollama_timer.start(30_000)

    # ── UI construction ───────────────────────────────────────

    def _build_ui(self) -> None:
        self.setStyleSheet(T.STYLESHEET)

        # ── Toolbar ──
        toolbar = QToolBar("Main Toolbar")
        toolbar.setMovable(False)
        toolbar.setStyleSheet(
            f"QToolBar {{ background: {T.BG_SURFACE}; "
            f"border-bottom: 1px solid {T.BORDER}; "
            f"padding: 4px 12px; spacing: 6px; }}"
        )
        self.addToolBar(toolbar)

        # Logo
        logo = QLabel("Guru")
        logo.setObjectName("logoLabel")
        logo.setStyleSheet(
            f"color: {T.ACCENT}; font-size: 20px; "
            f"font-family: Georgia, serif; padding-right: 8px;"
        )
        toolbar.addWidget(logo)

        # Separator widget
        def sep():
            s = QLabel("|")
            s.setStyleSheet(f"color: {T.BORDER}; padding: 0 4px;")
            return s

        toolbar.addWidget(sep())

        # Open PDF
        self._open_btn = QPushButton("Open PDF")
        self._open_btn.setObjectName("openBtn")
        toolbar.addWidget(self._open_btn)

        toolbar.addWidget(sep())

        # Navigation
        self._prev_btn = QPushButton("◀")
        self._prev_btn.setObjectName("navBtn")
        self._prev_btn.setToolTip("Previous page (←)")
        self._prev_btn.setEnabled(False)

        self._page_label = QLabel("— / —")
        self._page_label.setObjectName("pageLabel")
        self._page_label.setMinimumWidth(80)
        self._page_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._next_btn = QPushButton("▶")
        self._next_btn.setObjectName("navBtn")
        self._next_btn.setToolTip("Next page (→)")
        self._next_btn.setEnabled(False)

        toolbar.addWidget(self._prev_btn)
        toolbar.addWidget(self._page_label)
        toolbar.addWidget(self._next_btn)

        toolbar.addWidget(sep())

        # Zoom
        self._zoom_out_btn = QPushButton("−")
        self._zoom_out_btn.setObjectName("navBtn")
        self._zoom_out_btn.setEnabled(False)

        self._zoom_label = QLabel("100%")
        self._zoom_label.setObjectName("pageLabel")
        self._zoom_label.setMinimumWidth(40)
        self._zoom_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self._zoom_in_btn = QPushButton("+")
        self._zoom_in_btn.setObjectName("navBtn")
        self._zoom_in_btn.setEnabled(False)

        toolbar.addWidget(self._zoom_out_btn)
        toolbar.addWidget(self._zoom_label)
        toolbar.addWidget(self._zoom_in_btn)

        # ── Central widget ──
        central = QWidget()
        central.setStyleSheet(f"background: {T.BG_DEEP};")
        self.setCentralWidget(central)

        main_layout = QHBoxLayout(central)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Splitter: PDF viewer (left) + Sidebar (right)
        self._splitter = QSplitter(Qt.Orientation.Horizontal)
        self._splitter.setHandleWidth(1)
        self._splitter.setStyleSheet(
            f"QSplitter::handle {{ background: {T.BORDER}; }}"
        )

        self._viewer = PDFViewer(self._reader)
        self._sidebar = Sidebar()

        self._splitter.addWidget(self._viewer)
        self._splitter.addWidget(self._sidebar)
        self._splitter.setSizes([780, 360])
        self._splitter.setCollapsible(0, False)
        self._splitter.setCollapsible(1, False)

        main_layout.addWidget(self._splitter)

        # ── Status bar ──
        self.statusBar().showMessage("Welcome to Guru — open a PDF to begin")

    # ── Signal connections ────────────────────────────────────

    def _connect_signals(self) -> None:
        # Toolbar buttons
        self._open_btn.clicked.connect(self._open_pdf)
        self._prev_btn.clicked.connect(self._viewer.prev_page)
        self._next_btn.clicked.connect(self._viewer.next_page)
        self._zoom_in_btn.clicked.connect(self._on_zoom_in)
        self._zoom_out_btn.clicked.connect(self._on_zoom_out)

        # Viewer → update toolbar
        self._viewer.page_changed.connect(self._on_page_changed)

        # Sidebar → AI engine
        self._sidebar.explain_requested.connect(self._on_explain_requested)
        self._sidebar.ask_requested.connect(self._on_ask_requested)
        self._sidebar.model_changed.connect(self._ai.set_model)

    # ── Keyboard shortcuts ────────────────────────────────────

    def _setup_shortcuts(self) -> None:
        # Space → explain current page
        QShortcut(QKeySequence("Space"), self).activated.connect(
            self._on_explain_requested
        )
        # Ctrl+O → open file
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self._open_pdf)

    # ── Slots ─────────────────────────────────────────────────

    @pyqtSlot()
    def _open_pdf(self) -> None:
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Open PDF",
            os.path.expanduser("~"),
            "PDF Files (*.pdf)",
        )
        if not path:
            return

        if self._reader.open(path):
            self._viewer.on_pdf_opened()
            self._sidebar.set_pdf_loaded(True)
            self._prev_btn.setEnabled(True)
            self._next_btn.setEnabled(True)
            self._zoom_in_btn.setEnabled(True)
            self._zoom_out_btn.setEnabled(True)
            self.setWindowTitle(f"Sage — {self._reader.file_name}")
            self.statusBar().showMessage(
                f"Opened: {self._reader.file_name}  |  "
                f"{self._reader.page_count} pages"
            )
        else:
            self.statusBar().showMessage("Failed to open PDF.")

    @pyqtSlot(int, int, int)
    def _on_page_changed(self, current: int, total: int, zoom_pct: int) -> None:
        """current is already 1-based from PDFViewer signal."""
        self._page_label.setText(f"{current} / {total}")
        self._zoom_label.setText(f"{zoom_pct}%")

    @pyqtSlot()
    def _on_explain_requested(self) -> None:
        if not self._reader.is_open:
            return

        result = self._extractor.extract(self._viewer.current_page)

        if not result.is_usable:
            self._sidebar.show_error(result.status_message)
            return

        page_label = self._reader.get_page_label(self._viewer.current_page)
        self._sidebar.start_streaming(page_label)

        self._ai.set_model(self._sidebar.selected_model)
        self._ai.explain(
            result=result,
            on_token=self._sidebar.append_token,
            on_done=self._sidebar.finish_streaming,
            on_error=self._sidebar.show_error,
        )

    @pyqtSlot(str)
    def _on_ask_requested(self, question: str) -> None:
        if not self._reader.is_open:
            self._sidebar.show_error("Please open a PDF first.")
            return

        result = self._extractor.extract(self._viewer.current_page)
        if not result.is_usable:
            self._sidebar.show_error(result.status_message)
            return

        # Capture prior explanation BEFORE start_streaming() clears the display
        # If user hasn't explained the page yet, prior will be "" — that's fine,
        # the prompt template handles it gracefully
        prior = self._sidebar.last_response

        page_label = self._reader.get_page_label(self._viewer.current_page)
        self._sidebar.start_streaming(f"{page_label} — Q&A")

        self._ai.set_model(self._sidebar.selected_model)
        self._ai.ask(
            result=result,
            question=question,
            prior_explanation=prior,
            on_token=self._sidebar.append_token,
            on_done=self._sidebar.finish_streaming,
            on_error=self._sidebar.show_error,
        )

    @pyqtSlot()
    def _on_zoom_in(self) -> None:
        self._viewer.zoom_in()

    @pyqtSlot()
    def _on_zoom_out(self) -> None:
        self._viewer.zoom_out()

    # ── Ollama health check ───────────────────────────────────

    def _check_ollama(self) -> None:
        ok = is_ollama_running()
        self._sidebar.set_ollama_status(ok)
        if ok:
            models = fetch_available_models()
            self._sidebar.populate_models(models)
            if models:
                self._ai.set_model(self._sidebar.selected_model)

    # ── Cleanup ───────────────────────────────────────────────

    def closeEvent(self, event) -> None:
        self._ai.cancel()
        self._reader.close()
        super().closeEvent(event)
