#!/usr/bin/env python3
"""Restore inline bold spans in chapter sources from the source PDF."""

from __future__ import annotations

import argparse
import re
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from pathlib import Path


DEFAULT_SOURCE_PDF = (
    "Systematic Trading A unique new method for designing trading and investing systems-Robert.pdf"
)
SKIP_ENVS = {
    "figure",
    "table",
    "tabular",
    "tabularx",
    "longtable",
    "minipage",
    "center",
    "multicols",
}
SKIP_COMMANDS = {
    "addcontentsline",
    "phantomsection",
    "markboth",
    "includegraphics",
    "label",
    "ref",
    "pageref",
    "url",
    "hypersetup",
    "thispagestyle",
    "pagestyle",
    "frontmatter",
    "mainmatter",
    "appendix",
    "tableofcontents",
    "clearpage",
    "cleardoublepage",
    "toprule",
    "midrule",
    "bottomrule",
    "cmidrule",
    "addlinespace",
    "renewcommand",
    "setlength",
    "resizebox",
    "noindent",
    "centering",
    "scriptsize",
    "small",
    "footnotesize",
    "normalsize",
    "large",
    "Large",
    "huge",
    "Huge",
    "vspace",
    "hspace",
    "medskip",
    "smallskip",
    "begingroup",
    "endgroup",
    "par",
    "newline",
    "rule",
    "hfill",
    "leftskip",
    "rightskip",
    "raggedright",
    "frenchspacing",
}
COMMANDS_WITH_ARGS = {
    "addcontentsline": 3,
    "markboth": 2,
    "includegraphics": 2,
    "label": 1,
    "ref": 1,
    "pageref": 1,
    "url": 1,
    "hypersetup": 1,
    "thispagestyle": 1,
    "pagestyle": 1,
    "renewcommand": 2,
    "setlength": 2,
    "resizebox": 3,
    "vspace": 1,
    "hspace": 1,
    "rule": 2,
}
PAGE_RANGES = [
    (8, 17, "chapters/preface.tex"),
    (18, 25, "chapters/introduction.tex"),
    (28, 41, "chapters/chapter_one.tex"),
    (42, 65, "chapters/chapter_two.tex"),
    (68, 85, "chapters/chapter_three.tex"),
    (86, 107, "chapters/chapter_four.tex"),
    (110, 117, "chapters/chapter_five.tex"),
    (118, 125, "chapters/chapter_six.tex"),
    (126, 141, "chapters/chapter_seven.tex"),
    (142, 151, "chapters/chapter_eight.tex"),
    (152, 169, "chapters/chapter_nine.tex"),
    (170, 181, "chapters/chapter_ten.tex"),
    (182, 193, "chapters/chapter_eleven.tex"),
    (194, 223, "chapters/chapter_twelve.tex"),
    (226, 241, "chapters/chapter_thirteen.tex"),
    (242, 261, "chapters/chapter_fourteen.tex"),
    (262, 275, "chapters/chapter_fifteen.tex"),
    (276, 277, "chapters/epilogue.tex"),
    (292, 297, "chapters/appendix_a.tex"),
    (298, 305, "chapters/appendix_b.tex"),
    (306, 313, "chapters/appendix_c.tex"),
    (314, 317, "chapters/appendix_d.tex"),
]
CLEANUP_PATTERNS = [
    (r"\\textbf\{trading\}\s+rule\b", r"\\textbf{trading rule}"),
    (r"\\textbf\{trading\}\s+rules\b", r"\\textbf{trading rules}"),
    (r"\\textbf\{trading\}\s+system\b", r"\\textbf{trading system}"),
    (r"\\textbf\{trading\}\s+systems\b", r"\\textbf{trading systems}"),
    (r"\\textbf\{trading\}\s+capital\b", r"\\textbf{trading capital}"),
    (r"\\textbf\{asset allocating\}\s+investor\b", r"\\textbf{asset allocating investor}"),
    (r"\\textbf\{asset allocating\}\s+investors\b", r"\\textbf{asset allocating investors}"),
    (r"\\textbf\{asset\}\s+class\b", r"\\textbf{asset class}"),
    (r"\\textbf\{asset\}\s+classes\b", r"\\textbf{asset classes}"),
    (r"\\textbf\{collective\}\s+funds\b", r"\\textbf{collective funds}"),
    (r"\\textbf\{price\}\s+volatility\b", r"\\textbf{price volatility}"),
    (r"\\textbf\{execution\}\s+cost\b", r"\\textbf{execution cost}"),
    (r"\\textbf\{execution\}\s+costs\b", r"\\textbf{execution costs}"),
    (r"\\textbf\{volatility\}\s+target\b", r"\\textbf{volatility target}"),
    (r"\\textbf\{percentage\}\s+volatility target\b", r"\\textbf{percentage volatility target}"),
    (r"\\textbf\{Sharpe\}\s+ratio\b", r"\\textbf{Sharpe ratio}"),
    (r"\\textbf\{standard\}\s+deviation\b", r"\\textbf{standard deviation}"),
    (r"\\textbf\{forecast\}\s+weights\b", r"\\textbf{forecast weights}"),
    (r"\\textbf\{instrument\}\s+weight\b", r"\\textbf{instrument weight}"),
    (r"\\textbf\{instrument\}\s+weights\b", r"\\textbf{instrument weights}"),
    (r"\\textbf\{instrument\}\s+block\b", r"\\textbf{instrument block}"),
    (r"\\textbf\{instrument\}\s+blocks\b", r"\\textbf{instrument blocks}"),
    (r"\\textbf\{trend\}\s+following\b", r"\\textbf{trend following}"),
    (r"\\textbf\{semi-automatic\}\s+trader\b", r"\\textbf{semi-automatic trader}"),
    (r"\\textbf\{semi-automatic\}\s+traders\b", r"\\textbf{semi-automatic traders}"),
    (r"\\textbf\{staunch systems\}\s+trader\b", r"\\textbf{staunch systems trader}"),
    (r"\\textbf\{alternative\}\s+beta\b", r"\\textbf{alternative beta}"),
    (r"\\textbf\{relative\}\s+value\b", r"\\textbf{relative value}"),
    (r"\\textbf\{cognitive\}\s+biases\b", r"\\textbf{cognitive biases}"),
    (r"\\textbf\{portfolio\}\s+\\textbf\{optimisation\}", r"\\textbf{portfolio optimisation}"),
    (
        r"\\textbf\{Gaussian normal\}\s+\\textbf\{distribution\}",
        r"\\textbf{Gaussian normal distribution}",
    ),
]


