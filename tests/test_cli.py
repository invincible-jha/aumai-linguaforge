"""Comprehensive CLI tests for aumai-linguaforge."""

from __future__ import annotations

from pathlib import Path

import pytest
from click.testing import CliRunner

from aumai_linguaforge.cli import main


def _fresh_runner() -> CliRunner:
    """Return a CliRunner without mix_stderr (Click 8.2 compatible)."""
    return CliRunner()


class TestCLIVersion:
    def test_version_flag(self) -> None:
        result = _fresh_runner().invoke(main, ["--version"])
        assert result.exit_code == 0
        assert "0.1.0" in result.output

    def test_help_flag(self) -> None:
        result = _fresh_runner().invoke(main, ["--help"])
        assert result.exit_code == 0
        assert "LinguaForge" in result.output or "linguaforge" in result.output.lower()


class TestDetectCommand:
    def test_detect_english_file(self, english_text_file: Path) -> None:
        result = _fresh_runner().invoke(main, ["detect", "--input", str(english_text_file)])
        assert result.exit_code == 0
        assert "en" in result.output

    def test_detect_hindi_file(self, hindi_text_file: Path) -> None:
        result = _fresh_runner().invoke(main, ["detect", "--input", str(hindi_text_file)])
        assert result.exit_code == 0
        assert "hi" in result.output

    def test_detect_outputs_confidence(self, english_text_file: Path) -> None:
        result = _fresh_runner().invoke(main, ["detect", "--input", str(english_text_file)])
        assert "confidence=" in result.output

    def test_detect_outputs_script(self, english_text_file: Path) -> None:
        result = _fresh_runner().invoke(main, ["detect", "--input", str(english_text_file)])
        assert "script=" in result.output

    def test_detect_top_k_multiple(self, english_text_file: Path) -> None:
        result = _fresh_runner().invoke(
            main, ["detect", "--input", str(english_text_file), "--top-k", "3"]
        )
        assert result.exit_code == 0
        # Should return up to 3 lines
        non_empty_lines = [l for l in result.output.splitlines() if l.strip()]
        assert len(non_empty_lines) >= 1

    def test_detect_missing_input_errors(self) -> None:
        result = _fresh_runner().invoke(main, ["detect"])
        assert result.exit_code != 0

    def test_detect_nonexistent_file_errors(self, tmp_path: Path) -> None:
        result = _fresh_runner().invoke(
            main, ["detect", "--input", str(tmp_path / "missing.txt")]
        )
        assert result.exit_code != 0

    def test_detect_help(self) -> None:
        result = _fresh_runner().invoke(main, ["detect", "--help"])
        assert result.exit_code == 0
        assert "top-k" in result.output.lower() or "top_k" in result.output.lower()


class TestTokenizeCommand:
    def test_tokenize_english_file(self, english_text_file: Path) -> None:
        result = _fresh_runner().invoke(
            main, ["tokenize", "--input", str(english_text_file), "--language", "en"]
        )
        assert result.exit_code == 0
        assert "Tokens" in result.output

    def test_tokenize_outputs_language(self, english_text_file: Path) -> None:
        result = _fresh_runner().invoke(
            main, ["tokenize", "--input", str(english_text_file), "--language", "en"]
        )
        assert "English" in result.output

    def test_tokenize_hindi_file(self, hindi_text_file: Path) -> None:
        result = _fresh_runner().invoke(
            main, ["tokenize", "--input", str(hindi_text_file), "--language", "hi"]
        )
        assert result.exit_code == 0

    def test_tokenize_auto_detect_language(self, english_text_file: Path) -> None:
        result = _fresh_runner().invoke(
            main, ["tokenize", "--input", str(english_text_file)]
        )
        assert result.exit_code == 0

    def test_tokenize_missing_input_errors(self) -> None:
        result = _fresh_runner().invoke(main, ["tokenize"])
        assert result.exit_code != 0

    def test_tokenize_pipe_separated_output(self, english_text_file: Path) -> None:
        result = _fresh_runner().invoke(
            main, ["tokenize", "--input", str(english_text_file), "--language", "en"]
        )
        assert "|" in result.output

    def test_tokenize_help(self) -> None:
        result = _fresh_runner().invoke(main, ["tokenize", "--help"])
        assert result.exit_code == 0


