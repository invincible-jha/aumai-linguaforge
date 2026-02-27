# API Reference — aumai-linguaforge

Complete reference for all public classes, functions, and Pydantic models in
`aumai-linguaforge`. All public symbols are re-exported from the respective modules shown
below.

---

## Module: `aumai_linguaforge.models`

Pydantic models used as return types throughout the library. Every model inherits from
`pydantic.BaseModel` with strict field validation.

---

### `Language`

Represents a natural language entry in the registry.

```python
class Language(BaseModel):
    code: str
    name: str
    script: str
    family: str
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `code` | `str` | BCP-47 language code, e.g. `"hi"`, `"ta"`, `"en"`. |
| `name` | `str` | English name of the language, e.g. `"Hindi"`. |
| `script` | `str` | Primary writing script, e.g. `"Devanagari"`, `"Tamil"`. |
| `family` | `str` | Language family, e.g. `"Indo-Aryan"`, `"Dravidian"`. |

**Example:**

```python
from aumai_linguaforge.models import Language

lang = Language(code="ta", name="Tamil", script="Tamil", family="Dravidian")
print(lang.model_dump())
# {'code': 'ta', 'name': 'Tamil', 'script': 'Tamil', 'family': 'Dravidian'}
```

---

### `DetectionResult`

Result of a language detection operation.

```python
class DetectionResult(BaseModel):
    text: str
    language: Language
    confidence: float  # ge=0.0, le=1.0
```

**Fields:**

| Field | Type | Constraints | Description |
|-------|------|-------------|-------------|
| `text` | `str` | — | The original input text that was analysed. |
| `language` | `Language` | — | The detected (or most likely) language. |
| `confidence` | `float` | `0.0 <= confidence <= 1.0` | Confidence score. Values around 0.9 indicate script-based certainty. Values below 0.5 indicate low confidence from heuristics. |

**Example:**

```python
from aumai_linguaforge.core import LanguageDetector

detector = LanguageDetector()
result = detector.detect("नमस्ते")
assert 0.0 <= result.confidence <= 1.0
print(result.language.name)    # Hindi
print(result.confidence)       # 0.9
```

---

### `TransliterationResult`

Result of a script transliteration operation.

```python
class TransliterationResult(BaseModel):
    source: str
    target: str
    source_script: str
    target_script: str
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `source` | `str` | The original text before transliteration. |
| `target` | `str` | The transliterated output text. |
| `source_script` | `str` | The name of the source script as provided by the caller (e.g. `"Devanagari"`). |
| `target_script` | `str` | The name of the target script as provided by the caller (e.g. `"Latin"`). |

**Example:**

```python
from aumai_linguaforge.core import Transliterator

tr = Transliterator()
result = tr.transliterate("भारत", source_script="Devanagari", target_script="Latin")
print(result.source)        # भारत
print(result.target)        # bhaarat
print(result.source_script) # Devanagari
print(result.target_script) # Latin
```

---

### `TokenizationResult`

Result of a tokenization operation.

```python
class TokenizationResult(BaseModel):
    text: str
    tokens: list[str]
    language: Language
```

**Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `text` | `str` | The original input text before tokenization. |
| `tokens` | `list[str]` | Ordered list of tokens extracted from the text. |
| `language` | `Language` | The language used for tokenization (detected or provided). |

**Example:**

```python
from aumai_linguaforge.core import Tokenizer

tokenizer = Tokenizer()
result = tokenizer.tokenize("मैं घर जाता हूँ।")
print(result.tokens)         # ['मैं', 'घर', 'जाता', 'हूँ', '।']
print(result.language.name)  # Hindi
print(len(result.tokens))    # 5
```

---

## Module: `aumai_linguaforge.core`

The main operational module. All four processor classes live here, along with the
`SUPPORTED_LANGUAGES` registry.

---

### `SUPPORTED_LANGUAGES`

```python
SUPPORTED_LANGUAGES: dict[str, Language]
```

A dictionary mapping BCP-47 language codes to `Language` metadata objects. Contains 100+
languages including all 22 Indian Scheduled Languages and major world languages.

**Keys:** BCP-47 codes such as `"hi"`, `"ta"`, `"en"`, `"zh"`, `"ar"`.

