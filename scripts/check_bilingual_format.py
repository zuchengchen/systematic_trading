#!/usr/bin/env python3
"""Check whether bilingual chapter files follow EN -> ZH paragraph pairing."""

from __future__ import annotations

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


INLINE_BILINGUAL_COMMANDS = (
    "\\bichaptertitle{",
    "\\bisectiontitle{",
    "\\bisubsectiontitle{",
    "\\bilingualchapter{",
    "\\bilingualchapterstar{",
    "\\bilingualsection{",
    "\\bilingualsubsection{",
    "\\bilingualpart{",
    "\\rawfigurecaption{",
    "\\caption{",
    "\\audiencebox{",
    "\\conceptbox{",
)


STRUCTURAL_PREFIXES = (
    "\\bipairgap",
    "\\chapter",
    "\\section",
    "\\subsection",
    "\\subsubsection",
    "\\phantomsection",
    "\\addcontentsline",
    "\\markboth",
    "\\label",
    "\\clearpage",
    "\\thispagestyle",
    "\\vspace",
    "\\begin{figure",
    "\\end{figure",
    "\\begin{table",
    "\\end{table",
    "\\begin{quote",
    "\\end{quote",
    "\\begin{enumerate",
    "\\end{enumerate",
    "\\begin{itemize",
    "\\end{itemize",
    "\\begin{description",
    "\\end{description",
    "\\begin{multicols",
    "\\end{multicols",
    "\\begin{tabular",
    "\\end{tabular",
    "\\begin{longtable",
    "\\end{longtable",
    "\\begin{bilingualtableblock",
    "\\end{bilingualtableblock",
    "\\begin{center",
    "\\end{center",
    "\\begingroup",
    "\\endgroup",
    "\\medskip",
    "\\smallskip",
    "\\bigskip",
    "\\noindent\\begin{",
)


LATIN_WORD_RE = re.compile(r"[A-Za-z]+(?:[-'][A-Za-z]+)?")
LATIN_CHAR_RE = re.compile(r"[A-Za-z]")
CJK_RE = re.compile(r"[\u4e00-\u9fff]")
COMMENT_RE = re.compile(r"(?<!\\)%.*$")
WRAPPED_BLOCK_RE = re.compile(
    r"^\s*\\begin\{(?:englishblock|chineseblock)\}\s*(.*?)\s*\\end\{(?:englishblock|chineseblock)\}\s*$",
    re.DOTALL,
)


@dataclass
class Block:
    start_line: int
    end_line: int
    text: str


def split_blocks(text: str) -> list[Block]:
    lines = text.splitlines()
    blocks: list[Block] = []
    start: int | None = None

    for idx, line in enumerate(lines, start=1):
        if line.strip():
            if start is None:
                start = idx
        else:
            if start is not None:
                block_text = "\n".join(lines[start - 1 : idx - 1]).strip()
                if block_text:
                    blocks.append(Block(start, idx - 1, block_text))
                start = None

    if start is not None:
        block_text = "\n".join(lines[start - 1 :]).strip()
        if block_text:
            blocks.append(Block(start, len(lines), block_text))

    return blocks


def strip_tex(text: str) -> str:
    text = strip_command_with_braces(text, "footnote")
    text = re.sub(r"\\\((?:.|\n)*?\\\)", " ", text)
    text = re.sub(r"\\\[(?:.|\n)*?\\\]", " ", text)
    text = re.sub(r"\$(?:.|\n)*?\$", " ", text)
    text = COMMENT_RE.sub("", text)
    text = re.sub(r"\\[A-Za-z@]+(?:\*?)", " ", text)
    text = re.sub(r"\\.", " ", text)
    text = re.sub(r"[{}$&_^~]", " ", text)
    return text


def strip_command_with_braces(text: str, command: str) -> str:
    needle = f"\\{command}" + "{"
    while True:
        start = text.find(needle)
        if start == -1:
            return text
        i = start + len(needle)
        depth = 1
        while i < len(text) and depth:
            if text[i] == "{":
                depth += 1
            elif text[i] == "}":
                depth -= 1
            i += 1
        if depth != 0:
            return text
        text = text[:start] + " " + text[i:]


def unwrap_wrapped_block(text: str) -> str:
    match = WRAPPED_BLOCK_RE.match(text)
    if match:
        return match.group(1).strip()
    return text


