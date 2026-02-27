# Getting Started with aumai-linguaforge

Multi-language NLP toolkit with Indic language focus. This guide walks you from a fresh
Python environment to running language detection, tokenization, transliteration, and
normalization on real text in under ten minutes.

---

## Prerequisites

- Python 3.11 or higher
- `pip` 23+ (or `uv` for faster installs)
- No GPU, no model downloads, no external services required

Verify your Python version:

```bash
python --version
# Python 3.11.x or higher
```

---

## Installation

### From PyPI (recommended)

```bash
pip install aumai-linguaforge
```

### From source

```bash
git clone https://github.com/aumai/aumai-linguaforge
cd aumai-linguaforge
pip install -e ".[dev]"
```

The `[dev]` extra installs `pytest`, `ruff`, `mypy`, and `hypothesis` for running tests and
linting.

### Verify the install

```bash
python -c "import aumai_linguaforge; print(aumai_linguaforge.__version__)"
# 0.1.0

linguaforge --version
# linguaforge, version 0.1.0
```

---

## Step-by-Step Tutorial

### Step 1 — Detect the language of a string

```python
from aumai_linguaforge.core import LanguageDetector

detector = LanguageDetector()

# Devanagari text — script detection kicks in immediately
result = detector.detect("नमस्ते दुनिया")
print(result.language.name)    # Hindi
print(result.language.code)    # hi
print(result.language.script)  # Devanagari
print(result.confidence)       # 0.9

# Latin-script text — uses marker-word heuristics
spanish = detector.detect("el gato está en la casa")
print(spanish.language.name)   # Spanish
```

The `DetectionResult` is a Pydantic model. You can serialize it directly:

```python
print(result.model_dump_json(indent=2))
# {
#   "text": "नमस्ते दुनिया",
#   "language": {
#     "code": "hi",
#     "name": "Hindi",
#     "script": "Devanagari",
#     "family": "Indo-Aryan"
#   },
#   "confidence": 0.9
# }
```

### Step 2 — Get ranked candidates

When the language is uncertain (e.g. short or ambiguous Latin-script text), request top-k:

```python
candidates = detector.detect_multiple("de la musica", top_k=3)
for c in candidates:
    print(f"{c.language.name:<15} {c.confidence:.2%}")
# Spanish         38.46%
# English         23.08%
# French          15.38%
```

### Step 3 — Tokenize text

```python
from aumai_linguaforge.core import Tokenizer

tokenizer = Tokenizer()

# Hindi — splits on spaces and Devanagari danda (।)
hindi = tokenizer.tokenize("मैं घर जाता हूँ।")
print(hindi.tokens)
# ['मैं', 'घर', 'जाता', 'हूँ', '।']

# Japanese — each character is a token (no spaces in Japanese)
japanese = tokenizer.tokenize("日本語テスト")
print(japanese.tokens)
# ['日', '本', '語', 'テ', 'ス', 'ト']

# English — standard whitespace + punctuation split
english = tokenizer.tokenize("Hello, world! How are you?")
print(english.tokens)
# ['Hello', ',', 'world', '!', 'How', 'are', 'you', '?']
```

You can pass a language code to skip auto-detection and make processing faster:

```python
result = tokenizer.tokenize("नमस्ते", language="hi")
print(result.language.name)  # Hindi (from registry, not detection)
```

### Step 4 — Transliterate Devanagari to Latin

```python
from aumai_linguaforge.core import Transliterator

tr = Transliterator()

result = tr.transliterate("भारत", source_script="Devanagari", target_script="Latin")
print(result.target)  # bhaarat

result2 = tr.transliterate("नमस्ते", source_script="Devanagari", target_script="Latin")
print(result2.target)  # namasate
```

### Step 5 — Reverse: Latin to Devanagari

```python
back = tr.transliterate("bhaarat", source_script="Latin", target_script="Devanagari")
print(back.target)  # भारत
```

### Step 6 — Normalize text

```python
from aumai_linguaforge.core import TextNormalizer

normalizer = TextNormalizer()

# Collapse extra whitespace and remove zero-width space (U+200B)
messy = "नमस्ते   दुनिया\u200b"
clean = normalizer.normalize(messy, language="hi")
print(repr(clean))  # 'नमस्ते दुनिया'

# NFC normalization (ensures consistent byte representation)
import unicodedata
# Two visually identical strings that are byte-different without normalization
s1 = "caf\u00e9"           # NFC: é as single codepoint
s2 = "cafe\u0301"          # NFD: e + combining acute
normalized1 = normalizer.normalize(s1, language="fr")
normalized2 = normalizer.normalize(s2, language="fr")
print(normalized1 == normalized2)  # True
```

---

## Common Patterns and Recipes

### Pattern 1 — Auto-detect then process

The most common pattern: detect the language, then use that information for tokenization
and normalization in a single pass.

```python
from aumai_linguaforge.core import LanguageDetector, Tokenizer, TextNormalizer

detector = LanguageDetector()
tokenizer = Tokenizer()
normalizer = TextNormalizer()

def process(text: str) -> dict[str, object]:
    detection = detector.detect(text)
    lang_code = detection.language.code
    normalized = normalizer.normalize(text, language=lang_code)
    tokens = tokenizer.tokenize(normalized, language=lang_code)
    return {
        "language": detection.language.name,
        "confidence": detection.confidence,
        "token_count": len(tokens.tokens),
        "tokens": tokens.tokens,
    }

print(process("नमस्ते दुनिया"))
print(process("Hello world"))
print(process("日本語テスト"))
```