**Example:**

```python
from aumai_linguaforge.core import SUPPORTED_LANGUAGES

# Look up a specific language
hindi = SUPPORTED_LANGUAGES["hi"]
print(hindi.name)    # Hindi
print(hindi.script)  # Devanagari
print(hindi.family)  # Indo-Aryan

# List all Dravidian languages
dravidian = [
    lang for lang in SUPPORTED_LANGUAGES.values()
    if lang.family == "Dravidian"
]
```

**Registered language families:**
`Indo-Aryan`, `Dravidian`, `Sino-Tibetan`, `Germanic`, `Romance`, `Slavic`, `Semitic`,
`Turkic`, `Austronesian`, `Austroasiatic`, `Bantu`, `Niger-Congo`, `Afro-Asiatic`,
`Tai-Kadai`, `Uralic`, `Celtic`, `Hellenic`, `Kartvelian`, `Armenian`, `Baltic`,
`Albanian`, `Koreanic`, `Japonic`, `Mongolic`, `Iranian`, `Constructed`,
`Language isolate`.

---

### `LanguageDetector`

Detects the language of a text string using script analysis and word-frequency heuristics.

```python
class LanguageDetector:
    def detect(self, text: str) -> DetectionResult: ...
    def detect_multiple(self, text: str, top_k: int = 3) -> list[DetectionResult]: ...
```

#### `LanguageDetector.detect`

```python
def detect(self, text: str) -> DetectionResult
```

Detect the primary language of the text. Calls `detect_multiple` internally and returns
the top result.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `text` | `str` | Input text to analyse. May be of any length but longer text yields better results for Latin-script heuristics. |

**Returns:** `DetectionResult` — the most likely language with confidence score.

**Raises:** Nothing. For completely empty or unrecognizable text, returns English with low
confidence (0.30).

**Example:**

```python
detector = LanguageDetector()

result = detector.detect("নমস্কার")
print(result.language.name)  # Bengali
print(result.confidence)     # 0.9

result2 = detector.detect("Hello, how are you today?")
print(result2.language.name)   # English
print(result2.language.script) # Latin
```

---

#### `LanguageDetector.detect_multiple`

```python
def detect_multiple(self, text: str, top_k: int = 3) -> list[DetectionResult]
```

Detect top-k candidate languages for the text.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `text` | `str` | required | Input text to analyse. |
| `top_k` | `int` | `3` | Maximum number of candidates to return. The actual number returned may be less if fewer candidates are generated. |

**Returns:** `list[DetectionResult]` — list sorted by descending confidence. Each item
contains a unique language candidate.

**Notes:**
- For non-Latin scripts only one candidate is generated (the primary mapping). Requesting
  `top_k > 1` on Devanagari text will still return a single result.
- For Latin-script text, up to 5 candidates are generated (English, Spanish, French,
  German, Portuguese).

**Example:**

```python
detector = LanguageDetector()

candidates = detector.detect_multiple("the cat is on the mat", top_k=3)
for c in candidates:
    print(f"{c.language.name}: {c.confidence:.2%}")
# English: 52.17%
# Spanish: 21.74%
# Portuguese: 13.04%
```

---

### `Tokenizer`

Language-aware tokenizer supporting whitespace splitting, punctuation splitting, and CJK
character-by-character splitting.

```python
class Tokenizer:
    def tokenize(self, text: str, language: str | None = None) -> TokenizationResult: ...
```

#### `Tokenizer.tokenize`

```python
def tokenize(self, text: str, language: str | None = None) -> TokenizationResult
```

Tokenize text into a list of string tokens.

**Parameters:**

| Name | Type | Default | Description |
|------|------|---------|-------------|
| `text` | `str` | required | The text to tokenize. |
| `language` | `str \| None` | `None` | Optional BCP-47 language code. If `None`, the language is auto-detected from the text using `LanguageDetector`. Providing a known language code skips detection and is faster. |

**Returns:** `TokenizationResult` with `.tokens` (list of strings) and `.language`
(Language metadata).

**Tokenization strategy:**
- Scripts `CJK`, `Hiragana`, `Katakana`: each non-space character becomes one token.
- All other scripts: split on Unicode whitespace and zero-width boundaries, then
  sub-split on word/non-word character class boundaries.