@dataclass(frozen=True)
class Token:
    value: str
    start: int
    end: int


@dataclass(frozen=True)
class Candidate:
    page: int
    file_path: Path
    raw: str
    phrase_tokens: tuple[str, ...]
    left_context: tuple[str, ...]
    right_context: tuple[str, ...]


@dataclass(frozen=True)
class Replacement:
    start: int
    end: int
    raw: str
    page: int
    score: int


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def source_pdf_path(root: Path, pdf_path_arg: str | None) -> Path:
    if pdf_path_arg:
        return Path(pdf_path_arg).expanduser().resolve()
    return root / DEFAULT_SOURCE_PDF


def file_for_page(root: Path, page: int) -> Path | None:
    for start, end, rel in PAGE_RANGES:
        if start <= page <= end:
            return root / rel
    return None


def run_command(args: list[str]) -> None:
    subprocess.run(args, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def normalized_words(text: str) -> list[str]:
    return re.findall(r"[a-z0-9]+", text.lower())


def keep_phrase(words: list[str], raw: str) -> bool:
    if not words:
        return False
    if len(words) == 1:
        word = words[0]
        if len(word) < 5:
            return False
        if raw.strip().endswith("-"):
            return False
        if word in {"figure", "table", "chapter", "appendix"}:
            return False
    return True


def extract_candidates(root: Path, pdf_path: Path) -> dict[Path, list[Candidate]]:
    with tempfile.TemporaryDirectory() as tmpdir:
        xml_path = Path(tmpdir) / "out.xml"
        run_command(["pdftohtml", "-xml", str(pdf_path), str(xml_path)])
        tree = ET.parse(xml_path)

    candidates: dict[Path, list[Candidate]] = {}
    for page in tree.getroot().findall("page"):
        page_number = int(page.attrib["number"])
        file_path = file_for_page(root, page_number)
        if file_path is None:
            continue

        for text_node in page.findall("text"):
            children = list(text_node)
            if not any(child.tag == "b" for child in children):
                continue

            bold_only = "".join(child.text or "" for child in children if child.tag == "b").strip()
            full_text = "".join(text_node.itertext()).strip()
            if not full_text or full_text == bold_only:
                continue

            parts: list[tuple[str, str]] = []
            if text_node.text:
                parts.append(("plain", text_node.text))
            for child in children:
                if child.tag == "b":
                    parts.append(("bold", child.text or ""))
                if child.tail:
                    parts.append(("plain", child.tail))

            line_words: list[str] = []
            bold_ranges: list[tuple[int, int, str]] = []
            for kind, segment in parts:
                words = normalized_words(segment)
                start = len(line_words)
                line_words.extend(words)
                if kind == "bold" and words:
                    bold_ranges.append((start, len(line_words), segment.strip()))

            for start, end, raw in bold_ranges:
                phrase_tokens = tuple(line_words[start:end])
                if not keep_phrase(list(phrase_tokens), raw):
                    continue
                candidate = Candidate(
                    page=page_number,
                    file_path=file_path,
                    raw=raw,
                    phrase_tokens=phrase_tokens,
                    left_context=tuple(line_words[max(0, start - 4) : start]),
                    right_context=tuple(line_words[end : end + 4]),
                )
                candidates.setdefault(file_path, []).append(candidate)

    return candidates


def skip_whitespace(text: str, index: int) -> int:
    while index < len(text) and text[index].isspace():
        index += 1
    return index


def skip_optional_args(text: str, index: int) -> int:
    index = skip_whitespace(text, index)
    while index < len(text) and text[index] == "[":
        depth = 1
        index += 1
        while index < len(text) and depth:
            if text[index] == "[":
                depth += 1
            elif text[index] == "]":
                depth -= 1
            index += 1
        index = skip_whitespace(text, index)
    return index


def skip_braced_group(text: str, index: int) -> int:
    index = skip_whitespace(text, index)
    if index >= len(text) or text[index] != "{":
        return index
    depth = 1
    index += 1
    while index < len(text) and depth:
        if text[index] == "\\":
            index += 2
            continue
        if text[index] == "{":
            depth += 1
        elif text[index] == "}":
            depth -= 1
        index += 1
    return index


def tokenize_tex(text: str) -> list[Token]:
    tokens: list[Token] = []
    index = 0
    limit = len(text)

    while index < limit:
        if text[index] == "%" and (index == 0 or text[index - 1] != "\\"):
            line_end = text.find("\n", index)
            if line_end == -1:
                break
            index = line_end + 1
            continue

        if text.startswith("\\begin{", index):
            env_name_start = index + 7
            env_name_end = text.find("}", env_name_start)
            if env_name_end != -1:
                env_name = text[env_name_start:env_name_end]
                if env_name in SKIP_ENVS:
                    end_tag = f"\\end{{{env_name}}}"
                    end_index = text.find(end_tag, env_name_end + 1)
                    if end_index != -1:
                        index = end_index + len(end_tag)
                        continue

        if text[index] == "\\":
            next_index = index + 1
            if next_index < limit and text[next_index].isalpha():
                while next_index < limit and (
                    text[next_index].isalpha() or text[next_index] == "@"
                ):
                    next_index += 1

                command = text[index + 1 : next_index]
                if next_index < limit and text[next_index] == "*":
                    next_index += 1
                next_index = skip_optional_args(text, next_index)

                if command in {"begin", "end"}:
                    index = skip_braced_group(text, next_index)
                    continue

                if command in SKIP_COMMANDS:
                    arg_count = COMMANDS_WITH_ARGS.get(command, 0)
                    index = next_index
                    for _ in range(arg_count):
                        index = skip_braced_group(text, index)
                    continue

                index = next_index
                continue

            index += 2
            continue

        if text[index].isalnum():
            start = index
            while index < limit and text[index].isalnum():
                index += 1
            tokens.append(Token(value=text[start:index].lower(), start=start, end=index))
            continue

        index += 1

    return tokens


def context_score(words: list[str], start: int, end: int, left: tuple[str, ...], right: tuple[str, ...]) -> int:
    left_score = 0
    for width in range(1, min(len(left), start) + 1):
        if words[start - width : start] == list(left[-width:]):
            left_score = width

    right_score = 0
    for width in range(1, min(len(right), len(words) - end) + 1):
        if words[end : end + width] == list(right[:width]):
            right_score = width

    return left_score + right_score


def inside_existing_textbf(text: str, start: int) -> bool:
    window_start = max(0, start - 32)
    prefix = text[window_start:start]
    last_textbf = prefix.rfind("\\textbf{")
    if last_textbf == -1:
        return False
    last_close = prefix.rfind("}")
    return last_textbf > last_close


def expand_span_with_punctuation(text: str, start: int, end: int, raw: str) -> tuple[int, int]:
    stripped = raw.strip()
    leading_match = re.match(r"^[^A-Za-z0-9]+", stripped)
    trailing_match = re.search(r"[^A-Za-z0-9]+$", stripped)

    if leading_match:
        leading = leading_match.group(0)
        candidate_start = max(0, start - len(leading))
        if text[candidate_start:start] == leading:
            start = candidate_start

    if trailing_match:
        trailing = trailing_match.group(0)
        candidate_end = min(len(text), end + len(trailing))
        if text[end:candidate_end] == trailing:
            end = candidate_end

    return start, end


def match_file(file_path: Path, file_candidates: list[Candidate]) -> list[Replacement]:
    text = file_path.read_text(encoding="utf-8")
    tokens = tokenize_tex(text)
    words = [token.value for token in tokens]
    replacements: list[Replacement] = []
    cursor = 0
    seen_spans: set[tuple[int, int]] = set()

    for candidate in file_candidates:
        phrase = list(candidate.phrase_tokens)
        phrase_len = len(phrase)
        matches: list[tuple[int, int, int]] = []

        for start in range(cursor, len(words) - phrase_len + 1):
            if words[start : start + phrase_len] != phrase:
                continue
            end = start + phrase_len
            score = context_score(
                words,
                start,
                end,
                candidate.left_context,
                candidate.right_context,
            )
            if score:
                matches.append((score, start, end))

        if not matches and cursor:
            for start in range(0, len(words) - phrase_len + 1):
                if words[start : start + phrase_len] != phrase:
                    continue
                end = start + phrase_len
                score = context_score(
                    words,
                    start,
                    end,
                    candidate.left_context,
                    candidate.right_context,
                )
                if score:
                    matches.append((score, start, end))

        if not matches:
            continue

        matches.sort(key=lambda item: (-item[0], item[1]))
        best_score, start_idx, end_idx = matches[0]
        if best_score < 2:
            continue

        raw_start = tokens[start_idx].start
        raw_end = tokens[end_idx - 1].end
        raw_start, raw_end = expand_span_with_punctuation(text, raw_start, raw_end, candidate.raw)
        span = (raw_start, raw_end)
        if span in seen_spans:
            cursor = end_idx
            continue
        if inside_existing_textbf(text, raw_start):
            cursor = end_idx
            continue

        replacements.append(
            Replacement(
                start=raw_start,
                end=raw_end,
                raw=text[raw_start:raw_end],
                page=candidate.page,
                score=best_score,
            )
        )
        seen_spans.add(span)
        cursor = end_idx

    return replacements


def apply_replacements(text: str, replacements: list[Replacement]) -> str:
    updated = text
    for replacement in sorted(replacements, key=lambda item: item.start, reverse=True):
        updated = (
            updated[: replacement.start]
            + "\\textbf{"
            + updated[replacement.start : replacement.end]
            + "}"
            + updated[replacement.end :]
        )
    return updated


def cleanup_text(text: str) -> str:
    updated = text
    changed = True
    while changed:
        changed = False
        for pattern, replacement in CLEANUP_PATTERNS:
            newer = re.sub(pattern, replacement, updated)
            if newer != updated:
                updated = newer
                changed = True
    return updated


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pdf", help="Path to the source PDF.")
    parser.add_argument("--dry-run", action="store_true", help="Report matches without editing.")
    parser.add_argument(
        "--limit-files",
        nargs="*",
        default=None,
        help="Optional list of chapter paths to restrict processing.",
    )
    args = parser.parse_args()

    root = project_root()
    pdf_path = source_pdf_path(root, args.pdf)
    candidates_by_file = extract_candidates(root, pdf_path)

    allowed_files = None
    if args.limit_files:
        allowed_files = {Path(item).resolve() for item in args.limit_files}

    total_replacements = 0
    for file_path in sorted(candidates_by_file):
        if allowed_files and file_path.resolve() not in allowed_files:
            continue

        replacements = match_file(file_path, candidates_by_file[file_path])
        original = file_path.read_text(encoding="utf-8")
        updated = apply_replacements(original, replacements)
        updated = cleanup_text(updated)

        if replacements:
            total_replacements += len(replacements)
            rel_path = file_path.relative_to(root)
            print(f"{rel_path}: {len(replacements)} matches")
            for replacement in replacements[:8]:
                snippet = " ".join(replacement.raw.split())
                print(f"  p.{replacement.page} score={replacement.score}: {snippet}")

        if args.dry_run:
            continue

        if updated != original:
            file_path.write_text(updated, encoding="utf-8")

    print(f"Total replacements: {total_replacements}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
