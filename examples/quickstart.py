"""Quickstart examples for aumai-linguaforge.

Run this file directly to verify your installation and explore the API:

    python examples/quickstart.py

Each demo function is self-contained and prints its own output with a header.
"""

from __future__ import annotations


def demo_language_detection() -> None:
    """Demonstrate language detection across scripts and Latin-script disambiguation."""
    from aumai_linguaforge.core import LanguageDetector

    print("=" * 60)
    print("DEMO 1: Language Detection")
    print("=" * 60)

    detector = LanguageDetector()

    # Non-Latin scripts are identified via Unicode codepoint ranges
    samples = [
        ("नमस्ते दुनिया", "Devanagari (Hindi)"),
        ("নমস্কার বাংলাদেশ", "Bengali"),
        ("வணக்கம் தமிழ்நாடு", "Tamil"),
        ("日本語のテスト文章", "CJK (Japanese)"),
        ("مرحباً بالعالم", "Arabic"),
        ("Привет мир", "Cyrillic (Russian)"),
    ]

    print("\nSingle detection:")
    for text, label in samples:
        result = detector.detect(text)
        print(
            f"  [{label}]"
            f"\n    -> {result.language.name} ({result.language.code})"
            f"  confidence={result.confidence:.0%}"
            f"  script={result.language.script}"
        )

    # Latin-script disambiguation uses marker-word frequency scoring
    print("\nTop-3 candidates for Latin-script text:")
    latin_samples = [
        "the cat sat on the mat and was happy",
        "el gato está sentado en la alfombra",
        "le chat est assis sur le tapis",
    ]
    for text in latin_samples:
        candidates = detector.detect_multiple(text, top_k=3)
        print(f"\n  Input: '{text}'")
        for c in candidates:
            print(f"    {c.language.name:<15} {c.confidence:.1%}")


def demo_tokenization() -> None:
    """Demonstrate tokenization for different scripts."""
    from aumai_linguaforge.core import Tokenizer

    print("\n" + "=" * 60)
    print("DEMO 2: Tokenization")
    print("=" * 60)

    tokenizer = Tokenizer()

    samples = [
        ("Hindi", "hi", "मैं घर जाता हूँ।"),
        ("Tamil", "ta", "நான் வீட்டிற்கு போகிறேன்."),
        ("Bengali", "bn", "আমি বাড়ি যাচ্ছি।"),
        ("Japanese (CJK)", None, "日本語テストです"),
        ("English", "en", "Hello, world! How are you today?"),
        ("Mixed punctuation", None, "price: Rs.250/- (inclusive)"),
    ]

    for label, lang_code, text in samples:
        result = tokenizer.tokenize(text, language=lang_code)
        print(f"\n  [{label}] '{text}'")
        print(f"    Language: {result.language.name} ({result.language.code})")
        print(f"    Tokens ({len(result.tokens)}): {result.tokens}")


def demo_transliteration() -> None:
    """Demonstrate Devanagari <-> Latin transliteration."""
    from aumai_linguaforge.core import Transliterator

    print("\n" + "=" * 60)
    print("DEMO 3: Transliteration (Devanagari <-> Latin)")
    print("=" * 60)

    tr = Transliterator()

    # Devanagari to Latin (ITRANS-inspired)
    print("\nDevanagari -> Latin:")
    devanagari_words = [
        "भारत",       # India
        "नमस्ते",      # Namaste
        "धन्यवाद",     # Thank you
        "संस्कृत",     # Sanskrit
        "महाभारत",     # Mahabharata
        "राष्ट्र",      # Nation
    ]
    for word in devanagari_words:
        result = tr.transliterate(word, source_script="Devanagari", target_script="Latin")
        print(f"  {result.source:<15} -> {result.target}")

    # Latin to Devanagari (reverse mapping with longest-match-first)
    print("\nLatin -> Devanagari:")
    latin_words = ["bhaarat", "namasate", "dhanyavaad"]
    for word in latin_words:
        result = tr.transliterate(word, source_script="Latin", target_script="Devanagari")
        print(f"  {result.source:<20} -> {result.target}")

    # Attempt unsupported pair — demonstrates error handling
    print("\nUnsupported script pair (expected ValueError):")
    try:
        tr.transliterate("test", source_script="Bengali", target_script="Tamil")
    except ValueError as exc:
        print(f"  ValueError caught: {exc}")


def demo_text_normalization() -> None:
    """Demonstrate text normalization — NFC, whitespace, and script-specific rules."""
    from aumai_linguaforge.core import TextNormalizer

    print("\n" + "=" * 60)
    print("DEMO 4: Text Normalization")
    print("=" * 60)

    normalizer = TextNormalizer()

    cases = [
        (
            "Whitespace collapsing",
            "en",
            "hello    world\n\n\n\nend of document",
        ),
        (
            "Zero-width space removal (U+200B)",
            "hi",
            "नमस्ते\u200bदुनिया",
        ),
        (
            "Non-breaking space (U+00A0) removal",
            "en",
            "hello\u00a0world",
        ),
        (
            "Devanagari chandrabindu normalization (ँ -> ं)",
            "hi",
            "हँसना",
        ),
        (
            "BOM removal (U+FEFF)",
            "en",
            "\ufeffThis file has a BOM marker",
        ),
    ]

    for label, lang, text in cases:
        result = normalizer.normalize(text, language=lang)
        print(f"\n  [{label}]")
        print(f"    Before: {repr(text)}")
        print(f"    After:  {repr(result)}")


def demo_language_registry() -> None:
    """Show the SUPPORTED_LANGUAGES registry — 100+ languages with metadata."""
    from aumai_linguaforge.core import SUPPORTED_LANGUAGES

    print("\n" + "=" * 60)
    print("DEMO 5: Language Registry")
    print("=" * 60)

    # Count by script
    script_counts: dict[str, int] = {}
    for lang in SUPPORTED_LANGUAGES.values():
        script_counts[lang.script] = script_counts.get(lang.script, 0) + 1

    print(f"\nTotal languages registered: {len(SUPPORTED_LANGUAGES)}")
    print("\nLanguages per script (top 10):")
    for script, count in sorted(script_counts.items(), key=lambda x: -x[1])[:10]:
        print(f"  {script:<20} {count} language(s)")

    # Show all Indic languages
    print("\nAll Indic-family languages in registry:")
    indic_families = {"Indo-Aryan", "Dravidian", "Austroasiatic", "Sino-Tibetan"}
    indic = [
        lang for lang in SUPPORTED_LANGUAGES.values()
        if lang.family in indic_families
    ]
    for lang in sorted(indic, key=lambda l: l.name):
        print(f"  {lang.code:<6} {lang.name:<20} {lang.script:<15} ({lang.family})")


def main() -> None:
    """Run all demos in sequence."""
    print("\naumai-linguaforge quickstart\n")

    demo_language_detection()
    demo_tokenization()
    demo_transliteration()
    demo_text_normalization()
    demo_language_registry()

    print("\n" + "=" * 60)
    print("All demos completed successfully.")
    print("=" * 60)


if __name__ == "__main__":
    main()
