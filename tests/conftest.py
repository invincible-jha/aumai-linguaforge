"""Shared test fixtures for aumai-linguaforge."""

from __future__ import annotations

from pathlib import Path

import pytest

from aumai_linguaforge.core import (
    LanguageDetector,
    TextNormalizer,
    Tokenizer,
    Transliterator,
)


@pytest.fixture()
def detector() -> LanguageDetector:
    """A fresh LanguageDetector instance."""
    return LanguageDetector()


@pytest.fixture()
def tokenizer() -> Tokenizer:
    """A fresh Tokenizer instance."""
    return Tokenizer()


@pytest.fixture()
def transliterator() -> Transliterator:
    """A fresh Transliterator instance."""
    return Transliterator()


@pytest.fixture()
def normalizer() -> TextNormalizer:
    """A fresh TextNormalizer instance."""
    return TextNormalizer()


@pytest.fixture()
def english_text_file(tmp_path: Path) -> Path:
    """A text file containing English prose."""
    file = tmp_path / "english.txt"
    file.write_text("The quick brown fox is in the park.", encoding="utf-8")
    return file


@pytest.fixture()
def hindi_text_file(tmp_path: Path) -> Path:
    """A text file containing Hindi Devanagari text."""
    file = tmp_path / "hindi.txt"
    file.write_text("नमस्ते दुनिया", encoding="utf-8")
    return file
