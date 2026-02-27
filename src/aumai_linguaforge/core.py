"""Core logic for aumai-linguaforge."""

from __future__ import annotations

import re
import unicodedata

from aumai_linguaforge.models import (
    DetectionResult,
    Language,
    TokenizationResult,
    TransliterationResult,
)
from aumai_linguaforge.scripts import detect_script

__all__ = [
    "SUPPORTED_LANGUAGES",
    "LanguageDetector",
    "Tokenizer",
    "Transliterator",
    "TextNormalizer",
]

# ---------------------------------------------------------------------------
# Supported language registry
# ---------------------------------------------------------------------------

SUPPORTED_LANGUAGES: dict[str, Language] = {
    # 22 Indian Scheduled Languages
    "as": Language(code="as", name="Assamese", script="Bengali", family="Indo-Aryan"),
    "bn": Language(code="bn", name="Bengali", script="Bengali", family="Indo-Aryan"),
    "bo": Language(code="bo", name="Bodo", script="Devanagari", family="Sino-Tibetan"),
    "doi": Language(code="doi", name="Dogri", script="Devanagari", family="Indo-Aryan"),
    "gu": Language(code="gu", name="Gujarati", script="Gujarati", family="Indo-Aryan"),
    "hi": Language(code="hi", name="Hindi", script="Devanagari", family="Indo-Aryan"),
    "kn": Language(code="kn", name="Kannada", script="Kannada", family="Dravidian"),
    "ks": Language(code="ks", name="Kashmiri", script="Perso-Arabic", family="Indo-Aryan"),
    "kok": Language(code="kok", name="Konkani", script="Devanagari", family="Indo-Aryan"),
    "mai": Language(code="mai", name="Maithili", script="Devanagari", family="Indo-Aryan"),
    "ml": Language(code="ml", name="Malayalam", script="Malayalam", family="Dravidian"),
    "mni": Language(code="mni", name="Manipuri", script="Bengali", family="Sino-Tibetan"),
    "mr": Language(code="mr", name="Marathi", script="Devanagari", family="Indo-Aryan"),
    "ne": Language(code="ne", name="Nepali", script="Devanagari", family="Indo-Aryan"),
    "or": Language(code="or", name="Odia", script="Odia", family="Indo-Aryan"),
    "pa": Language(code="pa", name="Punjabi", script="Gurmukhi", family="Indo-Aryan"),
    "sa": Language(code="sa", name="Sanskrit", script="Devanagari", family="Indo-Aryan"),
    "sat": Language(code="sat", name="Santali", script="Ol Chiki", family="Austroasiatic"),
    "sd": Language(code="sd", name="Sindhi", script="Perso-Arabic", family="Indo-Aryan"),
    "si": Language(code="si", name="Sinhala", script="Sinhala", family="Indo-Aryan"),
    "ta": Language(code="ta", name="Tamil", script="Tamil", family="Dravidian"),
    "te": Language(code="te", name="Telugu", script="Telugu", family="Dravidian"),
    "ur": Language(code="ur", name="Urdu", script="Perso-Arabic", family="Indo-Aryan"),
    # Major world languages
    "en": Language(code="en", name="English", script="Latin", family="Germanic"),
    "es": Language(code="es", name="Spanish", script="Latin", family="Romance"),
    "fr": Language(code="fr", name="French", script="Latin", family="Romance"),
    "de": Language(code="de", name="German", script="Latin", family="Germanic"),
    "it": Language(code="it", name="Italian", script="Latin", family="Romance"),
    "pt": Language(code="pt", name="Portuguese", script="Latin", family="Romance"),
    "ru": Language(code="ru", name="Russian", script="Cyrillic", family="Slavic"),
    "zh": Language(code="zh", name="Chinese", script="CJK", family="Sino-Tibetan"),
    "ja": Language(code="ja", name="Japanese", script="Hiragana", family="Japonic"),
    "ko": Language(code="ko", name="Korean", script="Hangul", family="Koreanic"),
    "ar": Language(code="ar", name="Arabic", script="Arabic", family="Semitic"),
    "he": Language(code="he", name="Hebrew", script="Hebrew", family="Semitic"),
    "fa": Language(code="fa", name="Persian", script="Perso-Arabic", family="Iranian"),
    "tr": Language(code="tr", name="Turkish", script="Latin", family="Turkic"),
    "vi": Language(code="vi", name="Vietnamese", script="Latin", family="Austroasiatic"),
    "th": Language(code="th", name="Thai", script="Thai", family="Tai-Kadai"),
    "id": Language(code="id", name="Indonesian", script="Latin", family="Austronesian"),
    "ms": Language(code="ms", name="Malay", script="Latin", family="Austronesian"),
    "sw": Language(code="sw", name="Swahili", script="Latin", family="Bantu"),
    "nl": Language(code="nl", name="Dutch", script="Latin", family="Germanic"),
    "pl": Language(code="pl", name="Polish", script="Latin", family="Slavic"),
    "uk": Language(code="uk", name="Ukrainian", script="Cyrillic", family="Slavic"),
    "cs": Language(code="cs", name="Czech", script="Latin", family="Slavic"),
    "ro": Language(code="ro", name="Romanian", script="Latin", family="Romance"),
    "hu": Language(code="hu", name="Hungarian", script="Latin", family="Uralic"),
    "fi": Language(code="fi", name="Finnish", script="Latin", family="Uralic"),
    "sv": Language(code="sv", name="Swedish", script="Latin", family="Germanic"),
    "no": Language(code="no", name="Norwegian", script="Latin", family="Germanic"),
    "da": Language(code="da", name="Danish", script="Latin", family="Germanic"),
    "el": Language(code="el", name="Greek", script="Greek", family="Hellenic"),
    "bg": Language(code="bg", name="Bulgarian", script="Cyrillic", family="Slavic"),
    "hr": Language(code="hr", name="Croatian", script="Latin", family="Slavic"),
    "sk": Language(code="sk", name="Slovak", script="Latin", family="Slavic"),
    "lt": Language(code="lt", name="Lithuanian", script="Latin", family="Baltic"),
    "lv": Language(code="lv", name="Latvian", script="Latin", family="Baltic"),
    "et": Language(code="et", name="Estonian", script="Latin", family="Uralic"),
    "sq": Language(code="sq", name="Albanian", script="Latin", family="Albanian"),
    "mk": Language(code="mk", name="Macedonian", script="Cyrillic", family="Slavic"),
    "sr": Language(code="sr", name="Serbian", script="Cyrillic", family="Slavic"),
    "sl": Language(code="sl", name="Slovenian", script="Latin", family="Slavic"),
    "af": Language(code="af", name="Afrikaans", script="Latin", family="Germanic"),
    "ka": Language(code="ka", name="Georgian", script="Georgian", family="Kartvelian"),
    "hy": Language(code="hy", name="Armenian", script="Armenian", family="Armenian"),
    "az": Language(code="az", name="Azerbaijani", script="Latin", family="Turkic"),
    "kk": Language(code="kk", name="Kazakh", script="Cyrillic", family="Turkic"),
    "uz": Language(code="uz", name="Uzbek", script="Latin", family="Turkic"),
    "km": Language(code="km", name="Khmer", script="Khmer", family="Austroasiatic"),
    "lo": Language(code="lo", name="Lao", script="Lao", family="Tai-Kadai"),
    "my": Language(code="my", name="Burmese", script="Myanmar", family="Sino-Tibetan"),
    "mn": Language(code="mn", name="Mongolian", script="Cyrillic", family="Mongolic"),
    "tl": Language(code="tl", name="Filipino", script="Latin", family="Austronesian"),
    "jv": Language(code="jv", name="Javanese", script="Latin", family="Austronesian"),
    "ceb": Language(code="ceb", name="Cebuano", script="Latin", family="Austronesian"),
    "ha": Language(code="ha", name="Hausa", script="Latin", family="Afro-Asiatic"),
    "yo": Language(code="yo", name="Yoruba", script="Latin", family="Niger-Congo"),
    "ig": Language(code="ig", name="Igbo", script="Latin", family="Niger-Congo"),
    "am": Language(code="am", name="Amharic", script="Ethiopic", family="Semitic"),
    "so": Language(code="so", name="Somali", script="Latin", family="Afro-Asiatic"),
    "zu": Language(code="zu", name="Zulu", script="Latin", family="Bantu"),
    "xh": Language(code="xh", name="Xhosa", script="Latin", family="Bantu"),
    "ny": Language(code="ny", name="Chichewa", script="Latin", family="Bantu"),
    "mg": Language(code="mg", name="Malagasy", script="Latin", family="Austronesian"),
    "cy": Language(code="cy", name="Welsh", script="Latin", family="Celtic"),
    "ga": Language(code="ga", name="Irish", script="Latin", family="Celtic"),
    "eu": Language(code="eu", name="Basque", script="Latin", family="Language isolate"),
    "ca": Language(code="ca", name="Catalan", script="Latin", family="Romance"),
    "gl": Language(code="gl", name="Galician", script="Latin", family="Romance"),
    "eo": Language(code="eo", name="Esperanto", script="Latin", family="Constructed"),
    "la": Language(code="la", name="Latin", script="Latin", family="Romance"),
    "mt": Language(code="mt", name="Maltese", script="Latin", family="Semitic"),
    "is": Language(code="is", name="Icelandic", script="Latin", family="Germanic"),
    "be": Language(code="be", name="Belarusian", script="Cyrillic", family="Slavic"),
    "tt": Language(code="tt", name="Tatar", script="Cyrillic", family="Turkic"),
    "ba": Language(code="ba", name="Bashkir", script="Cyrillic", family="Turkic"),
    "cv": Language(code="cv", name="Chuvash", script="Cyrillic", family="Turkic"),
}

