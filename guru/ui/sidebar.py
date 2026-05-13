"""
guru/ui/sidebar.py

AI explanation panel — the right half of the main window.

Contains:
- Section header
- Explain This Page button
- Model picker (ComboBox)
- Streaming explanation display (QTextEdit)
- Ask a question input
- Ollama status indicator
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QFrame, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QTextEdit,
    QComboBox, QLineEdit, QSizePolicy,
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QTextCursor

import guru.ui.theme as T


class Sidebar(QFrame):
    """
    Right panel. Emits signals that MainWindow connects to core logic.

    Signals:
        explain_requested():        User clicked Explain This Page
        ask_requested(str):         User submitted a question
        model_changed(str):         User picked a different model
    """

    explain_requested = pyqtSignal()
    ask_requested     = pyqtSignal(str)
    model_changed     = pyqtSignal(str)

    def __init__(self, parent=None) -> None:
        super().__init__(parent)
        self.setObjectName("sidebar")
        self.setFixedWidth(360)
        self._last_full_response: str = ""
        self._build_ui()

    # ── UI construction ───────────────────────────────────────

    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # ── Header ──
        header = QFrame()
        header.setStyleSheet(
            f"QFrame {{ background: {T.BG_SURFACE}; "
            f"border-bottom: 1px solid {T.BORDER}; }}"
        )
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(T.PADDING, 14, T.PADDING, 14)
        header_layout.setSpacing(10)

        section_lbl = QLabel("PAGE EXPLANATION")
        section_lbl.setObjectName("sectionLabel")

        self._explain_btn = QPushButton("⚡  Explain This Page")
        self._explain_btn.setObjectName("explainBtn")
        self._explain_btn.setEnabled(False)
        self._explain_btn.clicked.connect(self.explain_requested.emit)
        self._explain_btn.setToolTip("Shortcut: Space")

        # Model picker row
        model_row = QHBoxLayout()
        model_row.setSpacing(6)
        model_lbl = QLabel("Model:")
        model_lbl.setObjectName("statusLabel")
        model_lbl.setFixedWidth(42)

        self._model_combo = QComboBox()
        self._model_combo.addItem("Loading models…")
        self._model_combo.currentTextChanged.connect(self._on_model_changed)
        self._model_combo.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed
        )

        model_row.addWidget(model_lbl)
        model_row.addWidget(self._model_combo)

        header_layout.addWidget(section_lbl)
        header_layout.addWidget(self._explain_btn)
        header_layout.addLayout(model_row)

        # ── Explanation text ──
        text_container = QFrame()
        text_container.setStyleSheet(
            f"QFrame {{ background: {T.BG_SURFACE}; }}"
        )
        text_layout = QVBoxLayout(text_container)
        text_layout.setContentsMargins(T.PADDING, T.PADDING, T.PADDING, T.PADDING)
        text_layout.setSpacing(0)

        self._text = QTextEdit()
        self._text.setObjectName("explanationText")
        self._text.setReadOnly(True)
        self._text.setPlaceholderText(
            "Open a PDF and click \"Explain This Page\" — "
            "Sage will simplify the current page for you, "
            "privately and offline."
        )
        body_font = QFont("Georgia", T.FONT_SIZE_BODY)
        self._text.setFont(body_font)
        self._text.setSizePolicy(
            QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding
        )
        text_layout.addWidget(self._text)

        # ── Ask a question ──
        ask_container = QFrame()
        ask_container.setStyleSheet(
            f"QFrame {{ background: {T.BG_SURFACE}; "
            f"border-top: 1px solid {T.BORDER}; }}"
        )
        ask_layout = QHBoxLayout(ask_container)
        ask_layout.setContentsMargins(T.PADDING, 10, T.PADDING, 10)
        ask_layout.setSpacing(8)

        self._ask_input = QLineEdit()
        self._ask_input.setPlaceholderText("Ask a question about this page…")
        self._ask_input.returnPressed.connect(self._on_ask_submitted)
        self._ask_input.setEnabled(False)

        ask_btn = QPushButton("Ask")
        ask_btn.setObjectName("navBtn")
        ask_btn.setFixedWidth(48)
        ask_btn.clicked.connect(self._on_ask_submitted)

        ask_layout.addWidget(self._ask_input)
        ask_layout.addWidget(ask_btn)

        # ── Status bar ──
        status_bar = QFrame()
        status_bar.setStyleSheet(
            f"QFrame {{ background: {T.BG_SURFACE}; "
            f"border-top: 1px solid {T.BORDER}; }}"
        )
        status_layout = QHBoxLayout(status_bar)
        status_layout.setContentsMargins(T.PADDING, 6, T.PADDING, 6)
        status_layout.setSpacing(8)

        self._status_dot = QLabel("●")
        self._status_dot.setStyleSheet(f"color: {T.TEXT_DIM}; font-size: 10px;")
        self._status_dot.setFixedWidth(12)

        self._status_text = QLabel("Checking Ollama…")
        self._status_text.setObjectName("statusLabel")

        status_layout.addWidget(self._status_dot)
        status_layout.addWidget(self._status_text)
        status_layout.addStretch()

        # ── Assemble ──
        layout.addWidget(header)
        layout.addWidget(text_container, stretch=1)
        layout.addWidget(ask_container)
        layout.addWidget(status_bar)

    # ── Public API ────────────────────────────────────────────

    def set_pdf_loaded(self, loaded: bool) -> None:
        """Enable/disable controls based on whether a PDF is open."""
        self._explain_btn.setEnabled(loaded)
        self._ask_input.setEnabled(loaded)

    def populate_models(self, models: list[str]) -> None:
        """Fill the model ComboBox."""
        self._model_combo.blockSignals(True)
        self._model_combo.clear()
        if models:
            self._model_combo.addItems(models)
            # Prefer mistral > llama3 > phi3 > first available
            preferred = ["mistral", "llama3", "phi3"]
            for p in preferred:
                for m in models:
                    if m.startswith(p):
                        self._model_combo.setCurrentText(m)
                        break
        else:
            self._model_combo.addItem("No models — run: ollama pull mistral")
        self._model_combo.blockSignals(False)

    def set_ollama_status(self, ok: bool) -> None:
        if ok:
            self._status_dot.setStyleSheet(f"color: {T.ACCENT2}; font-size: 10px;")
            self._status_text.setText("Ollama connected")
        else:
            self._status_dot.setStyleSheet(f"color: {T.DANGER}; font-size: 10px;")
            self._status_text.setText("Ollama offline — run: ollama serve")

    def start_streaming(self, page_label: str) -> None:
        """Clear the text area and show a page header before streaming starts."""
        self._text.clear()
        self._text.setHtml(
            f'<p style="color:{T.TEXT_DIM}; font-size:11px; '
            f'font-family: Consolas, monospace; margin:0 0 12px 0;">'
            f'📄 {page_label}</p>'
            f'<p id="stream" style="color:{T.TEXT_PRIMARY}; '
            f'font-family: Georgia, serif; font-size:{T.FONT_SIZE_BODY}px; '
            f'line-height: 1.8; margin:0;"></p>'
        )
        self._explain_btn.setEnabled(False)
        self._explain_btn.setText("⏳  Thinking…")
        self._last_full_response = ""

    def append_token(self, token: str) -> None:
        """Append a streaming token to the display."""
        cursor = self._text.textCursor()
        cursor.movePosition(QTextCursor.MoveOperation.End)
        cursor.insertText(token)
        self._text.setTextCursor(cursor)
        self._text.ensureCursorVisible()
        self._last_full_response += token

    def finish_streaming(self, full_text: str) -> None:
        """Called when streaming completes."""
        self._last_full_response = full_text
        self._explain_btn.setEnabled(True)
        self._explain_btn.setText("⚡  Explain This Page")

    def show_error(self, message: str) -> None:
        self._text.setHtml(
            f'<p style="color:{T.DANGER}; font-family: Georgia, serif; '
            f'font-size:{T.FONT_SIZE_BODY}px; line-height:1.8;">'
            f'<b>⚠ Could not explain this page</b><br><br>{message}</p>'
        )
        self._explain_btn.setEnabled(True)
        self._explain_btn.setText("⚡  Explain This Page")

    @property
    def last_response(self) -> str:
        return self._last_full_response

    @property
    def selected_model(self) -> str:
        return self._model_combo.currentText()

    # ── Private ───────────────────────────────────────────────

    def _on_model_changed(self, model_name: str) -> None:
        if model_name and "Loading" not in model_name and "No models" not in model_name:
            self.model_changed.emit(model_name)

    def _on_ask_submitted(self) -> None:
        question = self._ask_input.text().strip()
        if question:
            self._ask_input.clear()
            self.ask_requested.emit(question)
