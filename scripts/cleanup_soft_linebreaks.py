#!/usr/bin/env python3
"""Collapse unnecessary soft line breaks in chapter TeX files."""

from __future__ import annotations

import argparse
import re
from dataclasses import dataclass
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = ("chapters", "chapters_bilingual")
BLANK_BLOCK_RE = re.compile(r"(\n\s*\n+)")

STRUCTURAL_PREFIXES = (
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
    "\\tableofcontents",
    "\\parttitleblock",
    "\\bilingualchapter",
    "\\bilingualchapterstar",
    "\\bilingualsection",
    "\\bilingualsubsection",
    "\\bilingualpart",
    "\\bipairgap",
    "\\rawtablecaption",
    "\\rawfigurecaption",
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
    "\\begin{tabularx",
    "\\end{tabularx",
    "\\begin{longtable",
    "\\end{longtable",
    "\\begin{center",
    "\\end{center",
    "\\begingroup",
    "\\endgroup",
)

TRAILING_SKIPPABLE = set(" \t\r\n'\"”’`)]}.,;:!?%。，；：！？、》」』】")
LEADING_SKIPPABLE = set(" \t\r\n'\"“‘`([{（《「『【")
ROW_END_RE = re.compile(r"\\\\(?:\[[^\]]*\])?\s*$")
ENV_END_RE = re.compile(r"\\end\{[^}]+\}\s*$")
QUOTE_ENV_RE = re.compile(r"(\\begin\{quote\})(.*?)(\\end\{quote\})", re.DOTALL)
RULE_LINE_PATTERNS = (
    re.compile(r"^(\\cmidrule(?:\([^)]+\))?\{[^}]+\})(.+)$"),
    re.compile(r"^(\\addlinespace\[[^\]]+\]|\\addlinespace)(.+)$"),
    re.compile(r"^(\\toprule)(.+)$"),
    re.compile(r"^(\\midrule)(.+)$"),
    re.compile(r"^(\\bottomrule)(.+)$"),
)

STANDALONE_LINE_PREFIXES = (
    "\\toprule",
    "\\midrule",
    "\\bottomrule",
    "\\cmidrule",
    "\\addlinespace",
)

SEGMENT_START_PREFIXES = (
    "\\item",
    "\\par",
    "\\url{",
)

FORMATTING_GROUP_PREFIXES = (
    "{\\small",
    "{\\footnotesize",
    "{\\scriptsize",
    "{\\tiny",
    "{\\large",
    "{\\Large",
    "{\\LARGE",
    "{\\huge",
    "{\\Huge",
)


@dataclass(frozen=True)
class FileChange:
    path: Path
    blocks_changed: int


def default_targets() -> list[Path]:
    targets: list[Path] = []
    for dirname in TARGET_DIRS:
        base = ROOT / dirname
        for path in sorted(base.glob("*.tex")):
            targets.append(path)
    return targets


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("paths", nargs="*", help="Optional files to process.")
    parser.add_argument("--apply", action="store_true", help="Rewrite files in place.")
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit with status 1 if any files would change.",
    )
    return parser.parse_args()


def resolve_targets(raw_paths: list[str]) -> list[Path]:
    if not raw_paths:
        return default_targets()

    targets: list[Path] = []
    for raw in raw_paths:
        path = Path(raw)
        if not path.is_absolute():
            path = (ROOT / path).resolve()
        targets.append(path)
    return targets


def collapse_soft_breaks(block: str) -> str:
    lines = [line.strip() for line in block.splitlines()]
    segments = [line for line in lines if line]
    if not segments:
        return ""

    collapsed = segments[0]
    for segment in segments[1:]:
        if boundary_needs_space(collapsed, segment):
            collapsed += " "
        collapsed += segment

    collapsed = re.sub(r"\s*(?<![A-Za-z@])\\par(?![A-Za-z@])\s*", r" \\par ", collapsed)
    collapsed = re.sub(r"(\\(?:smallskip|medskip|bigskip))(?![\s\\])", r"\1 ", collapsed)
    collapsed = re.sub(r"\}(?=[A-Za-z0-9])", "} ", collapsed)
    collapsed = re.sub(r"\s+", " ", collapsed).strip()
    return collapsed


def is_standalone_line(line: str) -> bool:
    stripped = line.strip()
    if not stripped:
        return True
    if re.search(r"(?<!\\)%", stripped):
        return True
    if stripped.startswith(STANDALONE_LINE_PREFIXES):
        return True
    if stripped.startswith(FORMATTING_GROUP_PREFIXES):
        return True
    if stripped in {"{", "}"}:
        return True
    return False


def starts_new_segment(line: str) -> bool:
    stripped = line.strip()
    return stripped.startswith(SEGMENT_START_PREFIXES)


def line_ends_segment(line: str) -> bool:
    stripped = line.strip()
    if ROW_END_RE.search(stripped):
        return True
    if ENV_END_RE.search(stripped):
        return True
    if re.fullmatch(r"\\url\{[^{}]+\}", stripped):
        return True
    return False


def normalize_lines(lines: list[str]) -> list[str]:
    output: list[str] = []
    run: list[str] = []

    def flush_run() -> None:
        nonlocal run
        if not run:
            return
        output.append(collapse_soft_breaks("\n".join(run)))
        run = []

    expanded_lines: list[str] = []
    for line in lines:
        expanded_lines.extend(split_rule_line(line))

    for line in expanded_lines:
        if is_standalone_line(line):
            flush_run()
            output.append(line)
            continue

        if starts_new_segment(line):
            flush_run()

        run.append(line)
        if line_ends_segment(line):
            flush_run()

    flush_run()
    return output