**Example:**

```python
tokenizer = Tokenizer()

# With auto-detection
result = tokenizer.tokenize("日本語テスト")
print(result.tokens)  # ['日', '本', '語', 'テ', 'ス', 'ト']

# With explicit language (skips detection)
result = tokenizer.tokenize("मैं जाता हूँ।", language="hi")
print(result.tokens)  # ['मैं', 'जाता', 'हूँ', '।']

# Punctuation is its own token
result = tokenizer.tokenize("Hello, world!")
print(result.tokens)  # ['Hello', ',', 'world', '!']
```

---

### `Transliterator`

Rule-based script transliterator. Supports `Devanagari <-> Latin` in both directions.

```python
class Transliterator:
    def transliterate(
        self,
        text: str,
        source_script: str,
        target_script: str,
    ) -> TransliterationResult: ...
```

#### `Transliterator.transliterate`

```python
def transliterate(
    self,
    text: str,
    source_script: str,
    target_script: str,
) -> TransliterationResult
```

Transliterate text from one script to another.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `text` | `str` | Source text to transliterate. |
| `source_script` | `str` | Name of the source script. Case-insensitive. Must be `"Devanagari"` or `"Latin"` in the current release. |
| `target_script` | `str` | Name of the target script. Case-insensitive. Must be `"Latin"` or `"Devanagari"` in the current release. |

**Returns:** `TransliterationResult` with `.source`, `.target`, `.source_script`,
`.target_script`.

**Raises:**
- `ValueError` — if the script pair is not supported. Current supported pairs:
  `Devanagari -> Latin`, `Latin -> Devanagari`.

**Devanagari-to-Latin mapping covers:**
- Independent vowels: `अ`→`a`, `आ`→`aa`, `इ`→`i`, `ई`→`ii`, `उ`→`u`, `ऊ`→`uu`,
  `ऋ`→`ri`, `ए`→`e`, `ऐ`→`ai`, `ओ`→`o`, `औ`→`au`
- Dependent vowel matras (same mappings for attached forms)
- All 35 consonants (ka, kha, ga, gha, nga, cha, chha, ja, jha, nya, Ta, Tha, Da, Dha,
  Na, ta, tha, da, dha, na, pa, pha, ba, bha, ma, ya, ra, la, va, sha, Sha, sa, ha)
- Diacritics: anusvara (`ं`→`n`), visarga (`ः`→`h`), virama (`्`→`""`), chandrabindu
  (`ँ`→`n`), avagraha (`ऽ`→`'`)
- Devanagari digits: `०`→`0` through `९`→`9`

**Example:**

```python
tr = Transliterator()

# Devanagari to Latin
r = tr.transliterate("नमस्ते", "Devanagari", "Latin")
print(r.target)  # namasate

# Latin to Devanagari
r2 = tr.transliterate("namasate", "Latin", "Devanagari")
print(r2.target)  # नमसते

# Unsupported pair raises ValueError
try:
    tr.transliterate("text", "Bengali", "Tamil")
except ValueError as e:
    print(e)
# Transliteration from 'Bengali' to 'Tamil' is not yet supported. ...
```

---

### `TextNormalizer`

Applies Unicode NFC normalization, whitespace cleanup, and script-specific rules.

```python
class TextNormalizer:
    def normalize(self, text: str, language: str) -> str: ...
```

#### `TextNormalizer.normalize`

```python
def normalize(self, text: str, language: str) -> str
```

Normalize text for the given language.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `text` | `str` | Input text to normalize. |
| `language` | `str` | BCP-47 language code. Used to select script-specific normalization rules. If the code is not in `SUPPORTED_LANGUAGES`, only generic normalization is applied. |

**Returns:** `str` — the normalized text.

**Raises:** Nothing.

**Normalization steps (in order):**
1. `unicodedata.normalize("NFC", text)` — canonical composition
2. Collapse runs of spaces/tabs to a single space
3. Collapse 3+ consecutive newlines to 2 newlines
4. Strip leading and trailing whitespace
5. Remove `U+200B` (zero-width space), `U+2060` (word joiner), `U+FEFF` (BOM),
   `U+00A0` (non-breaking space). Note: `U+200C` (ZWNJ) and `U+200D` (ZWJ) are
   preserved intentionally.
