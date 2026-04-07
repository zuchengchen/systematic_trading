#!/usr/bin/env python3
"""Audit bilingual chapter files for missing translation structure."""

from __future__ import annotations

import argparse
import re
import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


CJK_RE = re.compile(r"[\u4e00-\u9fff]")
LATIN_RE = re.compile(r"[A-Za-z]")
INPUT_BILINGUAL_RE = re.compile(r"\\inputbilingual\{([^}]+)\}")


@dataclass
class Issue:
    path: Path
    line: int
    message: str


@dataclass
class CommandMatch:
    start: int
    args: list[str]


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def line_of(text: str, offset: int) -> int:
    return text.count("\n", 0, offset) + 1


def excerpt(text: str, limit: int = 110) -> str:
    single_line = " ".join(text.split())
    if len(single_line) <= limit:
        return single_line
    return single_line[: limit - 3] + "..."


def normalize_title(text: str) -> str:
    text = text.replace("\\allowbreak", "")
    text = text.replace("\\linebreak", "")
    text = text.replace("\\-", "")
    text = text.replace("\\\\", " ")
    text = text.replace("{", "")
    text = text.replace("}", "")
    return " ".join(text.split())


def parse_command_matches(
    text: str,
    command: str,
    *,
    nargs: int = 1,
    allow_optional: bool = False,
    allow_star: bool = False,
) -> list[CommandMatch]:
    needle = f"\\{command}"
    matches: list[CommandMatch] = []
    i = 0

    while True:
        i = text.find(needle, i)
        if i == -1:
            return matches

        j = i + len(needle)
        args: list[str] = []

        if allow_star and j < len(text) and text[j] == "*":
            j += 1

        if allow_optional:
            while j < len(text) and text[j].isspace():
                j += 1
            if j < len(text) and text[j] == "[":
                depth = 1
                j += 1
                while j < len(text) and depth:
                    if text[j] == "[":
                        depth += 1
                    elif text[j] == "]":
                        depth -= 1
                    j += 1

        ok = True
        for _ in range(nargs):
            while j < len(text) and text[j].isspace():
                j += 1
            if j >= len(text) or text[j] != "{":
                ok = False
                break
            start = j + 1
            depth = 1
            j += 1
            while j < len(text) and depth:
                if text[j] == "{":
                    depth += 1
                elif text[j] == "}":
                    depth -= 1
                j += 1
            if depth != 0:
                ok = False
                break
            args.append(text[start : j - 1])

        if ok:
            matches.append(CommandMatch(start=i, args=args))
            i = j
        else:
            i += len(needle)


def resolve_targets(paths: Iterable[str]) -> list[Path]:
    root = project_root()
    if paths:
        resolved: list[Path] = []
        for raw in paths:
            path = Path(raw)
            if not path.is_absolute():
                path = (root / path).resolve()
            resolved.append(path)
        return resolved

    main_bilingual = (root / "main_bilingual.tex").read_text(encoding="utf-8")
    names = INPUT_BILINGUAL_RE.findall(main_bilingual)
    return [root / "chapters_bilingual" / f"{name}.tex" for name in names]


def english_source_for(target: Path) -> Path:
    return project_root() / "chapters" / target.name


def compare_title_sequences(
    issues: list[Issue],
    target: Path,
    source_titles: list[str],
    bilingual_titles: list[str],
    label: str,
) -> None:
    source_norm = [normalize_title(title) for title in source_titles]
    bilingual_norm = [normalize_title(title) for title in bilingual_titles]
    if source_norm == bilingual_norm:
        return

    source_counter = Counter(source_norm)
    bilingual_counter = Counter(bilingual_norm)
    missing = list((source_counter - bilingual_counter).elements())
    extra = list((bilingual_counter - source_counter).elements())

    if missing:
        issues.append(
            Issue(
                path=target,
                line=1,
                message=(
                    f"{label} titles missing from bilingual file: "
                    + "; ".join(excerpt(item, 70) for item in missing[:5])
                ),
            )
        )

    if extra:
        issues.append(
            Issue(
                path=target,
                line=1,
                message=(
                    f"{label} titles only found in bilingual file: "
                    + "; ".join(excerpt(item, 70) for item in extra[:5])
                ),
            )
        )


def audit_titles(source_text: str, bilingual_text: str, target: Path, issues: list[Issue]) -> None:
    source_chapters = [
        m.args[0] for m in parse_command_matches(source_text, "chapter", nargs=1, allow_star=True)
    ]
    source_sections = [
        m.args[0] for m in parse_command_matches(source_text, "section", nargs=1, allow_star=True)
    ]
    source_subsections = [
        m.args[0] for m in parse_command_matches(source_text, "subsection", nargs=1, allow_star=True)
    ]

    bilingual_chapters = [
        m.args[0]
        for command in ("bilingualchapter", "bilingualchapterstar")
        for m in parse_command_matches(bilingual_text, command, nargs=2)
    ]
    bilingual_sections = [m.args[0] for m in parse_command_matches(bilingual_text, "bilingualsection", nargs=2)]
    bilingual_subsections = [
        m.args[0] for m in parse_command_matches(bilingual_text, "bilingualsubsection", nargs=2)
    ]

    compare_title_sequences(issues, target, source_chapters, bilingual_chapters, "Chapter")
    compare_title_sequences(issues, target, source_sections, bilingual_sections, "Section")
    compare_title_sequences(issues, target, source_subsections, bilingual_subsections, "Subsection")