def normalize_block(block: str) -> str:
    lines = [line.strip() for line in block.splitlines() if line.strip()]
    if len(lines) <= 1:
        return block.strip()
    return "\n".join(normalize_lines(lines))


def normalize_quote_environments(text: str) -> str:
    def repl(match: re.Match[str]) -> str:
        begin, body, end = match.groups()
        lines = [line.strip() for line in body.splitlines() if line.strip()]
        if not lines:
            return f"{begin}\n{end}"
        normalized = "\n".join(normalize_lines(lines))
        return f"{begin}\n{normalized}\n{end}"

    return QUOTE_ENV_RE.sub(repl, text)


def split_rule_line(line: str) -> list[str]:
    stripped = line.strip()
    if re.fullmatch(r"\\addlinespace(?:\[[^\]]+\])?", stripped):
        return [stripped]
    for pattern in RULE_LINE_PATTERNS:
        match = pattern.match(stripped)
        if not match:
            continue
        command, rest = match.groups()
        rest = rest.strip()
        if not rest:
            return [stripped]
        return [command, rest]
    return [stripped]


def should_merge_blocks(left: str, right: str) -> bool:
    left = left.strip()
    right = right.strip()
    if not left or not right:
        return False

    left_first = next((line.strip() for line in left.splitlines() if line.strip()), "")
    right_first = next((line.strip() for line in right.splitlines() if line.strip()), "")
    if not left_first or not right_first:
        return False
    if is_standalone_line(left_first) or is_standalone_line(right_first):
        return False
    if left_first.startswith(SEGMENT_START_PREFIXES) or right_first.startswith(SEGMENT_START_PREFIXES):
        return False
    if line_ends_segment(left.splitlines()[-1].strip()):
        return False

    left_tail = left.rstrip()
    while left_tail and left_tail[-1] in TRAILING_SKIPPABLE:
        if left_tail.endswith("\\%"):
            left_tail = left_tail[:-2]
            continue
        left_tail = left_tail[:-1]
    if not left_tail:
        return False
    if left_tail[-1] in ".!?:;。！？：；":
        return False

    right_head = right.lstrip()
    if right_head.startswith("\\footnote{") or right_head.startswith("\\text"):
        return True

    first_char = right_head[0]
    if first_char.islower() or first_char.isdigit():
        return True
    return False


def boundary_needs_space(left: str, right: str) -> bool:
    left_kind = trailing_boundary_kind(left)
    right_kind = leading_boundary_kind(right)
    if left_kind == "latin" and right_kind in {"latin", "command"}:
        return True
    if left_kind == "command" and right_kind == "latin":
        return True
    return False


def trailing_boundary_kind(text: str) -> str:
    idx = len(text) - 1
    while idx >= 0:
        char = text[idx]
        if char in TRAILING_SKIPPABLE:
            if char == "%" and idx > 0 and text[idx - 1] == "\\":
                idx -= 2
                continue
            idx -= 1
            continue
        if char.isascii() and char.isalnum():
            return "latin"
        if char == "\\":
            return "command"
        return "other"
    return "other"


def leading_boundary_kind(text: str) -> str:
    idx = 0
    while idx < len(text):
        char = text[idx]
        if char in LEADING_SKIPPABLE:
            idx += 1
            continue
        if char == "\\":
            return "command"
        if char.isascii() and char.isalnum():
            return "latin"
        return "other"
    return "other"


def rewrite_plain_text(text: str) -> tuple[str, int]:
    had_trailing_newline = text.endswith("\n")
    body = text.rstrip("\n")
    if not body:
        return text, 0

    parts = BLANK_BLOCK_RE.split(body)
    changed = 0
    merged_parts: list[str] = []
    idx = 0
    while idx < len(parts):
        part = parts[idx]
        if (
            idx + 2 < len(parts)
            and BLANK_BLOCK_RE.fullmatch(parts[idx + 1] or "")
            and should_merge_blocks(part, parts[idx + 2])
        ):
            merged_parts.append(part.rstrip() + "\n" + parts[idx + 2].lstrip())
            changed += 1
            idx += 3
            continue
        merged_parts.append(part)
        idx += 1

    parts = merged_parts
    rewritten: list[str] = []
    for part in parts:
        if not part:
            continue
        if BLANK_BLOCK_RE.fullmatch(part):
            rewritten.append(part)
            continue

        if "\n" in part:
            collapsed = normalize_block(part)
            if collapsed != part.strip():
                part = collapsed
                changed += 1
        rewritten.append(part)

    output = "".join(rewritten)
    output = normalize_quote_environments(output)
    output = re.sub(r"\s*\\par\s+\\medskip\s*", "\n\\\\par\n\\\\medskip\n", output)
    if had_trailing_newline:
        output += "\n"
    return output, (changed if output != text else 0)


def rewrite_file(path: Path) -> tuple[str, int]:
    text = path.read_text(encoding="utf-8")
    return rewrite_plain_text(text)


def main() -> int:
    args = parse_args()
    changes: list[FileChange] = []

    for path in resolve_targets(args.paths):
        new_text, blocks_changed = rewrite_file(path)
        if blocks_changed == 0:
            continue
        changes.append(FileChange(path=path, blocks_changed=blocks_changed))
        if args.apply:
            path.write_text(new_text, encoding="utf-8")

    action = "Rewrote" if args.apply else "Would rewrite"
    total_blocks = sum(change.blocks_changed for change in changes)
    print(f"{action} {total_blocks} blocks across {len(changes)} files.")
    for change in changes:
        try:
            display_path = change.path.relative_to(ROOT)
        except ValueError:
            display_path = change.path
        print(f"  {display_path}: {change.blocks_changed}")

    if args.check and changes:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
