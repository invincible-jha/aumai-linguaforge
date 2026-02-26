"""Script detection utilities for aumai-linguaforge."""

from __future__ import annotations

__all__ = ["detect_script", "SCRIPT_RANGES"]

# Unicode codepoint ranges for major writing scripts.
# Each entry: (start, end, script_name)
SCRIPT_RANGES: list[tuple[int, int, str]] = [
    (0x0041, 0x007A, "Latin"),
    (0x00C0, 0x024F, "Latin"),
    (0x0900, 0x097F, "Devanagari"),
    (0x0980, 0x09FF, "Bengali"),
    (0x0A00, 0x0A7F, "Gurmukhi"),
    (0x0A80, 0x0AFF, "Gujarati"),
    (0x0B00, 0x0B7F, "Odia"),
    (0x0B80, 0x0BFF, "Tamil"),
    (0x0C00, 0x0C7F, "Telugu"),
    (0x0C80, 0x0CFF, "Kannada"),
    (0x0D00, 0x0D7F, "Malayalam"),
    (0x0D80, 0x0DFF, "Sinhala"),
    (0x0E00, 0x0E7F, "Thai"),
    (0x0E80, 0x0EFF, "Lao"),
    (0x0F00, 0x0FFF, "Tibetan"),
    (0x1000, 0x109F, "Myanmar"),
    (0x10A0, 0x10FF, "Georgian"),
    (0x1100, 0x11FF, "Hangul"),
    (0x13A0, 0x13FF, "Cherokee"),
    (0x1700, 0x171F, "Tagalog"),
    (0x1800, 0x18AF, "Mongolian"),
    (0x3040, 0x309F, "Hiragana"),
    (0x30A0, 0x30FF, "Katakana"),
    (0x3400, 0x4DBF, "CJK"),
    (0x4E00, 0x9FFF, "CJK"),
    (0x0600, 0x06FF, "Arabic"),
    (0x0590, 0x05FF, "Hebrew"),
    (0x0400, 0x04FF, "Cyrillic"),
    (0x0370, 0x03FF, "Greek"),
]


def detect_script(text: str) -> str:
    """Detect the primary writing script used in the text.

    Counts characters belonging to each script and returns the most frequent.
    Falls back to 'Unknown' if no known script characters are found.

    Args:
        text: The input text to analyse.

    Returns:
        The name of the dominant script (e.g. 'Devanagari', 'Latin', 'CJK').
    """
    script_counts: dict[str, int] = {}

    for char in text:
        code_point = ord(char)
        for start, end, script_name in SCRIPT_RANGES:
            if start <= code_point <= end:
                script_counts[script_name] = script_counts.get(script_name, 0) + 1
                break

    if not script_counts:
        return "Unknown"

    return max(script_counts, key=lambda s: script_counts[s])