# Script -> language code mapping for detection heuristics
_SCRIPT_TO_LANG: dict[str, str] = {
    "Devanagari": "hi",
    "Bengali": "bn",
    "Gurmukhi": "pa",
    "Gujarati": "gu",
    "Tamil": "ta",
    "Telugu": "te",
    "Kannada": "kn",
    "Malayalam": "ml",
    "Odia": "or",
    "Sinhala": "si",
    "Thai": "th",
    "Lao": "lo",
    "Myanmar": "my",
    "Tibetan": "bo",
    "Georgian": "ka",
    "Hangul": "ko",
    "Hiragana": "ja",
    "Katakana": "ja",
    "CJK": "zh",
    "Arabic": "ar",
    "Hebrew": "he",
    "Cyrillic": "ru",
    "Greek": "el",
}


class LanguageDetector:
    """Detect the language of a text using script analysis and heuristics."""

    def detect(self, text: str) -> DetectionResult:
        """Detect the primary language of the text.

        Uses script-based detection as primary signal, with simple
        n-gram heuristics for Latin-script disambiguation.

        Args:
            text: Input text to analyse.

        Returns:
            DetectionResult with the most likely language and confidence.
        """
        results = self.detect_multiple(text, top_k=1)
        return results[0]

    def detect_multiple(self, text: str, top_k: int = 3) -> list[DetectionResult]:
        """Detect top-k candidate languages for the text.

        Args:
            text: Input text to analyse.
            top_k: Number of candidate languages to return.

        Returns:
            List of DetectionResult objects sorted by descending confidence.
        """
        script = detect_script(text)
        candidates: list[tuple[str, float]] = []

        if script in _SCRIPT_TO_LANG:
            primary_code = _SCRIPT_TO_LANG[script]
            candidates.append((primary_code, 0.90))
        elif script == "Latin":
            candidates = self._latin_heuristics(text)
        else:
            candidates = [("en", 0.30)]

        candidates.sort(key=lambda item: item[1], reverse=True)
        results: list[DetectionResult] = []
        for code, confidence in candidates[:top_k]:
            lang = SUPPORTED_LANGUAGES.get(code, SUPPORTED_LANGUAGES["en"])
            results.append(DetectionResult(text=text, language=lang, confidence=confidence))

        return results

    def _latin_heuristics(self, text: str) -> list[tuple[str, float]]:
        """Use common word patterns to distinguish Latin-script languages."""
        text_lower = text.lower()
        scores: dict[str, float] = {
            "en": 0.40,
            "es": 0.05,
            "fr": 0.05,
            "de": 0.05,
            "pt": 0.05,
        }
        # Simple marker words for common languages
        markers: dict[str, list[str]] = {
            "en": ["the", "and", "is", "are", "was", "of", "in", "to"],
            "es": ["el", "la", "los", "las", "de", "en", "que", "es"],
            "fr": ["le", "la", "les", "de", "du", "et", "est", "une"],
            "de": ["der", "die", "das", "und", "ist", "ich", "ein", "nicht"],
            "pt": ["o", "a", "os", "as", "de", "e", "do", "da"],
        }
        words = re.findall(r"\b\w+\b", text_lower)
        word_set = set(words)
        for lang_code, word_list in markers.items():
            hits = sum(1 for w in word_list if w in word_set)
            scores[lang_code] = scores.get(lang_code, 0.0) + hits * 0.08

        total = sum(scores.values()) or 1.0
        return [(code, min(score / total, 0.99)) for code, score in scores.items()]


