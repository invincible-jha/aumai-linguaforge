"""Pydantic models for aumai-linguaforge."""

from __future__ import annotations

from pydantic import BaseModel, Field

__all__ = [
    "Language",
    "DetectionResult",
    "TransliterationResult",
    "TokenizationResult",
]


class Language(BaseModel):
    """Represents a natural language."""

    code: str = Field(description="BCP-47 language code, e.g. 'hi', 'ta', 'en'.")
    name: str = Field(description="English name of the language.")
    script: str = Field(description="Primary writing script, e.g. 'Devanagari'.")
    family: str = Field(description="Language family, e.g. 'Indo-Aryan'.")


class DetectionResult(BaseModel):
    """Result of language detection for a text input."""

    text: str
    language: Language
    confidence: float = Field(ge=0.0, le=1.0)


class TransliterationResult(BaseModel):
    """Result of script transliteration."""

    source: str
    target: str
    source_script: str
    target_script: str


class TokenizationResult(BaseModel):
    """Result of text tokenization."""

    text: str
    tokens: list[str]
    language: Language
