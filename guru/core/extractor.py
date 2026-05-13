"""
guru/core/extractor.py

Text extraction and validation layer.

Sits between PDFReader (raw bytes) and AIEngine (needs good text).
Detects scanned pages, cleans extracted content, and provides
useful metadata about what was found.
"""

from __future__ import annotations
from dataclasses import dataclass
from guru.core.pdf_reader import PDFReader


@dataclass
class ExtractionResult:
    """Everything the AI engine needs to know about a page's text."""
    text: str
    word_count: int
    is_scanned: bool        # True if no embedded text found
    is_too_short: bool      # True if < MIN_WORDS threshold
    page_num: int           # 0-based
    display_page: int       # 1-based (for UI)

    @property
    def is_usable(self) -> bool:
        """Can we send this to the AI?"""
        return not self.is_scanned and not self.is_too_short

    @property
    def status_message(self) -> str:
        """Human-readable status for the UI."""
        if self.is_scanned:
            return (
                "This page appears to be a scanned image. "
                "Sage works best with text-based PDFs. "
                "Try enabling OCR in a future update."
            )
        if self.is_too_short:
            return (
                f"Only {self.word_count} words found on this page — "
                "it may be a chapter title, diagram, or blank page. "
                "Try navigating to a content-heavy page."
            )
        return ""


class TextExtractor:
    """
    Validates and prepares page text for the AI engine.

    Usage:
        extractor = TextExtractor(pdf_reader)
        result = extractor.extract(page_num=2)
        if result.is_usable:
            send_to_ai(result.text)
    """

    # Pages with fewer words than this get flagged as "too short"
    MIN_WORDS = 30
    # Maximum characters we send to the model (keeps prompts fast)
    MAX_CHARS = 4000

    def __init__(self, reader: PDFReader) -> None:
        self._reader = reader

    def extract(self, page_num: int) -> ExtractionResult:
        """
        Extract and validate text from a page.

        Args:
            page_num: 0-based page index.

        Returns:
            ExtractionResult with text and validation flags.
        """
        raw = self._reader.extract_text(page_num)
        word_count = len(raw.split()) if raw else 0

        return ExtractionResult(
            text=self._truncate(raw),
            word_count=word_count,
            is_scanned=(len(raw.strip()) < 10),
            is_too_short=(0 < word_count < self.MIN_WORDS),
            page_num=page_num,
            display_page=page_num + 1,
        )

    # ── Private ───────────────────────────────────────────────

    def _truncate(self, text: str) -> str:
        """
        Trim text to MAX_CHARS without cutting mid-word.
        Adds a note if truncated so the AI knows context may be partial.
        """
        if len(text) <= self.MAX_CHARS:
            return text
        truncated = text[: self.MAX_CHARS].rsplit(" ", 1)[0]
        return truncated + "\n\n[... page continues — showing first portion only]"
