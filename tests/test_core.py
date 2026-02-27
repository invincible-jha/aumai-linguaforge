"""Comprehensive tests for aumai-linguaforge core module."""

from __future__ import annotations

import pytest

from aumai_linguaforge.core import (
    SUPPORTED_LANGUAGES,
    LanguageDetector,
    TextNormalizer,
    Tokenizer,
    Transliterator,
)
from aumai_linguaforge.models import (
    DetectionResult,
    Language,
    TokenizationResult,
    TransliterationResult,
)
from aumai_linguaforge.scripts import detect_script


# ---------------------------------------------------------------------------
# SUPPORTED_LANGUAGES registry tests
# ---------------------------------------------------------------------------


class TestSupportedLanguages:
    def test_contains_22_indic_languages(self) -> None:
        indic_codes = {
            "as", "bn", "bo", "doi", "gu", "hi", "kn", "ks", "kok",
            "mai", "ml", "mni", "mr", "ne", "or", "pa", "sa", "sat",
            "sd", "si", "ta", "te", "ur",
        }
        for code in indic_codes:
            assert code in SUPPORTED_LANGUAGES, f"Missing Indic language: {code}"

    def test_contains_major_world_languages(self) -> None:
        world_codes = {"en", "es", "fr", "de", "zh", "ja", "ko", "ar", "ru"}
        for code in world_codes:
            assert code in SUPPORTED_LANGUAGES, f"Missing world language: {code}"

    def test_language_has_required_fields(self) -> None:
        for code, lang in SUPPORTED_LANGUAGES.items():
            assert lang.code == code
            assert lang.name
            assert lang.script
            assert lang.family

    def test_hindi_metadata(self) -> None:
        hi = SUPPORTED_LANGUAGES["hi"]
        assert hi.name == "Hindi"
        assert hi.script == "Devanagari"
        assert hi.family == "Indo-Aryan"

    def test_at_least_90_languages_registered(self) -> None:
        assert len(SUPPORTED_LANGUAGES) >= 90


# ---------------------------------------------------------------------------
# detect_script tests
# ---------------------------------------------------------------------------


class TestDetectScript:
    def test_latin_script_english(self) -> None:
        assert detect_script("Hello world") == "Latin"

    def test_devanagari_script_hindi(self) -> None:
        assert detect_script("नमस्ते दुनिया") == "Devanagari"

    def test_bengali_script(self) -> None:
        assert detect_script("আমার সোনার বাংলা") == "Bengali"

    def test_arabic_script(self) -> None:
        assert detect_script("مرحبا بالعالم") == "Arabic"

    def test_cyrillic_script_russian(self) -> None:
        assert detect_script("Привет мир") == "Cyrillic"

    def test_cjk_script_chinese(self) -> None:
        assert detect_script("你好世界") == "CJK"

    def test_hiragana_script(self) -> None:
        assert detect_script("こんにちは") == "Hiragana"

    def test_unknown_returns_unknown(self) -> None:
        assert detect_script("") == "Unknown"

    def test_mixed_script_returns_dominant(self) -> None:
        # Majority Devanagari with one Latin char
        text = "नमस्ते X"
        script = detect_script(text)
        assert script == "Devanagari"

    def test_tamil_script(self) -> None:
        assert detect_script("வணக்கம்") == "Tamil"

    def test_telugu_script(self) -> None:
        assert detect_script("నమస్కారం") == "Telugu"

    def test_hangul_syllables_detected(self) -> None:
        # Hangul Syllables (U+AC00-U+D7AF) are now in SCRIPT_RANGES; modern
        # Korean text composed of syllable blocks must resolve to "Hangul".
        assert detect_script("안녕하세요") == "Hangul"


# ---------------------------------------------------------------------------
# LanguageDetector tests
# ---------------------------------------------------------------------------