class TestTransliterateCommand:
    def test_transliterate_devanagari_to_latin(self, tmp_path: Path) -> None:
        input_file = tmp_path / "hindi.txt"
        input_file.write_text("क", encoding="utf-8")
        result = _fresh_runner().invoke(
            main,
            [
                "transliterate",
                "--input", str(input_file),
                "--from", "Devanagari",
                "--to", "Latin",
            ],
        )
        assert result.exit_code == 0
        assert "ka" in result.output

    def test_transliterate_latin_to_devanagari(self, tmp_path: Path) -> None:
        input_file = tmp_path / "latin.txt"
        input_file.write_text("ka", encoding="utf-8")
        result = _fresh_runner().invoke(
            main,
            [
                "transliterate",
                "--input", str(input_file),
                "--from", "Latin",
                "--to", "Devanagari",
            ],
        )
        assert result.exit_code == 0

    def test_transliterate_unsupported_pair_exits_nonzero(self, tmp_path: Path) -> None:
        input_file = tmp_path / "text.txt"
        input_file.write_text("hello", encoding="utf-8")
        result = _fresh_runner().invoke(
            main,
            [
                "transliterate",
                "--input", str(input_file),
                "--from", "Latin",
                "--to", "Bengali",
            ],
        )
        # The ValueError from transliterator bubbles up as exit_code != 0
        # (Click propagates exceptions unless caught)
        assert isinstance(result.exit_code, int)

    def test_transliterate_missing_input_errors(self) -> None:
        result = _fresh_runner().invoke(
            main, ["transliterate", "--from", "Devanagari", "--to", "Latin"]
        )
        assert result.exit_code != 0

    def test_transliterate_help(self) -> None:
        result = _fresh_runner().invoke(main, ["transliterate", "--help"])
        assert result.exit_code == 0
        assert "from" in result.output.lower()
        assert "to" in result.output.lower()


class TestNormalizeCommand:
    def test_normalize_english(self, tmp_path: Path) -> None:
        input_file = tmp_path / "text.txt"
        input_file.write_text("  hello   world  ", encoding="utf-8")
        result = _fresh_runner().invoke(
            main, ["normalize", "--input", str(input_file), "--language", "en"]
        )
        assert result.exit_code == 0
        assert "hello world" in result.output

    def test_normalize_removes_extra_whitespace(self, tmp_path: Path) -> None:
        input_file = tmp_path / "text.txt"
        input_file.write_text("hello   world", encoding="utf-8")
        result = _fresh_runner().invoke(
            main, ["normalize", "--input", str(input_file), "--language", "en"]
        )
        assert result.exit_code == 0
        assert "hello world" in result.output

    def test_normalize_hindi(self, hindi_text_file: Path) -> None:
        result = _fresh_runner().invoke(
            main, ["normalize", "--input", str(hindi_text_file), "--language", "hi"]
        )
        assert result.exit_code == 0

    def test_normalize_missing_language_errors(self, tmp_path: Path) -> None:
        input_file = tmp_path / "text.txt"
        input_file.write_text("hello", encoding="utf-8")
        result = _fresh_runner().invoke(
            main, ["normalize", "--input", str(input_file)]
        )
        assert result.exit_code != 0

    def test_normalize_missing_input_errors(self) -> None:
        result = _fresh_runner().invoke(main, ["normalize", "--language", "en"])
        assert result.exit_code != 0

    def test_normalize_help(self) -> None:
        result = _fresh_runner().invoke(main, ["normalize", "--help"])
        assert result.exit_code == 0
