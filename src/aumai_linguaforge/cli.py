"""CLI entry point for aumai-linguaforge."""

from __future__ import annotations

from pathlib import Path

import click

from aumai_linguaforge.core import (
    LanguageDetector,
    TextNormalizer,
    Tokenizer,
    Transliterator,
)

_detector = LanguageDetector()
_tokenizer = Tokenizer()
_transliterator = Transliterator()
_normalizer = TextNormalizer()


@click.group()
@click.version_option()
def main() -> None:
    """AumAI LinguaForge — Multi-language NLP toolkit CLI."""


@main.command("detect")
@click.option(
    "--input",
    "input_file",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Input text file.",
)
@click.option("--top-k", default=1, show_default=True, type=int, help="Number of candidates.")
def detect(input_file: Path, top_k: int) -> None:
    """Detect the language(s) of a text file."""
    text = input_file.read_text(encoding="utf-8")
    results = _detector.detect_multiple(text, top_k=top_k)
    for result in results:
        click.echo(
            f"{result.language.code}  {result.language.name:<20}  "
            f"confidence={result.confidence:.2%}  script={result.language.script}"
        )


@main.command("tokenize")
@click.option(
    "--input",
    "input_file",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Input text file.",
)
@click.option("--language", default=None, help="BCP-47 language code (auto-detect if omitted).")
def tokenize(input_file: Path, language: str | None) -> None:
    """Tokenize a text file."""
    text = input_file.read_text(encoding="utf-8")
    result = _tokenizer.tokenize(text, language=language)
    click.echo(f"Language: {result.language.name} ({result.language.code})")
    click.echo(f"Tokens ({len(result.tokens)}):")
    click.echo(" | ".join(result.tokens))


@main.command("transliterate")
@click.option(
    "--input",
    "input_file",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Input text file.",
)
@click.option("--from", "source_script", required=True, help="Source script (e.g. devanagari).")
@click.option("--to", "target_script", required=True, help="Target script (e.g. latin).")
def transliterate(input_file: Path, source_script: str, target_script: str) -> None:
    """Transliterate a text file from one script to another."""
    text = input_file.read_text(encoding="utf-8")
    result = _transliterator.transliterate(text, source_script=source_script, target_script=target_script)
    click.echo(result.target)


@main.command("normalize")
@click.option(
    "--input",
    "input_file",
    required=True,
    type=click.Path(exists=True, dir_okay=False, path_type=Path),
    help="Input text file.",
)
@click.option("--language", required=True, help="BCP-47 language code.")
def normalize(input_file: Path, language: str) -> None:
    """Normalize text using Unicode NFC and script-specific rules."""
    text = input_file.read_text(encoding="utf-8")
    normalized = _normalizer.normalize(text, language=language)
    click.echo(normalized)


if __name__ == "__main__":
    main()