def audit_footnotes(source_text: str, bilingual_text: str, target: Path, issues: list[Issue]) -> None:
    source_footnotes = parse_command_matches(source_text, "footnote", nargs=1, allow_optional=True)
    bilingual_footnotes = parse_command_matches(bilingual_text, "footnote", nargs=1, allow_optional=True)

    if len(source_footnotes) != len(bilingual_footnotes):
        issues.append(
            Issue(
                path=target,
                line=1,
                message=(
                    "Footnote count mismatch "
                    f"(source={len(source_footnotes)}, bilingual={len(bilingual_footnotes)})"
                ),
            )
        )

    for match in bilingual_footnotes:
        text = match.args[0]
        line = line_of(bilingual_text, match.start)
        has_cjk = bool(CJK_RE.search(text))
        has_latin = bool(LATIN_RE.search(text))
        has_split = "\\par" in text

        if not has_cjk:
            issues.append(
                Issue(
                    path=target,
                    line=line,
                    message=f"Footnote lacks Chinese translation | {excerpt(text)}",
                )
            )
        elif not has_latin:
            issues.append(
                Issue(
                    path=target,
                    line=line,
                    message=f"Footnote lacks English source text | {excerpt(text)}",
                )
            )
        elif not has_split:
            issues.append(
                Issue(
                    path=target,
                    line=line,
                    message=f"Footnote is not stored as EN+ZH in one note | {excerpt(text)}",
                )
            )


def audit_captions(source_text: str, bilingual_text: str, target: Path, issues: list[Issue]) -> None:
    source_captions = (
        parse_command_matches(source_text, "caption", nargs=1)
        + parse_command_matches(source_text, "rawfigurecaption", nargs=1)
        + parse_command_matches(source_text, "rawtablecaption", nargs=1)
    )
    bilingual_captions = (
        parse_command_matches(bilingual_text, "caption", nargs=1)
        + parse_command_matches(bilingual_text, "rawfigurecaption", nargs=1)
        + parse_command_matches(bilingual_text, "rawtablecaption", nargs=1)
    )

    if len(source_captions) != len(bilingual_captions):
        issues.append(
            Issue(
                path=target,
                line=1,
                message=(
                    "Caption count mismatch "
                    f"(source={len(source_captions)}, bilingual={len(bilingual_captions)})"
                ),
            )
        )

    for match in bilingual_captions:
        text = match.args[0]
        line = line_of(bilingual_text, match.start)
        has_cjk = bool(CJK_RE.search(text))
        has_latin = bool(LATIN_RE.search(text))
        has_split = "\\\\" in text or "\\par" in text

        if not has_cjk:
            issues.append(
                Issue(
                    path=target,
                    line=line,
                    message=f"Caption lacks Chinese translation | {excerpt(text)}",
                )
            )
        elif not has_latin:
            issues.append(
                Issue(
                    path=target,
                    line=line,
                    message=f"Caption lacks English source text | {excerpt(text)}",
                )
            )
        elif not has_split:
            issues.append(
                Issue(
                    path=target,
                    line=line,
                    message=f"Caption is not stored as EN+ZH content | {excerpt(text)}",
                )
            )


def audit_file(target: Path) -> list[Issue]:
    issues: list[Issue] = []
    source = english_source_for(target)

    if not target.exists():
        return [Issue(path=target, line=1, message="Missing bilingual file")]
    if not source.exists():
        return [Issue(path=target, line=1, message="Missing English source file")]

    source_text = source.read_text(encoding="utf-8")
    bilingual_text = target.read_text(encoding="utf-8")

    audit_titles(source_text, bilingual_text, target, issues)
    audit_footnotes(source_text, bilingual_text, target, issues)
    audit_captions(source_text, bilingual_text, target, issues)

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Audit bilingual TeX files for missing EN/ZH structure in titles, captions, and footnotes."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional bilingual .tex files to audit. Defaults to chapters from main_bilingual.tex.",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Only print per-file issue counts instead of every issue detail.",
    )
    args = parser.parse_args()

    targets = resolve_targets(args.paths)
    if not targets:
        print("No target files found.", file=sys.stderr)
        return 1

    total = 0
    for target in targets:
        issues = audit_file(target)
        if issues:
            total += len(issues)
            if args.summary:
                print(f"[FAIL {len(issues):>3}] {target}")
            else:
                print(f"[FAIL] {target}")
                for issue in issues:
                    print(f"  - {issue.path}:{issue.line}: {issue.message}")
        else:
            print(f"[OK]   {target}")

    return 1 if total else 0


if __name__ == "__main__":
    raise SystemExit(main())
