"""
tests/test_extractor.py

Unit tests for the TextExtractor.
Tests run without needing Ollama or a real PDF.
"""
import pytest
from unittest.mock import MagicMock
from guru.core.extractor import TextExtractor, ExtractionResult


def make_extractor(extracted_text: str) -> TextExtractor:
    """Helper: build a TextExtractor backed by a mock PDFReader."""
    mock_reader = MagicMock()
    mock_reader.extract_text.return_value = extracted_text
    return TextExtractor(mock_reader)


class TestExtractionResult:
    def test_usable_when_enough_text(self):
        ext = make_extractor("word " * 50)
        result = ext.extract(0)
        assert result.is_usable is True

    def test_scanned_when_no_text(self):
        ext = make_extractor("")
        result = ext.extract(0)
        assert result.is_scanned is True
        assert result.is_usable is False

    def test_too_short_when_few_words(self):
        ext = make_extractor("just a few words")
        result = ext.extract(0)
        assert result.is_too_short is True
        assert result.is_usable is False

    def test_truncates_long_text(self):
        long_text = "word " * 2000   # ~10000 chars
        ext = make_extractor(long_text)
        result = ext.extract(0)
        assert len(result.text) <= TextExtractor.MAX_CHARS + 100

    def test_display_page_is_1_based(self):
        ext = make_extractor("word " * 50)
        result = ext.extract(page_num=0)
        assert result.display_page == 1
        result2 = ext.extract(page_num=4)
        assert result2.display_page == 5

    def test_status_message_for_scanned(self):
        ext = make_extractor("")
        result = ext.extract(0)
        assert "scanned" in result.status_message.lower()

    def test_status_message_for_too_short(self):
        ext = make_extractor("short")
        result = ext.extract(0)
        assert "words" in result.status_message.lower()