### Pattern 2 — Transliterate a list of words for indexing

Common in search systems where you need to store both native-script and romanized versions
of a term in an index.

```python
from aumai_linguaforge.core import Transliterator

tr = Transliterator()

def romanize(words: list[str]) -> list[tuple[str, str]]:
    pairs = []
    for word in words:
        result = tr.transliterate(word, source_script="Devanagari", target_script="Latin")
        pairs.append((word, result.target))
    return pairs

pairs = romanize(["दिल्ली", "मुंबई", "कोलकाता", "चेन्नई"])
for native, roman in pairs:
    print(f"{native} -> {roman}")
```

### Pattern 3 — Filter a corpus by language

Useful when processing multilingual data and you only want documents in specific languages.

```python
from aumai_linguaforge.core import LanguageDetector

detector = LanguageDetector()

def filter_by_language(texts: list[str], target_codes: set[str]) -> list[str]:
    results = []
    for text in texts:
        detection = detector.detect(text)
        if detection.language.code in target_codes:
            results.append(text)
    return results

corpus = [
    "Hello from New York",
    "नमस्ते भारत",
    "Hola desde Madrid",
    "মুম্বাই থেকে শুভেচ্ছা",
]

hindi_and_bengali = filter_by_language(corpus, {"hi", "bn"})
print(hindi_and_bengali)
# ['नमस्ते भारत', 'মুম্বাই থেকে শুভেচ্ছা']
```

### Pattern 4 — Normalizing a batch before embedding

Before passing text to any embedding model, normalize it to avoid duplicate embeddings for
identical text with different byte representations.

```python
from aumai_linguaforge.core import TextNormalizer, LanguageDetector

normalizer = TextNormalizer()
detector = LanguageDetector()

def prepare_for_embedding(texts: list[str]) -> list[str]:
    prepared = []
    for text in texts:
        lang = detector.detect(text).language.code
        prepared.append(normalizer.normalize(text, language=lang))
    return prepared
```

### Pattern 5 — Checking if a language uses Devanagari

Useful for routing to the correct transliteration or font rendering path.

```python
from aumai_linguaforge.core import SUPPORTED_LANGUAGES

devanagari_languages = [
    code for code, lang in SUPPORTED_LANGUAGES.items()
    if lang.script == "Devanagari"
]
print(devanagari_languages)
# ['bo', 'doi', 'hi', 'kok', 'mai', 'mr', 'ne', 'sa', 'de', ...]
# Note: 'de' here is German — a different 'de' code. In practice, check
# SUPPORTED_LANGUAGES["hi"].script == "Devanagari"
```

---

## Troubleshooting FAQ

### Q: Language detection returns English for Hindi text with very few words.

**A:** For very short inputs (1-2 words) the heuristics have limited signal. The script
detector is reliable for non-Latin scripts regardless of length. If you know the script,
use `detect_multiple` with `top_k=3` and inspect the `language.script` field to pick the
right candidate. Alternatively, if you know the language in advance, bypass detection and
pass `language="hi"` directly to `Tokenizer.tokenize`.

### Q: Transliteration gives wrong output for some Devanagari words.

**A:** The transliteration is a rule-based character-by-character substitution. It does not
perform syllabic analysis or apply sandhi rules. For MVP romanization and indexing purposes
it is sufficient. For linguistically accurate scholarly transliteration (ISO 15919), use
`aumai-bharatvaani`'s `IndicTransliterator.to_latin`, which uses diacritical marks.

### Q: `Tokenizer` is splitting on ZWJ/ZWNJ characters in my Devanagari text.

**A:** ZWJ (U+200D) and ZWNJ (U+200C) are intentionally preserved by `TextNormalizer`. The
tokenizer splits on U+200B (zero-width space) which is semantically a word boundary marker.
If you are seeing unexpected splits, check whether your text contains U+200B rather than
ZWJ/ZWNJ.

### Q: I want to detect languages that are not in `SUPPORTED_LANGUAGES`.

**A:** You can add languages to the registry at runtime:

```python
from aumai_linguaforge.core import SUPPORTED_LANGUAGES
from aumai_linguaforge.models import Language

SUPPORTED_LANGUAGES["bho"] = Language(
    code="bho", name="Bhojpuri", script="Devanagari", family="Indo-Aryan"
)
```

Script detection will still work because it operates on Unicode ranges, not the registry.
The registry is used for the return value's `Language` metadata object.

### Q: The CLI raises `UnicodeDecodeError` when reading a file.

**A:** The CLI always reads files as UTF-8. Ensure your input files are saved as UTF-8. On
Windows, files may be saved as Windows-1252 by default in some editors. Convert with:

```bash
iconv -f windows-1252 -t utf-8 input.txt > input_utf8.txt
```

### Q: How do I use LinguaForge with `aumai-bharatvaani`?

**A:** LinguaForge provides the language detection and general tokenization layer.
BharatVaani provides Indic-specific NER and sentiment. A typical pipeline:

```python
from aumai_linguaforge.core import LanguageDetector, TextNormalizer
from aumai_bharatvaani.core import IndicSentimentAnalyzer

detector = LanguageDetector()
normalizer = TextNormalizer()
sentiment = IndicSentimentAnalyzer()

text = "यह बहुत अच्छा है"
lang = detector.detect(text).language.code       # "hi"
normalized = normalizer.normalize(text, lang)     # cleaned text
result = sentiment.analyze(normalized, lang)      # sentiment
print(result.sentiment)  # positive
```