def classify(block: Block) -> str:
    stripped = unwrap_wrapped_block(block.text.strip())

    if any(command in stripped for command in INLINE_BILINGUAL_COMMANDS):
        return "inline"

    if stripped.startswith(STRUCTURAL_PREFIXES):
        return "structural"

    if stripped.startswith("{\\footnotesize") or stripped.startswith("{\\small") or stripped.startswith("{\\scriptsize"):
        return "structural"

    if is_standalone_url_block(stripped):
        return "structural"

    if stripped.startswith("\\noindent *") or stripped.startswith("\\noindent **") or stripped.startswith("\\noindent ***"):
        return "structural"

    if any(
        token in stripped
        for token in (
            "\\detokenize{",
            "\\ttfamily",
            "\\includegraphics",
            "\\toprule",
            "\\midrule",
            "\\bottomrule",
            "\\begin{tabular",
            "\\begin{tabularx}",
            "\\begin{longtable",
            "\\begin{minipage",
            "\\begin{multicols",
        )
    ):
        return "structural"

    if re.fullmatch(r"(\\[A-Za-z@]+(?:\*?)|\{|\}|\[.*?\]|\(.*?\)|\s|[-–—:;,.])+",
                    stripped, flags=re.DOTALL):
        return "structural"

    plain = strip_tex(stripped)
    cjk_count = len(CJK_RE.findall(plain))
    latin_words = LATIN_WORD_RE.findall(plain)
    latin_count = len(latin_words)
    latin_chars = len(LATIN_CHAR_RE.findall(plain))

    if cjk_count == 0 and latin_count == 0:
        return "structural"

    if cjk_count >= 8 and latin_chars <= max(24, cjk_count // 2):
        return "zh"

    if latin_count >= 8 and cjk_count == 0:
        return "en"

    if latin_count >= 8 and cjk_count <= max(4, latin_chars // 8):
        return "en"

    if cjk_count >= 8 and latin_chars >= 8:
        return "mixed"

    if cjk_count > 0 and latin_count == 0:
        return "zh"

    if latin_count > 0 and cjk_count == 0:
        return "en"

    return "mixed"


def is_standalone_url_block(text: str) -> bool:
    candidate = text.strip()
    if not candidate:
        return False
    if candidate.startswith("\\noindent"):
        candidate = candidate[len("\\noindent"):].strip()
    return bool(re.fullmatch(r"\\url\{[^{}]+\}", candidate))


def excerpt(text: str, limit: int = 90) -> str:
    single_line = " ".join(text.split())
    if len(single_line) <= limit:
        return single_line
    return single_line[: limit - 3] + "..."


def iter_targets(paths: Iterable[str]) -> list[Path]:
    if paths:
        return [Path(p) for p in paths]
    root = Path(__file__).resolve().parents[1] / "chapters_bilingual"
    return sorted(root.glob("*.tex"))


def check_file(path: Path) -> list[str]:
    text = path.read_text(encoding="utf-8")
    blocks = split_blocks(text)
    issues: list[str] = []
    pending_en: Block | None = None

    for block in blocks:
        kind = classify(block)

        if kind in {"structural", "inline", "mixed"}:
            continue

        if kind == "en":
            if pending_en is not None:
                issues.append(
                    f"{path}:{pending_en.start_line}: English block is not followed by a Chinese block"
                    f" | {excerpt(pending_en.text)}"
                )
            pending_en = block
            continue

        if kind == "zh":
            if pending_en is None:
                issues.append(
                    f"{path}:{block.start_line}: Chinese block appears without a preceding English block"
                    f" | {excerpt(block.text)}"
                )
            else:
                pending_en = None

    if pending_en is not None:
        issues.append(
            f"{path}:{pending_en.start_line}: File ends with an English block lacking Chinese follow-up"
            f" | {excerpt(pending_en.text)}"
        )

    return issues


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Check whether bilingual TeX files roughly follow EN -> ZH paragraph pairing."
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Optional .tex files to check. Defaults to chapters_bilingual/*.tex",
    )
    parser.add_argument(
        "--summary",
        action="store_true",
        help="Only print per-file issue counts instead of every issue detail.",
    )
    args = parser.parse_args()

    targets = iter_targets(args.paths)
    if not targets:
        print("No target files found.", file=sys.stderr)
        return 1

    total_issues = 0
    for path in targets:
        issues = check_file(path)
        if issues:
            total_issues += len(issues)
            if args.summary:
                print(f"[FAIL {len(issues):>3}] {path}")
            else:
                print(f"[FAIL] {path}")
                for issue in issues:
                    print(f"  - {issue}")
        else:
            print(f"[OK]   {path}")

    return 1 if total_issues else 0


if __name__ == "__main__":
    raise SystemExit(main())