class TestLanguageDetector:
    def test_detect_returns_detection_result(self, detector: LanguageDetector) -> None:
        result = detector.detect("Hello world")
        assert isinstance(result, DetectionResult)

    def test_detect_english_text(self, detector: LanguageDetector) -> None:
        result = detector.detect("The quick brown fox jumps over the lazy dog")
        assert result.language.code == "en"

    def test_detect_hindi_text(self, detector: LanguageDetector) -> None:
        result = detector.detect("नमस्ते दुनिया")
        assert result.language.code == "hi"

    def test_detect_arabic_text(self, detector: LanguageDetector) -> None:
        result = detector.detect("مرحبا بالعالم")
        assert result.language.code == "ar"

    def test_detect_confidence_in_range(self, detector: LanguageDetector) -> None:
        result = detector.detect("Hello world")
        assert 0.0 <= result.confidence <= 1.0

    def test_detect_returns_text(self, detector: LanguageDetector) -> None:
        text = "The sun is shining"
        result = detector.detect(text)
        assert result.text == text

    def test_detect_multiple_returns_list(self, detector: LanguageDetector) -> None:
        results = detector.detect_multiple("Hello world", top_k=3)
        assert isinstance(results, list)
        assert len(results) <= 3

    def test_detect_multiple_sorted_by_confidence(self, detector: LanguageDetector) -> None:
        results = detector.detect_multiple("Hello and world", top_k=5)
        confidences = [r.confidence for r in results]
        assert confidences == sorted(confidences, reverse=True)

    def test_detect_multiple_top_k_1(self, detector: LanguageDetector) -> None:
        results = detector.detect_multiple("Hello world", top_k=1)
        assert len(results) == 1

    def test_detect_non_script_text_fallback(self, detector: LanguageDetector) -> None:
        # Empty string returns Unknown script -> fallback path
        result = detector.detect("   ")
        assert isinstance(result, DetectionResult)

    def test_detect_chinese_text(self, detector: LanguageDetector) -> None:
        result = detector.detect("你好世界")
        assert result.language.code == "zh"

    def test_detect_korean_text_resolves_to_hangul(self, detector: LanguageDetector) -> None:
        # Hangul Syllables are now in SCRIPT_RANGES; the detector maps
        # Hangul -> "ko" with high confidence.
        result = detector.detect("안녕하세요")
        assert result.language.code == "ko"
        assert result.confidence > 0.5

    def test_detect_russian_text(self, detector: LanguageDetector) -> None:
        result = detector.detect("Привет мир")
        assert result.language.code == "ru"


# ---------------------------------------------------------------------------
# Tokenizer tests
# ---------------------------------------------------------------------------


class TestTokenizer:
    def test_tokenize_returns_result(self, tokenizer: Tokenizer) -> None:
        result = tokenizer.tokenize("Hello world", language="en")
        assert isinstance(result, TokenizationResult)

    def test_tokenize_english_simple(self, tokenizer: Tokenizer) -> None:
        result = tokenizer.tokenize("Hello world", language="en")
        assert "Hello" in result.tokens
        assert "world" in result.tokens

    def test_tokenize_preserves_text(self, tokenizer: Tokenizer) -> None:
        text = "The quick brown fox"
        result = tokenizer.tokenize(text, language="en")
        assert result.text == text

    def test_tokenize_empty_string(self, tokenizer: Tokenizer) -> None:
        result = tokenizer.tokenize("", language="en")
        assert isinstance(result.tokens, list)

    def test_tokenize_cjk_per_character(self, tokenizer: Tokenizer) -> None:
        result = tokenizer.tokenize("你好世界", language="zh")
        # Each CJK character should be its own token
        assert len(result.tokens) == 4

    def test_tokenize_hindi_splits_on_whitespace(self, tokenizer: Tokenizer) -> None:
        result = tokenizer.tokenize("नमस्ते दुनिया", language="hi")
        assert len(result.tokens) >= 2

    def test_tokenize_language_auto_detect_when_none(self, tokenizer: Tokenizer) -> None:
        result = tokenizer.tokenize("The quick brown fox", language=None)
        assert result.language.code == "en"

    def test_tokenize_language_field_populated(self, tokenizer: Tokenizer) -> None:
        result = tokenizer.tokenize("Hello world", language="en")
        assert result.language.code == "en"
        assert result.language.name == "English"

    def test_tokenize_splits_punctuation(self, tokenizer: Tokenizer) -> None:
        result = tokenizer.tokenize("Hello, world!", language="en")
        # Comma and exclamation should not be merged into word tokens
        assert any(t.isalpha() for t in result.tokens)

    def test_tokenize_unsupported_lang_falls_back_to_english(self, tokenizer: Tokenizer) -> None:
        result = tokenizer.tokenize("Hello world", language="xx-invalid")
        # Should not raise; falls back gracefully
        assert isinstance(result.tokens, list)