6. For Devanagari script languages: normalize chandrabindu `U+0901` (ँ) to anusvara
   `U+0902` (ं).

**Example:**

```python
normalizer = TextNormalizer()

# Whitespace collapsing
result = normalizer.normalize("hello    world\n\n\n\nend", language="en")
print(repr(result))  # 'hello world\n\nend'

# ZWS removal (but ZWJ/ZWNJ preserved)
result = normalizer.normalize("test\u200bvalue", language="en")
print(repr(result))  # 'testvalue'

# Devanagari chandrabindu normalization
result = normalizer.normalize("हँसना", language="hi")  # ँ -> ं
print(repr(result))  # 'हंसना'
```

---

## Module: `aumai_linguaforge.scripts`

Low-level script detection utilities. Typically not called directly — use `LanguageDetector`
or `Tokenizer` which call this internally.

---

### `SCRIPT_RANGES`

```python
SCRIPT_RANGES: list[tuple[int, int, str]]
```

List of Unicode codepoint ranges mapping to script names. Each entry is
`(start_codepoint, end_codepoint, script_name)`. Used by `detect_script`.

Contains 29 entries covering: Latin, Devanagari, Bengali, Gurmukhi, Gujarati, Odia, Tamil,
Telugu, Kannada, Malayalam, Sinhala, Thai, Lao, Tibetan, Myanmar, Georgian, Hangul,
Cherokee, Tagalog, Mongolian, Hiragana, Katakana, CJK, Arabic, Hebrew, Cyrillic, Greek.

---

### `detect_script`

```python
def detect_script(text: str) -> str
```

Detect the primary writing script used in the text by counting characters per script.

**Parameters:**

| Name | Type | Description |
|------|------|-------------|
| `text` | `str` | Input text. Can be any length. Single characters are handled correctly. |

**Returns:** `str` — the name of the dominant script (e.g. `"Devanagari"`, `"Latin"`,
`"CJK"`, `"Arabic"`). Returns `"Unknown"` if no recognized script characters are found.

**Algorithm:**
- Iterates every character in `text`.
- For each character, finds the first matching range in `SCRIPT_RANGES`.
- Tallies a frequency count per script name.
- Returns the script with the highest count.
- Time complexity: O(n * r) where n = text length, r = len(SCRIPT_RANGES) = 29.

**Example:**

```python
from aumai_linguaforge.scripts import detect_script

print(detect_script("नमस्ते"))          # Devanagari
print(detect_script("Hello"))           # Latin
print(detect_script("日本語"))           # CJK
print(detect_script("مرحبا"))           # Arabic
print(detect_script("Привет"))          # Cyrillic
print(detect_script(""))               # Unknown
print(detect_script("!@#$%"))          # Unknown
```

---

## Error Reference

| Exception | Raised By | Condition |
|-----------|-----------|-----------|
| `ValueError` | `Transliterator.transliterate` | Script pair is not supported. Message includes the unsupported pair and lists supported pairs. |
| `KeyError` | Direct `SUPPORTED_LANGUAGES` access | Language code not in registry. Use `.get()` to avoid this. |
| `pydantic.ValidationError` | Any model constructor | Field constraint violated (e.g. `confidence` outside `[0.0, 1.0]`). This only occurs when constructing models directly with invalid data. |

---

## Type Summary

| Symbol | Module | Type |
|--------|--------|------|
| `SUPPORTED_LANGUAGES` | `core` | `dict[str, Language]` |
| `LanguageDetector` | `core` | class |
| `Tokenizer` | `core` | class |
| `Transliterator` | `core` | class |
| `TextNormalizer` | `core` | class |
| `Language` | `models` | `pydantic.BaseModel` |
| `DetectionResult` | `models` | `pydantic.BaseModel` |
| `TransliterationResult` | `models` | `pydantic.BaseModel` |
| `TokenizationResult` | `models` | `pydantic.BaseModel` |
| `SCRIPT_RANGES` | `scripts` | `list[tuple[int, int, str]]` |
| `detect_script` | `scripts` | `(str) -> str` |