class Tokenizer:
    """Language-aware tokenizer supporting whitespace and punctuation splitting."""

    def tokenize(self, text: str, language: str | None = None) -> TokenizationResult:
        """Tokenize text into tokens.

        Uses Unicode-aware punctuation splitting. For CJK scripts each
        character is treated as a token.

        Args:
            text: The text to tokenize.
            language: Optional BCP-47 language code for language-aware behavior.

        Returns:
            TokenizationResult with the token list and detected language.
        """
        lang = SUPPORTED_LANGUAGES.get(language or "", SUPPORTED_LANGUAGES["en"])
        if language is None:
            detected = LanguageDetector().detect(text)
            lang = detected.language

        script = detect_script(text)
        if script in {"CJK", "Hiragana", "Katakana"}:
            tokens = list(text.replace(" ", ""))
        else:
            tokens = self._unicode_tokenize(text)

        return TokenizationResult(text=text, tokens=tokens, language=lang)

    def _unicode_tokenize(self, text: str) -> list[str]:
        """Split on whitespace and punctuation boundaries."""
        # Split on any sequence of whitespace or punctuation characters
        raw_tokens = re.split(r"[\s\u200b\u200c\u200d\u2060\ufeff]+", text.strip())
        result: list[str] = []
        for token in raw_tokens:
            if not token:
                continue
            # Further split on ASCII punctuation boundaries
            sub = re.split(r"(?<=[^\W\d_])(?=[\W\d_])|(?<=[\W\d_])(?=[^\W\d_])", token)
            result.extend(t for t in sub if t and not re.fullmatch(r"\s+", t))
        return result