# ---------------------------------------------------------------------------
# Transliterator tests
# ---------------------------------------------------------------------------


class TestTransliterator:
    def test_devanagari_to_latin(self, transliterator: Transliterator) -> None:
        result = transliterator.transliterate("क", "Devanagari", "Latin")
        assert isinstance(result, TransliterationResult)
        assert result.target == "ka"

    def test_transliterate_preserves_source(self, transliterator: Transliterator) -> None:
        result = transliterator.transliterate("क", "Devanagari", "Latin")
        assert result.source == "क"

    def test_transliterate_records_script_names(self, transliterator: Transliterator) -> None:
        result = transliterator.transliterate("क", "Devanagari", "Latin")
        assert result.source_script == "Devanagari"
        assert result.target_script == "Latin"

    def test_latin_to_devanagari_roundtrip(self, transliterator: Transliterator) -> None:
        original = "ka"
        to_deva = transliterator.transliterate(original, "Latin", "Devanagari")
        assert "क" in to_deva.target

    def test_unsupported_pair_raises_value_error(self, transliterator: Transliterator) -> None:
        with pytest.raises(ValueError, match="not yet supported"):
            transliterator.transliterate("hello", "Latin", "Bengali")

    def test_case_insensitive_script_names(self, transliterator: Transliterator) -> None:
        result = transliterator.transliterate("क", "devanagari", "latin")
        assert result.target == "ka"

    def test_devanagari_vowels_transliterated(self, transliterator: Transliterator) -> None:
        result = transliterator.transliterate("अ", "Devanagari", "Latin")
        assert result.target == "a"

    def test_devanagari_numerals_transliterated(self, transliterator: Transliterator) -> None:
        result = transliterator.transliterate("०१२", "Devanagari", "Latin")
        assert "0" in result.target
        assert "1" in result.target
        assert "2" in result.target

    def test_unknown_chars_pass_through(self, transliterator: Transliterator) -> None:
        result = transliterator.transliterate("X", "Devanagari", "Latin")
        assert "X" in result.target


# ---------------------------------------------------------------------------
# TextNormalizer tests
# ---------------------------------------------------------------------------


class TestTextNormalizer:
    def test_normalize_strips_edges(self, normalizer: TextNormalizer) -> None:
        result = normalizer.normalize("  hello world  ", "en")
        assert result == "hello world"

    def test_normalize_collapses_whitespace(self, normalizer: TextNormalizer) -> None:
        result = normalizer.normalize("hello   world", "en")
        assert result == "hello world"

    def test_normalize_removes_zero_width_joiners(self, normalizer: TextNormalizer) -> None:
        text_with_zwj = "hello\u200bworld"
        result = normalizer.normalize(text_with_zwj, "en")
        assert "\u200b" not in result

    def test_normalize_removes_bom(self, normalizer: TextNormalizer) -> None:
        text = "\ufeffhello"
        result = normalizer.normalize(text, "en")
        assert "\ufeff" not in result

    def test_normalize_devanagari_chandrabindu(self, normalizer: TextNormalizer) -> None:
        # U+0901 (chandrabindu ँ) should be normalized to U+0902 (anusvar ं) for Hindi
        text = "हाँ"  # contains U+0901
        result = normalizer.normalize(text, "hi")
        assert "\u0901" not in result

    def test_normalize_nfc_normalization(self, normalizer: TextNormalizer) -> None:
        import unicodedata
        # NFD form: e + combining acute
        nfd_text = "e\u0301"  # e + combining acute accent
        result = normalizer.normalize(nfd_text, "en")
        assert unicodedata.is_normalized("NFC", result)

    def test_normalize_collapses_excessive_newlines(self, normalizer: TextNormalizer) -> None:
        text = "line one\n\n\n\nline two"
        result = normalizer.normalize(text, "en")
        assert "\n\n\n" not in result

    def test_normalize_non_indic_language_no_special_rules(
        self, normalizer: TextNormalizer
    ) -> None:
        text = "Hello World"
        result = normalizer.normalize(text, "en")
        assert result == "Hello World"
