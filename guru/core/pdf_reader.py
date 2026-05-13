"""
guru/core/pdf_reader.py

PDF loading and page rendering engine.
Uses PyMuPDF (fitz) — the fastest Python PDF library available.

Responsibilities:
- Open / close PDF documents
- Render any page to a QPixmap for display
- Report page count, current page metadata
"""

from __future__ import annotations

import fitz  # PyMuPDF
from PyQt6.QtGui import QImage, QPixmap
from PyQt6.QtCore import Qt


class PDFReader:
    """
    Wraps a fitz.Document and exposes clean methods
    for the UI layer to render pages without caring
    about PyMuPDF internals.
    """

    def __init__(self) -> None:
        self._doc: fitz.Document | None = None
        self._path: str = ""
        self._page_count: int = 0

    # ── Public API ────────────────────────────────────────────

    def open(self, path: str) -> bool:
        """
        Open a PDF file.

        Args:
            path: Absolute path to the .pdf file.

        Returns:
            True on success, False if the file couldn't be opened.
        """
        try:
            if self._doc:
                self._doc.close()

            self._doc = fitz.open(path)
            self._path = path
            self._page_count = len(self._doc)
            return True

        except Exception as e:
            print(f"[PDFReader] Failed to open '{path}': {e}")
            self._doc = None
            self._page_count = 0
            return False

    def close(self) -> None:
        """Release the document from memory."""
        if self._doc:
            self._doc.close()
            self._doc = None
            self._page_count = 0
            self._path = ""

    def render_page(self, page_num: int, zoom: float = 1.5) -> QPixmap | None:
        """
        Render a page to a QPixmap ready for display in PyQt6.

        Args:
            page_num: 0-based page index.
            zoom:     Scale factor. 1.5 = 150% (good default for readability).

        Returns:
            QPixmap if successful, None otherwise.
        """
        if not self._doc or not self._valid_page(page_num):
            return None

        try:
            page = self._doc[page_num]

            # fitz.Matrix scales the render resolution
            mat = fitz.Matrix(zoom, zoom)
            pix = page.get_pixmap(matrix=mat, alpha=False)

            # Convert PyMuPDF pixmap → QImage → QPixmap
            # PyMuPDF gives us raw RGB bytes we feed directly into QImage
            img = QImage(
                pix.samples,
                pix.width,
                pix.height,
                pix.stride,
                QImage.Format.Format_RGB888,
            )
            return QPixmap.fromImage(img)

        except Exception as e:
            print(f"[PDFReader] Render error on page {page_num}: {e}")
            return None

    def extract_text(self, page_num: int) -> str:
        """
        Extract raw text from a page.

        PyMuPDF reads the actual text objects in the PDF —
        not OCR. Scanned PDFs without embedded text return "".

        Args:
            page_num: 0-based page index.

        Returns:
            Cleaned text string, or "" if nothing found.
        """
        if not self._doc or not self._valid_page(page_num):
            return ""

        try:
            page = self._doc[page_num]
            # "text" mode preserves reading order better than "rawtext"
            text = page.get_text("text")
            return self._clean_text(text)

        except Exception as e:
            print(f"[PDFReader] Text extraction error on page {page_num}: {e}")
            return ""

    def get_page_label(self, page_num: int) -> str:
        """
        Returns the display label for a page (e.g. 'Page 3 of 24').
        """
        return f"Page {page_num + 1} of {self._page_count}"

    # ── Properties ────────────────────────────────────────────

    @property
    def is_open(self) -> bool:
        return self._doc is not None

    @property
    def page_count(self) -> int:
        return self._page_count

    @property
    def file_name(self) -> str:
        """Returns just the filename (not full path)."""
        import os
        return os.path.basename(self._path) if self._path else ""

    # ── Private helpers ───────────────────────────────────────

    def _valid_page(self, page_num: int) -> bool:
        return 0 <= page_num < self._page_count

    @staticmethod
    def _clean_text(text: str) -> str:
        """
        Normalize whitespace and remove junk characters
        that PDF extraction sometimes produces.
        """
        import re
        # Collapse multiple spaces/tabs into one space
        text = re.sub(r"[ \t]+", " ", text)
        # Collapse 3+ newlines into 2 (preserve paragraph breaks)
        text = re.sub(r"\n{3,}", "\n\n", text)
        return text.strip()