# ---------------------------------------------------------------------------
# Devanagari <-> Latin transliteration tables (ITRANS-inspired mapping)
# ---------------------------------------------------------------------------

_DEVANAGARI_TO_LATIN: dict[str, str] = {
    "अ": "a", "आ": "aa", "इ": "i", "ई": "ii", "उ": "u", "ऊ": "uu",
    "ऋ": "ri", "ए": "e", "ऐ": "ai", "ओ": "o", "औ": "au",
    "ा": "aa", "ि": "i", "ी": "ii", "ु": "u", "ू": "uu",
    "ृ": "ri", "े": "e", "ै": "ai", "ो": "o", "ौ": "au",
    "क": "ka", "ख": "kha", "ग": "ga", "घ": "gha", "ङ": "nga",
    "च": "cha", "छ": "chha", "ज": "ja", "झ": "jha", "ञ": "nya",
    "ट": "Ta", "ठ": "Tha", "ड": "Da", "ढ": "Dha", "ण": "Na",
    "त": "ta", "थ": "tha", "द": "da", "ध": "dha", "न": "na",
    "प": "pa", "फ": "pha", "ब": "ba", "भ": "bha", "म": "ma",
    "य": "ya", "र": "ra", "ल": "la", "व": "va", "श": "sha",
    "ष": "Sha", "स": "sa", "ह": "ha",
    "ं": "n", "ः": "h", "्": "", "ँ": "n", "ऽ": "'",
    "०": "0", "१": "1", "२": "2", "३": "3", "४": "4",
    "५": "5", "६": "6", "७": "7", "८": "8", "९": "9",
}

# Reverse mapping for Latin -> Devanagari (multi-char keys first)
_LATIN_TO_DEVANAGARI: dict[str, str] = {v: k for k, v in _DEVANAGARI_TO_LATIN.items() if v}


class Transliterator:
    """Rule-based script transliterator (Devanagari <-> Latin as MVP)."""

    def transliterate(
        self,
        text: str,
        source_script: str,
        target_script: str,
    ) -> TransliterationResult:
        """Transliterate text from one script to another.

        Args:
            text: Source text.
            source_script: Name of source script (e.g. 'Devanagari').
            target_script: Name of target script (e.g. 'Latin').

        Returns:
            TransliterationResult containing the converted text.

        Raises:
            ValueError: If the script pair is not supported.
        """
        source_norm = source_script.lower()
        target_norm = target_script.lower()

        if source_norm == "devanagari" and target_norm == "latin":
            result = self._devanagari_to_latin(text)
        elif source_norm == "latin" and target_norm == "devanagari":
            result = self._latin_to_devanagari(text)
        else:
            raise ValueError(
                f"Transliteration from '{source_script}' to '{target_script}' is not yet supported. "
                "Supported pairs: Devanagari<->Latin."
            )

        return TransliterationResult(
            source=text,
            target=result,
            source_script=source_script,
            target_script=target_script,
        )

    def _devanagari_to_latin(self, text: str) -> str:
        result: list[str] = []
        for char in text:
            result.append(_DEVANAGARI_TO_LATIN.get(char, char))
        return "".join(result)

    def _latin_to_devanagari(self, text: str) -> str:
        # Sort keys by length descending to match multi-char sequences first
        sorted_keys = sorted(_LATIN_TO_DEVANAGARI.keys(), key=len, reverse=True)
        result = text
        for key in sorted_keys:
            result = result.replace(key, _LATIN_TO_DEVANAGARI[key])
        return result


class TextNormalizer:
    """Normalize text with Unicode NFC, whitespace cleanup, and script-specific rules."""

    def normalize(self, text: str, language: str) -> str:
        """Normalize text for the given language.

        Performs:
        - Unicode NFC normalization
        - Whitespace normalization (collapse runs, strip edges)
        - Script-specific zero-width character cleanup
        - Devanagari: normalize chandrabindu variants

        Args:
            text: Input text to normalize.
            language: BCP-47 language code.

        Returns:
            Normalized string.
        """
        # Unicode NFC normalization
        normalized = unicodedata.normalize("NFC", text)

        # Collapse whitespace
        normalized = re.sub(r"[ \t]+", " ", normalized)
        normalized = re.sub(r"\n{3,}", "\n\n", normalized)
        normalized = normalized.strip()

        # Remove zero-width characters that have no linguistic meaning.
        # U+200C (ZWNJ) and U+200D (ZWJ) are intentionally preserved because
        # they are semantically significant in Brahmic/Indic scripts (e.g. they
        # control conjunct formation in Devanagari, Malayalam, etc.).
        for zwc in ("\u200b", "\u2060", "\ufeff", "\u00a0"):
            normalized = normalized.replace(zwc, "")

        lang = SUPPORTED_LANGUAGES.get(language)
        if lang and lang.script == "Devanagari":
            # Normalize anunaasika variants
            normalized = normalized.replace("\u0901", "\u0902")  # ँ -> ं

        return normalized
